# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://covidspace.atlassian.net/rest/api/3/project/COV/role/10002"

auth = HTTPBasicAuth("rohanmaloney@outlook.com", "lxZVdyemldyTFkmwM5Hn94BD")

headers = {
   "Accept": "application/json"
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   auth=auth
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))