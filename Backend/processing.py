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


def createSortedTaskList(priorityList=True):
    activeList = MeetingRequest.select().where(
        MeetingRequest.priority == priorityList & MeetingRequest.requestFilled == False
    )
    requestList = []
    scoreList = []
    personCount = []

    print(activeList.count())

    for request in activeList.iterator():

        print("afterDate:")
        print(request.afterDate)
        print("today:")
        print(dt.date.today())

        if request.afterDate_date < dt.date.today():
            continue
        print("in request")
        # score is set by multiplying a time score (relative to end date closeness) to (the sum of its partcipants active task count)
        score = math.exp(-0.231049 * (request.beforeDate_date - dt.date.today()).days)
        personScore = 0
        personCounter = 0
        people = PersonTickets.select().where(
            PersonTickets.ticketID == request.ticketID
        )
        for person in people.iterator():
            personScore += (
                MeetingRequest.select()
                .join(
                    PersonTickets,
                    on=(PersonTickets.ticketID == MeetingRequest.ticketID),
                )
                .where(
                    MeetingRequest.requestFilled
                    == False & PersonTickets.person
                    == person.person
                )
                .count()
            )
            personCounter += 1

        score *= personScore

        requestList.append(request)
        scoreList.append(score)
        personCount.append(personCounter)

    combinedList = [
        (requestList[i], scoreList[i], personCount[i]) for i in range(len(requestList))
    ]
    combinedList.sort(key=(lambda x: x[1]))
    # sortedRequests = [x for _, x in sorted(zip(scoreList, requestList))]
    # sortedCount = [x for _, x in sorted(zip(scoreList, personCount))]

    return {
        "requests": [i[0] for i in combinedList],
        "personCount": [i[2] for i in combinedList],
    }


# TODO: improve this so there are more people doing the same task in a day
def makeAllocations():
    print("--------- make is called")
    # for each task calculate a score
    sortedList = createSortedTaskList(True)

    # fill in tasks refering to priority up to the person count maximum
    capacity = CompanyBuildings.get().personCapacity
    currentAllocatedPersonCount = 0
    allocationDate = dt.date.today() + dt.timedelta(days=1)
    # if weekend tomorrow
    if allocationDate.weekday() >= 5:
        allocationDate += dt.timedelta(days=2)

    # if there are gaps that are too small for important tasks, fill down particpant count
    i = 0
    while currentAllocatedPersonCount <= capacity and i < len(sortedList["requests"]):
        if (capacity - currentAllocatedPersonCount) >= sortedList["personCount"][i]:
            sortedList["requests"][i].allocateDate(allocationDate)
            currentAllocatedPersonCount += sortedList["personCount"][i]

        i += 1

    # for each task calculate a score
    lowPrioritySortedList = createSortedTaskList(False)
    i = 0
    while currentAllocatedPersonCount <= capacity and i < len(
        lowPrioritySortedList["requests"]
    ):
        if (capacity - currentAllocatedPersonCount) >= lowPrioritySortedList[
            "personCount"
        ][i]:
            lowPrioritySortedList["requests"][i].allocateDate(allocationDate)
            currentAllocatedPersonCount += lowPrioritySortedList["personCount"][i]

        i += 1

    print("allocate finish ---------------")


# contact tracing
# takes a personID
# ID is the name
def contactTrace(p_id):
    tickets = []
    contacted = []

    # join personTickets to Requests as PersonTicketRequests
    PersonMeetingRequest = (
        MeetingRequest.select()
        .join(PersonTickets, on=(MeetingRequest.ticketID == PersonTickets.ticketID))
        .where(PersonTickets.person == p_id)
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
