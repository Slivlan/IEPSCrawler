#!/usr/bin/python

import sqlite3
from preprocessing import *
import time
import sys
start_time = time.time()

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

def search_words(words):
    result = []
    for word in words:

        conn.execute("SELECT * FROM Posting WHERE word = ? ORDER BY frequency DESC;", (word,))
        rows = conn.fetchall()

        for row in rows:
            documentName = row[1]
            frequency = row[2]
            indexes = [int(i) for i in row[3].split(",")]

            words = get_words_from_file(documentName)
            neighbourhood_words = [words[i-3:i+4] for i in indexes]
            fin_s = ""

            for neighbourhood in neighbourhood_words:
                fin_s += "..."
                for i, word in enumerate(neighbourhood):
                    if word in {"[","]","'", '"', "\n", "\t"}:
                        continue
                    if word not in {",", ".", ")"} or i == 0 :
                        fin_s +=  " " + word
                    else:
                        fin_s += word
                fin_s += " "

            result.append((frequency, "  {:<12}{:<59}{}".format(frequency, documentName, fin_s)))

    result = sorted(result, key= lambda x: x[0], reverse=True)
    return result


def save_to_database(data):
    print("Saving to database...")
    for dict in data:
        words = dict["words"]
        documentName = dict["documentName"]

        processed_words = set()

        for index, word in enumerate(words):
            if word not in processed_words:
                indices = [i for i, x in enumerate(words) if x == word]
                indices_string = str(indices).strip('[]').replace(" ", "")

                insert_word(word)
                insert_posting(word, documentName, len(indices), indices_string)

            processed_words.add(word)

conn = sqlite3.connect('inverted-index.db', isolation_level=None).cursor()

'''
print("Clearing database...")
db_init()

print("Getting words and filenames...")
data = get_words_from_all_files()
save_to_database(data)
'''

w = sys.argv[1:]
w = str(w)
w.lower()
w = text_to_tokens_without_stopwords(w)

print('Searching for a query: "{}"'.format(" ".join(w)))
results = search_words(w)
print('Results for a query: "{}"'.format(" ".join(w)))
print("\n  Results found in %s seconds" % (time.time() - start_time))
print ("""
  Frequencies Document                                                   Snippet
  ----------- ---------------------------------------------------------- ----------------------------------------------------------------------------------------
""")


for freq, s in results:
    print(s)
conn.close()
