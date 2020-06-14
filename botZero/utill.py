import hashlib
from datetime import datetime
import ast
import requests


# Generate Hash
def generate_hash(string):
    result = hashlib.md5(string.encode())
    result = result.hexdigest()
    return result


def load_session(session_id, cache_client):
    session = dict()

    if cache_client.get(session_id) is not None:
        session = cache_client.get(session_id).decode("utf-8")
        session = ast.literal_eval(session)

    if session:
        session['sessionLastActiveAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    else:
        session['sessionCreatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['sessionLastActiveAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session['activeFlow'] = ''
        session['botResponseLanguage'] = 'en'
        save_session(session_id, session, cache_client)
    cache_client.close()
    return session


def save_session(session_id, current_session, cache_client):
    cache_client.set(session_id, current_session)
    cache_client.close()
