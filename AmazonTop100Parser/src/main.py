# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import sys
import os
import re
import Amazon
import codecs


def displayHelp():
    print("usage : " + os.path.basename(sys.argv[0]) + " <Amazon top 100 folder> <destination CSV file>")

def parseEbookDescriptionHtmlFile(ebookDescriptionHtmlFile):
    print("Parsing " + ebookDescriptionHtmlFile)
    f = open(ebookDescriptionHtmlFile,"r")
    html = f.read()
    
    # Must use the lxml HTML parser even though it has external dependecies, because the default python one is not good enough to parse the Kijiji pages
    # lxml Windows distribution was downloaded from http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
    soup = BeautifulSoup(html, "lxml")
    
    ebook = Amazon.Ebook() 

    print(ebook)
    return ebook

def parseEbookCategories(html):
    # Must use the lxml HTML parser even though it has external dependecies, because the default python one is not good enough to parse the Kijiji pages
    # lxml Windows distribution was downloaded from http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml
    soup = BeautifulSoup(html, "lxml") 

    categories = ''
    for allKindleEbooksLink in soup.body.find_all('a', href = re.compile('/ebooks-kindle/.*')):
        nextTag = allKindleEbooksLink.findNext()
        if nextTag.name == 'a':
            categories += nextTag.text + "\t"
        
    return categories
        

def parseTop100HtmlFile(top100HtmlFileName, csvFile):
    
    top100HtmlFile = open(top100HtmlFileName, "r")
    html = top100HtmlFile.read()
    top100HtmlFile.close()
    
    ebooksRepositoryFolder = os.path.join(os.path.split(top100HtmlFileName)[0], "ebooks")

    
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

        ebookFileName = os.path.join(ebooksRepositoryFolder, asin + ".html")
        ebookFile = open(ebookFileName, "r")
        ebookHtml = ebookFile.read()
        ebookFile.close()

        categories = parseEbookCategories(ebookHtml)
        line = str(rank)  + '\t' + str(daysInTop100) + '\t' + str(rating) + '\t' + str(nbReviews) + '\t' + str(price) + '\t' + title + '\t' + asin + '\t' + author + '\t' + ebookUrl + '\t' + categories
        print(line)
        csvFile.write(line + "\r\n")
        csvFile.flush()
            

def analyzeFolder(folder, csvFile):
    print("Analyzing folder " + folder)
    folder = os.path.normpath(folder)
    for f in os.listdir(folder):
        fileextension = os.path.splitext(f)[1]
        if fileextension == ".html":
            parseTop100HtmlFile(os.path.join(folder, f), csvFile)
    
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
    
    analyzeFolder(top100Folder, csvFile)
    
if __name__ == "__main__":
    main()
