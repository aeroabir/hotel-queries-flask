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
    if req.get("result").get("action") != "show.mobile.plans":  # Intent?
        return {}
    result = req.get("result")
    parameters = result.get("parameters")

    per_month = parameters.get("mobile-plan")  # parameter name

    plan = {'lowest': '1 GB Data, Unlimited Standard National Talk and Text',
            'low': '3.5 GB Data, Unlimited Standard National Talk and Text; Upto 150 International Minutes',
            'medium': '3.5 GB Data, Unlimited Standard National Talk and Text; Upto 300 International Minutes',
            'high': '3.5 GB Data, Unlimited Standard National Talk and Text; Upto 400 International Minutes',
            'highest': '3.5 GB Data, Unlimited Standard National Talk and Text; Unlimited International Minutes'}

    if per_month in plan.keys():
        speech = "For monthly " + per_month + "$ you get " + plan[per_month]
    else:
        speech = 'Monthly plans are available only for $40, 65, 85, 100 and 120'

    # zone = parameters.get("shipping-zone")
    # cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}
    # speech = "The cost of shipping to " + zone + " is " + str(cost[zone]) + " euros."

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
