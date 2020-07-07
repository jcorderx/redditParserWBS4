import requests
from bs4 import BeautifulSoup
import tkinter

# Main

# Variables
#   steamResultList - Stores and results that are on discord

#string lists
htmlResultList = []
compareResultList = []
finalResultList = []

#int List
resultIntListing = []

count = 0

# Request the url
url = "https://old.reddit.com/r/FreeGameFindings/"
page = requests.get(url, headers = {'User-agent': 'your bot 0.1'})
print("Page Response : ", page)

# parse html file Store in htmlResult
soup = BeautifulSoup(page.text, 'html.parser')
toFile = soup.prettify()

# String Variables for Comparison
steamVar = "store.steampowered.com"
microsoft = "www.microsoft.com"
epicGames = "www.epicgames.com"

# print(soup.prettify())

# cycle through list and store all instances of href/links into resultList
# stored as strings

for a in soup.find_all('a', href=True) :
    htmlResultList.append(a['href'])

# split at /
for a in range(htmlResultList.__len__()) :
    compareResultList.append(htmlResultList[a].split('/'))

# index 206 is a good example of "www.epicgames.com"
# index 297 "store.steampowered.com
# index 288 "microsoft"

# go through and store the index number of strings containing steamVar, epicGames, microsoft
for item in compareResultList :
    for i in item :
         if i == "domain":
            break
         elif i == steamVar :
             resultIntListing.append(count)
         elif i == epicGames :
            resultIntListing.append(count)
         elif i == microsoft :
             resultIntListing.append(count)
         else:
            continue
    count = count + 1

# go through compareResultList using the index numbers from resultIntListing
# store the results in finalResultList
# finalResultList contains all links from html document

for i in resultIntListing:
   finalResultList.append(htmlResultList[i])

for link in finalResultList:
    print(link)





