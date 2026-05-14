from urllib.request import urlopen
from collections import Counter
import sqlite3 
import tkinter as TK
import re

con = sqlite3.connect('web.db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT)");
cur.execute("CREATE TABLE IF NOT EXISTS word_counts (id INTEGER PRIMARY KEY AUTOINCREMENT,book_id INTEGER NOT NULL,word TEXT NOT NULL,count INTEGER NOT NULL,FOREIGN KEY (book_id) REFERENCES books(id)");
con.commit()

def save_book(title, url, most_common):
    cur.execute("INSERT INTO books (title, url) VALUES (?, ?)",(title, url));
    book_id = cur.lastrowid
    for word, count in most_common:
        cur.execute("INSERT INTO word_counts (book_id, word, count) VALUES (?, ?, ?)",(book_id, word, count))
    con.commit()

def scraper(link):
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
    wordlist = re.findall(r"\b[a-z]+\b", content.lower())
    filtered_words = [
        word for word in wordlist
        if word not in STOP_WORDS
    ]
    most_common = Counter(filtered_words).most_common(10)
    return most_common

def commonreturner(most_common):
        return "\n".join(f"{word}: {count}" for word, count in most_common)

def titlefinder(content):
    title = content.split("title: ", 1)[1].split("author:", 1)[0].strip()
    return title


def urlfromdatabase(title):
    cur.execute("SELECT url FROM books WHERE title LIKE ?",(f"%{title}%",));
    return cur.fetchall()
