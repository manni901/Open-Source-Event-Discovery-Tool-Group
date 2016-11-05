import requests, json
accessToken = "K7XY42IJBLIZRO5Z6D5M"
def getResponse(request):
    return requests.get(
        request,
        headers={
            "Authorization": "Bearer " + accessToken,
        },
        verify=True,  # Verify SSL certificate
    )

# get eventid to name mapping
def getEventIdMap():
    request = "https://www.eventbriteapi.com/v3/categories/?page_size=100000"
    response = getResponse(request)
    if response.status_code == 200 :
        responseData = response.json()
        resultMap = {}
        for category in responseData['categories']:
            resultMap.__setitem__(category['id'],category['name'])
        return resultMap
    else :
        print "Verification failed..something wrong with url"
    return None

def getDataForThisPage(pageNum, requesturl):
    requesturl += "&page=" + str(pageNum)
    # print requesturl
    response = getResponse(requesturl)
    if response.status_code == 200 :
        return response.json()['events']
    else :
        print "Verification failed..something wrong with url"
    return None


def generateData():
    requesturl = "https://www.eventbriteapi.com/v3/events/search/?start_date.keyword=tomorrow"
    response = getResponse(requesturl)
    if response.status_code == 200 :
        page_count = response.json()['pagination']['page_count']
        result = []
        for page in xrange(1) :#page_count
            result.extend(getDataForThisPage(page, requesturl))

        return result
    else :
        print "Verification failed..something wrong with url"
    return None

def writeToFile(filename, data):
    with open(filename, 'w+') as f:
        for event in data:
            if event is not None:
                f.write(str(event).replace("u'", "\"").replace("\'","\""))
                f.write("\n")

def filterEvents(events, categories):
    new_events = []
    for event in events :
        # print str((event['description']['text']).encode('utf-8')).replace("\r","").replace("\n","").replace("\'", "")
        start = flattenObj("", convertToDict(event['start']))
        end = flattenObj("", convertToDict(event['end']))
        d = {"name":str(event['name']['text'].encode('utf-8')).replace("\r","").replace("\n",""),
                           "description": str(event['description']['text'].encode('utf-8')).replace("\r","").replace("\n","").replace("\"", "").replace("\xc2","").replace("\xa0","").replace("\x7f",""),
                           "id":str(event['id']),
                           "url":str(event['url']),
                           "category_id":str(event['category_id']),
                           "venue_id":str(event['venue_id']),
                           "category":str(categories.get(event['category_id']))}
        d.update(start)
        d.update(end)
        new_events.append(d)
    return new_events

def convertToDict(data):
    data = dict(data)
    new_dict = {}
    for key in data.keys():
        typeVal = type(data.get(key))
        val = None

        if typeVal is dict:
            val = str(convertToDict(data.get(key)))
        else:
            if typeVal is unicode:
                val = str(data.get(key).encode('utf-8')).replace("\r","").replace("\n","")
            elif typeVal is list :
                val = [str(_.encode('utf-8')) for _ in data.get(key)]
        # print val, key, typeVal
        if val : new_dict.__setitem__(str(key), val)
    return new_dict

def getVenueObj(venueID):
    if not venueID :
        print "Verification failed..something wrong with venueID url" + venueID
        return None
    response = getResponse("https://www.eventbriteapi.com/v3/venues/"+venueID)
    if response.status_code == 200 :
        return convertToDict(response.json())
    else :
        print "Verification failed..something wrong with venueID url"+venueID
    return None

def flattenObj(name, di):
    new_dict = {}
    for key in di.keys():
        # if type(di.get(key)) is dict :
        if name+key == "venue.address":
            try :

                # print type(di.get(key)), di.get(key).replace("\'", "\""), json.loads(di.get(key).replace("'", "\""))
                new_dict.update(flattenObj(name+key+".", json.loads(di.get(key).replace("'", "\""))))
            except ValueError:
                new_dict.__setitem__(name + key +".", "None")
        else :
            try :
                new_dict.__setitem__(name+key, (str(di.get(key)).encode('utf-8')).replace("\r","").replace("\n","").replace("\'", ""))
            except UnicodeDecodeError :
                new_dict.__setitem__(name + key + ".", "None")
    return new_dict

def getVenues(events):
    venueIds = []
    venueIdMap = {}
    for event in events :
        if event.get("venue_id") : venueIds.append(event.get("venue_id"))
    # print len(venueIds)
    venueIds = list(set(venueIds))
    # print len(venueIds)
    for venueId in venueIds:
        if getVenueObj(venueId) :
            venueIdMap.__setitem__(venueId, getVenueObj(venueId))
    return venueIdMap

def updateEvents(events, venues):
    for event in events :
        venueId = event.__getitem__("venue_id")
        if venueId in venues.keys():
            if venues.get(venueId):
                event.update(flattenObj("venue.", venues.get(venueId)))
        else :
            print 'venue information not found for this id', venueId
    return events

if __name__ == "__main__":
    categories = getEventIdMap()
    if categories : writeToFile('../outputFolder/categories.data', [categories.get(key) for key in categories])
    events = generateData()
    print 'categories generated\n fetching events.. Hold on...'
    if events : events = filterEvents(events, categories)
    venues = getVenues(events)
    print 'Updating Events..\n'
    events = updateEvents(events, venues)
    print 'writing events to datastore..\n'
    if events : writeToFile('../outputFolder/eventbrite.data', events)