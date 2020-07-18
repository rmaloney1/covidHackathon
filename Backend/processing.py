from models import CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest, model_to_dict
import datetime as dt

# if low priority, the number of days before due date an item can be pushed back by
SECRUTIY_BUFFER = 3

#numsafedays 
UNSAFEDAYS = 14


def makeAllocations():
    requestList = MeetingRequest.select().where(MeetingRequest.requestFilled == False).order_by(MeetingRequest.beforeDate)
    # allCurrentAllocations = PersonTickets.select().join(MeetingRequest).where(MeetingRequest.requestFilled == False).switch(PersonTickets).join(Person)
    peopleList = Person.select()
    allocatedPeople = []

    for request in requestList.iterator():
        if (request.beforeDate - dt.date.today() <= SECRUTIY_BUFFER and not request.priority):
            request.elevatePriority()

#contact tracing   
#takes a personID
#ID is the name
def contactTrace(p_id):
    tickets = []
    contacted = [] 

    #join personTickets to Requests as PersonTicketRequests 
    PersonMeetingRequest = (MeetingRequest.select().join(PersonTickets).where(PersonTickets.person=p_id)) 
    #for p_id in personTicketRequests 
    for pmr in PersonMeetingRequest.iterator(): 
        #if dateallocated in last 2 weeks 
        if pmr.requestFilled: 
            if (dt.date.today() - pmr.dateAllocated).days < UNSAFEDAYS:
                #add to list of tickets 
                tickets.append(pmr.ticketID)
            
    for t_id in tickets:
        ticketRequest = (PersonMeetingRequest.select().where(PersonMeetingRequest.ticketID=t_id))
        for person in ticketRequest.iterator():
            if person.person not in contacted:
                contacted.append(person.person) 
    #returns a list of people that one person has been incontact with
    return contacted