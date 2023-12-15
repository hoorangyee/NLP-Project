import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def parsing_basic_information(soup):
    data = []
    for row in soup.find_all('row'):
        recipe_id = row.find('recipe_id').text
        recipe_nm_ko = row.find('recipe_nm_ko').text
        nation_nm = row.find('nation_nm').text
        ty_nm = row.find('ty_nm').text
        level_nm = row.find('level_nm').text
        irdnt_code = row.find('irdnt_code').text
        data.append([recipe_id, recipe_nm_ko, nation_nm, ty_nm, level_nm, irdnt_code])

    df = pd.DataFrame(data, columns=['recipe_id', 'recipe_nm_ko', 'nation_nm', 'ty_nm', 'level_nm', 'irdnt_code'])
    return df

def parsing_ingredient_information(soup):
    irdnt_nms = {}
    for row in soup.find_all('row'):
        recipe_id = row.find('recipe_id').text
        irdnt_nm = row.find('irdnt_nm').text
        if recipe_id in irdnt_nms:
            irdnt_nms[recipe_id].append(irdnt_nm)
        else:
            irdnt_nms[recipe_id] = [irdnt_nm]
    
    return irdnt_nms

def parsing_recipe_information(soup):
    cooking_steps = {}
    for row in soup.find_all('row'):
        recipe_id = row.find('recipe_id').text
        cooking_no = row.find('cooking_no').text
        cooking_dc = row.find('cooking_dc').text
        step = f"{cooking_no}. {cooking_dc}"
        if recipe_id in cooking_steps:
            cooking_steps[recipe_id].append(step)
        else:
            cooking_steps[recipe_id] = [step]
    
    return cooking_steps


BASIC_START_IDX = 1; BASIC_END_IDX = 100
INGREDIENT_START_IDX = 1; INGREDIENT_END_IDX = 1000
PROCEDURE_START_IDX = 1; PROCEDURE_END_IDX = 550

api_key = "905d2def4466b92591b8768c474313e0443fb1d98612aeae6b336bdda94c950d"
start_idx = BASIC_START_IDX; end_idx = BASIC_END_IDX
basic_url = f"http://211.237.50.150:7080/openapi/{api_key}/xml/Grid_20150827000000000226_1/{start_idx}/{end_idx}"

start_idx = INGREDIENT_START_IDX; end_idx = INGREDIENT_END_IDX
ingredient_url = f"http://211.237.50.150:7080/openapi/{api_key}/xml/Grid_20150827000000000227_1/{start_idx}/{end_idx}"

start_idx = PROCEDURE_START_IDX; end_idx = PROCEDURE_END_IDX
procedure_url = f"http://211.237.50.150:7080/openapi/{api_key}/xml/Grid_20150827000000000228_1/{start_idx}/{end_idx}"

basic_res = requests.get(basic_url)
time.sleep(1)
procedure_res = requests.get(procedure_url)
time.sleep(1)
ingredient_res = requests.get(ingredient_url)

if basic_res.status_code != 200 or procedure_res.status_code != 200 or ingredient_res.status_code != 200:
    print("API 호출 에러 발생")
    exit()

basic_soup = BeautifulSoup(basic_res.content, 'lxml')
procedure_soup = BeautifulSoup(procedure_res.content, 'lxml')

INGREDIENT_START_IDX = 1001; INGREDIENT_END_IDX = 1135
start_idx = INGREDIENT_START_IDX; end_idx = INGREDIENT_END_IDX
ingredient_url = f"http://211.237.50.150:7080/openapi/{api_key}/xml/Grid_20150827000000000227_1/{start_idx}/{end_idx}"
ingredient_soup = BeautifulSoup(ingredient_res.content + requests.get(ingredient_url).content, 'lxml')


df = parsing_basic_information(basic_soup)
irdnt_nms = parsing_ingredient_information(ingredient_soup)
cooking_steps = parsing_recipe_information(procedure_soup)

df['irdnt_nm'] = df['recipe_id'].apply(lambda x: ', '.join(irdnt_nms[x]) if x in irdnt_nms else "")
df['cooking_cd'] = df['recipe_id'].apply(lambda x: ', '.join(cooking_steps[x]) if x in cooking_steps else "")

df.to_csv('test_recipe.csv', index=False)
