from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
import pandas as pd
import pickle
from openai import OpenAI
from load_data import load_data

df, ingredient_list, corpus_embeddings, ingredient_list_embeddings = load_data()

class model:
    def __init__(self, embedder, client):
        self.embedder = embedder
        self.client = client
    
    def retrieve(self, query, retrieve_item='recipe', top_k=5):
        assert retrieve_item in ['recipe', 'ingredient']
        
        if retrieve_item == 'recipe':
            kb_embeddings = corpus_embeddings
        else:
            kb_embeddings = ingredient_list_embeddings

        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        cos_scores = util.pytorch_cos_sim(query_embedding, kb_embeddings)[0]
        cos_scores = cos_scores.cpu()

        top_results = np.argpartition(-cos_scores, range(top_k))[0:top_k]

        # print("\n\n======================\n\n")
        # print("Query:", query)
        # print("\nTop 5 most similar sentences in corpus:")

        # for idx in top_results[0:top_k]:
        #     print(df['name'][idx.item()], "(Score: %.4f)" % (cos_scores[idx]))

        if retrieve_item != 'recipe':
            bottom_results = np.argpartition(cos_scores, range(top_k))[0:top_k]
            # print("\nBottom 5 most similar sentences in corpus:")
            # for idx in bottom_results[0:top_k]:
            #     print(df['name'][idx.item()], "(Score: %.4f)" % (cos_scores[idx]))
            
            return top_results, bottom_results

        return top_results
    
    def generate_recipe(self, query, top_k=5):
        top_results = self.retrieve(query, retrieve_item='recipe', top_k=top_k)
        
        system_prompt = "당신은 주어진 재료를 활용하는 요리의 레시피를 제공하는 요리 전문가입니다."
        user_prompt = f"다음은 사용자가 보유하고 있는 재료 목록과 관련 레시피 목록 입니다. 이를 참고하여 보유 재료를 사용하는 레시피를 추천해주세요. 답변을 생각할 때, step-by-step으로 생각해보세요.\n재료 목록: {query}\n"
        additional_prompt = "관련 레시피 목록: " + ' '.join([f"{i+1}. {df['name'][top_results[i].item()]}" for i in range(top_k)])

        print(f"prompt: {system_prompt + user_prompt + additional_prompt}")

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt + additional_prompt}
            ]
        )

        return response.choices[0].message.content
    
    def generate_ingredient(self, query, top_k=5):
        top_results, bottom_results = self.retrieve(query, retrieve_item='ingredient', top_k=top_k)
        
        system_prompt = "당신은 주어진 재료를 보고 보충 재료를 추천하는 요리 전문가입니다."
        user_prompt = f"다음은 사용자가 보유하고 있는 재료 목록과 그와 연관성이 높은 재료 목록, 연관성이 낮은 재료 목록입니다. 이를 참고하여 보충하면 유용한 재료들을 추천해주세요. 답변을 생각할 때, step-by-step으로 생각해보세요.\n재료 목록: {query}\n"
        additional_prompt = ("보유 재료와 연관성이 높은 재료 목록:" + 
                            ' '.join([f"{i+1}. {ingredient_list['ingredient'][top_results[i].item()]}" for i in range(top_k)]) + "\n" +
                            "보유 재료와 연관성이 낮은 재료 목록:" +
                            ' '.join([f"{i+1}. {ingredient_list['ingredient'][bottom_results[i].item()]}" for i in range(top_k)])
        )

        print(f"prompt: {system_prompt + user_prompt + additional_prompt}")

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt + additional_prompt}
            ]
        )

        return response.choices[0].message.content