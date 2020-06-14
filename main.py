# Python libraries that we need to import for our bot
from flask import Flask, request, jsonify
from pymemcache.client import base
from pymessenger.bot import Bot
from wit import Wit

from botZero import webhooks, utill, flowManager

ACCESS_TOKEN = 'XXXXXXXX2MAYBAMZBNMFTBUasYZCHdlC03lzjW7eZBELrffmEA6yBRcDNL0zdxPZCVqp0x8JxDRLXXXXXXXXXXXXX7CBNgZCdqgl6WkmZBMJQbi4P08WfyZAEZCAh78lp6mThEFa3KATp18Sv4m01ZAEXXXXXXX'
VERIFY_TOKEN = 'XXXXXXXXXX'
WIT_TOKEN = 'XXWUIUODWGXXXXXXKJVO6JEUKTOZEBXX'
MEMCACHE_IP = 'localhost'
MEMCACHE_PORT = 11211

bot = Bot(ACCESS_TOKEN)
client = Wit(WIT_TOKEN)
app = Flask(__name__)

FLOW_DEFINITION = {"intent_self_assessment": {"flow_name": "intent_self_assessment",
                                              "flow_entities": ["symptoms", "conditions", "travel", "contact"],
                                              "entity_definitions": [{
                                                  "entity_name": "symptoms",
                                                  "req_msg": "Are you experiencing any of the symptoms such as cough, fever, difficulty in breathing?",
                                                  "rep_req_msg": "Please select from the options provided. Are you experiencing any of the symptoms such as cough, fever, difficulty in breathing?",
                                                  "entity_validator": [{"type": "options", "loc": "constant",
                                                                        "value": {"Yes": "Yes", "No": "No",
                                                                                  "Cancel": "Cancel"}}],
                                                  "can_skip": False,
                                                  "webhook": {},
                                                  "options": {"loc": "constant",
                                                              "value": {"Yes": "Yes", "No": "No", "Cancel": "Cancel"}}
                                              },
                                                  {
                                                      "entity_name": "conditions",
                                                      "req_msg": "Have you ever had any of the following conditions like Diabetes, Hypertension, Heart or lung disease?",
                                                      "rep_req_msg": "Please select from the options provided. Have you ever had any of the following conditions like Diabetes, Hypertension, Heart or lung disease?",
                                                      "entity_validator": [{"type": "options", "loc": "constant",
                                                                            "value": {"Yes": "Yes", "No": "No",
                                                                                      "Cancel": "Cancel"}}],
                                                      "can_skip": False,
                                                      "webhook": {},
                                                      "options": {"loc": "constant", "value": {"Yes": "Yes", "No": "No",
                                                                                               "Cancel": "Cancel"}}
                                                  },
                                                  {
                                                      "entity_name": "travel",
                                                      "req_msg": "Have you travelled internationally anywhere in the last 45 days?",
                                                      "rep_req_msg": "Please select from the options provided. Have you travelled internationally anywhere in the last 45 days?",
                                                      "entity_validator": [{"type": "options", "loc": "constant",
                                                                            "value": {"Yes": "Yes", "No": "No",
                                                                                      "Cancel": "Cancel"}}],
                                                      "can_skip": False,
                                                      "webhook": {},
                                                      "options": {"loc": "constant", "value": {"Yes": "Yes", "No": "No",
                                                                                               "Cancel": "Cancel"}}
                                                  },
                                                  {
                                                      "entity_name": "contact",
                                                      "req_msg": "Have you recently came in contact with a person who has tested positive for COVID 19?.",
                                                      "rep_req_msg": "Please select from the options provided. Have you travelled internationally anywhere in the last 45 days.",
                                                      "entity_validator": [{"type": "options", "loc": "constant",
                                                                            "value": {"Yes": "Yes", "No": "No",
                                                                                      "Cancel": "Cancel"}}],
                                                      "can_skip": False,
                                                      "webhook": {},
                                                      "options": {"loc": "constant", "value": {"Yes": "Yes", "No": "No",
                                                                                               "Cancel": "Cancel"}}
                                                  }
                                              ],
                                              "final_webhook": {"webhook_name": "assessment",
                                                                "headers": {},
                                                                "body": {"symptoms": {
                                                                    "loc": "flowEntityData",
                                                                    "flow_name": "intent_self_assessment",
                                                                    "key": "symptoms",
                                                                    "mandatory": True
                                                                }, "conditions": {
                                                                    "loc": "flowEntityData",
                                                                    "flow_name": "intent_self_assessment",
                                                                    "key": "conditions",
                                                                    "mandatory": True
                                                                }, "travel": {
                                                                    "loc": "flowEntityData",
                                                                    "flow_name": "intent_self_assessment",
                                                                    "key": "travel",
                                                                    "mandatory": True
                                                                }, "contact": {
                                                                    "loc": "flowEntityData",
                                                                    "flow_name": "intent_self_assessment",
                                                                    "key": "contact",
                                                                    "mandatory": True
                                                                }},
                                                                "http_method": "POST",
                                                                "url": "https://vedika-virtual-assistant.uc.r.appspot.com/analyze"
                                                                },
                                              "res_msg": "<<webhookData___assessment___respmsg>>",
                                              "persist_data": False
                                              }}


