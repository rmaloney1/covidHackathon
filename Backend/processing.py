from models import CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest, model_to_dict
import datetime as dt

# if low priority, the number of days before due date an item can be pushed back by
SECRUTIY_BUFFER = 3

def makeAllocations():
    # allCurrentAllocations = PersonTickets.select().join(MeetingRequest).where(MeetingRequest.requestFilled == False).switch(PersonTickets).join(Person)
    peopleList = Person.select().order_by(-Person.activeTicketCount).join(PersonTickets)
    personMeetingRequests = MeetingRequest.select().join(PersonTickets)
    
    requestList = MeetingRequest.select().where(MeetingRequest.requestFilled == False).order_by(MeetingRequest.beforeDate)
    for request in requestList.iterator():
        if ((request.beforeDate - dt.date.today()).days <= SECRUTIY_BUFFER and not request.priority):
            request.elevatePriority()
            