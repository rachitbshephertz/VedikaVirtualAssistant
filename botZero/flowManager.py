import re
from pymemcache.client import base
from datetime import datetime
import requests
import ast

MEMCACHE_IP = '10.83.64.3'
MEMCACHE_PORT = 11211


def get_session(session_id):
    cache_client = base.Client((MEMCACHE_IP, MEMCACHE_PORT))
    session = cache_client.get(session_id)
    if session:
        session = session.decode("utf-8")
        session = ast.literal_eval(session)
    cache_client.close()
    return session


def set_session(session_id, current_session):
    cache_client = base.Client((MEMCACHE_IP, MEMCACHE_PORT))
    cache_client.set(session_id, current_session, 120)
    cache_client.close()


def extract_entity(entity_validator_rule, can_skip, query, session=None):
    for rule in entity_validator_rule:
        print(rule)
        if can_skip and (str(query).lower() == 'skip'):
            return "SKIP"
        elif rule["type"] == "word_count":
            if len(query.split()) <= int(rule["value"]):
                return query
        elif rule["type"] == "regex":
            all_match = re.findall(rule["value"], str(query).strip())
            if len(all_match) > 0:
                return all_match[0]
        elif rule["type"] == "options":
            valid_options = dict()
            if rule["loc"] == 'session':
                valid_options = session.get(rule["key"])
                if query in valid_options.keys():
                    return valid_options[query]
            elif rule["loc"] == 'flowEntityData':
                valid_options = session.get(rule["flow_name"] + "_entity_data")
                if query in valid_options.keys():
                    return valid_options[query]
            elif rule["loc"] == 'webhookData':
                print(rule["webhook_name"] + "_webhook_data")
                valid_options = session.get(rule["webhook_name"] + "_webhook_data")
                if str(query).strip() in list(valid_options.keys()):
                    return valid_options[query]
            elif rule["loc"] == 'constant':
                valid_options = rule["value"]
                print("============>>" + str(valid_options.keys()))
                if query in valid_options.keys():
                    return valid_options[query]
    return None


def get_options(options, session):
    avbl_options = {}
    if options["loc"] == 'session':
        avbl_options = session.get(options["key"])
    elif options["loc"] == 'flowEntityData':
        avbl_options = session.get(options["flow_name"] + "_entity_data")
    elif options["loc"] == 'webhookData':
        avbl_options = session.get(options["webhook_name"] + "_webhook_data")
    elif options["loc"] == 'constant':
        avbl_options = options["value"]
    if avbl_options:
        return avbl_options.keys()
    else:
        return []


def generate_response_msg(msg, session):
    for word in msg.split():
        match = re.search(r"<<.*>>", str(word).strip())
        replace_word = str(word).replace("<<", "").replace(">>", "")
        if match:
            loc = str(replace_word).split("___")[0]
            if loc == 'session':
                msg = msg.replace(word, str(session.get(str(replace_word).split("___")[1])))
            elif loc == 'flowEntityData':
                msg = msg.replace(word, str(
                    session.get(str(replace_word).split("___")[1] + "_entity_data")[str(replace_word).split("___")[2]]))
            elif loc == 'webhookData':
                msg = msg.replace(word, str(session.get(str(replace_word).split("___")[1] + "_webhook_data")[
                                                str(replace_word).split("___")[2]]))
            elif loc == 'constant':
                msg = msg.replace(word, str(str(replace_word).split("___")[1]))
    return msg


def execute_webhook(webhook_def, session):
    request_body = dict()
    if webhook_def.get("body"):
        for key in webhook_def.get("body").keys():
            param_loc_data = webhook_def.get("body")[key]
            if param_loc_data["loc"] == 'session':
                request_body[key] = str(session.get(param_loc_data["key"]))
            elif param_loc_data["loc"] == 'flowEntityData':
                request_body[key] = str(
                    session.get(param_loc_data["flow_name"] + "_entity_data")[param_loc_data["key"]])
            elif param_loc_data["loc"] == 'webhookData':
                request_body[key] = str(
                    session.get(param_loc_data["webhook_name"] + "_webhook_data")[param_loc_data["key"]])
            elif param_loc_data["loc"] == 'constant':
                request_body[key] = str(param_loc_data["value"])

    headers = dict()
    if webhook_def.get("headers"):
        for key in webhook_def.get("headers").keys():
            param_loc_data = webhook_def.get("headers")[key]
            if param_loc_data["loc"] == 'session':
                headers[key] = str(session.get(param_loc_data["key"]))
            elif param_loc_data["loc"] == 'flowEntityData':
                headers[key] = str(
                    session.get(param_loc_data["flow_name"] + "_entity_data")[param_loc_data["key"]])
            elif param_loc_data["loc"] == 'webhookData':
                headers[key] = str(
                    session.get(param_loc_data["webhook_name"] + "_webhook_data")[param_loc_data["key"]])
            elif param_loc_data["loc"] == 'constant':
                headers[key] = str(param_loc_data["value"])
    try:
        print("WEBHOOK")
        request_url = generate_response_msg(webhook_def["url"], session)
        print(request_body)
        print(request_url)
        response = requests.post(request_url, headers=headers, json=request_body)
        print(response.status_code)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            return None
    except Exception as e:
        print(e.args)
        print("something went wrong")
        return None

