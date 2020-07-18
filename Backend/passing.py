from models import CompanyBuildings, Person, Project, JiraTicket, PersonTickets, MeetingRequest

def ticketURL(ticketID):
    return f"https://covidspace.atlassian.net/browse/{ticketID}"