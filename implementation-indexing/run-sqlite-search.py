#!/usr/bin/python

import sqlite3

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
    conn.execute("INSERT INTO IndexWord (word) VALUES ('{}')".format(s))
    conn.commit()

def insert_posting():
    conn.execute("INSERT INTO Posting (word,documentName,frequency,indexes) VALUES (‘davek’, ‘evem.gov.si/evem.gov.si.4.html’, 3, ‘2,34,894’)")
    conn.commit()

conn = sqlite3.connect('inverted-index.db')
db_init()
insert_word("makja")
conn.close()