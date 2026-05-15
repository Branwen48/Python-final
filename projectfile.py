#Brandon Mark
#May 15, 2026
#Project Gutenberg
#Gives you the 10 most common words in a book without the fluff. Loads each book into an sql database.

from urllib.request import urlopen
from urllib.parse import urlencode
import json
from collections import Counter
import sqlite3 
import tkinter as TK
import re

con = sqlite3.connect('web.db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS word_counts (id INTEGER PRIMARY KEY AUTOINCREMENT,book_id INTEGER NOT NULL,word TEXT NOT NULL,count INTEGER NOT NULL,FOREIGN KEY (book_id) REFERENCES books(id)")
con.commit()

def findgbook(title):
    '''Creates a url to search for the book on gutenberg, returns the title and url'''
    search_url="https://gutendex.com/books?" + urlencode({"search": title,"languages": "en"})
    response=urlopen(search_url)
    data=json.loads(response.read().decode())

    if data["count"]==0:
        return None
    
    book = data["results"][0]
    book_title = book["title"]
    formats = book["formats"]
    text_url=None

    for file_type,file_url in formats.items():
        if file_type.startswith("text/plain"):
            text_url=file_url
            break
    if text_url is None:
        return None
    return book_title,text_url

def loaddatabase(title):
    '''takes the title, passes it through findgbook and uses the url to return the most common words'''
    try:
        result=findgbook(title)
        if result is None:
            return "book was not found"
        book_title , text_url=result
        content = scraper(text_url)
        most_common=commonfinder(content)
        save_book(book_title,text_url,most_common)
        return "\n".join(f"{word}: {count}" for word, count in most_common)
    except:
        return "book was not found"

def loadurl(url):
    '''Loads a Gutenberg URL, saves its word counts, and returns formatted results.'''
    try:
        content = scraper(url)
        title = titlefinder(content)
        most_common = commonfinder(content)
        save_book(title, url, most_common)
        return commonreturner(most_common)
    except:
        return "book was not found"
    
def titlefinder(content):
    title = content.split("title: ", 1)[1].split("author:", 1)[0].strip()
    return title


def searchdatabase(title):
    '''searches database for the title and returns the stored most_common'''
    cur.execute("SELECT word_counts.word, word_counts.count FROM books JOIN word_counts ON books.id=word_counts.book_id WHERE books.title LIKE ? ORDER BY word_counts.count DESC", (f"%{title}%",))
    results=cur.fetchall()
    if len(results)>0:
        return commonreturner(results)
    return loaddatabase(title)

def save_book(title, url, most_common):
    '''puts the book info into sql'''
    cur.execute("INSERT INTO books (title, url) VALUES (?, ?)",(title, url))
    book_id = cur.lastrowid
    for word, count in most_common:
        cur.execute("INSERT INTO word_counts (book_id, word, count) VALUES (?, ?, ?)",(book_id, word, count))
    con.commit()

def scraper(link):
    '''turns the html file into a string'''
    response=urlopen(link)
    html=response.read()
    content=html.decode().lower()
    return content

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but","he", "she", "it", 
    "they", "we", "you", "i","is", "are", "was", "were", 
    "be", "been","to", "of", "in", "on", "for", "with", 
    "as","that", "this", "these", "those","like","at", "by", 
    "from", "not", "so", "if", "then", "there",
    "their", "his", "her", "my", "me", "him", "them", "our",
    "your", "what", "which", "who", "when", "where", "why",
    "how", "all", "any", "can", "do", "did", "does"
}

def commonfinder(content):
    '''takes a string and returns a list of tuples with the 10 most common words and their count'''
    wordlist = re.findall(r"\b[a-z]+\b", content.lower())
    filtered_words = [word for word in wordlist if word not in STOP_WORDS]
    most_common = Counter(filtered_words).most_common(10)
    return most_common

def commonreturner(most_common):
    '''takes a dictionary of most_common and returns it into a nicely formatted output string'''
    return "\n".join(f"{word}: {count}" for word, count in most_common)


     