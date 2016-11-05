
# Please create an access token in eventbrite application before accessing our application
1. Run getEventBriteData.py :: outputFolder/[catogeries, eventbrite].data
	Uses scrapy api to fetch data from websites (pluggable architecture).. and write data to nfs (can be modified to mongodb)
2. Run content-based-recommender.py ::
       outputFolder/[output.data] --> list of events that should be notified for this user.
       Uses Content based filtering for identificaiton likely events based on the facebook likes data for a specific user. This can be extended to multiple attributes based on the use case.