import requests
import json
import ast


def current_covid_date(country, cache_client):

    data = dict()
    covid_data = []
    url = "https://api.covid19api.com/summary"

    payload = {}
    headers = {}

    if cache_client.get("covid_data"):
        data = cache_client.get("covid_data").decode("utf-8")
        data = ast.literal_eval(data)

    else:
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            data = str(response.json())
            data = data.replace("ô", "o")
            cache_client.set("covid_data", data, 100000)
            data = json.dumps(data)
            data = json.loads(data)

    if data:
        if country == 'global':
            covid_data.append(data["Global"])
        else:
            for country_data in data["Countries"]:
                if str(country_data["Slug"]).lower().replace("-"," ") in str(country).lower():
                    covid_data.append(country_data)
    return covid_data


def get_facebook_user_name(user_id, token):
    facebook_graph_url = "https://graph.facebook.com/"+str(user_id)+"?fields=first_name,last_name&access_token=" + str(token)

    response = requests.get(url=facebook_graph_url)

    try:
        if response.status_code == 200:
            response_data = response.json()
            name = response_data["first_name"]
        else:
            name = ""
    except:
        name = ""
    return name