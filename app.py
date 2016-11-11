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
        speech = 'Roaming plans are available for $10 a day'

    elif req.get("result").get("action") == "show.simonly.plans":  # action name
        result = req.get("result")
        parameters = result.get("parameters")
        period = parameters.get("plan-period")  # monthly or yearly
        user_input = parameters.get("unit-currency")  # parameter name

        monthly_amount = '100'

        if 'amount' in user_input:
            monthly_amount = str(user_input.get("amount"))

        if 'number' in parameters:
            monthly_amount = str(parameters.get('number'))

        if period == "monthly":

            plan = {'35': '1.5 GB Data, Unlimited Standard National Talk and Text',
                    '50': '6 GB Data, Unlimited Standard National Talk and Text; Upto 300 International Minutes',
                    '60': '9 GB Data, Unlimited Standard National Talk and Text; Upto 500 International Minutes'}

            if monthly_amount in plan.keys():
                speech = "For a monthly plan of $" + monthly_amount + " you get " + plan[monthly_amount]
            else:
                speech = 'Monthly plans are available only for $35, 50 and 60'

        elif period == "yearly":

            plan = {'30': '1.5 GB Data and Unlimited Standard National Talk and Text',
                    '40': '6 GB Data, Unlimited Standard National Talk and Text and Upto 300 International Minutes',
                    '50': '9 GB Data, Unlimited Standard National Talk and Text and Upto 500 International Minutes'}

            if monthly_amount in plan.keys():
                speech = "For a yearly plan of $" + monthly_amount + " per month you get " + plan[monthly_amount]
            else:
                speech = 'Yearly plans are available only for $30, 40 and 50'

        else:
            speech = 'No matching plan found for ' + period

    elif req.get("result").get("action") == "show.bundle.plans":  # action name

        result = req.get("result")
        parameters = result.get("parameters")
        # period = parameters.get("plan-period")  # monthly or yearly
        user_input = parameters.get("unit-currency")  # parameter name

        monthly_amount = '100'

        if 'amount' in user_input:
            monthly_amount = str(user_input.get("amount"))

        if 'number' in parameters:
            monthly_amount = str(parameters.get('number'))

        # 2-yearly plans for phone+sim
        plan = {'40': '1 GB Data, Unlimited Standard National Talk and Text',
                '65': '3.5 GB Data, Unlimited Standard National Talk and Text; Upto 150 International Minutes',
                '85': '8 GB Data, Unlimited Standard National Talk and Text; Upto 300 International Minutes',
                '100': '15 GB Data, Unlimited Standard National Talk and Text; Upto 400 International Minutes',
                '120': '20 GB Data, Unlimited Standard National Talk and Text; Unlimited International Minutes and International Roaming'}

        if monthly_amount in plan.keys():
            speech = "For a two-yearly plan of $" + monthly_amount + " you get " + plan[monthly_amount]
        else:
            speech = 'Yearly plans are available only for $40, 65, 85, 100 and 120'
    else:
        speech = 'No matching intent found ... python returns None'


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
