import requests
import json
import pandas as pd

headers = {'User-Agent': "mguan2@scu.edu"}
tickers = []
try:
    companyTickers = requests.get(
        "https://www.sec.gov/files/company_tickers.json", 
    	headers=headers) 
    
    data = companyTickers.json()
    print("API fetch succeeded")
    # print(data.keys())
except requests.exceptions.RequestException as err:
    print(f"An error was encountered while fetching data: {err}")

for i in data.keys():
    print(data[i]["ticker"])
    print(data[i]["cik_str"])
    