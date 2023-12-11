from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
import pandas as pd
import pickle
from openai import OpenAI
from model import model

def ask(model, query, retrieve_item='recipe', top_k=5):
    if retrieve_item == 'recipe':
        return model.generate_recipe(query, top_k=top_k)
    else:
        return model.generate_ingredient(query, top_k=top_k)

if __name__ == '__main__':
    embedder = SentenceTransformer('jhgan/ko-sroberta-multitask')
    client = OpenAI()

    model = model(embedder, client)

    while True:
        query = input("Enter your query: ")
        if query == 'exit':
            break

        response = ask(model, query, retrieve_item='recipe', top_k=5)
        print("=" * 50)
        print(f"response: {response}")
    