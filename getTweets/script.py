from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from datetime import datetime
import pytz
import rethinkdb as r

import json

#consumer key, consumer secret, access token, access secret.
ckey=""
csecret=""
atoken=""
asecret=""

r.connect('localhost', 28015).repl()

class listener(StreamListener):

    def on_data(self, data):
        data = json.loads(data)
        time = datetime.strptime(data["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        time = pytz.utc.localize(time)
        data["created_at"] = time
        r.table('tweets_without_location').insert(data).run()
        if data["coordinates"] != None :
            if data["coordinates"]["coordinates"][0] != 2.3508 or data["coordinates"]["coordinates"][1] != 45.8567 :
                data["coordinates"] = r.point(data["coordinates"]["coordinates"][0], data["coordinates"]["coordinates"][1])
                r.table('tweets').insert(data).run()
        return(True)

    def on_error(self, status):
        print(status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
# Paris
twitterStream.filter(locations=[2.235816, 48.812222, 2.428420, 48.904606])

#Tokyo
#twitterStream.filter(locations=[139.014123, 35.489535, 139.912255, 35.884944])

#twitterStream.filter(locations=[-6.38,49.87,1.77,55.81])
