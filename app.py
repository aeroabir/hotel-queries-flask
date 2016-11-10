#!/usr/bin/env python

import urllib
import json
import os

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
    if req.get("result").get("action") == 'show.travel.plans':
        result = req.get("result")
        parameters = result.get("parameters")
        plan_type = parameters.get("travel-plan")
        speech = 'Roaming plans are available only for $10 a day'

    elif req.get("result").get("action") == "show.simonly.plans":  # action name
        result = req.get("result")
        parameters = result.get("parameters")

        plan_type = parameters.get("mobile-plan")  # parameter name

        # 2-yearly plans for phone+sim
        plan = {'lowest': [40, '1 GB Data, Unlimited Standard National Talk and Text'],
                'low': [65, '3.5 GB Data, Unlimited Standard National Talk and Text; Upto 150 International Minutes'],
                'medium': [85, '8 GB Data, Unlimited Standard National Talk and Text; Upto 300 International Minutes'],
                'high': [100, '15 GB Data, Unlimited Standard National Talk and Text; Upto 400 International Minutes'],
                'highest': [120, '20 GB Data, Unlimited Standard National Talk and Text; Unlimited International Minutes and International Roaming']}

        if plan_type in plan.keys():
            speech = "For a monthly plan of $" + str(plan[plan_type][0]) + " you get " + plan[plan_type][1]
        else:
            speech = 'Monthly plans are available only for $40, 65, 85, 100 and 120'

    elif req.get("result").get("action") == "show.mobile.plans":  # action name
        result = req.get("result")
        parameters = result.get("parameters")

        plan_type = parameters.get("mobile-plan")  # parameter name

        # 2-yearly plans for phone+sim
        plan = {'lowest': [40, '1 GB Data, Unlimited Standard National Talk and Text'],
                'low': [65, '3.5 GB Data, Unlimited Standard National Talk and Text; Upto 150 International Minutes'],
                'medium': [85, '8 GB Data, Unlimited Standard National Talk and Text; Upto 300 International Minutes'],
                'high': [100, '15 GB Data, Unlimited Standard National Talk and Text; Upto 400 International Minutes'],
                'highest': [120, '20 GB Data, Unlimited Standard National Talk and Text; Unlimited International Minutes and International Roaming']}

        if plan_type in plan.keys():
            speech = "For a monthly plan of $" + str(plan[plan_type][0]) + " you get " + plan[plan_type][1]
        else:
            speech = 'Monthly plans are available only for $40, 65, 85, 100 and 120'


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
