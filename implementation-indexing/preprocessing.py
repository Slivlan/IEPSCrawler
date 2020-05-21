import html2text
import string
import os
from bs4 import BeautifulSoup
from pathlib import Path
from nltk.tokenize import word_tokenize
from stopwords import stop_words_slovene
#from nltk.stem import WordNetLemmatizer


'''
    Prebere vse html datoteke znotraj ./data (rekurzivno globinsko)
    Vrne array tuplov s polji words in documentName
'''
def get_words_from_all_files():
    data = []
    for path in Path('./data').rglob('*.html'):
        entry = {}
        a = get_words_from_file(path)
        entry['words'] = a
        entry['documentName'] = str(path)
        #entry['documentName'] = os.path.basename(path)
        data.append(entry)
    return data

def get_words_from_file(path):
    html = open(path, 'r', encoding='utf').read()

    # print(path)

    '''
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    text = h.handle(html)
    '''

    text = html_to_text(html)

    text = text.lower()

    # tokenizacija in stopword removal
    a = text_to_tokens_without_stopwords(text)
    return a

def html_to_text(html):
    # https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def text_to_tokens_without_stopwords(text):
    a = word_tokenize(text)
    # stop word removal
    a = [w for w in a if not w in stop_words_slovene]
    return a
        

'''
d = get_words_and_files()
print(d[0]['documentName'])
print(d[0]['words'])
'''
