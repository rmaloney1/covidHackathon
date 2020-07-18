# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://covidspace.atlassian.net/rest/api/3/search"

auth = HTTPBasicAuth("rohanmaloney@outlook.com", "lxZVdyemldyTFkmwM5Hn94BD")

headers = {
   "Accept": "application/json"
}

query = {
   'jql': 'project = COV',
   'fields' : 'key,id,self,assignee,summary,priority,duedate,creator,watches'
}

# response = requests.request(
#    "GET",
#    url,
#    headers=headers,
#    params=query,
#    auth=auth
# )

# print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

class apiUser(object):
    def __init__(self, email, apitoken):
        self.email = email
        self.apitoken = apitoken
    def getAuth(self):
        return HTTPBasicAuth(self.email, self.apitoken)

class jiraQuery(object):
    def __init__(self, auth, domain, path, query=None, method="GET"):
        self.domain = domain
        self.path = path
        self.query = query
        self.method = method
        self.auth = auth
    def send(self):
        url = "https://" + self.domain + self.path
        response = requests.request(
            self.method,
            url,
            headers=headers,
            params=self.query,
            auth=self.auth)
        return response

class Project(object):
    def __init__(self, domain, projKey):
        self.domain = domain
        self.projKey = projKey

    def getIssueKeys(self, auth):
        path = "/rest/api/3/search"
        query = {
            'jql': f'project = {self.projKey}',
            'fields' : 'key',
        }
        queryObj = jiraQuery(auth, self.domain, path, query=query)
        response = queryObj.send()
        lis = [x["key"] for x in json.loads(response.text)["issues"]]
        return lis
    
    def getIssues(self, auth):
        return [Issue(key, self) for key in self.getIssueKeys(auth)]
        


class Issue(object):
    def __init__(self, key, project):
        self.key = key
        self.project = project
    
    def getFields(self, fields, auth):
        path = "/rest/api/3/issue/" + self.key
        query = {
            'fields' : ','.join(fields)
        }
        queryObj = jiraQuery(auth, self.project.domain, path, query=query)
        response = queryObj.send()
        return json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
    
    def getWatchers(self, auth):
        path = f"/rest/api/3/issue/{self.key}/watchers"
        queryObj = jiraQuery(auth, self.project.domain, path)
        response = queryObj.send()
        data = json.loads(response.text)["watchers"]
        #print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        return [{k:i[k] for k in ["accountId", "displayName", "avatarUrls"]} for i in data]

if __name__ == "__main__":
    me = apiUser("rohanmaloney@outlook.com", "lxZVdyemldyTFkmwM5Hn94BD")
    auth = me.getAuth()
    test = Project("covidspace.atlassian.net", "COV")
    # print()
    keys = test.getIssueKeys(auth)
    print(keys)
    # print(test.getIssueKeys(auth))
    testIssue = test.getIssues(auth)[0]
    print()
    print(testIssue.getFields(['summary', 'id', 'assignee'], auth))
    print()
    print(json.dumps(testIssue.getWatchers(auth), indent=4, separators=(",", ": ")))