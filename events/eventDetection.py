# -*- coding: utf-8 -*-
import rethinkdb as r
import Stemmer
from sklearn.externals import joblib

stemmer = Stemmer.Stemmer('french')


def clean_tweet(full_text, entities):
    word_to_remove = []
    for hashtag in entities["hashtags"]:
        word_to_remove.append("#" + hashtag["text"])
    for url in entities["urls"]:
        word_to_remove.append(url["url"])
    for user_mention in entities["user_mentions"]:
        word_to_remove.append("@" + user_mention["screen_name"])
    if "media" in entities:
        for media in entities["media"]:
            word_to_remove.append(media["url"])
    for word in word_to_remove:
        full_text = full_text.replace(word, '')
    return full_text


def stemTweet(tweet_cleaned):
    words = tweet_cleaned.split(" ")
    words = clean_words(words)
    stemmed_words = stemmer.stemWords(words)
    tmp = list(stemmed_words)
    for word in tmp:
        if len(word) < 3:
            stemmed_words.remove(word)
    return stemmed_words


def clean_words(words):
    for i in range(len(words)):
        words[i] = ''.join(l for l in words[i] if l.isalpha())
        words[i] = words[i].lower()
    return words


def get_hashtag_properties(hashtagproperties, tmptweet):
    for hashtag in tmptweet["entities"]["hashtags"]:
        if hashtag["text"] in hashtagproperties["hashtagList"]:
            hashtagproperties["hashtagList"][hashtag["text"]] = hashtagproperties["hashtagList"][hashtag["text"]] + 1
        else:
            hashtagproperties["hashtagList"][hashtag["text"]] = 1

    hashtagproperties["numberOfHashtag"] = len(hashtagproperties["hashtagList"])
    return hashtagproperties


def get_mention_properties(mentionproperties, tmptweet):
    for mention in tmptweet["entities"]["user_mentions"]:
        if mention["screen_name"] in mentionproperties["mentionList"]:
            mentionproperties["mentionList"][mention["screen_name"]] = mentionproperties["mentionList"][
                                                                           mention["screen_name"]] + 1
        else:
            mentionproperties["mentionList"][mention["screen_name"]] = 1

    mentionproperties["numberOfMention"] = len(mentionproperties["mentionList"])
    return mentionproperties


def get_user_properties(userproperties, tmptweet):
    if tmptweet["user"]["id_str"] in userproperties["userList"]:
        userproperties["userList"][tmptweet["user"]["id_str"]] = userproperties["userList"][
                                                                     tmptweet["user"]["id_str"]] + 1
    else:
        userproperties["userList"][tmptweet["user"]["id_str"]] = 1
    userproperties["numberOfUser"] = len(userproperties["userList"])
    return userproperties


def get_scoring(tweetslist):
    number_of_tweets = len(tweetslist)
    words = []
    tweets_stemmed = []
    word_count = []
    total_words = 0
    somme_theme = 0
    for i in range(len(tweetslist)):
        if "extended_tweet" in tweetslist[i].keys():
            cleantmp = clean_tweet(tweetslist[i]["extended_tweet"]["full_text"],
                                   tweetslist[i]["extended_tweet"]["entities"])
        else:
            cleantmp = clean_tweet(tweetslist[i]["text"], tweetslist[i]["entities"])
        stem_wordstmp = stemTweet(cleantmp)
        tweetslist[i]["stemText"] = stem_wordstmp
        tweets_stemmed.append(stem_wordstmp)
        for word in stem_wordstmp:
            if not (word in words):
                words.append(word)
                word_count.append(1)
                total_words = total_words + 1
            else:
                word_count[words.index(word)] = word_count[words.index(word)] + 1
    for i in range(len(words)):
        if (word_count[i] / total_words) == 1:
            somme_theme = somme_theme + 0
        else:
            somme_theme = somme_theme + ((word_count[i] * number_of_tweets) / total_words)

    # the 3 has been choosed based on the paper
    commonthemescore = somme_theme / (3 * total_words)

    # add ranking score in tweet list
    for i in range(len(tweetslist)):
        if len(tweetslist[i]["stemText"]) > 0:
            tweetslist[i]["tweetScore"] = get_tweet_ranking_score(words, word_count, tweetslist[i]["stemText"])

    scoring = {
        "tweetList": tweetslist,
        "commonTheme": commonthemescore,
        "wordsCount": word_count,
        "wordsList": words
    }
    return scoring


