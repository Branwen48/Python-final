from urllib.request import urlopen
from collections import Counter
import sqlite3 
import tkinter as TK
import re

con = sqlite3.connect('web.db')
cur = con.cursor()
cur.execute("CREATE TABLE books(title text, url text)")

def scraper(link):
    response=urlopen(link)
    html=response.read()
    content=html.decode().lower()
    return content

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but","he", "she", "it", 
    "they", "we", "you", "i","is", "are", "was", "were", 
    "be", "been","to", "of", "in", "on", "for", "with", 
    "as","that", "this", "these", "those","like"
}

def commonfinder(content):
    wordlist = re.findall(r"\b[a-z]+\b", content.lower())
    filtered_words = [
        word for word in wordlist
        if word not in STOP_WORDS
    ]
    most_common = Counter(filtered_words).most_common(10)
    return "\n".join(f"{word}: {count}" for word, count in most_common)

def titlefinder(content):
    title = content.split("Title: ", 1)[1].split("Author:", 1)[0].strip()
    return title

def databaseinput(link):
    title=titlefinder(scraper(link))
    cur.execute("INSERT INTO books VALUES(?,?)",(title,link))
    cur.commit()

def urlfromdatabase(title):
    cur.execute("SELECT url FROM books WHERE title LIKE ?",(f"%{title}%",))
    return cur.fetchall()
