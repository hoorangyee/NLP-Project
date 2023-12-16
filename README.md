# RAG 기반 레시피 및 재료 추천 모델 개발
자연어처리(2023-2학기)

* test.py를 실행하기 위해서는 OpenAI API KEY가 환경변수로 설정되어 있어야 합니다.
* load_data.py에 설정된 파일 경로 변수의 내용을 변경해야할 수 있습니다.


## Overview
  최근 고물가 상황에서 많은 사람들이 직접 요리를 하려는 추세가 증가하고 있다. 그러나, 대부분의 요리 레시피는 제공자의 기준에 맞춰 재료가 제시되어, 필요하지 않은 재료를 구매해야 하는 문제가 발생한다. 이러한 상황을 해결하고자, 사용자가 이미 가지고 있는 재료를 기반으로 레시피를 검색하고 추천하는 시스템을 개발하였다. 또한, 재료 활용을 극대화하기 위해 필요한 보충 재료도 함께 추천하는 기능을 제공함으로써, 효율적이고 경제적인 요리 경험을 지원하고자 한다.

## Task
![task](https://github.com/hoorangyee/NLP-Project/assets/119475060/82307206-a932-4abc-bf4d-7e2e8da7e13c)
* Input: 보유중인 재료 목록
* Output: (1) 해당 재료들을 활용하여 만들 수 있는 음식 레시피 (2) 보충하면 좋은 재료

## Data

* 만개의 레시피( http://10000recipe.com )에서 음식 카테고리별로 나누어 크롤링함.
* 카테고리는 총 15개(소고기, 돼지고기, 닭고기, 채소류, 해물류, 달걀/유제품, 가공식품류, 쌀, 밀가루, 건어물류, 버섯류, 과일류, 콩/견과류. 곡류, 기타)로, 카테고리별로 약 1800장씩 수집, 총 27,358장의 데이터를 수집함.
* 테스트 데이터는 농림축산식품부 공공데이터 포털( https://data.mafra.go.kr/main.do )에서 제공하는 레시피 데이터 API를 활용하여 총 100장을 수집함.

## Model
![model](https://github.com/hoorangyee/NLP-Project/assets/119475060/4419fb84-9f3b-4627-9308-5a01aaf6f996)
- Retrieval Augmented Generation(RAG) 기반 모델
1) Transformer Encoder로 입력된 재료 목록의 임베딩 생성
2) Retriever를 통해 유사한 재료 목록을 가진 레시피 검색
3) Retriever를 통해 유사한 재료, 유사하지 않은 재료 검색
4) LLM에 top-k의 검색된 레시피와 top-k(유사한 k개), bottom-k(유사하지 않은 재료)의 검색된 재료 입력
5) LLM을 통해 추천 레시피 및 추천 재료 생성

* Transformer Encoder: ko-sroberta-multitask(https://huggingface.co/jhgan/ko-sroberta-multitask)
* Retriever: Cosine similarity 기반
* LLM: ChatGPT(GPT-3.5-turbo)

## Evaluation
### 레시피 생성
* 평가 기준을 세워, GPT-4에게 점수로 평가하도록 요청
* ROUGE 점수 계산
<p align="center">
  <img src="https://github.com/hoorangyee/NLP-Project/assets/119475060/63a180f3-bb39-4160-a030-90ebffb969f6"/>
</p>

![image](https://github.com/hoorangyee/NLP-Project/assets/119475060/d7fd980f-a796-4c23-961c-48daf5f59275)

![image](https://github.com/hoorangyee/NLP-Project/assets/119475060/378be415-eaad-463c-b3c8-b856ced135f6)


### 재료 생성
* 평가 기준을 세워, GPT-4에게 점수로 평가하도록 요청

![image](https://github.com/hoorangyee/NLP-Project/assets/119475060/0fdb99e5-4fd8-482f-8140-bab1a529d12e)

![image](https://github.com/hoorangyee/NLP-Project/assets/119475060/3881e865-be12-490c-b99f-fbfbc2543a41)

## Conclusion
### 레시피 추천:
* 대부분 보유 재료와 검색한 레시피 목록을 보고, 둘을 적절히 결합하여 보유 재료에 가장 적합한 레시피를 추천해줌.

* 그러나, 추천된 레시피의 주재료가 보유 재료 목록에 없는 경우가 가끔 존재함.

* 모델의 답변 템플릿이 명확하게 지정되어 있지 않아 이상한 답변 형식을 제공하는 경우도 존재함.

### 재료 추천:
* 대부분 보유 재료에 기반하여 보충했을 때의 활용 방안을 같이 제시하며 합리적으로 재료를 추천함.

* 관련 재료를 검색해서 제안할 때, 검색 성능이 좋지 못한 것으로 보임.

* 재료 목록과 단일 재료 간 유사도 비교를 기반으로 검색하는 것의 한계

* 재료 조합을 고려하여 검색하는 것이 아닌, 절대적으로 많이/적게 등장하는 재료가 검색됨.

## Discussion
* 데이터셋을 더 다양한 source에서 수집한다면 더 다양한 레시피를 검색해서 제공할 수 있음.

* LLM을 Instruction-tunning등을 통해 좀 더 의도에 맞는 형태의 답변을 하도록 유도할 수 있음.

* 재료 목록과 단일 재료 간 비교가 아닌, 재료 목록과 재료 목록을 비교하여 둘 사이의 유사점 및 차이점을 통해 재료 추천을 하도록 모델을 개선할 수 있음.

















