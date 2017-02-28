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

    elif req.get("result").get("action") == "get.property.details":  # action name
        result = req.get("result")
        parameters = result.get("parameters")

        if 'property_code' in parameters:
            property_code = parameters.get('property_code')
        else:
            property_code = 'ma199'

        try:
            r = requests.post("https://www.choicehotels.com/webapi/hotel/"+ property_code.lower(),
                               data={"businessFunction": "view_hotel",
                                     "include": ["amenities", "amenity_groups"], "preferredLocaleCode": "en-us"})
            d = json.loads(r.text)
            descriptions = [a['description'] for a in d['hotel']['amenities']]
            out_string = ' '.join(descriptions)
            speech = "Following amenities are available in " + property_code + ": " + out_string
            data = descriptions
        except:
            speech = 'Cannot fetch any data for ' + property_code
            data = {}

    elif req.get("result").get("action") == "specific.answer":  # action name

        result = req.get("result")
        # parameters = result.get("parameters")
        parameters = result.get("contexts")[0].get("parameters")  # data coming from previous context

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

        if 'specific_requests' in parameters:
            specific_request = parameters.get("specific_requests")
        else:
            specific_request = 'NA'

        specific_key = 'NA'
        if specific_request in ['pet', 'pets']:
            specific_key = 'Pet-friendly Hotel'
        elif specific_request in ['free breakfast', 'breakfast']:
            specific_key = 'Free Hot Breakfast'

        try:
            r = requests.post("https://www.choicehotels.com/webapi/location/hotels", data={"placeName": place,
                "adults": num_adults, "checkInDate": start_date, "checkOutDate": end_date,
                "ratePlans": "RACK%2CPREPD%2CPROMO%2CSCPM", "rateType":"LOW_ALL"})
            if r.status_code == 200:
                d = json.loads(r.text)
                hotels = d['hotels']
                hotel_id_dict = {}
                for h in hotels:
                    hotel_id_dict[h['id']] = h['name']
                # hotel_names = [': '.join([h['id'], h['name']]) for h in hotels if h['hotelSectionType'] == 'AVAILABLE_HOTELS']
                hotel_ids = [h['id'] for h in hotels if h['hotelSectionType'] == 'AVAILABLE_HOTELS']
                selected_hotels = []
                # out_str = ''
                for id in hotel_ids:
                    r2 = requests.post("https://www.choicehotels.com/webapi/hotel/"+id.lower(),
                                       data={"businessFunction": "view_hotel",
                                             "include": ["amenities", "amenity_groups"], "preferredLocaleCode": "en-us"})
                    d2 = json.loads(r2.text)
                    descriptions = [a['description'] for a in d2['hotel']['amenities']]
                    # out_str += id + '--'.join(descriptions)
                    if specific_key in descriptions:
                        selected_hotels.append(hotel_id_dict[id])

                hotel_names_string = '\t'.join(selected_hotels)
                speech = "Found " + str(len(selected_hotels)) + " hotel(s) for " + specific_request + ": " + hotel_names_string
                # speech = out_str
                data = selected_hotels
            else:
                speech = "Requesting for " + place + ' returned status: ' + str(r.status_code) + r.reason
                data = {}

        except:
            speech = 'Not working for ' + place
            data = {}

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
