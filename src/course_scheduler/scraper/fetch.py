import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

def get_page(url, timeout=10) -> str:
'''
Obtain raw HTML script from McGill e-calendar homepage

PARAMETERS:
url (str): URL to homepage
timeout (float): max time until Timeout exception is raised

RETURNS:
str: HTML from homepage
'''
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raises HTTPError if status is 4xx or 5xx
        return response.text
    except HTTPError as http_err:
        print(f"[HTTP ERROR] {url} returned status {response.status_code}: {http_err}")
    except ConnectionError:
        print(f"[CONNECTION ERROR] Could not connect to {url}")
    except Timeout:
        print(f"[TIMEOUT] {url} took too long to respond")
    except RequestException as err:
        print(f"[UNKNOWN ERROR] An error occurred: {err}")
    return None
