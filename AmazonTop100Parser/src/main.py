# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import sys
import os
import re
import Amazon
import codecs


def displayHelp():
    print("usage : " + os.path.basename(sys.argv[0]) + " <Amazon top 100 folder> <destination CSV file>")

def parseEbookCategories(html):
    # Must use the lxml HTML parser even though it has external dependecies, because the default python one is not good enough to parse the Kijiji pages
    # lxml Windows distribution was downloaded from http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
    soup = BeautifulSoup(html, "lxml") 

    categories = []
    for allKindleEbooksLink in soup.body.find_all('a', href = re.compile('/ebooks-kindle/.*')):
        nextTag = allKindleEbooksLink.findNext()
        if nextTag.name == 'a':
            categories.append(nextTag.text)
        
    return categories
        

def parseTop100HtmlFile(top100HtmlFileName):
    result = []
    
    top100HtmlFile = open(top100HtmlFileName, "r")
    html = top100HtmlFile.read()
    top100HtmlFile.close()
    
    ebooksRepositoryFolder = os.path.join(os.path.split(top100HtmlFileName)[0], "ebooks")

    
    # Must use the lxml HTML parser even though it has external dependecies, because the default python one is not good enough to parse the Kijiji pages
    # lxml Windows distribution was downloaded from http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
    soup = BeautifulSoup(html, "lxml") 

    #Extract details of each book in the top 100
    for bookDiv in soup.body.find_all('div', {'class', 'zg_itemImmersion'}):
        ebook = Amazon.Ebook()
        ebook.rank = int(bookDiv.div.span.text.rstrip('.'))
        itemWrapper = bookDiv.find('div', {'class', 'zg_itemWrapper'})
        ebook.daysInTop100 = int(itemWrapper.find('div', {'class', 'zg_rankLine'}).text.split(' ', 1)[0])
        ebook.title = itemWrapper.find('div', {'class', 'zg_title'}).text.strip(' ')
        ebook.author = itemWrapper.find('div', {'class', 'zg_byline'}).text.strip()[3:]
        ebook.URL = itemWrapper.find('div', {'class', 'zg_itemImageImmersion'}).a['href'].strip()
        ebook.ASIN = ebook.URL[-10:]
        ebook.avgStarsTag = ''
        ebook.rating = ''
        ebook.nbReviews = ''
        if itemWrapper is not None:
            zgReviewsTag = itemWrapper.find('div', {'class', 'zg_reviews'})
            if zgReviewsTag is not None: 
                avgStarsTag = zgReviewsTag.find('span', {'class', 'crAvgStars'})
                ebook.rating = float(avgStarsTag.text.split(' ', 1)[0])
                ebook.nbReviews = int(avgStarsTag.find_all('a')[2].text)
        ebook.price = float(itemWrapper.find('div', {'class', 'zg_itemPriceBlock_compact'}).text.split(' ')[2].replace(',', '.'))

        ebookFileName = os.path.join(ebooksRepositoryFolder, ebook.ASIN + ".html")
        ebookFile = open(ebookFileName, "rb")
        ebookHtml = ebookFile.read()
        ebookFile.close()

        ebook.categories = parseEbookCategories(ebookHtml)
        result.append(ebook)
        
    return result
            

def analyzeTop100Folder(folder):
    print("Analyzing folder " + folder)
    result = []
    folder = os.path.normpath(folder)
    for f in os.listdir(folder):
        fileextension = os.path.splitext(f)[1]
        if fileextension == ".html":
            result.extend(parseTop100HtmlFile(os.path.join(folder, f)))
    return result
    
def main():
    if len(sys.argv) <= 2:
        displayHelp()
        return

    top100Folder = sys.argv[1]
    if not os.path.exists(top100Folder):
        print(top100Folder + " doesn't exist") 
        displayHelp()
        return
    
    csvFileName = sys.argv[2]
