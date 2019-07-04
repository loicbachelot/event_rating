import Stemmer
import json

stemmer = Stemmer.Stemmer('french')

def clean_tweet(full_text, entities):
    word_to_remove = []
    for hashtag in entities["hashtags"]:
        word_to_remove.append("#"+hashtag["text"])
    for url in entities["urls"]:
        word_to_remove.append(url["url"])
    for user_mention in entities["user_mentions"] :
        word_to_remove.append("@"+user_mention["screen_name"]);
    if "media" in entities :
        for media in entities["media"] :
            word_to_remove.append(media["url"])

    for word in word_to_remove :
        full_text = full_text.replace(word, '')

    return full_text

def stemTweet(tweet_cleaned):
    words = tweet_cleaned.split(" ")
    print(words)
    print(stemmer.stemWords(words))
