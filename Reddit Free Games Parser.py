"""
todo:
    Create gog tables with all gog games currently in there.
    Create Free games table for keeping track of reddit games we have found
    Create any other games tables and populate them
    connect to server and update free games table and other game tables
    cross check if I have already seen link for game if so don't include in message.
    


"""

from config import CONFIGURATIONS
import requests
from bs4 import BeautifulSoup
import smtplib
import sys
import logging
from email.message import EmailMessage
import mariadb


CARRIERS = CONFIGURATIONS['carriers']
EMAIL = CONFIGURATIONS['credentials']['email']
PASSWORD = CONFIGURATIONS['credentials']['password']
PHONENUMBER = CONFIGURATIONS['credentials']['phone']

def send_message(phone_number, carrier, message):
    msg = EmailMessage()
    msg['Subject'] = f'Free Games Findings'
    msg.set_content(message)
    
    recipient = phone_number + CARRIERS[carrier]
    auth = (EMAIL, PASSWORD)
 
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])
 
    server.sendmail(auth[0], recipient, message)

def parseData(soup,stores):
    htmlResultList = []
    for a in soup.find_all('a', href=True) :
        try:
            for store in stores:
                link = (a['href'].split('/')[2])
                if ((link == store) and ('domain' not in a['href']) ):
                    htmlResultList.append(a['href'])
                

        except:
            continue
    return htmlResultList

def insertIntoDatabase(htmlResultList, cur, ):
    cur.execute(
    "insert"
    )
    
    print("hello")



if __name__ == "__main__":
    #---------------------------------------------------------------------
    #Main
    #Log File config
    logging.basicConfig(filename='parser.log', encoding='utf-8', level=logging.DEBUG)

    gameList = []
    tmp = []

    # Request the url
    url = "https://old.reddit.com/r/FreeGameFindings/"
    page = requests.get(url, headers = {'User-agent': 'your bot 0.1'})
    #print("Page Response : ", page)

    # parse html file and store into soup
    soup = BeautifulSoup(page.text, 'html.parser')
    toFile = soup.prettify()

    #string lists
    stores = ["store.steampowered.com","www.microsoft.com","store.epicgames.com","www.gog.com"]

    htmlResultList = parseData(soup, stores)
    htmlResultList = [*set(htmlResultList)]

    for item in htmlResultList:
        tempString = item.split("/")
        gameName = tempString.pop()
        if(gameName == ""):
            gameName = tempString.pop()
        gameName = gameName.replace("-", " ")
        gameName = gameName.replace("_", " ")
        #gameList.append(gameName)
        tmp.append("""\n""" + gameName + """\n""" + item + """,\n""")

  

    message = """ """.join(tmp)


    logging.info(message)


    send_message(PHONENUMBER,'tmobile', message)
