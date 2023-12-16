import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import time
import random
from tqdm import tqdm
from fake_useragent import UserAgent

class Crawler:
    def remove_data(self, df, food_dict, food_list):
        for i in range(len(food_list)):
            df = df[df['name'] != food_dict[food_list[i]['href'].split('/')[-1]]]
        return df

    def is_valid_json(self, json_data):
        try:
            json.loads(json_data)
        except ValueError:
            return False
        return True

    def save_data(self, df, file_name='./food_info_new.csv'):
        print("Saving data...")
        current_data = pd.read_csv(file_name)
        df_new = pd.concat([current_data, df], ignore_index=True)
        df_new.to_csv(file_name, index=False)
        print("Data saved.")

        return df_new

    def food_info(self, df, file_name='./food_info_new.csv', start_page=1, end_page=50, category_num=34):
        try:
            page_num = start_page
            while True:
                if page_num > end_page:
                    break
                print(f"page: {page_num}")
                
                user_agent = UserAgent(use_cache_server=True)
                headers = {"User-Agent": user_agent.random}
                url = f"https://www.10000recipe.com/recipe/list.html?cat3={category_num}&order=reco&page={page_num}"
                response = requests.get(url, headers=headers) # This respense is for getting recipe id, not for recipe info
                if response.status_code == 200:
                    html = response.text
                    soup = BeautifulSoup(html, 'html.parser')
                else : 
                    print("HTTP response error :", response.status_code)
                    continue
                
                if soup.find_all(attrs={'class':'result_none'}) != []: # page out of range
                    break

                food_list = soup.find_all(attrs={'class':'common_sp_link'}) # indexes of recipe
                food_name_list = soup.find_all(attrs={'class':'common_sp_caption_tit line2'})

                food_dict = {}
                for i, food in enumerate(food_list): # make a dictionary contains food_id and food_name
                    food_dict[food['href'].split('/')[-1]] = food_name_list[i].text

                if food_list == []: # page out of range
                    print("page out of range")
                    continue

                for i in tqdm(range(len(food_list))): # num of recipes(data)
                    food_id = food_list[i]['href'].split('/')[-1] # recipe id
                    new_url = f'https://www.10000recipe.com/recipe/{food_id}' # url for recipe info
                    new_response = requests.get(new_url, headers=headers)
                    if new_response.status_code == 200:
                        html = new_response.text
                        soup = BeautifulSoup(html, 'html.parser')
                    else : 
                        print("HTTP response error :", response.status_code)
                        return
                    
                    food_info = soup.find(attrs={'type':'application/ld+json'})

                    if food_info == None:
                        print("food_info is None")
                        continue

                    if self.is_valid_json(food_info.text): # check if json data is valid
                        result = json.loads(food_info.text)
                    else:
                        print("Invalid json data")
                        continue

                    if 'recipeIngredient' not in result.keys(): # no recipeIngredient in result
                        print("No recipeIngredient")
                        continue
                    if 'recipeInstructions' not in result.keys(): # no recipeInstructions in result
                        print("No recipeInstructions")
                        continue

                    ingredient = ','.join(result['recipeIngredient'])

                    # Because recipeInstructions is list of dict, we need to concat text from it
                    recipe = [result['recipeInstructions'][i]['text'] for i in range(len(result['recipeInstructions']))]

                    # Make recipe as string
                    recipe_str = ""
                    for i in range(len(recipe)):
                        recipe[i] = f'{i+1}. ' + recipe[i] # add number to each recipe step
                        recipe_str += recipe[i] + '\n'
                    # Find all <a> tags with the specific onclick attribute
                    a_tags = soup.find_all('a', attrs={'onclick': lambda e: e.startswith("ga('send', 'event', '레시피본문', '재료정보버튼클릭',") if e else False})

                    # Extract the text of the <li> tag and the <span> tag inside each <a> tag
                    ingredients = [{'name': a.find('li').contents[0].strip(), 'amount': a.find('span', class_='ingre_unit').text} for a in a_tags]
                    ingredients_dict = {'name': [ingredient['name'] for ingredient in ingredients], 'amount': [ingredient['amount'] for ingredient in ingredients]}
                    ingredients_dict['name']= ', '.join(ingredients_dict['name'])
                    ingredients_dict['amount']= ', '.join(ingredients_dict['amount'])

                    # Find the <div> tag with class 'view_tag'
                    try:
                        div_tag = soup.find('div', class_='view_tag')

                        # Find all <a> tags inside the <div> tag and extract their text
                        tags = [a.text[1:] for a in div_tag.find_all('a')]  # We use [1:] to remove the '#' at the start of each tag
                        tags = ', '.join(tags)
                    except:
                        tags = ""

                    category = {70: '소고기', 71: '돼지고기', 72:'닭고기', 28:'채소류', 24:'해물류', 50:'달걀/유제품',
                                33:'가공식품류', 47:'쌀', 32:'밀가루', 25:'건어물류', 31:'버섯류', 48:'과일류', 27:'콩/견과류',
                                26:'곡류', 34:'기타'}

                    df = pd.concat([df, pd.DataFrame({
                        'name': [food_dict[food_id]],
                        'ingredients': [ingredient],
                        'recipe': [recipe_str],
                        'ingredients_name': [ingredients_dict['name']],
                        'ingredients_amount': [ingredients_dict['amount']],
                        'tags': [tags],
                        'category': [category[category_num]]
                    })], ignore_index=True) # add data to dataframe

                    # sleep for 1 seconds
                    time.sleep(1)
                
                page_num += 1

        except Exception as e:
            print(f"Error occured. error: {e}, page_num: {page_num}, food_id: {food_id}")
            df = self.remove_data(df, food_dict, food_list)
            df_new = self.save_data(df)
            is_success = False
            return df_new, page_num, is_success
        else:
            print("Successfully finished.")
            df_new = self.save_data(df)
            is_success = True
        return df_new, page_num, is_success


if __name__ == '__main__':
    crawler = Crawler()

    start_page = 1
    end_page = 50

    is_success = False
    while not is_success:
        df = pd.DataFrame(columns=['name', 'ingredients', 'recipe', 'ingredients_name', 'ingredients_amount', 'tags', 'category'])
        df_new, page_num, is_success = crawler.food_info(df, start_page=start_page , end_page=end_page)
 
        start_page = page_num
        if not is_success:
            print("Retrying...")
            time.sleep(15)
    
    print(f"df_new.shape: {df_new.shape}")

