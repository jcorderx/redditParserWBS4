import requests
from bs4 import BeautifulSoup


#request URL
url = "https://old.reddit.com/r/FreeGameFindings/"
page = requests.get(url)
print("out")

# parse html file Store in htmlResult
soup = BeautifulSoup(page.text, 'html.parser')
htmlResult = soup.find_all('a')


#Store html document in file
f = open("redditHtmlRequest.txt", "w")
f.write(htmlResult)
f.close()