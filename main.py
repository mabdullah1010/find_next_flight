import requests
import os
from pprint import pprint
from get_sheet_data import sheet_data
import datetime as dt
import smtplib
import json
def starting_questions():
    print("Welcome to Abdullah's Flight Club")
    user_choice = input("Do you want to add your email address to the mailing list? (Y/N): ").lower()
    if user_choice == "y":
        name = input("Enter name: ")
        last_name = input("Enter last name: ")
        email = input("Enter email: ")
        confirm_email = input("Confirm email: ")
        if email != confirm_email:
            print("Please enter the correct email address.")
        else:
            headers1 = {'Content-Type': 'application/json'}
            ex = {
                "timestamp": dt.datetime.now().isoformat(),
                "firstName": name,
                "lastName": last_name,
                "email": email,
                "confirmEmail": email
            }
            body = {"formResponses1": ex}
            response1 = requests.post(
                url="https://api.sheety.co/7687b746f7aa3562a45758e38efe0c56/flightHunterUserList/formResponses1",
                headers=headers1,
                json=body
            )
            if response1.status_code == 200:
                print("You are now added to the mailing list. Check your email for amazing flight deals.")
            else:
                print(f"Failed to add to the mailing list. Status code: {response1.status_code}, "
                      f"Response: {response1.text}")


def send_mails(my_message: str):
    print("Sending emails.....")
    my_email = os.environ["MY_EMAIL"]
    my_password = os.environ["MY_PASSWORD"]


    mail_list = "https://api.sheety.co/7687b746f7aa3562a45758e38efe0c56/flightHunterUserList/formResponses1"
    sheet_response = requests.get(url=mail_list)

    sheet_data_email = sheet_response.json()["formResponses1"]

    for row in sheet_data_email:
        first_name = row["firstName"]
        last_name = row["lastName"]
        email = row["email"]
        confirm_email = row["confirmEmail"]
        if email == confirm_email:
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(user=my_email, password=my_password)
                connection.sendmail(from_addr=my_email,
                                    to_addrs=email,
                                    msg=f"Subject:Check out these Cheap Flights \n\nHi {first_name} {last_name} check "
                                        f"out these flights.\n{my_message}")
        else:
            print("Invalid email given")


today = dt.datetime.now()
this_date = str(today + dt.timedelta(days=30))[0:10]

starting_questions()

for a in sheet_data:
    code = a["iataCode"]
    lowest_price = a["lowestPrice"]
    # a
    url = "https://tripadvisor16.p.rapidapi.com/api/v1/flights/searchFlights"
    querystring = {
        "sourceAirportCode": "LHE",
        "destinationAirportCode": code,
        "date": this_date,
        "itineraryType": "ONE_WAY",
        "sortOrder": "PRICE",
        "numAdults": "1",
        "numSeniors": "0",
        "classOfService": "ECONOMY",
        "pageNumber": "1",
        "nearby": "no",
        "nonstop": "no",
        "currencyCode": "PKR",
        "region": "USA"
    }

    headers = {
        "x-rapidapi-key": "4103f73080msh91a9a41eaedc05cp151552jsncfbd53686894",
        "x-rapidapi-host": "tripadvisor16.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    # a
    flight_list = data["data"]["flights"]
    all_flights = []

    for i in range(3):
        k = - 1
        legs = []
        for j in flight_list[i]["segments"][0]["legs"]:
            k += 1
            chopped_data = flight_list[i]["segments"][0]["legs"][k]
            origin = chopped_data["originStationCode"]
            destination = chopped_data["destinationStationCode"]
            departure_date_time = chopped_data["departureDateTime"]
            arrival_date_time = chopped_data["arrivalDateTime"]
            airline = chopped_data["operatingCarrier"]["displayName"]

            layover = flight_list[i]["segments"][0]["layovers"]
            chopped_links = flight_list[i]["purchaseLinks"][0]
            provider_id = chopped_links["providerId"]
            price = chopped_links["totalPrice"]
            currency = chopped_links["currency"]
            link = chopped_links["url"]

            this_leg = {
                    "origin": origin,
                    "destination": destination,
                    "departure_date_time": departure_date_time,
                    "arrival_date_time": arrival_date_time,
                    "airline": airline,
                    "layover": layover,
                    "provider_id": provider_id,
                    "price": price,
                    "currency": currency,
                    "link": link
                }
            legs.append(this_leg)

        all_flights.append(legs)
        legs = []
    if float(price) < float(lowest_price):
        message = ""
        for flight in all_flights:
            message += "\n"
            my_stops = [flight[0]["origin"]]
            airlines = []
            message += f"departure date/time : {flight[0]["departure_date_time"]}\n"
            for stops in flight:
                my_stops.append(stops["destination"])
                airlines.append(stops["airline"])
                arrival_dt = stops["arrival_date_time"]
                price_final = stops["price"]
                link_final = stops["link"]
            message += f"departure date/time : {arrival_dt} \nPrice: {price_final} PKR \nRoute: {my_stops} \nURL: {link_final}"
            message += "\n"
        send_mails(message)
