#!/usr/bin/python

import sqlite3
from preprocessing import *

def db_init():
    conn.execute('''
      DROP TABLE IF EXISTS IndexWord;
      ''')
    conn.execute('''
      CREATE TABLE IndexWord (word TEXT PRIMARY KEY);
      ''')

    conn.execute('''
      DROP TABLE IF EXISTS Posting;
      ''')
    conn.execute('''
      CREATE TABLE Posting (
      word TEXT NOT NULL,
      documentName TEXT NOT NULL,
      frequency INTEGER NOT NULL,
      indexes TEXT NOT NULL,
      PRIMARY KEY(word, documentName),
      FOREIGN KEY (word) REFERENCES IndexWord(word));
      ''')


def insert_word(s):
    conn.execute("INSERT OR IGNORE INTO IndexWord (word) VALUES (?)",(s,))

def insert_posting(word, documentName, frequnecy, indexes):
    conn.execute("INSERT INTO Posting (word,documentName,frequency,indexes) VALUES (?, ?, ?, ?)",(word,documentName,frequnecy,indexes))

def get_neighbourhood_of_word():
    pass

def search_word(word):
    conn.execute("SELECT * FROM Posting WHERE word = ? ORDER BY frequency DESC;", (word,))
    rows = conn.fetchall()

    for row in rows:

        documentName = row[1]
        frequency = row[2]
        indexes = [int(i) for i in row[3].split(",")]

        words = get_words_from_file(documentName)

        found_words = [words[i-3:i+4] for i in indexes]

        print("  {:<12}{:<59}{}".format(frequency,documentName,str(found_words).replace(",", "").replace("[", "").replace("]", "").replace("'", "")))


def save_to_database(data):
    print("Saving to database...")
    for dict in data:
        words = dict["words"]
        documentName = dict["documentName"]

        # print(documentName)

        processed_words = set()

        for index, word in enumerate(words):
            if word not in processed_words:
                indices = [i for i, x in enumerate(words) if x == word]
                indices_string = str(indices).strip('[]').replace(" ", "")

                insert_word(word)
                insert_posting(word, documentName, len(indices), indices_string)

            processed_words.add(word)

conn = sqlite3.connect('inverted-index.db', isolation_level=None).cursor()

# print("Clearing database...")
# db_init()
#
# print("Getting words and filenames...")
# data = get_words_from_all_files()
# save_to_database(data)
print ("""
  Frequencies Document                                                   Snippet
  ----------- ---------------------------------------------------------- ----------------------------------------------------------------------------------------
""")
search_word("uporabo")




conn.close()