#     if os.path.exists(csvFileName):
#         print(csvFileName + " already exists.") 
#         displayHelp()
#         return

    csvFile = codecs.open(csvFileName, "w", "latin-1")
    ebook = Amazon.Ebook()
    ebook.rank = "Rank"
    ebook.daysInTop100 = "DaysInTop100"
    ebook.rating = "rating"
    ebook.nbReviews = "nbReviews"
    ebook.price = "price"
    ebook.title = "title"
    ebook.ASIN = "ASIN"
    ebook.author = "author"
    ebook.URL = "URL"
    csvFile.write(ebook.__repr__())
    
    bestsellersCountPerCategory = dict()
    bestsellers = analyzeTop100Folder(top100Folder)
    for ebook in bestsellers:
        csvFile.write(ebook.__repr__())
        for category in ebook.categories:
            if category in bestsellersCountPerCategory:
                bestsellersCountPerCategory[category] = bestsellersCountPerCategory[category] + 1 
            else:
                bestsellersCountPerCategory[category] = 1

    print("Bestsellers count per category :")                
    for category in bestsellersCountPerCategory:
        print(" - " + category + " = " + bestsellersCountPerCategory[category].__str__())

    bestsellersCount = len(bestsellers)
    bestsellersCountHalf = bestsellersCount / 2
    
    bestsellers.sort(cmp=None, key=lambda ebook : ebook.rank, reverse=False)
    avgDaysInTop100 = sum(ebook.daysInTop100 for ebook in bestsellers[:bestsellersCountHalf]) / bestsellersCountHalf
    print "Average days in top 100 of the 50 highest ranked= " + avgDaysInTop100.__str__()
    avgDaysInTop100 = sum(ebook.daysInTop100 for ebook in bestsellers[bestsellersCountHalf:]) / bestsellersCountHalf
    print "Average days in top 100 of the 50 lowest ranked= " + avgDaysInTop100.__str__()
    
    avgPrice = sum(ebook.price for ebook in bestsellers[:bestsellersCountHalf]) / bestsellersCountHalf
    print "Average price of the 50 highest ranked ebooks = €" + avgPrice.__str__()
    avgPrice = sum(ebook.price for ebook in bestsellers[bestsellersCountHalf:]) / bestsellersCountHalf
    print "Average price of the 50 lowest ranked ebooks = €" + avgPrice.__str__()

    bestsellers.sort(cmp=None, key=lambda ebook : ebook.price, reverse=False)
    avgPrice = sum(ebook.price for ebook in bestsellers) / bestsellersCount
    medianPrice = bestsellers[(bestsellersCount + 1)/2].price        
    print "Average price = €" + avgPrice.__str__()
    print "Median price = €" + medianPrice.__str__()

    bestsellers.sort(cmp=None, key=lambda ebook : ebook.daysInTop100, reverse=False)
    avgDaysInTop100 = sum(ebook.daysInTop100 for ebook in bestsellers) / bestsellersCount
    medianDaysInTop100 = bestsellers[(bestsellersCount + 1)/2].daysInTop100        
    print "Average days in top 100 = " + avgDaysInTop100.__str__()
    print "Median days in top 100 = " + medianDaysInTop100.__str__()

    avgPrice = sum(ebook.price for ebook in bestsellers[:bestsellersCountHalf]) / bestsellersCountHalf
    print "Average price of the 50 youngest ebooks = €" + avgPrice.__str__()
    avgPrice = sum(ebook.price for ebook in bestsellers[bestsellersCountHalf:]) / bestsellersCountHalf
    print "Average price of the 50 oldest ebooks = €" + avgPrice.__str__()

# Average number of reviews
# Average rating
    ratedBestsellers = [ebook for ebook in bestsellers if isinstance(ebook.rating, float)]
    ratedBestsellersCount = len(ratedBestsellers)
    ratedBestsellersCountHalf = ratedBestsellersCount / 2
    print "Percentage of top 100 books with at least one review = %" + (float(ratedBestsellersCount)/float(bestsellersCount)*100.0).__str__()
    avgRating = sum(ebook.rating for ebook in ratedBestsellers) / ratedBestsellersCount
    print "Average rating = " + avgRating.__str__()
    avgRating = sum(ebook.rating for ebook in ratedBestsellers[:ratedBestsellersCountHalf]) / ratedBestsellersCountHalf
    print "Average rating of the 50 youngest ebooks = " + avgRating.__str__()
    avgRating = sum(ebook.rating for ebook in ratedBestsellers[ratedBestsellersCountHalf:]) / ratedBestsellersCountHalf
    print "Average rating of the 50 oldest ebooks = " + avgRating.__str__()
    avgReviewsCount = sum(ebook.nbReviews for ebook in ratedBestsellers) / ratedBestsellersCount
    print "Average reviews count = " + avgReviewsCount.__str__()
    avgReviewsCount = sum(ebook.nbReviews for ebook in ratedBestsellers[:ratedBestsellersCountHalf]) / ratedBestsellersCountHalf
    print "Average reviews count of the 50 youngest ebooks = " + avgReviewsCount.__str__()
    avgReviewsCount = sum(ebook.nbReviews for ebook in ratedBestsellers[ratedBestsellersCountHalf:]) / ratedBestsellersCountHalf
    print "Average reviews count of the 50 oldest ebooks = " + avgReviewsCount.__str__()


    csvFile.close()
    
if __name__ == "__main__":
    main()
