#!/usr/bin/env python

import urllib
import datetime
import json
import os
import random
import requests
import time
from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def makeWebhookResult(req):

    if req.get("result").get("action") == 'get.coverage.url':
        result = req.get("result")
        parameters = result.get("parameters")
        device_type = parameters.get("device_home")
        if device_type == 'home':  # broadband
            all_texts = ['see: http://www.optus.com.au/shop/broadband/home-broadband',
                         'check: http://www.optus.com.au/shop/broadband/home-broadband',
                         'visit: http://www.optus.com.au/shop/broadband/home-broadband']
            speech = random.sample(all_texts, 1)[0]
        elif device_type == 'mobile':  # mobile
            all_texts = ['please check: http://www.optus.com.au/about/network/service-status',
                         'you can check: http://www.optus.com.au/about/network/service-status',
                         'see: http://www.optus.com.au/about/network/service-status']
            speech = random.sample(all_texts, 1)[0]
        else:
            speech = 'cannot find a suitable link for '+device_type



    elif req.get("result").get("action") == 'show.travel.plans':
        result = req.get("result")
        parameters = result.get("parameters")
        plan_type = parameters.get("travel-plan")
        speech = 'Roaming plans are available for $10 a day'

    elif req.get("result").get("action") == "show.simonly.plans":  # action name
        result = req.get("result")
        parameters = result.get("parameters")
        period = parameters.get("plan-period")  # monthly or yearly
        user_input = parameters.get("unit-currency")  # parameter name

        if 'amount' in user_input:
            monthly_amount = str(user_input.get("amount"))
        elif 'number' in parameters:
            monthly_amount = str(parameters.get('number'))
        else:
            monthly_amount = '100'

        if period == "monthly":

            plan = {'35': '1.5 GB Data, Unlimited Standard National Talk and Text',
                    '50': '6 GB Data, Unlimited Standard National Talk and Text; Upto 300 International Minutes',
                    '60': '9 GB Data, Unlimited Standard National Talk and Text; Upto 500 International Minutes'}

            if monthly_amount in plan.keys():
                speech = "For a monthly plan of $" + monthly_amount + " you get " + plan[monthly_amount]
            else:
                speech = 'Monthly plans are available only for $35, 50 and 60. (you have entered "' + monthly_amount + '")'

        elif period == "yearly":

            plan = {'30': '1.5 GB Data and Unlimited Standard National Talk and Text',
                    '40': '6 GB Data, Unlimited Standard National Talk and Text and Upto 300 International Minutes',
                    '50': '9 GB Data, Unlimited Standard National Talk and Text and Upto 500 International Minutes'}

            if monthly_amount in plan.keys():
                speech = "For a yearly plan of $" + monthly_amount + " per month you get " + plan[monthly_amount]
            else:
                speech = 'Yearly plans are available only for $30, 40 and 50. (you have entered "' + monthly_amount + '")'

        else:
            speech = 'No matching plan found for user-defined period: ' + period

    elif req.get("result").get("action") == "show.bundle.plans":  # action name

        result = req.get("result")
        parameters = result.get("parameters")
        # period = parameters.get("plan-period")  # monthly or yearly
        user_input = parameters.get("unit-currency")  # parameter name

        if 'amount' in user_input:
            monthly_amount = str(user_input.get("amount"))
        elif 'number' in parameters:
            monthly_amount = str(parameters.get('number'))
        else:
            monthly_amount = '100'

        # 2-yearly plans for phone+sim
        plan = {'40': '1 GB Data, Unlimited Standard National Talk and Text',
                '65': '3.5 GB Data, Unlimited Standard National Talk and Text; Upto 150 International Minutes',
                '85': '8 GB Data, Unlimited Standard National Talk and Text; Upto 300 International Minutes',
                '100': '15 GB Data, Unlimited Standard National Talk and Text; Upto 400 International Minutes',
                '120': '20 GB Data, Unlimited Standard National Talk and Text; Unlimited International Minutes and International Roaming'}

        if monthly_amount in plan.keys():
            speech = "For a two-yearly plan of $" + monthly_amount + " you get " + plan[monthly_amount]
        else:
            speech = 'Yearly plans are available only for $40, 65, 85, 100 and 120. (you have entered "' + monthly_amount + '")'

    elif req.get("result").get("action") == "show.hotels":  # action name

        result = req.get("result")
        parameters = result.get("parameters")

        if 'geo-city' in parameters:
            place = parameters.get("geo-city")
        else:
            place = 'London'

        if 'start-date' in parameters:
            start_date = parameters.get("start-date")
        else:
            start_date = time.strftime('%Y-%m-%d')  # today's date

        if 'end-date' in parameters:
            end_date = parameters.get("end-date")
        else:
            today = datetime.datetime.today()
            tomorrow = today + datetime.timedelta(1)
            end_date = datetime.datetime.strftime(tomorrow,'%Y-%m-%d')  # tomorrow's date

        if 'cardinal' in parameters:
            num_adults = int(parameters.get('cardinal'))
        else:
            num_adults = 1

        try:
            # r = requests.post("https://www.choicehotels.com/webapi/location/hotels", data={"placeName": place})
            r = requests.post("https://www.choicehotels.com/webapi/location/hotels", data={"placeName": place,
                "adults": num_adults, "checkInDate": start_date, "checkOutDate": end_date,
                "ratePlans": "RACK%2CPREPD%2CPROMO%2CSCPM", "rateType":"LOW_ALL"})
            # speech = "Requesting for " + place + ' found: ' + str(r.status_code) + r.reason
            if r.status_code == 200:
                d = json.loads(r.text)
                hotels = d['hotels']
                # hotel_names = [h['name'] for h in hotels if h['hotelSectionType'] == 'AVAILABLE_HOTELS']
                hotel_names = [': '.join([h['id'], h['name']]) for h in hotels if h['hotelSectionType'] == 'AVAILABLE_HOTELS']
                hotel_names_string = '\t'.join(hotel_names)
                speech = "Found " + str(len(hotel_names)) + " hotel(s): " + hotel_names_string
                data = hotel_names
            else:
                speech = "Requesting for " + place + ' returned status: ' + str(r.status_code) + r.reason
                data = {}

        except:
            speech = 'Not working for ' + place
            data = {}

    else:
        speech = 'No matching intent found ... python code returns None'
        data = {}


    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "data": data,
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')
