# -*- coding: cp1252 -*-

__author__ = 'noahg_000'

from alchemyapi import AlchemyAPI
import json
from warnings import warn

class AlchemyException(Exception):
    def __init__(self, statusInfo):
        self.statusInfo = statusInfo

class InputException(Exception):
    def __init__(self, exp):
        self.exp = exp

"""
CLASS: Article
Object to represent an analyzed article. It contains basic info like the url, author, title, and processed
sentences as well as the analysis output -- the bias indicator.

It can be initialized by specifying its data, or by passing the file name of a previously analyzed article.

Available public fields include:
    url: the input url
    author: the article author
    title: the article title
    sentences: the processed sentences passed through Extraction's sentence boundary disambiguator
    bias: the calculated sentiment value of the article
    data: JSON representation of the article's data.

Static methods:
    store(article): stores an Article object through file IO. Does not store if a file with the article's title
                    already exists.

Usage:

article = Article(url, author, title, sentences, bias)
Article.store(article)

or...

article = Article(fileName)
"""
class Article():
    def __init__(self, url, author, title, sentences, bias):
        self.url = url
        self.author = author
        self.title = title
        self.sentences = sentences
        self.bias = bias

        self.data = {u"url": url,
                     u"author": author,
                     u"title": title,
                     u"sentences": sentences,
                     u"bias": bias}

    @classmethod
    def fromFile(cls, fileName):
        import os
        if os.path.isfile(fileName) is False:
            raise InputException("Invalid filename")
            return

        inFile = open(fileName, 'r')
        data = json.load(inFile)
        inFile.close()

        return Article.fromDict(data)

    @classmethod
    def fromDict(cls, data):
        return cls(data[u"url"], data[u"author"], data[u"title"], data[u"sentences"], data[u"bias"])

    @staticmethod
    def store(article):
        import os
        if os.path.isfile(article.title):
            return

        outFile = open(article.title[:10], 'w')
        outFile.write(json.dumps(article.data, indent=4))
        outFile.close()


"""
CLASS: Extraction
Class to call when the user inputs an initial URL to analyze, generally the first step.
It utilizes AlchemyAPI natural language processing to identify the title, author, and text.
The text is then divided into a list of individual sentences to analyze, without any quotes.

processText(url) must be called after initializing an instance of this class.
Available members include:
    url: the input URL for the article
    title: the title of the article in the URL
    author: the author of the article in the URL
    sentences: a list of sentences sent through the sentence boundary disambiguator -- __sbdText(extractedText)

usage:
extraction = Extraction(url)
extraction.processText()

"""
class Extraction:
    def __init__(self, url):
        self.alchemyAPI = AlchemyAPI()
        self.alchemyAPI.outputMode = 'json'
        self.url = url
        # must call extraction after initialization

    """
    Goes through all URL processing routines for the constructor-specified URL
    """
    def processText(self):
        text = self.__extractText(self.url)
        self.sentences = self.__sbdText(text)
        self.author    = self.__extractAuthor(self.url)
        self.title     = self.__extractTitle(self.url)


    """
    Calls AlchemyAPI to extract the text from the given article
    """
    def __extractText(self, url):
        if url is None or url == "":
            raise InputException("Invalid URL")

        response = self.alchemyAPI.text('url', url)
        if response['status'] != 'OK':
            warn(response['statusInfo'])

        return response['text'].encode('utf-8')

    """
    Calls AlchemyAPI to extract the author of the article.
    """
    def __extractAuthor(self, url):
        if url is None or url == "":
            raise InputException("Invalid URL")

        response = self.alchemyAPI.author('url', url)
        if response['status'] != 'OK':
            warn(response['statusInfo'])

        return response['author'].encode('utf-8')

    """
    Gets the article title with
    """
    def __extractTitle(self, url):
        if url is None or url == "":
            raise InputException("Invalid URL")

        response = self.alchemyAPI.title('url', url)
        if response['status'] != 'OK':
            warn(response['statusInfo'])
        return response['title'].encode('utf-8')


    """
    Applies a sentence boundary disambiguation algorithm to the extracted
    article text. We then have access to the individual sentences of the article.
    From there any quotes are removed, so sentiment analysis is performed on the writer's
    additions only.
    """
    def __sbdText(self, extractedText):
        import re
        sentenceEnders = re.compile(r"""
            # Split sentences on whitespace between them.
            (?:               # Group for two positive lookbehinds.
              (?<=[.!?])      # Either an end of sentence punct,
            | (?<=[.!?]['"])  # or end of sentence punct and quote.
            )                 # End group of two positive lookbehinds.
            (?<!  Mr\.   )    # Don't end sentence on "Mr."
            (?<!  Mrs\.  )    # Don't end sentence on "Mrs."
            (?<!  Jr\.   )    # Don't end sentence on "Jr."
            (?<!  Dr\.   )    # Don't end sentence on "Dr."
            (?<!  Prof\. )    # Don't end sentence on "Prof."
            (?<!  Sr\.   )    # Don't end sentence on "Sr."
            \s+               # Split on whitespace between sentences.
            """,
        re.IGNORECASE | re.VERBOSE)
        sentenceList = sentenceEnders.split(extractedText)

        """
        remove any quotes by recognizing ascii/unicode double sentences.
        any quotes within sentences are left, because this paraphrasing/choice
        is still somewhat indicative of possible bias
        """
        for sentence in list(sentenceList):
            if sentence[:3] == "“" or sentence[:1] == '"': # “ = unicode representation of slanted double quote
                sentenceList.remove(sentence)

        return sentenceList


#what to do if this file is run independently
if __name__ == '__main__':
    url = raw_input("Enter an article URL: ")
    extraction = Extraction(url)
    extraction.processText()

    data = {u"title": extraction.title,
             u"author":extraction.author,
             u"text":extraction.sentences,
             u"url":extraction.url}

    print(json.dumps(data, indent=4))