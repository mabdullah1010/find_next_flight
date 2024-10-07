import json

import requests
import datetime as dt
sheet_url = "https://api.sheety.co/7687b746f7aa3562a45758e38efe0c56/flightDeals/sheet1"

sheet_response = requests.get(url=sheet_url)

sheet_data = sheet_response.json()["sheet1"]




