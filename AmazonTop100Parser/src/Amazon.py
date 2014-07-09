# -*- coding: utf-8 -*-

class Ebook:
    rank = "<Unknown>"
    daysInTop100 = "<Unknown>"
    rating = "<Unknown>"
    nbReviews = "<Unknown>"
    price = "<Unknown>"
    title = "<Unknown>"
    ASIN = "<Unknown>"
    author = "<Unknown>"
    URL = "<Unknown>"
    
    def __init__(self):
        self.data = []
        
    def __str__(self):
        return self.rank + "\t" + self.daysInTop100 + "\t" + self.rating + "\t" + self.nbReviews + "\t" + self.price + "\t" + self.title + "\t" + self.ASIN + "\t" + self.author + "\t" + self.URL + "\n"
        
    def __repr__(self):
        return self.__str__()
