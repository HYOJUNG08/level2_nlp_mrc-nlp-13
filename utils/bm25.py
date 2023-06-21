from omegaconf import OmegaConf
import json
import os
import pickle
import time
from contextlib import contextmanager
from typing import List, Optional, Tuple, Union
import re

import faiss
import numpy as np
import pandas as pd
from datasets import Dataset, concatenate_datasets, load_from_disk
from tqdm.auto import tqdm

from rank_bm25 import BM25Okapi
from transformers import AutoTokenizer
from utils.cross_encoder import ce,ce_doc
from utils.preprocess import *

@contextmanager
def timer(name):
    t0 = time.time()
    yield
    print(f"[{name}] done in {time.time() - t0:.3f} s")


class BM25Retrieval:
    def __init__(
        self,
        tokenize_fn,
        data_path: Optional[str] = "../data/",
        context_path: Optional[str] = "wikipedia_documents.json",
        stage = 'predict',
        use_normalize = False,
        use_sub = False,
        use_drop_duplicated_wiki= False,
        use_drop_less_than_50_percent_of_korean= False,
        use_drop_too_long_text = False,
        use_add_title_to_text = False
    ) -> None:
        
        self.stage = stage
        self.data_path = data_path
        with open(os.path.join(data_path, context_path), "r", encoding="utf-8") as f:
            wiki = json.load(f)
            
        if use_drop_duplicated_wiki: # 위키피디아 text 중복 제거
            wiki = drop_duplicated_wiki(wiki)
        if use_drop_less_than_50_percent_of_korean: # 위키피디아 text에서 한글비중 50%이하 제거
            wiki = drop_less_than_50_percent_of_korean(wiki)
        if use_drop_too_long_text: # 위키피다아 text 길이 가장 긴 상위 1% 제거
            wiki = drop_too_long_text(wiki)
        if use_add_title_to_text: # 검색능력 향상을 위해 title을 text 앞에 붙이기
            wiki = add_title_to_text(wiki)

        self.contexts = list(
            dict.fromkeys([v["text"] for v in wiki.values()])
            )  # set 은 매번 순서가 바뀌므로
        print(f"Lengths of unique contexts : {len(self.contexts)}")

        # context 데이터 전처리(sub=특수문자 처리, normalize=반각 문자 변환)
        if use_sub:
            self.contexts = list_sub_context(self.contexts)
        if use_normalize:
            self.contexts = list_normalize_context(self.contexts)

        self.tokenize_fn = tokenize_fn
        self.tokenized_contexts = list()
        self.bm25 = None 
    
    def get_bm25(self) -> None:
    
        pickle_name = f"tokenized_context_{self.stage}.bin"
        emd_path = os.path.join(self.data_path, pickle_name)
    
        if os.path.isfile(emd_path):
            with open(emd_path, "rb") as file:
                self.tokenized_contexts = pickle.load(file)
            print("Tokenized context pickle load.")
        else:
            for doc in tqdm(self.contexts, desc='Tokenizing for BM25'):
                self.tokenized_contexts.append(self.tokenize_fn(doc))
            print("Finished Tokenizing!")            
            
            with open(emd_path, "wb") as file:
                pickle.dump(self.tokenized_contexts, file)
            print("Tokenized context pickle saved.")
        self.bm25 = BM25Okapi(self.tokenized_contexts)
        print("Finished setting BM25!")

    def retrieve(
            self, query_or_dataset: Union[str, Dataset], topk: Optional[int] = 1, add_ce:Optional[bool]=True,
    ) -> Union[Tuple[List, List], pd.DataFrame]:
        
        assert len(self.tokenized_contexts) != 0, "get_bm25() 메소드를 먼저 실행해주세요."

        if isinstance(query_or_dataset, str):
            doc_scores, doc_indices = self.get_relevant_doc(query_or_dataset, k=topk)
            print("[Search query]\n", query_or_dataset, "\n")
            print("instance is string")
            if add_ce==True:
                topk_index=[]
                for i in range(topk):
                    #print(f"Top-{i+1} passage with score {doc_scores[i]:4f}")
                    #print(self.contexts[doc_indices[i]])
                    topk_index.append(doc_indices[i])
                    similarity_scores, contexts = ce(query_or_dataset,topk_index,self.contexts)
                    return (similarity_scores, contexts)

            else : return (doc_scores, [self.contexts[doc_indices[i]] for i in range(topk)])

        elif isinstance(query_or_dataset, Dataset):
            print("instance is dataset")
            # Retrieve한 Passage를 pd.DataFrame으로 반환합니다.
            total = []
            with timer("query exhaustive search"):
                doc_scores, doc_indices = self.get_relevant_doc_bulk(
                    query_or_dataset["question"], k=topk
                )
                if add_ce==True:
                    doc_scores, doc_indices = ce_doc(query_or_dataset["question"],doc_indices,self.contexts)
            for idx, example in enumerate(
                tqdm(query_or_dataset, desc="BM25 retrieval: ")
            ):
                tmp = {
                    # Query와 해당 id를 반환합니다.
                    "question": example["question"],
                    "id": example["id"],
                    # Retrieve한 Passage의 id, context를 반환합니다.
                    "context": " ".join(
                        [self.contexts[pid] for pid in doc_indices[idx]]
                    ),
                }
                if "context" in example.keys() and "answers" in example.keys():
                    # validation 데이터를 사용하면 ground_truth context와 answer도 반환합니다.
                    tmp["original_context"] = example["context"]
                    tmp["answers"] = example["answers"]
                total.append(tmp)

            cqas = pd.DataFrame(total)
            return cqas
        
    def get_relevant_doc(self, query: str, k: Optional[int] = 1) -> Tuple[List, List]:

        """
        Arguments:
            query (str):
                하나의 Query를 받습니다.
            k (Optional[int]): 1
                상위 몇 개의 Passage를 반환할지 정합니다.
        Note:
            vocab 에 없는 이상한 단어로 query 하는 경우 assertion 발생 (예) 뙣뙇?
        """

        with timer("transform"):
            tokenized_query = self.tokenize_fn(query)
            result = self.bm25.get_scores(tokenized_query) / 100

        if not isinstance(result, np.ndarray):
            result = result.toarray()

        sorted_result = np.argsort(result)[::-1]
        doc_score = result[sorted_result].tolist()[:k]
        doc_indices = sorted_result.tolist()[:k]
        return doc_score, doc_indices
    
    def get_relevant_doc_bulk(
        self, queries: List, k: Optional[int] = 1
    ) -> Tuple[List, List]:

        """
        Arguments:
            queries (List):
                하나의 Query를 받습니다.
            k (Optional[int]): 1
                상위 몇 개의 Passage를 반환할지 정합니다.
        Note:
            vocab 에 없는 이상한 단어로 query 하는 경우 assertion 발생 (예) 뙣뙇?
        """
        tokenized_queries = list()
        for question in queries:
             tokenized_queries.append(self.tokenize_fn(question))
        results = list()

        pickle_name = f"{self.stage}_scores.bin"
        emd_path = os.path.join(self.data_path, pickle_name)
    
        if os.path.isfile(emd_path):
            with open(emd_path, "rb") as file:
                results = pickle.load(file)
            print("Score pickle load.")
        else:
            for q in tqdm(tokenized_queries, desc='Getting Scores'):
             results.append(self.bm25.get_scores(q) / 100)
        
            if not isinstance(results[0], np.ndarray):
                results = results.toarray()
            
            with open(emd_path, "wb") as file:
                pickle.dump(results, file)
            print("Score pickle saved.")

        doc_scores = []
        doc_indices = []
        for i in range(len(results)):
            sorted_result = np.argsort(results[i])[::-1]
            doc_scores.append(results[i][sorted_result].tolist()[:k])
            doc_indices.append(sorted_result.tolist()[:k])
        return doc_scores, doc_indices
        


