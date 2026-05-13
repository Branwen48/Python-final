from urllib.request import urlopen
from collections import Counter
import sqlite3 
con = sqlite3.connect('web.db')
cur = con.cursor()
cur.execute("CREATE TABLE books(title text, url text)")

#stuff that goes into the output box (link -> most common words)
def scraper(link):
    response=urlopen(link)
    html=response.read()
    content=html.decode().lower()
    return content

def commonfinder(content):
    wordlist=content.split()
    most_common = Counter(wordlist).most_common(10)
    return most_common

def titlefinder(content):
    title = content.split("Title: ", 1)[1].split("Author:", 1)[0].strip()
    return title

def databaseinput(link):
    title=titlefinder(scraper(link))
    cur.execute("INSERT INTO books VALUES(?,?)",(title,link))
    cur.commit()

        