# -*- coding: utf-8 -*-

class Ebook:
    rank = 0
    daysInTop100 = 0
    rating = 0.0
    nbReviews = 0
    price = 0.0
    title = "<Unknown>"
    ASIN = "<Unknown>"
    author = "<Unknown>"
    URL = "<Unknown>"
    categories = []
    
    def __init__(self):
        self.data = []
        
    def __str__(self):
        csvLine = self.rank.__str__() + "\t" + self.daysInTop100.__str__() + "\t" + self.rating.__str__() + "\t" + self.nbReviews.__str__() + "\t" + self.price.__str__() + "\t" + self.title + "\t" + self.ASIN + "\t" + self.author + "\t" + self.URL
        for category in self.categories:
            csvLine += "/t" + category
        return csvLine + "\n"
        
    def __repr__(self):
        return self.__str__()