# Health
@app.route("/healthCheck", methods=['GET'])
def health():
    try:
        cache_client = base.Client((MEMCACHE_IP, MEMCACHE_PORT))
        cache_client.set("TEST", "VALUE")
        value = cache_client.get("TEST", "DEF")
        return value
    except Exception as e:
        print("EXCEPTION" + str(e.args))
        return str(e.args)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/analyze", methods=['POST'])
def analyze_assessment():
    print("analyze_assessment")
    resp = {"respmsg": "Something went wrong. Please check back later."}
    if request.json:
        print(request.json)
        if request.json["contact"] == 'Yes' and request.json["symptoms"] == 'No':
            resp = {"respmsg": "Since you have came in contact with COVID19 patient and do not have any symptoms, your infection risk is moderate."
                    " Please stay in home quarantine, Do remember that currently it is safer to consult a doctor through phone or video than to visit hospital."
                    " Please get a test at the earliest from Day 5 onwards, and within 14 days of the first interaction or earlier if symptoms appear."}
        elif request.json["contact"] == 'Yes' and request.json["symptoms"] == 'Yes':
            resp = {"respmsg": "Since you have came in contact with COVID19 patient and have symptoms, your infection risk is high."
                    " Please get a test done from your nearest COVID19 hospital."
                    " I recommend you stay at home to avoid any chance of exposure to the Novel Coronavirus."}
        elif request.json["symptoms"] == 'Yes' and request.json["travel"] == 'Yes':
            resp = {"respmsg": "While you are unwell and have a travel history, your infection risk is moderate. \n\n"
                    " Do remember that currently it is safer to consult a doctor through phone or video than to visit hospital. \n\n"
                    " I recommend you stay at home to avoid any chance of exposure to the Novel Coronavirus.  "}
        elif request.json["symptoms"] == 'Yes' and request.json["travel"] == 'No':
            resp = {"respmsg": "While you are unwell, your infection risk is low."
                    " Do remember that currently it is safer to consult a doctor through phone or video than to visit hospital."
                    " I recommend you stay at home to avoid any chance of exposure to the Novel Coronavirus.  "}
        else:
            resp = {"respmsg": "Your Infection risk is low. I recommend you stay at home to avoid any chance of exposure to the Novel Coronavirus"}
    return jsonify(resp)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        print(output)
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    cache_client = base.Client((MEMCACHE_IP, MEMCACHE_PORT))
                    session = utill.load_session(recipient_id, cache_client)

                    if session.get("activeFlow"):
                        response_sent_text, options, flow_complete = flowManager.run(
                            flow_def=FLOW_DEFINITION[str(session.get("activeFlow"))],
                            begin=False,
                            query=message['message'].get('text'),
                            session=session,
                            session_id=recipient_id)
                        if flow_complete:
                            session['activeFlow'] = ''
                            utill.save_session(recipient_id, session, cache_client)
                            options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]
                        response_sent_text = [response_sent_text]
                        send_message(recipient_id, response_sent_text, options)

                    elif message['message'].get('text'):
                        wit_resp = client.message(message['message'].get('text'))
                        print('Yay, got Wit.ai response: ' + str(wit_resp))
                        response_sent_text, options, image = get_message(wit_resp, recipient_id)
                        send_message(recipient_id, response_sent_text, options, image)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    elif message['message'].get('attachments'):
                        send_message(recipient_id, "Format Not supported", [])

                elif message.get('postback'):
                    recipient_id = message['sender']['id']
                    cache_client = base.Client((MEMCACHE_IP, MEMCACHE_PORT))
                    session = utill.load_session(recipient_id, cache_client)
                    if session.get("activeFlow"):
                        response_sent_text, options, flow_complete = flowManager.run(
                            flow_def=FLOW_DEFINITION[str(session.get("activeFlow"))],
                            begin=False,
                            query=message['postback'].get('payload'),
                            session=session,
                            session_id=recipient_id)
                        if flow_complete:
                            session['activeFlow'] = ''
                            utill.save_session(recipient_id, session, cache_client)
                            options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]
                        response_sent_text = [response_sent_text]
                        send_message(recipient_id, response_sent_text, options)
                    elif message['postback'].get('payload'):
                        wit_resp = client.message(message['postback'].get('payload'))
                        print('Yay, got Wit.ai response: ' + str(wit_resp))
                        response_sent_text, options, image = get_message(wit_resp, recipient_id)
                        send_message(recipient_id, response_sent_text, options, image)

    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#  Get Response to user query
