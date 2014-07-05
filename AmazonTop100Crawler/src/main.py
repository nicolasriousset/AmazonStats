# -*- coding: utf-8 -*-
import urllib2
import re
import os
import datetime
import codecs
from bs4 import BeautifulSoup

def downloadTop100(top100Url, destinationFolder):
    print(top100Url)
    fields = top100Url.split("-")
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

def parseEbookCategories(html):
    try:

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
        
                
def getTop100Info(resultsPageUrl, pageIndex, destinationFolder, csvFile):
    try:
        response = urllib2.urlopen(resultsPageUrl + str(pageIndex))
        html = response.read()
        
        fromRank = (pageIndex-1) * 20 + 1
        toRank = fromRank + 19 
        localFile = open(os.path.join(destinationFolder, str(fromRank) + "-" + str(toRank) + ".html"), "w")
        localFile.write(html)
        localFile.close()
        
        ebooksDestinationFolder = os.path.join(destinationFolder, "ebooks")
        if not os.path.exists(ebooksDestinationFolder): 
            os.makedirs(ebooksDestinationFolder)

        
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
            response = urllib2.urlopen(ebookUrl)
            ebookHtml = response.read()
            ebookFileName = os.path.join(ebooksDestinationFolder, asin + ".html")
            ebookFile = open(ebookFileName, "w")
            ebookFile.write(ebookHtml)
            ebookFile.close()

            categories = parseEbookCategories(ebookHtml)
            line = str(rank)  + '\t' + str(daysInTop100) + '\t' + str(rating) + '\t' + str(nbReviews) + '\t' + str(price) + '\t' + title + '\t' + asin + '\t' + author + '\t' + ebookUrl + '\t' + categories
            print(line)
            csvFile.write(line + "\r\n")
            csvFile.flush()
            
    except urllib2.URLError as e:
        print("Failed to download from " + resultsPageUrl + ":" + e.reason)
    
def main():
    destinationFolder = os.path.join("data", str(datetime.date.today()) + " " + str(datetime.datetime.now().strftime("%Hh%M")))
    if not os.path.exists(destinationFolder): 
        os.makedirs(destinationFolder)

    csvFileName = os.path.join(destinationFolder, "top100.csv")
    
    csvFile = codecs.open(csvFileName, "w", "latin-1")
    print("Rank\tDaysInTop100\tRating\tNbReviews\tPrice\tTitle\tASIN\tAuthor\tURL")
    csvFile.write("Rank\tDaysInTop100\tRating\tNbReviews\tPrice\tTitle\tASIN\tAuthor\tURL\r\n")
    
    #bestSellersPage = 'http://www.amazon.fr/gp/bestsellers/digital-text/695398031#3';

    bestSellersPage = 'http://www.amazon.fr/gp/bestsellers/digital-text/695398031/ref=zg_bs_695398031_pg_2/276-1310913-3876205?ie=UTF8&pg='
    for i in range(1, 6):
        getTop100Info(bestSellersPage, i, destinationFolder, csvFile)
        
    csvFile.close()
    
if __name__ == "__main__":
    main()
