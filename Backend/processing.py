from models import (
    CompanyBuildings,
    Person,
    Project,
    JiraTicket,
    PersonTickets,
    MeetingRequest,
    model_to_dict,
)
import datetime as dt
import math

# if low priority, the number of days before due date an item can be pushed back by
SECRUTIY_BUFFER = 3

# numsafedays
UNSAFEDAYS = 14


def createSortedTaskList(requestList):
    requestList = []
    scoreList = []
    personCount = []

    for request in activeList.iterator():
        # score is set by multiplying a time score (relative to end date closeness) to (the sum of its partcipants active task count)
        score = math.exp(-0.231049 * request.beforeDate)
        personScore = 0
        personCounter = 0
        people = PersonTickets.select().where(
            PersonTickets.ticketID == request.ticketID
        )
        for person in people.iterator():
            personScore += person.activeTicketCount
            personCounter += 1

        score *= personScore

        requestList.append(request)
        scoreList.append(score)
        personCount.append(personCounter)

    sortedRequests = [x for _, x in sorted(zip(scoreList, requestList))]
    sortedCount = [x for _, x in sorted(zip(scoreList, personCount))]

    return {"requests": sortedRequests, "personCount": sortedCount}


# TODO: improve this so there are more people doing the same task in a day
def makeAllocations():
    requestList = (
        MeetingRequest.select()
        .where(MeetingRequest.requestFilled == False)
        .order_by(MeetingRequest.beforeDate)
    )
    for request in requestList.iterator():
        if (
            request.beforeDate - dt.date.today()
        ).days <= SECRUTIY_BUFFER and not request.priority:
            request.elevatePriority()

    # get a list of active tasks with high priority (after start date), sorted refering to end date
    activeList = MeetingRequest.select().where(
        MeetingRequest.priority
        == True & MeetingRequest.requestFilled
        == False & MeetingRequest.beforeDate
        >= dt.date.today()
    )

    # for each task calculate a score
    sortedList = createSortedTaskList(activeList)

    # fill in tasks refering to priority up to the person count maximum
    capacity = CompanyBuildings.get().personCapacity
    currentAllocatedPersonCount = 0
    allocationDate = dt.date.today + dt.timedelta(days=1)
    # if weekend tomorrow
    if allocationDate.weekday() >= 5:
        allocationDate += dt.timedelta(days=2)

    # if there are gaps that are too small for important tasks, fill down particpant count
    i = 0
    while currentAllocatedPersonCount <= capacity or i < len(sortedList["requests"]):
        if (capacity - currentAllocatedPersonCount) >= sortedList["personCount"][i]:
            sortedList["requests"][i].allocatedDate = allocationDate
            currentAllocatedPersonCount += sortedList["personCount"][i]

        i += 1

    # if all high priority filled and still space, fill through low priority using same method
    lowPriorityActiveList = MeetingRequest.select().where(
        MeetingRequest.priority
        == False & MeetingRequest.requestFilled
        == False & MeetingRequest.beforeDate
        >= dt.date.today()
    )

    # for each task calculate a score
    lowPrioritySortedList = createSortedTaskList(lowPriorityActiveList)
    i = 0
    while currentAllocatedPersonCount <= capacity or i < len(
        lowPriorityActiveList["requests"]
    ):
        if (capacity - currentAllocatedPersonCount) >= lowPriorityActiveList[
            "personCount"
        ][i]:
            lowPriorityActiveList["requests"][i].allocatedDate = allocationDate
            currentAllocatedPersonCount += lowPriorityActiveList["personCount"][i]

        i += 1


# contact tracing
# takes a personID
# ID is the name
def contactTrace(p_id):
    tickets = []
    contacted = []

    # join personTickets to Requests as PersonTicketRequests
    PersonMeetingRequest = (
        MeetingRequest.select().join(PersonTickets).where(PersonTickets.person == p_id)
    )
    # for p_id in personTicketRequests
    for pmr in PersonMeetingRequest.iterator():
        # if dateallocated in last 2 weeks
        if pmr.requestFilled:
            if (dt.date.today() - pmr.dateAllocated).days < UNSAFEDAYS:
                # add to list of tickets
                tickets.append(pmr.ticketID)

    for t_id in tickets:
        ticketRequest = PersonMeetingRequest.select().where(
            PersonMeetingRequest.ticketID == t_id
        )
        for person in ticketRequest.iterator():
            if person.person not in contacted:
                contacted.append(person.person)
    # returns a list of people that one person has been incontact with
    return contacted
