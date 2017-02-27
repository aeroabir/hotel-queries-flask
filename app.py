#!/usr/bin/env python

import urllib
import json
import os
import random
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

        place = parameters.get("place")
        request_string = '{"placeName": "' + place + '"}'
        # r = requests.post("https://www.choicehotels.com/webapi/location/hotels", data=request_string)
        # r = '{"status":"OK","placeCount":16,"hotelCount":3,"totalHotelCount":3,"searchRadiusUsed":25.0,"places":[{"name":"California","id":"390342","type":"City","lat":"38.303101","lon":"-76.518600","city":"California","subdivision":"MD","country":"US","popularity":20,"usedForHotelSearch":true,"radius":25.0},{"name":"University of California-Berkeley","id":"635007","type":"College","lat":"37.872372","lon":"-122.266243","city":"Berkeley","subdivision":"CA","country":"US","popularity":16,"radius":25.0},{"name":"California","id":"412270","type":"City","lat":"40.066799","lon":"-79.892349","city":"California","subdivision":"PA","country":"US","popularity":14,"radius":25.0},{"name":"California","id":"400038","type":"City","lat":"38.635792","lon":"-92.566299","city":"California","subdivision":"MO","country":"US","popularity":5,"radius":25.0},{"name":"California","id":"415386","type":"City","lat":"38.917702","lon":"-84.263428","city":"California","subdivision":"KY","country":"US","popularity":3,"radius":25.0},{"name":"California","id":"34256","type":"City","lat":"46.848061","lon":"-67.761047","city":"California","subdivision":"NB","country":"CA","popularity":2,"radius":25.0},{"name":"Emiliano Zapata","id":"260294","type":"City","lat":"22.208639","lon":"-97.836861","city":"Emiliano Zapata","subdivision":"VER","country":"MX","popularity":1,"radius":25.0},{"name":"California","id":"287731","type":"City","lat":"16.179520","lon":"-93.269051","city":"California","subdivision":"CHP","country":"MX","popularity":1,"radius":25.0},{"name":"California","id":"1234041","type":"City","lat":"22.205469","lon":"-97.840286","city":"California","subdivision":"VER","country":"MX","radius":25.0},{"name":"California","id":"1226921","type":"City","lat":"22.140150","lon":"-101.022720","city":"California","subdivision":"SLP","country":"MX","radius":25.0},{"name":"California","id":"271625","type":"City","lat":"26.796370","lon":"-101.419098","city":"California","subdivision":"COA","country":"MX","radius":25.0},{"name":"California","id":"1245426","type":"City","lat":"22.285080","lon":"-102.253189","city":"California","subdivision":"AGU","country":"MX","radius":25.0},{"name":"Calif\xf3rnia","id":"786130","type":"City","lat":"-20.702841","lon":"-46.619160","city":"Calif\xf3rnia","subdivision":"MG","country":"BR","radius":25.0},{"name":"California","id":"1236913","type":"City","lat":"27.195419","lon":"-104.851967","city":"California","subdivision":"CHH","country":"MX","radius":25.0},{"name":"Calif\xf3rnia","id":"298456","type":"City","lat":"37.303169","lon":"-8.023890","city":"Calif\xf3rnia","country":"PT","radius":25.0},{"name":"California","id":"susca","type":"CountrySubdivision","subdivision":"CA","country":"US"}],"hotels":[{"id":"MD275","name":"Island Inn & Suites, an Ascend Hotel Collection Member","brandCode":"AC","brandName":"Ascend Hotel Collection","productCode":"HO","productName":"Hotel","phone":"(301) 994-1234","lat":"38.130094","lon":"-76.494514","distanceValue":12.028672556519004,"distanceUnit":"Miles","direction":173.74962303176878,"daylightSavings":true,"floors":3,"gmtOffset":-300,"timezoneLocation":"America/New_York","guestRooms":28,"meetingRooms":0,"address":{"city":"Piney Point","country":"US","line1":"16810 Piney Point Road","postalCode":"20674","subdivision":"MD"},"hasCategory":false,"status":"ACTIVE","rateRanges":[{"min":{"ratePlanCode":"SCPM","currencyCode":"USD","avgNightlyBeforeTax":"160.55","avgNightlyAfterTax":"178.21","nights":1,"startDate":"2017-02-28","endDate":"2017-03-01","beforeTax":"160.55","afterTax":"178.21"}},{"min":{"ratePlanCode":"RACK","currencyCode":"USD","avgNightlyBeforeTax":"169.00","avgNightlyAfterTax":"187.59","nights":1,"startDate":"2017-02-28","endDate":"2017-03-01","beforeTax":"169.00","afterTax":"187.59"}}],"hotelSectionType":"AVAILABLE_HOTELS"},{"id":"MD414","name":"Quality Inn Solomons - Beacon Marina","description":"Behind every great day is a great night at the Comfort Inn Solomons - Beacon Marina hotel in Solomons, MD near Solomons Island. Located off Routes 2 and 4, our waterfront hotel is on the Beacon Marina near Calvert Marine Museum, Tiki Bar of Solomons Island, St. Mary\'s College of Maryland and more. We cater to both business and leisure travelers alike with hotel amenities like free breakfast, free WiFi, a restaurant and lounge, a seasonal outdoor pool, an exercise room, business center and much more. Enjoy the space you need to spread out in your guest room complete with a TV, refrigerator and microwave. Also, earn rewards including free nights and gift cards with our Choice Privileges Rewards program. ","brandCode":"QI","brandName":"Quality","productCode":"IN","productName":"Inn","coOpParticipant":true,"phone":"(410) 326-6303","lat":"38.333048","lon":"-76.462718","distanceValue":3.666697199281809,"distanceUnit":"Miles","direction":55.69931616502005,"floors":2,"guestRooms":60,"meetingRooms":0,"address":{"city":"Solomons","country":"US","line1":"255 Lore Rd.","postalCode":"20688","subdivision":"MD"},"status":"ACTIVE","hotelSectionType":"UNAVAILABLE_HOTELS"},{"id":"MD232","name":"Comfort Inn & Suites","description":"Behind every great day is a great night at the award-winning Comfort Inn and Suites in Lexington Park, MD, which is conveniently located near Naval Air Station Patuxent River. A recipient of the Choice Hotels Preferred Platinum Award, this hotel gives you easy access to such nearby points of interest as Colonial Sotterley Plantation, Point Lookout State Park, Solomons Island and Elms Beach Park. Get ready to take on the day with such amenities as free WiFi, free hot breakfast, fitness and business centers. Rest and refresh in your guest room, which features a refrigerator, microwave, coffee maker and TV. Also, earn rewards including free nights and gift cards with our Choice Privileges Rewards program. Rested. Set. Go. ","brandCode":"CI","brandName":"Comfort","productCode":"AS","productName":"Inn & Suites","coOpParticipant":true,"phone":"(301) 863-1051","lat":"38.268177","lon":"-76.458036","distanceValue":4.079465047401413,"distanceUnit":"Miles","direction":126.32683555803536,"floors":5,"guestRooms":55,"meetingRooms":0,"address":{"city":"Lexington Park","country":"US","line1":"21885 Three Notch Road","postalCode":"20653","subdivision":"MD","county":"St Marys"},"status":"ACTIVE","hotelSectionType":"UNAVAILABLE_HOTELS"}]}'
        # d = json.loads(r)
        # hotels = d['hotels']
        # hotel_names = [h['name'] for h in hotels]
        # hotel_names_string = '\t'.join(hotel_names)
        # speech = "Found " + len(hotels) + " hotels: " + hotel_names_string

        speech = 'No data stored yet ...'

    else:
        speech = 'No matching intent found ... python code returns None'


    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')
