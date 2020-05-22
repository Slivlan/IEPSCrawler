# Iskanje in ekstrakcija podatkov s spleta
Dobrodošli v repozitoriju naše skupine (Mihael Švigelj, Lovro Vražič, Luka Zakšek) za oddajo seminarskih nalog pri predmetu Iskanje in ekstrakcija podatkov s spleta (2019/20) na Fakulteti za računalništvo in informatiko Univerze v Ljubljani.

# Seminarska 1: Crawler

Crawler je projekt, ki smo ga razvili Luka, Mihael in Lovro za prvo domačo nalogo pri predmetu Iskanje in ekstrakcija podatkov s spleta.


## Namestitev

Uporabi [pip](https://pip.pypa.io/en/stable/) za namestitev.

```bash
pip install psycopg2
pip install selenium
pip install tldextract
pip install beautifulsoup4
pip install requests
```
Chrome webdriver je že v repozitoriju, tako da ga ni potrebno posebej inštalirat.
## Postgres

Postgres baza že teče na vps-ju, zato v kodi ni potrebno spreminjat nobenih argumentov, ampak bo ob zagonu skripte vse delovalo "out of the box".   
Opomba: Ob vsakem zagonu crawlerja, se baza na začetku resetira. Tako da vnosov iz prejšnjih izvedb crawlerja ni v bazi.

## Uporaba

Poženi crawler z ukazom 
```python
cd crawler
python crawler.py <int_stevilo_threadov>
```
Primer za 6 threadov:
```python
 cd crawler
 python crawler.py 6
```

## Vizualizacija

Za pregled vizualizacije se lahko uporabi Gephi program, v katerem odpremo datoteko [links_visualisation.gephi](/links_visualisation.gephi).

# Seminarska 2: Data Extractor
Cilj seminarske naloge je bil razviti 3 metode ekstrakcije podatkov s podanih vzorcev spletnih strani.
## Namestitev

Uporabi [pip](https://pip.pypa.io/en/stable/) za namestitev. Potrebne so sledeče knjižnice:

```bash
pip install lxml
pip install html2text
pip install htmldom
```
## Uporaba
Skripta run-extraction.py se nahaja v direktoriju "implementation-extraction", od koder jo tudi poženemo.

Na voljo so 3 načini ekstrakcije:
- A: Uporaba [RegEx](https://en.wikipedia.org/wiki/Regular_expression) (Regular expressions):
```python
 python run-extraction.py A
```
- B: Uporaba [XPath](https://en.wikipedia.org/wiki/XPath) ekstrakcije:
```python
 python run-extraction.py B
```
- C: TODOTODOTODO Uporaba ... TODO ...:
```python
 python run-extraction.py C
```
Če podamo napačen način izvedbe (A/B/C), nas program o tem opozori ter se preneha izvajati.
Ekstrakcija se naredi na spletnih straneh, podanih v direktoriju "input-extraction".

# Seminarska 3: Indexing

## Namestitev

Uporabi [pip](https://pip.pypa.io/en/stable/) za namestitev.

```bash
pip install beautifulsoup4
pip install nltk
pip install 
```

Ob zagonu knjižnica nltk morda potrebuje dodatne pakete, katere pridobite s sledenjem izpisanih navodil v terminalu.

## Uporaba

Vse skripte se nahajajo v mapi implementation-indexing. Tam se nahaja tudi mapa data znotraj katere so shranjene html datoteke iz katerih program ekstrahira tekst. 

Za preiskovanje z naivnim algoritmom:

```python
 python .\run-basic-search.py [vnos za poizvedovanje]
```

Za preiskovanje z uporabo inverted-index:

```python
 python .\run-sqlite-search.py [vnos za poizvedovanje]
```
