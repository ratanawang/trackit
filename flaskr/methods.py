import requests
from random import choice


def getQuote(): #Returns a list in the format [quote, author]
    data = requests.get("https://type.fit/api/quotes").json()
    quote = choice(data)
    return([quote['text'], quote['author']])
