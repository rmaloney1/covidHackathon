from models import CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest, model_to_dict

# if low priority, the number of days before due date an item can be pushed back by
SECRUTIY_BUFFER = 3

def makeAllocations():
    requestList = MeetingRequest.select().where(MeetingRequest.requestFilled == False).order_by(MeetingRequest.beforeDate.desc())
    requests = model_to_dict(MeetingRequest)
    # go through all requests
    # make a list of all people