#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('inverted-index.db')

print ("Opened database successfully")

conn.execute('''
  DROP TABLE IF EXISTS IndexWord;
  ''')
conn.execute('''
  CREATE TABLE IndexWord (word TEXT PRIMARY KEY);
  ''')
print ("Table IndexWord created successfully")

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

print ("Table Posting created successfully")

conn.close()