def get_tweet_ranking_score(wordslist, wordscount, tweetstemedtext):
    tweetscore = 0
    for tmpword in tweetstemedtext:
        if tmpword in wordslist:
            tweetscore = tweetscore + wordscount[wordslist.index(tmpword)]
    return tweetscore / len(tweetstemedtext)


def verify_event(numberoftweets, commontheme, hashtagproperties, mentionproperties, userproperties):
    if hashtagproperties["numberOfHashtag"] == 0:
        hashtagproperties["mostUsedHashtag"]["frequencyOnHashtags"] = 0
        hashtagproperties["mostUsedHashtag"]["frequencyOnTweets"] = 0

    if mentionproperties["numberOfMention"] == 0:
        mentionproperties["mostUsedMention"]["frequencyOnMentions"] = 0
        mentionproperties["mostUsedMention"]["frequencyOnTweets"] = 0
    input_verif = [[
        commontheme,
        hashtagproperties["numberOfHashtag"],
        hashtagproperties["mostUsedHashtag"]["frequencyOnHashtags"],
        hashtagproperties["mostUsedHashtag"]["frequencyOnTweets"],
        mentionproperties["numberOfMention"],
        mentionproperties["mostUsedMention"]["frequencyOnMentions"],
        mentionproperties["mostUsedMention"]["frequencyOnTweets"],
        numberoftweets,
        userproperties["numberOfUser"],
        userproperties["ratioMaxTweetPerUser"]
    ]]
    clf = joblib.load("AI/mlp_events_1.pkl")
    result = clf.predict(input_verif)
    print(result[0])
    return result[0]


def update_event(event, tmptweet):
    # location
    locationa = (event["coordinates"]["coordinates"][0] * event["numberOfTweets"] +
                 tmptweet["coordinates"]["coordinates"][
                     0]) / (event["numberOfTweets"] + 1)
    locationb = (event["coordinates"]["coordinates"][1] * event["numberOfTweets"] +
                 tmptweet["coordinates"]["coordinates"][
                     1]) / (event["numberOfTweets"] + 1)

    # number of tweets
    numberoftweets = event["numberOfTweets"] + 1

    # start date
    if tmptweet["created_at"] > event["startDate"]:
        startdate = event["startDate"]
    else:
        startdate = tmptweet["created_at"]

    # hashtag list
    hashtagproperties = event["hashtags"]
    hashtagproperties = get_hashtag_properties(hashtagproperties, tmptweet)
    # hastag stats
    if hashtagproperties["numberOfHashtag"] > 0:
        numberofappearenceh = 0
        mostusedhashtag = ""
        for i in hashtagproperties["hashtagList"]:
            if hashtagproperties["hashtagList"][i] > numberofappearenceh:
                mostusedhashtag = i
                numberofappearenceh = hashtagproperties["hashtagList"][i]

        hashtagproperties["mostUsedHashtag"]["text"] = mostusedhashtag
        hashtagproperties["mostUsedHashtag"]["numberOfAppearence"] = numberofappearenceh
        hashtagproperties["mostUsedHashtag"]["frequencyOnTweets"] = numberofappearenceh / numberoftweets
        hashtagproperties["mostUsedHashtag"]["frequencyOnHashtags"] = numberofappearenceh / hashtagproperties[
            "numberOfHashtag"]
        hashtagproperties["avgNumberOfHashtag"] = numberofappearenceh / numberoftweets

    # mentions properties
    mentionproperties = event["mentions"]
    mentionproperties = get_mention_properties(mentionproperties, tmptweet)
    # mentions stats
    if mentionproperties["numberOfMention"] > 0:
        numberofappearencem = 0
        mostusedmention = ""
        for i in mentionproperties["mentionList"]:
            if mentionproperties["mentionList"][i] > numberofappearencem:
                mostusedmention = i
                numberofappearencem = mentionproperties["mentionList"][i]

        mentionproperties["mostUsedMention"]["text"] = mostusedmention
        mentionproperties["mostUsedMention"]["numberOfAppearence"] = numberofappearencem
        mentionproperties["mostUsedMention"]["frequencyOnTweets"] = numberofappearencem / numberoftweets
        mentionproperties["mostUsedMention"]["frequencyOnMentions"] = numberofappearencem / mentionproperties[
            "numberOfMention"]
        mentionproperties["avgNumberOfMention"] = numberofappearencem / numberoftweets

    # users properties
    userproperties = event["users"]
    userproperties = get_user_properties(userproperties, tmptweet)
    maxtweetperuser = max(userproperties["userList"].values())
    userproperties["tweetPerUserAvg"] = numberoftweets / userproperties["numberOfUser"]
    userproperties["ratioMaxTweetPerUser"] = maxtweetperuser / numberoftweets
    userproperties["maxTweetPerUser"] = maxtweetperuser

    # tweet list
    tweetslist = event["tweetList"]
    tweetslist.append(tmptweet)

    # scoring
    scoring = get_scoring(tweetslist)
    commontheme = scoring["commonTheme"]
    tweetslist = scoring["tweetList"]

    # insertion in the DB
    r.table('events').insert([{
        "numberOfTweets": numberoftweets,
        "commontheme": commontheme,
        "coordinates": r.point(locationa, locationb),
        "startDate": startdate,
        "hashtags": hashtagproperties,
        "mentions": mentionproperties,
        "users": userproperties,
        "tweetList": tweetslist,
        "wordsCount": scoring["wordsCount"],
        "wordsList": scoring["wordsList"]
    }]).run()


