__author__ = 'noahg_000'

from text_extraction import Extraction, Article

# create a hash table of words and their associated values...
import csv
tsv = open("AFINN-111.txt", "r")

sentimentData = dict(csv.reader(tsv, dialect="excel-tab"))

def sentence_sentiment(sentence):
    totalSentiment = 0
    count = 0
    negated = False
    for word in sentence.split(" "):
        m_word = word
        if negated is True:
            m_word = "not " + word

        if word == "not" or word == "n't":
            negated = not negated

        if sentimentData.has_key(m_word):
            totalSentiment += float(sentimentData[m_word])
            count += 1
        elif sentimentData.has_key(word) and negated is True:
            totalSentiment += float(sentimentData[word]) * -1 - 1.0
            count += 1

    if totalSentiment == 0 or count == 0:
        return 0

    return (totalSentiment/count)

if __name__ == '__main__':

    url = raw_input("Enter a URL: ")

    while url != "exit":
        extraction = Extraction(url)
        extraction.processText()

        totalSent = 0
        for sentence in extraction.sentences:
            totalSent += sentence_sentiment(sentence)

        print "average article sent: " + repr(float(totalSent / len(extraction.sentences)))

        article = Article(url, extraction.author, extraction.title, extraction.sentences, float(totalSent / len(extraction.sentences)))
        Article.store(article)

        url = raw_input("Enter a URL: ")

# now we have all the nice base data to perform sentiment analysis on
#article = Article(url, "test", "test", ["test", "anotherTest"], 1.20) #sample

# store in JSON format to reference later
#Article.store(article)