def get_message(wit_resp, recipient_id):
    cache_client = base.Client((MEMCACHE_IP, MEMCACHE_PORT))
    options = []
    image = ""
    if wit_resp:
        if wit_resp["entities"].get("intent") and len(wit_resp["entities"]["intent"]) > 0 and \
                wit_resp["entities"]["intent"][0]["confidence"] > .7:
            if wit_resp["entities"]["intent"][0]["value"] == 'intent_greeting':
                response = ["Hello " + webhooks.get_facebook_user_name(recipient_id,
                                                                    bot.access_token).capitalize() + "!, I am Vedika. I am here to assist you in your fight against COVID19"]
                options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]
                image = r"https://vedika-virtual-assistant.uc.r.appspot.com/static/FB-03.png"

            elif wit_resp["entities"]["intent"][0]["value"] == 'intent_stats':
                options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]
                if wit_resp["entities"].get("location"):
                    covid_data = webhooks.current_covid_date(wit_resp["entities"].get("location")[0]["value"],
                                                             cache_client)
                    if len(covid_data) == 1:
                        region = str(covid_data[0]["Country"]).capitalize()
                        response = ["Here are the current " + region + " COVID19 stats. \n\nNew Confirmed : "
                                    + str(covid_data[0]["NewConfirmed"]) + \
                                    "\nTotal confirmed : " + str(covid_data[0]["TotalConfirmed"]) + "\nNew Deaths : " + \
                                    str(covid_data[0]["NewDeaths"]) + "\nTotal Deaths : " + str(
                            covid_data[0]["TotalDeaths"]) + \
                                    "\nNew Recovered : " + str(
                            covid_data[0]["NewRecovered"]) + "\nTotal Recovered : " + str(
                            covid_data[0]["TotalRecovered"])]
                    else:
                        response = ['I am sorry I do not have COVID19 data for this country.']
                else:
                    print("GLOBAL STATS")
                    covid_data = webhooks.current_covid_date("global", cache_client)
                    region = "Global".capitalize()
                    if len(covid_data) == 1:
                        response = ["Here are the current " + region + " COVID19 stats. \n\nNew Confirmed : " + str(
                            covid_data[0]["NewConfirmed"]) + \
                                    "\nTotal confirmed : " + str(covid_data[0]["TotalConfirmed"]) + "\nNew Deaths : " + \
                                    str(covid_data[0]["NewDeaths"]) + "\nTotal Deaths : " + str(
                            covid_data[0]["TotalDeaths"]) + \
                                    "\nNew Recovered : " + str(
                            covid_data[0]["NewRecovered"]) + "\nTotal Recovered : " + str(
                            covid_data[0]["TotalRecovered"]),
                                    "You can also get the country wise stats. For Eg: try \"Current COVID19 stats in India.\""]
                    else:
                        response = ['I am sorry I do not have COVID19 data for this country.']
            elif wit_resp["entities"]["intent"][0]["value"] == 'intent_self_assessment':
                print("intent_self_assessment")
                cache_client = base.Client((MEMCACHE_IP, MEMCACHE_PORT))
                session = utill.load_session(recipient_id, cache_client)

                response, options, flow_complete = flowManager.run(
                    flow_def=FLOW_DEFINITION["intent_self_assessment"],
                    begin=True,
                    query=None,
                    session=session,
                    session_id=recipient_id)
                response = [response]
                if flow_complete:
                    session['activeFlow'] = ''
                    utill.save_session(recipient_id, session, cache_client)
                    options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]
                else:
                    session['activeFlow'] = 'intent_self_assessment'
                    utill.save_session(recipient_id, session, cache_client)
            elif wit_resp["entities"]["intent"][0]["value"] == 'intent_covid19_symptoms':
                response = ["Seek immediate medical attention if you have serious symptoms. Always call before visiting your doctor or health facility."]
                image = r"https://vedika-virtual-assistant.uc.r.appspot.com/static/FB-02.png"
                options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]
            elif wit_resp["entities"]["intent"][0]["value"] == 'intent_precautions':
                response = ["Here are some precautions you can take."]
                image = r"https://vedika-virtual-assistant.uc.r.appspot.com/static/FB-01.png"
                options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]
            else:
                response = ['I am not sure of your request.']
                options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]
        else:
            response = ['I am not sure of your request.']
            options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]
    else:
        response = ['I am not sure of your request.']
        options = ["Self assessment", "Live COVID19 tracker", "Symptoms", "Precautions"]

    # return selected item to the user
    return response, options, image


# uses PyMessenger to send response to user
def send_message(recipient_id, response, options, image=None):
    # sends user the text message provided via input response parameter
    print("Response::::" + str(response))
    if options:
        buttons = []
        message = dict()

        if image:
            bot.send_image_url(image_url=image, recipient_id=recipient_id)

        for msg in response[:-1]:
            bot.send_text_message(recipient_id, msg)

        for option in options:
            quick_replies = dict()
            quick_replies["content_type"] = "text"
            quick_replies["title"] = option
            quick_replies["payload"] = option
            buttons.append(quick_replies)

        message['text'] = response[-1]
        message['quick_replies'] = buttons
        bot.send_message(recipient_id, message)

    elif image:
        for msg in response:
            bot.send_text_message(recipient_id, msg)
        bot.send_image_url(image_url=image, recipient_id=recipient_id)
    else:
        for msg in response:
            bot.send_text_message(recipient_id, msg)

    return "success"


if __name__ == "__main__":
    app.run()