def tweets_list_to_event(tweetslist):
    # common theme
    scoring = get_scoring(tweetslist)
    commontheme = scoring["commonTheme"]
    tweetslist = scoring["tweetList"]
    if commontheme > 0.18:
        locationa = 0
        locationb = 0
        startdate = 0
        hashtagproperties = {
            "hashtagList": {},
            "mostUsedHashtag": {}
        }
        mentionproperties = {
            "mentionList": {},
            "mostUsedMention": {}
        }
        userproperties = {
            "userList": {},
        }
        numberoftweets = len(tweetslist)
        for tmptweet in tweetslist:

            # get event center location
            locationa = locationa + tmptweet["coordinates"]["coordinates"][0]
            locationb = locationb + tmptweet["coordinates"]["coordinates"][1]

            # get event start date
            if startdate == 0 or startdate > tmptweet["created_at"]:
                startdate = tmptweet["created_at"]

            # hashtag, mention and user basic properties
            hashtagproperties = get_hashtag_properties(hashtagproperties, tmptweet)
            mentionproperties = get_mention_properties(mentionproperties, tmptweet)
            userproperties = get_user_properties(userproperties, tmptweet)

        if userproperties["numberOfUser"] > 1:

            # hastag stats
            if hashtagproperties["numberOfHashtag"] > 0:
                numberofappearenceh = 0
                mostusedhashtag = ""
                for i in hashtagproperties["hashtagList"]:
                    if hashtagproperties["hashtagList"][i] > numberofappearenceh:
                        mostusedhashtag = i
                        numberofappearenceh = hashtagproperties["hashtagList"][i]

                hashtagproperties["mostUsedHashtag"]["text"] = mostusedhashtag
                hashtagproperties["mostUsedHashtag"]["numberOfAppearence"] = numberofappearenceh
                hashtagproperties["mostUsedHashtag"]["frequencyOnTweets"] = numberofappearenceh / numberoftweets
                hashtagproperties["mostUsedHashtag"]["frequencyOnHashtags"] = numberofappearenceh / hashtagproperties[
                    "numberOfHashtag"]
                hashtagproperties["avgNumberOfHashtag"] = numberofappearenceh / numberoftweets

            # mentions stats
            if mentionproperties["numberOfMention"] > 0:
                numberofappearencem = 0
                mostusedmention = ""
                for i in mentionproperties["mentionList"]:
                    if mentionproperties["mentionList"][i] > numberofappearencem:
                        mostusedmention = i
                        numberofappearencem = mentionproperties["mentionList"][i]

                mentionproperties["mostUsedMention"]["text"] = mostusedmention
                mentionproperties["mostUsedMention"]["numberOfAppearence"] = numberofappearencem
                mentionproperties["mostUsedMention"]["frequencyOnTweets"] = numberofappearencem / numberoftweets
                mentionproperties["mostUsedMention"]["frequencyOnMentions"] = numberofappearencem / mentionproperties[
                    "numberOfMention"]
                mentionproperties["avgNumberOfMention"] = numberofappearencem / numberoftweets

            # users stats
            maxtweetperuser = max(userproperties["userList"].values())
            userproperties["tweetPerUserAvg"] = numberoftweets / userproperties["numberOfUser"]
            userproperties["ratioMaxTweetPerUser"] = maxtweetperuser / numberoftweets
            userproperties["maxTweetPerUser"] = maxtweetperuser

            if userproperties["ratioMaxTweetPerUser"] < 0.7:
                if verify_event(numberoftweets, commontheme, hashtagproperties, mentionproperties, userproperties) == 1:
                    # insertion in the DB
                    r.table('events').insert([{
                        "numberOfTweets": numberoftweets,
                        "commontheme": commontheme,
                        "coordinates": r.point(locationa / len(listTweets), locationb / len(listTweets)),
                        "startDate": startdate,
                        "hashtags": hashtagproperties,
                        "mentions": mentionproperties,
                        "users": userproperties,
                        "tweetList": tweetslist,
                        "wordsCount": scoring["wordsCount"],
                        "wordsList": scoring["wordsList"]
                    }]).run()
                    return True
    else:
        return False


