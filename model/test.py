from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
import pandas as pd
import pickle
from openai import OpenAI
from model import model, corpus_df, ingredient_list
import time

def ask(model, query, retrieve_item='recipe', top_k=5):
    if retrieve_item == 'recipe':
        return model.generate_recipe(query, top_k=top_k)
    else:
        return model.generate_ingredient(query, top_k=top_k)

if __name__ == '__main__':
    embedder = SentenceTransformer('jhgan/ko-sroberta-multitask')
    client = OpenAI()

    model = model(embedder, client)

    result_df = pd.DataFrame(columns=['query', 'retrieved_recipe(top_k)', 'retrieved_ingredient(top_k)', 'retrieved_ingredient(bottom_k)', 'model_response(recipe)', 'model_response(ingredient)'])
    test_df = pd.read_csv('./data/test_recipe.csv')
    for i in tqdm(range(len(test_df))):
        query = test_df['irdnt_nm'][i]
        top_k = 3

        time.sleep(10)
        model_response_recipe, recipe_top_k = ask(model, query, retrieve_item='recipe', top_k=top_k)
        time.sleep(10)
        model_response_ingredient, ingredient_top_k, ingredient_bottom_k = ask(model, query, retrieve_item='ingredient', top_k=top_k)

        retrieved_recipe_top_k = ' '.join([f"{i+1}. {corpus_df['name'][recipe_top_k[i].item()]}" for i in range(top_k)])
        retrieved_ingredient_top_k = ' '.join([f"{i+1}. {ingredient_list[ingredient_top_k[i].item()]}" for i in range(top_k)])
        retrieved_ingredient_bottom_k = ' '.join([f"{i+1}. {ingredient_list[ingredient_bottom_k[i].item()]}" for i in range(top_k)])

        result_df.loc[i] = [query, retrieved_recipe_top_k, retrieved_ingredient_top_k, retrieved_ingredient_bottom_k, model_response_recipe, model_response_ingredient]
    
    result_df.to_csv('./data/result2.csv', index=False)
    