# -*- coding: utf-8 -*-

import rethinkdb as r

r.connect('vps542128.ovh.net', 28015).repl()

count = r.table('tweets_without_location').count().run()
collection = r.table('tweets_without_location').filter(r.row["lang"] == "fr").run()

compteur_tweets = 0
stop = 0

# for tweet in tweets_json:
for tweet in collection :
    stop = stop + 1
    if tweet["coordinates"] is not None:
        compteur_tweets = compteur_tweets + 1
print("% tweets avec localisation:")
print(compteur_tweets/(stop/100))
print("nombre de tweets utilisables")
print(compteur_tweets)
print(stop)
print(count)
