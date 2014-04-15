import urllib2
import re
import os
from bs4 import BeautifulSoup

def downloadAd(adUrl, destinationFolder):
    print(adUrl)
    fields = adUrl.split("-")
    filename = os.path.join(destinationFolder, fields[-1] + ".html")
    
    if os.path.exists(filename):
        print("Already downloaded, skipping")
        return # ad already downloaded, ignore
    
    try:
        print("Downloading to " + filename)
        response = urllib2.urlopen(adUrl)
        html = response.read()
    
        
        destinationFile = open(filename, "w")
        destinationFile.write(html) 
        destinationFile.close()
    except urllib2.URLError as e:
        print("Failed to download from " + adUrl + ":" + e.reason)

def getEbookCategories(ebookUrl):
    try:
        response = urllib2.urlopen(ebookUrl)
        html = response.read()

        # Must use the lxml HTML parser even though it has external dependecies, because the default python one is not good enough to parse the Kijiji pages
        # lxml Windows distribution was downloaded from http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
        soup = BeautifulSoup(html, "lxml") 

        categories = ''
        for allKindleEbooksLink in soup.body.find_all('a', href = re.compile('/ebooks-kindle/.*')):
            nextTag = allKindleEbooksLink.findNext()
            if nextTag.name == 'a':
                categories += nextTag.text + "\t"
            
        return categories
        
    except urllib2.URLError as e:
        print("Failed to download from " + ebookUrl + ":" + e.reason)
        
                
def getTop100Info(resultsPageUrl, destinationFolder):
    try:
        response = urllib2.urlopen(resultsPageUrl)
        html = response.read()
        
        # Must use the lxml HTML parser even though it has external dependecies, because the default python one is not good enough to parse the Kijiji pages
        # lxml Windows distribution was downloaded from http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
        soup = BeautifulSoup(html, "lxml") 
    
        #Extract details of each book in the top 100
        for bookDiv in soup.body.find_all('div', {'class', 'zg_itemImmersion'}):
            rank = int(bookDiv.div.span.text.rstrip('.'))
            itemWrapper = bookDiv.find('div', {'class', 'zg_itemWrapper'})
            daysInTop100 = int(itemWrapper.find('div', {'class', 'zg_rankLine'}).text.split(' ', 1)[0])
            title = itemWrapper.find('div', {'class', 'zg_title'}).text.strip(' ')
            author = itemWrapper.find('div', {'class', 'zg_byline'}).text.strip()[3:]
            ebookUrl = itemWrapper.find('div', {'class', 'zg_itemImageImmersion'}).a['href'].strip()
            asin = ebookUrl[-10:]
            avgStarsTag = ''
            rating = ''
            nbReviews = ''
            if itemWrapper is not None:
                zgReviewsTag = itemWrapper.find('div', {'class', 'zg_reviews'})
                if zgReviewsTag is not None: 
                    avgStarsTag = zgReviewsTag.find('span', {'class', 'crAvgStars'})
                    rating = float(avgStarsTag.text.split(' ', 1)[0])
                    nbReviews = int(avgStarsTag.find_all('a')[2].text)
            price = float(itemWrapper.find('div', {'class', 'zg_itemPriceBlock_compact'}).text.split(' ')[2].replace(',', '.'))
            categories = getEbookCategories(ebookUrl)
            print(str(rank)  + '\t' + str(daysInTop100) + '\t' + str(rating) + '\t' + str(nbReviews) + '\t' + str(price) + '\t' + title + '\t' + asin + '\t' + author + '\t' + ebookUrl + '\t' + categories)
            
    except urllib2.URLError as e:
        print("Failed to download from " + resultsPageUrl + ":" + e.reason)
    
def main():
    destinationFolder = "data"
    if not os.path.exists(destinationFolder): 
        os.makedirs(destinationFolder)

    print('Rank\tDaysInTop100\tRating\tNbReviews\tPrice\tTitle\tASIN\tAuthor\tURL')
    
    #bestSellersPage = 'http://www.amazon.fr/gp/bestsellers/digital-text/695398031#3';

    bestSellersPage = 'http://www.amazon.fr/gp/bestsellers/digital-text/695398031/ref=zg_bs_695398031_pg_2/276-1310913-3876205?ie=UTF8&pg='
    for i in range(1, 6):
        getTop100Info(bestSellersPage + str(i), destinationFolder)
    
if __name__ == "__main__":
    main()
