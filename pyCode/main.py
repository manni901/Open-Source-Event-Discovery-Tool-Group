import imp

def readDataFromFile(filename):
    with open(filename) as f :
        return f.readlines()


def getCategories(likes):
    categories = readDataFromFile("outputFolder/categories.data")
    filter_categories = []
    for like in likes :
        words = like.split(" ")
        filter_categories.extend([word for word in words if word.lower() in categories])
    filter_categories = list(set(filter_categories ))
    return filter_categories

def getLikes():
    #dummy code
    return readDataFromFile("input/likes.data")

def getEvents(categories):
    events = readDataFromFile("outputFolder/eventbrite.data")
    finalEvents = []
    for event in events :
        finalEvents.extend([event for categoryWord in event['category'].split(" ") if categoryWord in categories])
    finalEvents = list(set(finalEvents))
    return finalEvents


if __name__ == "__main__":
    # eb = imp.load_module("getEventBriteData")
    likes = getLikes()
    categories = getCategories(likes)
    events = getEvents(categories)