# Add dynamic req msg and type


def run(**kwargs):
    options = []
    flow_def = kwargs.get("flow_def")
    flow_name = flow_def["flow_name"]
    session = kwargs.get("session")
    session_id = kwargs.get("session_id")
    query = kwargs.get("query")
    flow_complete = False

    if str(query).lower() == "cancel":
        session.pop(str(flow_name) + "_entity_data", {})
        session["activeFlow"] = ""
        set_session(session_id, session)
        return "I have canceled your previous request", options, True

    if kwargs.get("begin"):
        flow_entity_values = {}
        session.pop(str(flow_name) + "_entity_data", {})
        # TODO; See it entities already exist in first user query
        for entity in flow_def.get("flow_entities"):
            if entity not in flow_entity_values:
                for ent_def in flow_def.get("entity_definitions"):
                    if ent_def["entity_name"] == entity:
                        if ent_def.get("pre_webhook"):
                            webhook_response = execute_webhook(ent_def.get("pre_webhook"), session)
                            if webhook_response:
                                session[str(ent_def.get("pre_webhook")["webhook_name"]) + "_webhook_data"] = webhook_response
                                set_session(session_id, session)
                            else:
                                pass
                        if ent_def["can_skip"]:
                            options = ['SKIP']
                        session[str(flow_name) + "_entity_data"] = flow_entity_values
                        set_session(session_id, session)
                        if ent_def.get("options"):
                            options = get_options(ent_def.get("options"), session)
                        return generate_response_msg(ent_def["req_msg"], session), options, flow_complete
    else:
        value_set = False
        flow_entity_values = session.get(str(flow_name) + "_entity_data", {})
        for entity in flow_def.get("flow_entities"):
            if value_set:
                break
            if entity not in flow_entity_values:
                for ent_def in flow_def.get("entity_definitions"):
                    if ent_def["entity_name"] == entity:
                        value = extract_entity(ent_def["entity_validator"], ent_def["can_skip"], query, session)
                        if value:
                            flow_entity_values[entity] = value
                            value_set = True
                            if ent_def.get("post_webhook"):
                                webhook_response = execute_webhook(ent_def.get("post_webhook"), session)
                                if webhook_response:
                                    session[str(ent_def.get("post_webhook")[
                                                    "webhook_name"]) + "_webhook_data"] = webhook_response
                                    set_session(session_id, session)
                                else:
                                    pass
                            break
                        else:
                            if ent_def["can_skip"]:
                                options = ['SKIP']
                            session[str(flow_name) + "_entity_data"] = flow_entity_values
                            if ent_def.get("options"):
                                options = get_options(ent_def.get("options"), session)
                            set_session(session_id, session)
                            return generate_response_msg(ent_def["rep_req_msg"], session), options, flow_complete

        for entity in flow_def.get("flow_entities"):
            if entity not in flow_entity_values:
                for ent_def in flow_def.get("entity_definitions"):
                    if ent_def["entity_name"] == entity:
                        if ent_def.get("pre_webhook"):
                            webhook_response = execute_webhook(ent_def.get("pre_webhook"), session)
                            if webhook_response:
                                session[str(ent_def.get("pre_webhook")[
                                                "webhook_name"]) + "_webhook_data"] = webhook_response
                                set_session(session_id, session)
                            else:
                                pass
                        if ent_def["can_skip"]:
                            options = ['SKIP']
                        session[str(flow_name) + "_entity_data"] = flow_entity_values
                        set_session(session_id, session)
                        if ent_def.get("options"):
                            options = get_options(ent_def.get("options"), session)
                        return generate_response_msg(ent_def["req_msg"], session), options, flow_complete

    session[str(flow_name) + "_entity_data"] = flow_entity_values
    set_session(session_id, session)

    if flow_def.get("final_webhook"):
        webhook_response = execute_webhook(flow_def.get("final_webhook"), session)
        if webhook_response:
            session[str(flow_def.get("final_webhook")["webhook_name"]) + "_webhook_data"] = webhook_response
            set_session(session_id, session)

    flow_complete = True
    response_msg = generate_response_msg(flow_def["res_msg"], session)

    if not flow_def.get("persist_data"):
        session.pop(str(flow_name) + "_entity_data", {})
        set_session(session_id, session)

    return response_msg, options, flow_complete

