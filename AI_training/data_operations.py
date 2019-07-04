import csv
import re
import string
import rethinkdb as r
from debian.debtags import output

LOG = False


def average(list):
    output = 0
    for value in list:
        output += float(value)
    output /= len(list)
    return output


def furthest(list):
    output = []
    for value in list:
        output.append(float(value))
    return max(output, key=abs)


def save_word(word, score):
    with open('AFINN-111.csv', 'a', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow([word, score])


def upgrade_database(unused, used):
    for word in unused:
        save_word(word, 0.01)
    for word in used:
        update_word(word, 0.01)


def update_word(word, score):
    r = csv.reader(open('AFINN-111.csv'), delimiter=',')  # Here your csv file
    lines = [l for l in r]  # get the file contents

    for line in lines:
        if line[0] == word:
            line[1] = score + float(line[1])

    # create a new file to save the contents
    writer = csv.writer(open('AFINN-111.csv', 'w'), delimiter=',')

    # write/save
    writer.writerows(lines)


def check_word(word_list):
    output = []
    used = []
    with open('AFINN-fr-165.csv', newline='') as fp:
        csvreader = csv.reader(fp, delimiter=",")

        next(csvreader, None)  # skip the headers
        for row in csvreader:
            for word in word_list:
                result = re.findall('^\\b' + word + '\\b', row[0], flags=re.IGNORECASE)
                if result:
                    output.append(row[1])
                    used.append(word)
    unused = word_list
    for word in used:
        for x in range(word_list.count(word)):
            unused.remove(word)
    return output, used, unused


def check_emoji(word_list):
    output = []
    used = []

    with open('emoji_data.csv', newline='') as fp:
        csvreader = csv.reader(fp, delimiter=",")
        next(csvreader, None)  # skip the headers

        for row in csvreader:
            for word in word_list:
                result = row[0] in word
                if result:
                    output.append(row[11])
                    used.append(word)
    unused = word_list

    for word in used:
        for x in range(word_list.count(word)):
            unused.remove(word)
    return output, used, unused


def list_values():
    with open('AFINN-111.csv', newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in data:
            print(', '.join(row))


def data_sanitization(file):
    file = re.sub(r'@([A-Za-z0-9_]+)', "", file)
    file = re.sub('[%s]' % re.escape(string.punctuation), '', file)
    file = re.sub(r"http\S+", "", file)
    file = file.split(' ')
    for x in range(file.count('')):
        file.remove('')
    return file


def main():
    r.connect('vps542128.ovh.net', 28015).repl()

    cursor = r.table('tweets_without_location').run()

    if LOG:
        log_file = open("words_number.txt", "w")

    for tweet in cursor:

        if tweet["lang"] == "fr":
            file = tweet["text"]
            file = data_sanitization(file)
            output, used, unused, = check_emoji(file)
            output_sec, used, unused, = check_word(file)

            if (output_sec != []) & (output != []):
                print(tweet["text"], "\n")
                print(average(output), furthest(output))
                print(average(output_sec), furthest(output_sec), "\n\n")


if __name__ == "__main__":
    # execute only if run as a script
    main()
