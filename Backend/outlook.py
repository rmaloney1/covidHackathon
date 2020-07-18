
import random
issueList=["PAJ-1","PAJ-2","PAJ-3","PAJ-4","PAJ-5","PAJ-6","PAJ-7","PAJ-8","PAJ-9","PAJ-10","PAJ-11","PAJ-12","PAJ-13","PAJ-14","PAJ-15","PAJ-16","PAJ-17","PAJ-18","PAJ-19","PAJ-20","PAJ-21","PAJ-22","PAJ-23","PAJ-24","PAJ-25","PAJ-26","PAJ-27","PAJ-28","PAJ-29","PAJ-30","PAJ-31","PAJ-32","PAJ-33","PAJ-34","PAJ-35","PAJ-36","PAJ-37","PAJ-38","PAJ-39","PAJ-40","PAJ-41","PAJ-42","PAJ-43","PAJ-44","PAJ-45","PAJ-46","PAJ-47","PAJ-48","PAJ-49","PAJ-50","PAJ-51","PAJ-52","PAJ-53","PAJ-54","PAJ-55","PAJ-56","PAJ-57","PAJ-58","PAJ-59","PAJ-60","PAJ-61","PAJ-62","PAJ-63","PAJ-64","PAJ-65","PAJ-66"]
personList=["Bessie Oakley", "Aaron Bryant", "Lester Hayward", "Asim Hobbs", "Harvie Betts", "Polly Findlay", "Philippa Rocha", "Rajveer Wright", "Zain Li", "Isobel Landry", "Myrtle Schroeder", "Gracie Byrd", "Ariana Bevan", "Sameeha Bowers", "Luc Fletcher", "Fred Gallagher", "Sneha Marsh", "Isha Wilson", "Cassie Mccartney", "Bea Key", "Nela Hoffman", "Ihsan Vu", "Ivy Ayala", "Aasiyah Mata", "Esmai Clark", "Isla Good", "Arman Yoder", "Meerab Hills", "Brandi Davey", "Kaitlyn Pineda"]

for i in issueList:
    randomNumber = random.randint(2,7)
    chois = random.choices(personList, k=randomNumber)
    for j in range(randomNumber):
        print(f"PersonTickets.assignTickets(\"{i}\", \"{chois[j]}\")")

{
  "Start": "2015-07-17T00:00:00-04:00",
  "End": "2015-07-18T00:00:00-04:00",
  "StartTimeZone": "Eastern Standard Time",
  "EndTimeZone": "Eastern Standard Time",
  "IsAllDay": "true",
  "ShowAs": "Free",
  "Body": {
    "ContentType": "Text",
    "Content": "Test"
  },
  "Subject": "TZ AllDay Test"
}