r.connect('vps542128.ovh.net', 28015).repl()
# reinitialisation for tests
r.table('waitingTweets').delete().run()
r.table('events').delete().run()

# to change by the live stream of rated tweets
collection = r.table('tweets').filter(r.row["lang"] == "fr").order_by(r.row['created_at']).run()
print(len(collection))
compteur = 0

# for tweet in tweets_json:
for tweet in collection:
    if compteur % 100 == 0:
        print(compteur)
    compteur = compteur + 1
    circle1 = r.circle([tweet["coordinates"]["coordinates"][0], tweet["coordinates"]["coordinates"][1]], 1000, unit='m')
    events = r.table('events').get_intersecting(circle1, index='coordinates').filter(
         r.row['startDate'].to_epoch_time() > (tweet["created_at"] - r.epoch_time(172800))).run()
    listEvents = list(events)
    if len(listEvents) > 0:
        for i in range(len(listEvents)):
            if "extended_tweet" in tweet.keys():
                clean = clean_tweet(tweet["extended_tweet"]["full_text"], tweet["extended_tweet"]["entities"])
            else:
                clean = clean_tweet(tweet["text"], tweet["entities"])
            stem_words = stemTweet(clean)
            if len(stem_words) > 0:
                if get_tweet_ranking_score(listEvents[0]["wordsList"], listEvents[0]["wordsCount"], stem_words) > 2:
                    update_event(listEvents[0], tweet)
                    # delete the old event
                    r.table("events2").filter({"id": listEvents[0]["id"]}).delete().run()
                    break
            else:
                break
    else:
        collection2 = r.table('waitingTweets').get_intersecting(circle1, index='coordinates').filter(
         r.row["created_at"].to_epoch_time() > (tweet["created_at"] - r.epoch_time(172800))).order_by("created_at").run()
        listTweets = list(collection2)
        if len(listTweets) > 5:
            listTweets.append(tweet)
            # create new event with the tweet list
            if tweets_list_to_event(listTweets):
                # delete the
                for delTweet in listTweets:
                    r.table("waitingTweets2").filter({"id": delTweet["id"]}).delete().run()
            else:
                r.table('waitingTweets').insert(tweet).run()
        else:
            r.table('waitingTweets').insert(tweet).run()
