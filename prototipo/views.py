from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from datetime import datetime, timedelta
import requests
import json

API_CODES = {
        'MCC' : '11567',
        'OCC' : '2280',
        }

# Search Algorithm
def searchPlacement(userTimeSeconds:int, resultTimesSeconds:list) -> int:
    # simple terrible linear search
    i = 0
    startTime = resultTimesSeconds[i]
    while userTimeSeconds > startTime:
        i += 1
        startTime = resultTimesSeconds[i]

    return i

# Remember how to make it faster with multi-threading
def findPlacement(userTimeString, results:list):
    # parse the user time
    format = "%H:%M:%S"

    userTimeDatetime = datetime.strptime(userTimeString, format)
    userTime = timedelta(hours=userTimeDatetime.hour, minutes=userTimeDatetime.minute, seconds=userTimeDatetime.second).seconds

    # parse the result times
    resultTimes = []

    for r in results:
        if r.get("time"):
            unitTime = datetime.strptime(r.get("time"), format)
            resultTimes.append(timedelta(hours=unitTime.hour, minutes=unitTime.minute, seconds=unitTime.second).seconds)

    return searchPlacement(userTime, resultTimes)


# Create your views here.
def index(request):
    r = requests.get("https://api.utmb.world/races/2280.daciautmb-montblancocc.2023/results?lang=en&offset=0&limit=3000") 
    context = {
            "participantes" : json.loads(r.text).get("results")
        } 
    template = loader.get_template("prototipo/index.html") 
    return HttpResponse(template.render(context, request))
    # return JsonResponse(context)

def results(request):
    # start = raceResults.get("results")[0].get("rank")
    getHeaders = request.GET

    r = requests.get(f"https://api.utmb.world/races/{API_CODES.get(request.GET['races'])}.daciautmb-montblancocc.2023/results?lang=en&offset=0&limit=3000") 

    raceResults = json.loads(r.text)


    userName:str = getHeaders.get("name")
    lastName:str = getHeaders.get("surname")
    userTime:str = f"{int(getHeaders.get('hours')) :02d}:{int(getHeaders.get('minutes')) :02d}:{int(getHeaders.get('seconds')) :02d}" 

    userPlacement = findPlacement(userTime, raceResults.get("results"))

    contet = {}
    
    if userPlacement > 10:

        start = userPlacement - 10
        finish = userPlacement + 10

        fresults = []

        for r in raceResults.get("results")[userPlacement:finish] :
            data = {
                    "rank" : r.get("rank") + 1,
                    "fullname" : r.get("fullname"),
                    "time" : r.get("time"),
                    }
            fresults.append(data)

        context = {
            "userRank" : userPlacement + 1,
            "fullname" : {
                "fname" : userName.capitalize(),
                "lname" : lastName.upper(),
            },
            "time" : userTime,
            "sresults" : raceResults.get("results")[start:userPlacement],
            "fresults" : fresults,
        } 
    elif userPlacement <= 10:
        start = 0

        fresults = []

        for r in raceResults.get("results")[userPlacement:19] :
            data = {
                    "rank" : r.get("rank") + 1,
                    "fullname" : r.get("fullname"),
                    "time" : r.get("time"),
                    }
            fresults.append(data)

        context = {
                "userRank" : userPlacement + 1,
                "fullname" : {
                        "fname" : userName.capitalize(),
                        "lname" : lastName.upper(),
                    },
                "time" : userTime,
                "sresults" : raceResults.get("results")[0:userPlacement],
                "fresults" : fresults,
            }

    template = loader.get_template("prototipo/results.html") 
    return HttpResponse(template.render(context,request))
