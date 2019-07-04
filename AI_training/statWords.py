import rethinkdb as r
import json
import Stemmer
import numpy as np
import re
import random
import csv
import re
import string

EMOJI_CSV = 'emoji_data.csv'

CSV = 'AFINN-fr-165.csv'

LOG = False

pos_regex = re.compile(
    u"[\U0001F600|\U0001F601|\U0001F602|\U0001F923|\U0001F603|\U0001F604|\U0001F605|\U0001F606|\U0001F609|\U0001F60A|\U0001F60B|\U0001F60E|\U0001F60D|\U0001F618|\U0001F970|\U0001F617|\U0001F619|\U0001F61A|\U0000263A|\U0001F642|\U0001F917|\U0001F929]")
neg_regex = re.compile(
    u"[\U00002639|\U0001F641|\U0001F616|\U0001F61E|\U0001F61F|\U0001F624|\U0001F622|\U0001F62D|\U0001F626|\U0001F627|\U0001F628|\U0001F629|\U0001F92F|\U0001F62C|\U0001F630|\U0001F631|\U0001F975|\U0001F976|\U0001F633|\U0001F92A|\U0001F635|\U0001F621|\U0001F620|\U0001F92C]")
neut_regex = re.compile(
    u"[\U0001F914|\U0001F928|\U0001F610|\U0001F611|\U0001F636|\U0001F644|\U0001F60F|\U0001F623|\U0001F625|\U0001F62E|\U0001F910|\U0001F62F|\U0001F62A|\U0001F62B|\U0001F634|\U0001F60C|\U0001F61B|\U0001F61C|\U0001F61D|\U0001F924|\U0001F612|\U0001F613|\U0001F614|\U0001F615|\U0001F643|\U0001F911|\U0001F632]")

stemmer = Stemmer.Stemmer('french')


def average(list):  # average of all the scores in the list
    output = 0
    for value in list:
        output += float(value)
    output /= len(list)
    return output


def furthest(list):  # output the furthest value from 0
    output = []
    for value in list:
        output.append(float(value))
    return max(output, key=abs)


