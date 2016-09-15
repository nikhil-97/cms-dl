import requests

def site_check(url):
    try:
        response=requests.get(url,timeout=10)
        if(int(response.status_code)==200):
            return True
    except ((requests.ConnectionError) or (requests.HTTPError)):
        return False

