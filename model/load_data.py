import pandas as pd
import pickle

CORPUS_DF_PATH = './data/food_info.csv'
CORPUS_EMBEDDING_PATH = './data/corpus_embeddings.pkl'
INGREDIENT_LIST_EMBEDDING_PATH = './data/ingredient_list_embeddings.pkl'
INGREDIENT_LIST_PATH = './data/ingredient_list.pkl'

def load_data():
    corpus_df = pd.read_csv(CORPUS_DF_PATH)

    with open(INGREDIENT_LIST_PATH, 'rb') as f:
        ingredient_list = pickle.load(f)

    with open(CORPUS_EMBEDDING_PATH, 'rb') as f:
        corpus_embeddings = pickle.load(f)

    with open(INGREDIENT_LIST_EMBEDDING_PATH, 'rb') as f:
        ingredient_list_embeddings = pickle.load(f)


    return corpus_df, ingredient_list, corpus_embeddings, ingredient_list_embeddings

if __name__ == '__main__':
    corpus_df, ingredient_list, corpus_embeddings, ingredient_list_embeddings = load_data()
    print(corpus_df.head())
    print(ingredient_list[:10])
    print(corpus_embeddings[:10])
    print(ingredient_list_embeddings[:10])