def save_word(word, score):  # save a word and it's score n the csv
    with open('AFINN-fr-165.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([word, score])


def upgrade_database(unused, used):  # upgrade the csv with new scores and words
    for word in unused:  # all new words in the list
        save_word(word, 0.01)
    for word in used:  # all the used word inthe list
        update_word(word, 0.01)


def update_word(word, score_update):
    r = csv.reader(open('AFINN-fr-165.csv'), delimiter=',')  # csv file
    lines = [l for l in r]  # get the file contents

    for line in lines:  # edit the score of the used word
        if line[0] == word:
            line[1] = score_update + float(line[1])

    # create a new file to save the contents
    writer = csv.writer(open('AFINN-fr-165.csv', 'w'), delimiter=',')

    # write/save
    writer.writerows(lines)


def check_word(word_list):
    output = []  # all scores of the found words
    used = []  # all words with a score
    with open('AFINN-fr-165.csv', newline='') as fp:
        csvreader = csv.reader(fp, delimiter=",")  # read the scores in the list

        next(csvreader, None)  # skip the headers
        for row in csvreader:
            for word in word_list:
                result = re.findall('^\\b' + word + '\\b', row[0],
                                    flags=re.IGNORECASE)  # use the regex to find the words
                if result:  # if a result is found add the score to the output
                    output.append(row[1])
                    used.append(word)
    unused = word_list  # list of non used words
    for word in used:
        for x in range(word_list.count(word)):
            unused.remove(word)
    return output, used, unused


def check_emoji(word_list):
    output = []  # all scores of the found words
    used = []  # all words with a score

    with open('%s' % EMOJI_CSV, newline='') as fp:
        csvreader = csv.reader(fp, delimiter=",")  # read the scores in the list
        next(csvreader, None)  # skip the headers

        for row in csvreader:
            for word in word_list:
                result = row[0] in word
                if result:  # if a result is found add the score to the output
                    output.append(row[11])
                    used.append(word)
    unused = word_list  # list of non used words

    for word in used:
        for x in range(word_list.count(word)):
            unused.remove(word)
    return output, used, unused


def list_values():  # list all the score in the current database
    with open(CSV, newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in data:
            print(', '.join(row))


def data_sanitization(file):  # data from text to a tab of words
    file = re.sub(r'@([A-Za-z0-9_]+)', "", file)  # remove twitter mentions
    file = re.sub('[%s]' % re.escape(string.punctuation), '', file)  # remove ponctuations
    file = re.sub(r"http\S+", "", file)  # remove urls
    file = file.split(' ')
    for x in range(file.count('')):  # remove empty fiels
        file.remove('')
    return file


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


def get_label(full_text, computation=0, feature=0):  # get the score of a tweet
    ## computation 0 average
    #              1 distance
    ## feature 0 words
    #          1 emojis
    if feature == 1:
        output, used, unused, = check_emoji(data_sanitization(full_text))
    else:
        output, used, unused, = check_word(data_sanitization(full_text))
    if output:
        if computation == 0:
            return average(output)
        else:
            return furthest(output)

    else:
        return -2  # no score found


def clean_words(words):
    for i in range(len(words)):
        words[i] = ''.join(l for l in words[i] if l.isalpha())
        words[i] = words[i].lower()
    return words


def stemTweet(tweet_cleaned):
    words = tweet_cleaned.split(" ")
    words = clean_words(words)
    stemmed_words = stemmer.stemWords(words)
    tmp = list(stemmed_words)
    for word in tmp:
        if len(word) < 2:
            stemmed_words.remove(word)
    return stemmed_words


# Create a feature vector from words in a tweet and the list of all
# the words
def create_vector(tweet_stemmed, words):
    vector = np.zeros(len(words))
    for word in tweet_stemmed:
        if word in words:
            vector[words.index(word)] = 1
    return vector


# shuffle two lists the same way
def shuffle_lists(a, b):
    c = list(zip(a, b))
    random.shuffle(c)
    a, b = zip(*c)
    return a, b


# delete rare words
def delete_unused_words(words, word_count, threshold=3):
    new_words = []
    for i in range(len(words)):
        if word_count[i] > threshold:
            new_words.append(words[i])
    return new_words


def main():
    print("Connecting to database")
    r.connect('vps542128.ovh.net', 28015).repl()
    print("Requesting tweets")
    cursor = r.table('tweets_without_location').filter(r.row["lang"] == "fr").run()
    step = 0
    words = []
    tweets_stemmed = []

    labels = [[], []]  # array of all the label [ avr , distance]

    inputs = []
    word_count = []
    if LOG:
        log_file = open("words_number.txt", "w")
    print("Iterating over all tweets to create the learning dataset")
    for tweet in cursor:
        step = step + 1
        if step % 1000 == 0:
            print("Tweet number : " + str(step))
            print("Number of different words : " + str(len(words)))
            print("Usable tweets : " + str(len(tweets_stemmed)))

        if "extended_tweet" in tweet.keys():

            label_e_average = get_label(tweet["extended_tweet"]["full_text"], 1, 0)
            label_e_distance = get_label(tweet["extended_tweet"]["full_text"], 1, 1)

            clean = clean_tweet(tweet["extended_tweet"]["full_text"], tweet["extended_tweet"]["entities"])
        else:

            label_e_average = get_label(tweet["text"], 1, 0)
            label_e_distance = get_label(tweet["text"], 1, 1)

            clean = clean_tweet(tweet["text"], tweet["entities"])

        if label_e_average > -2:
            stem_words = stemTweet(clean)
            tweets_stemmed.append(stem_words)
            for word in stem_words:
                if not(word in words):
                    words.append(word)
                    word_count.append(1)
                else:
                    word_count[words.index(word)] = word_count[words.index(word)] + 1
            labels[0].append(label_e_average)
            labels[1].append(label_e_distance)

        if LOG:
            log_file.write(str(step) + " " + str(len(words)) + "\n")

    if LOG:
        log_file.close()
        word_file = open("words.txt", "w")
        words.sort()

        for word in words:
            word_file.write(word.encode('utf-8') + "\n")

        word_file.close()
    print("Removing rare words")
    print("Size before clean : " + str(len(words)))
    words = delete_unused_words(words, word_count)
    print("Size after clean : " + str(len(words)))
    print("Creating feature vectors")
    for tweet in tweets_stemmed:
        vector = create_vector(tweet, words)
        inputs.append(vector)
    print("Creating training and test datasets")
    input_size = len(inputs)
    label_size = len(labels[0])
    if label_size == input_size:
        inputs, labels = shuffle_lists(inputs, labels)
    else:
        print("input_size not the same as label_size, aborting")
        quit()
    cut = label_size[0] / 4
    train_inputs = inputs[:-cut]
    train_labels = []
    train_labels[0] = labels[0][:-cut]
    train_labels[1] = labels[1][:-cut]
    test_inputs = inputs[-cut:]
    test_labels = []
    test_labels[0] = labels[0][-cut:]
    test_labels[1] = labels[1][-cut:]
    np.savetxt("dataset/train_inputs.txt", train_inputs)
    np.savetxt("dataset/train_labels_avr.txt", train_labels[0])
    np.savetxt("dataset/train_labels_dist.txt", train_labels[1])
    np.savetxt("dataset/test_inputs.txt", test_inputs)
    np.savetxt("dataset/test_labels_avr.txt", test_labels[0])
    np.savetxt("dataset/test_labels_dist.txt", test_labels[1])


if __name__ == "__main__":
    # execute only if run as a script
    main()
