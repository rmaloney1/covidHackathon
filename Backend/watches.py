# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://covidspace.atlassian.net/rest/api/3/issue/COV-20/watchers"

auth = HTTPBasicAuth("rohanmaloney@outlook.com", "lxZVdyemldyTFkmwM5Hn94BD")

headers = {
   "Accept": "application/json"
}

query = {
   'jql': 'project = COV',
   'fields' : 'key,id,self,assignee,summary,priority,duedate,creator,watches'
}

response = requests.request(
   "GET",
   url,
   headers=headers,
#    params=query,
   auth=auth
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))