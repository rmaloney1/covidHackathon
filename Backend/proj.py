# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

orgID = "88acec8b-a342-4741-aeae-90a7e795e6a3"
orgAPIKey = "dNxRkWHznNBexigeDpTP"

url = "https://covidspace.atlassian.net/rest/api/3/project/COV/roledetails"

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

try:
    print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
except:
    print(response.text)