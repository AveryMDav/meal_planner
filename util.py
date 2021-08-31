import requests
import json

api = "https://api.edamam.com/api/food-database/v2/parser?app_id=7b2a570a&app_key=646da4c4e9f6333037b153ee76254132"

def items_info(search):
    """returns kcals and name of matching items"""

    item = json.loads(requests.get(f"{api}&ingr={search}").text)
    
    info =  dict(zip([label['food']['label'] for label in item['hints']],
                          [int(cal['food']['nutrients']['ENERC_KCAL']) for cal in item['hints']]))
    
    return info

def calculate_cal(kcal, weight):
    cal = (kcal / 100) * weight
    return cal