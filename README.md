# Crawler

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

## Uporaba

Poženi crawler z ukazom 
```python
python crawler.py --TODO argument kakorkol je oblika idk?
```

## Vizualizacija

