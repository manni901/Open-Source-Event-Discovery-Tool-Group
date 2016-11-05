import pandas as pd
import time, json, sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def info(msg):
    print msg


class ContentEngine(object):

    SIMKEY = 'p:smlr:%s'


    def getPDDs(self, filename):
        with open(filename) as f :
            idx = 0
            for line in f.readlines():
                # line = unicodedata.normalize('NFKD', line).encode('ascii', 'ignore')
                try :
                    # print line
                    event = json.loads(line)
                    if 'venue.latitude' in event and 'venue.longitude' in event :
                        #     item.category,
                        #     item.name,
                        #     item.venue.name,
                        #     item.venue.address.localized_address_display,
                        #     item.start.utc,
                        # item.url,
                        # item.venue.latitude,
                        # item.venue.longitude
                        # print event['id'], idx
                        self.eventDict.__setitem__(event['id'], idx)
                        self.data.append((event['id'], event['name'], event['venue.latitude'], event['venue.longitude'], event['description']))#this shoudlbe changed to description
                        idx+= 1
                        # data.append((event['id'],
                        #              event['description']))  # this shoudlbe changed to description
                except ValueError :
                    continue
                    #ignoring for now
        return pd.DataFrame(self.data, columns=["id", "name", "venue.latitude", "venue.longitude", "description"])
        # return pd.DataFrame(data, columns=["id",  "description"])

    def getPDDLikes(self, filename):
        data = []
        idx = -sys.maxint - 1
        with open(filename) as f:
            for line in f.readlines():

                # line = unicodedata.normalize('NFKD', line).encode('ascii', 'ignore')
                try :
                    # print line
                    like = json.loads(line)
                    self.likeDict.__setitem__( like['name'], idx)
                    if like and like != "": data.append((idx, like['name']))#this shoudlbe changed to description
                    idx += 1
                except ValueError :
                    continue
                    #ignoring for now
        return pd.DataFrame(data, columns=["id", "description"])

    def __init__(self):
        # self._r = redis.StrictRedis.from_url(current_app.config['REDIS_URL'])
        self._r = {}
        self.likeDict = {}
        self.eventDict = {}
        self.data = []

    def train(self):
        start = time.time()
        # ds = pd.read_csv(data_source)
        # ds = getPDDs("getEventBriteData/eventbrite.data")
        ds = self.getPDDs("outputFolder/eventbrite.data")
        likes = self.getPDDLikes("input/likes.data")
        # print likes
        # print ds
        info("Training data ingested in %s seconds." % (time.time() - start))

        # Flush the stale training data from redis
        # self._r.flushdb()

        # print ds
        start = time.time()
        self._train(ds, likes)
        info("Engine trained in %s seconds." % (time.time() - start))

    def _train(self, ds, likes):
        data = pd.concat([ds, likes], keys = ['id','description'])
        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
        tfidf_matrix = tf.fit_transform(data['description'])
        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
        # print cosine_similarities.shape, data.shape
        for idx, row in data.iterrows():
            idx = idx[1]
            similar_indices = cosine_similarities[idx].argsort()[:-100:-1]
            similar_items = [(cosine_similarities[idx][i], str(data['id'][i])) for i in similar_indices]
            # print '\n---->', similar_indices
            # print '\n', similar_items
            similar_items = sorted(similar_items, key=lambda x: x[0], reverse=True)
            similar_items = [item for item in similar_items if item[0] > 0]
            self._r.__setitem__(self.SIMKEY % row['id'], similar_items)

    def predict(self, item_id, num):
        return [event for event in self._r.get(self.SIMKEY % item_id) if event >0 ]

def construct_event(t):
    return {"id":  t[0],
            "name" : t[1],
            "venue.latitude" : t[2],
            "venue.longitude" : t[3],
            "description" : t[4]}

def getUnique(dicts):
    new_dict = {}
    for item in dicts:
        if item['id'] not in new_dict.keys() :
            new_dict.__setitem__(item['id'], item)
    return new_dict.values()

if __name__ == "__main__":
    content_engine = ContentEngine()
    content_engine.train()
    likes = content_engine.likeDict
    # print likes.values()
    finalEvents = []
    for like in likes:
        filteredEvents = content_engine.predict(likes.get(like), 10)
        # print content_engine.data
        eventsForthisLike = []
        for item in filteredEvents:
            if content_engine.eventDict.get(item[1]):
                eventsForthisLike.append(construct_event(content_engine.data[content_engine.eventDict.get(item[1])]))
        # if len(eventsForthisLike) :  print like, "--->>",eventsForthisLike
        finalEvents.extend(eventsForthisLike)
    with open("outputFolder/output.data", 'wb') as f :
        events = getUnique(finalEvents)
        for event in events :
            f.write(str(event))
            f.write("\n")
    print 'output written in outputFolder/output.data\n'