if __name__ == "__main__":
    # python utils/bm25.py
    cfg = OmegaConf.load('retrieval.yaml')

    dataset_name = cfg.dataset_name
    model = cfg.model_name_or_path
    data_path = cfg.data_path
    context_path = cfg.context_path
    tokenizer = AutoTokenizer.from_pretrained(model, truncation=True)
    tokenize_fn = tokenizer.tokenize
    topk = cfg.topk
    use_ce=cfg.use_ce

    org_dataset = load_from_disk(dataset_name)
    full_ds = concatenate_datasets(
        [
            org_dataset["train"].flatten_indices(),
            org_dataset["validation"].flatten_indices(),
        ]
    )  # train dev 를 합친 4192 개 질문에 대해 모두 테스트
    print("*" * 40, "query dataset", "*" * 40)
    print(full_ds)
    
    retriever = BM25Retrieval(
            tokenize_fn=tokenize_fn,
            data_path=data_path,
            context_path=context_path,
        )
    retriever.get_bm25()
   
    
    query = "대통령을 포함한 미국의 행정부 견제권을 갖는 국가 기관은?"

    # with timer("bulk query by exhaustive search"):
    #         df = retriever.retrieve(full_ds, topk)
    #         df["correct"] = df["original_context"] == df["context"]
    #         print(
    #             "correct retrieval result by exhaustive search",
    #             df["correct"].sum() / len(df),
    #         )

    with timer("single query by exhaustive search"):
            scores, indices = retriever.retrieve(query, topk)