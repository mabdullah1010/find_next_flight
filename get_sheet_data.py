import json
import requests
import datetime as dt
sheet_url = "https://api.sheety.co/APIKEY/flightDeals/sheet1"

sheet_response = requests.get(url=sheet_url)

sheet_data = sheet_response.json()["sheet1"]
