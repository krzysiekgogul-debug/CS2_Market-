# from fastapi import FastAPI
from pathlib import Path
import httpx


URL = "https://api.skinport.com/v1/items"
PARAMS = {"app_id": 730, "currency": "PLN", "tradable": False}
HEADERS = {"Accept-Encoding": "br"}
CACHE_FILE = Path("../items.json")


def fetch_items():
    response = httpx.get(URL, params=PARAMS, headers=HEADERS, timeout=30)
    response.raise_for_status()

    print("status:", response.status_code)
    print("url:", response.url)
    print("content-encoding:", response.headers.get("content-encoding"))
    print("czas:", response.elapsed)

    return response.json()





# import httpx
#
# dict_atributes = {'app_id': 730,
#                   'currency': 'PLN',
#                   'tradable': False}
# def get_itmes():
#     response = httpx.get('https://api.skinport.com/v1/items', headers={'Accept-Encoding': 'br'}, params=dict_atributes, timeout=30)
#
#     data = response.json()
#     return data


