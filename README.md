# level2_nlp_mrc-nlp-13

[ENG](#ENG)   
[한국어](#한국어)

## ENG
# Open-Domain Question Answering Project

This project is divided into two stages:   
The retriever stage, which finds documents related to the given question by searching through a pre-built knowledge resource.   
The reader stage, which reads the relevant documents and extracts or generates appropriate answers to the questions. 

## Getting Started

To use this project, follow these steps:

### Train and Test the Model
```
python main.py
```

## 한국어
## ✅ 목차
[1. 정보](##-📜-정보) > [2. 진행 과정](##-진행-과정) > [3. 리더보드](##-🏆-리더보드) > [4. 팀원](##-팀원) > [5. 역할](##-역할) > [6. 디렉토리 구조](##-📁-디렉토리-구조) > [7. 프로젝트 구성](##-프로젝트-구성)

➡️ [랩업 리포트 보기](https://docs.google.com/document/d/1G9enGVjgYiu4gTudxhtDOsBVsxjTNCaEtGt1hS2chKI/edit?usp=sharing)
<br>

## 📜 정보
- 주제 : 부스트캠프 5기 Level 2 프로젝트 - 기계독해 : 질문 답하기(MRC, Open-Domain Question Answering)
- 프로젝트 기간 : 2023년 6월 7일 ~ 2023년 6월 22일
- 프로젝트 내용 : 질문에 관련된 문서를 찾아주는 retriever 단계와 관련된 문서를 읽고 적절한 답변을 찾거나 만드는 reader 단계로 나누어 주어지는 지문이 따로 존재하지 않고 사전에 구축되어있는 knowledge resource에서 질문에 대답할 수 있는 문서를 찾는 프로젝트

<br>

## 🏆 리더보드
- Private 리더보드에서 13팀 중 5위로 마무리
![리더보드](https://user-images.githubusercontent.com/42113966/257057180-28ca3a8e-3599-4ba3-9655-191d8f8fdb61.PNG)

<br>

## 🗓️ 진행 과정

![ganttchart](https://github.com/boostcampaitech5/level2_nlp_mrc-nlp-13/assets/42113966/dce61fd0-ceba-4da1-8426-d413533084ed)

<br>

## 👨🏼‍💻 팀원

<table>
    <tr height="160px">
        <td align="center" width="150px">
            <a href="https://github.com/Yunhee000"><img height="120px" width="120px" src="https://avatars.githubusercontent.com/Yunhee000"/></a>
            <br/>
            <a href="https://github.com/Yunhee000"><strong>김윤희</strong></a>
            <br />
        </td>
        <td align="center" width="150px">
            <a href="https://github.com/8804who"><img height="120px" width="120px" src="https://avatars.githubusercontent.com/8804who"/></a>
            <br/>
            <a href="https://github.com/8804who"><strong>김주성</strong></a>
            <br />
        </td>
        <td align="center" width="150px">
            <a href="https://github.com/ella0106"><img height="120px" width="120px" src="https://avatars.githubusercontent.com/ella0106"/></a>
            <br/>
            <a href="https://github.com/ella0106"><strong>박지연</strong></a>
            <br />
        </td>
        <td align="center" width="150px">
            <a href="https://github.com/bom1215"><img height="120px" width="120px" src="https://avatars.githubusercontent.com/bom1215"/></a>
            <br/>
            <a href="https://github.com/bom1215"><strong>이준범</strong></a>
            <br />
        </td>
        <td align="center" width="150px">
            <a href="https://github.com/HYOJUNG08"><img height="120px" width="120px" src="https://avatars.githubusercontent.com/HYOJUNG08"/></a>
            <br/>
            <a href="https://github.com/HYOJUNG08"><strong>정효정</strong></a>
            <br />
        </td>
    </tr>
</table>
<br>

## 🧑🏻‍🔧 역할

| 이름 | 역할 |
| :----: | --- |
| **김윤희** | 코드 모듈화, Wandb 추가, Curriculum Learning |
| **김주성** | 외부 데이터셋 탐색, 데이터 전처리 |
| **박지연** | Retriever에 BM25 추가 |
| **이준범** | 데이터 전처리 |
| **정효정** | 코드 모듈화, Retriever의 BM25에 Cross Encoder 추가 |


<br>

## 📁 디렉토리 구조

```bash
├── level2_nlp_mrc-nlp-13
|   ├── basecode/ (private)
│   ├── data/ (private)
│   ├── results/ (private)
│   ├── utils/
│   │   ├── DataLoader.py
│   │   ├── Inference.py
│   │   ├── Model.py
│   │   ├── Retrieval.py
│   │   ├── Train.py
│   │   ├── bm25.py
│   │   ├── cross_encoder.py
│   │   ├── preprocess.py
│   │   ├── retrieval.yaml
│   │   ├── utils_qa.py
│   │   └── utils_retrieval.py
│   ├── main.py
│   ├── README.md
│   ├── config.yaml
|   ├── sweep.py
│   └── curriculum_learning.py
```
<br>

## ⚙️ 프로젝트 구성

|분류|내용|
|:--:|--|
|데이터|![데이터 구성](https://github.com/boostcampaitech5/level2_nlp_mrc-nlp-13/assets/42113966/503f8204-8efa-4391-82e8-6074aa116acb)|
|Retrieval|• `BM25` 알고리즘 및 `Cross Encoder` 활용|
|Reader 모델|• [`klue/roberta-large`](https://huggingface.co/klue/roberta-large)를 백본 모델로 활용, `HuggingFace Transformer Model`+`Pytorch Lightning`활용|
|전처리|• 반각문자 변환, 불필요한 문자 제거|
|증강|• KLUE-MRC 데이터셋과 비슷한 형태인 `KorQuAD 1.0 데이터셋`과 `AI-Hub 기계독해 데이터셋` 활용|
|앙상블 방법|• 서로 다른 retrieval 방식을 활용한 모델 5가지를 이용하여 hard voting 적용|
|모델 성능 개선 노력|• `Curriculum Learning`, Learning Rate Scheduling, Focal Loss 적용, fp16으로 학습 속도 향상|

<br>
