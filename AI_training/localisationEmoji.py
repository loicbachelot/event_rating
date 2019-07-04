# -*- coding: utf-8 -*-
import json
import re
import pymongo

from pymongo import MongoClient

test_size = 78743.0
client = MongoClient('localhost', 27017)
db = client['tweets']
collection = db.tweets

pos_regex = re.compile(
    u"[\U0001F600|\U0001F601|\U0001F602|\U0001F923|\U0001F603|\U0001F604|\U0001F605|\U0001F606|\U0001F609|\U0001F60A|\U0001F60B|\U0001F60E|\U0001F60D|\U0001F618|\U0001F970|\U0001F617|\U0001F619|\U0001F61A|\U0000263A|\U0001F642|\U0001F917|\U0001F929]")
neg_regex = re.compile(
    u"[\U00002639|\U0001F641|\U0001F616|\U0001F61E|\U0001F61F|\U0001F624|\U0001F622|\U0001F62D|\U0001F626|\U0001F627|\U0001F628|\U0001F629|\U0001F92F|\U0001F62C|\U0001F630|\U0001F631|\U0001F975|\U0001F976|\U0001F633|\U0001F92A|\U0001F635|\U0001F621|\U0001F620|\U0001F92C]")
neut_regex = re.compile(
    u"[\U0001F914|\U0001F928|\U0001F610|\U0001F611|\U0001F636|\U0001F644|\U0001F60F|\U0001F623|\U0001F625|\U0001F62E|\U0001F910|\U0001F62F|\U0001F62A|\U0001F62B|\U0001F634|\U0001F60C|\U0001F61B|\U0001F61C|\U0001F61D|\U0001F924|\U0001F612|\U0001F613|\U0001F614|\U0001F615|\U0001F643|\U0001F911|\U0001F632]")
compteur_tweets = 0
stop = 0

# for tweet in tweets_json:
for tweet in collection.find():
    stop = stop + 1
    if stop > test_size:
        break
    if tweet["coordinates"] is not None:
        pos = pos_regex.findall(tweet["text"])
        neg = neg_regex.findall(tweet["text"])
        neut = neut_regex.findall(tweet["text"])
        if pos or neg or neut:
            compteur_tweets = compteur_tweets + 1
print("% de tweets avec emoji et localisation")
print(compteur_tweets / (test_size / 100))
print("nombre de tweets utilisables")
print(compteur_tweets)
