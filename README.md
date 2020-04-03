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
Opomba: Ob vsakem zagonu crawlerja, se baza na začetku resetira. Tako da vnosov iz prejšnjih izvedb crawlerja ni v bazi.

## Uporaba

Poženi crawler z ukazom 
```python
python crawler.py <int_stevilo_threadov>
primer za 6 threadov:
  python crawler.py 6
```

## Vizualizacija

Za pregled vizualizacije se lahko uporabi Gephi program, v katerem odpremo datoteko [links_visualisation.gephi](/links_visualisation.gephi).