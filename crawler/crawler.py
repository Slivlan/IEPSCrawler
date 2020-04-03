import urllib
from selenium import webdriver
from urllib import robotparser
from urllib.parse import urlparse
import psycopg2
import threading
import concurrent.futures
from bs4 import BeautifulSoup
import re
import requests
from operator import itemgetter
import datetime
from frontier import Frontier
import datetime
import hashlib
from colorama import Style
from colorama import Fore
from colorama import init
import os
from tldextract import extract
import time
import traceback
import sys

init()



# Frontier object for frontier interaction
frontier = Frontier()

domains = ["gov.si", "evem.gov.si", "e-uprava.gov.si", "e-prostor.gov.si"]
urls = ["https://www.gov.si", "http://evem.gov.si/evem/drzavljani/zacetna.evem", "https://e-uprava.gov.si/", "https://www.e-prostor.gov.si/"]

allowed_domain = 'gov.si'
type_codes = {
	'application/msword' : 'doc',
	'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : 'docx',
	'application/pdf' : 'pdf',
	'application/vnd.ms-powerpoint' : 'ppt',
	'application/vnd.openxmlformats-officedocument.presentationml.presentation' : 'pptx',
	'text/html' : 'html'
}
request_rate_sec = 5
user_agent = "fri-ieps-nasagrupa"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
driver = webdriver.Chrome(chrome_options = chrome_options)

conn = psycopg2.connect("host=167.71.67.220 dbname=crawler user=crawler password=tojegeslo")
conn.autocommit = True
'''
Cursors are not thread safe: a multithread application can create many cursors from the same connection and should use each cursor from a single thread. See Thread and process safety for details.
'''
cur = conn.cursor()

#lock za multithreading se more nucat vedno kadar se karkoli pošilja na bazo al pa bere iz baze
#sam das with lock: pred kodo, ki rabi lock
lock = threading.Lock()

def reset_database():
	cur.execute("DELETE FROM crawldb.image *")
	cur.execute("DELETE FROM crawldb.page_data *")
	cur.execute("DELETE FROM crawldb.link *")
	cur.execute("DELETE FROM crawldb.page *")
	cur.execute("DELETE FROM crawldb.site *")
	
	cur.execute("ALTER SEQUENCE	crawldb.image_id_seq RESTART WITH 1;")
	cur.execute("ALTER SEQUENCE	crawldb.page_data_id_seq RESTART WITH 1;")
	cur.execute("ALTER SEQUENCE	crawldb.page_id_seq RESTART WITH 1;")
	cur.execute("ALTER SEQUENCE	crawldb.site_id_seq RESTART WITH 1;")

"""
	Get hash for html
"""
def html_md5(html):
	hasher = hashlib.md5()
	a = hasher.update(html.encode('utf-8'))
	return str(hasher.hexdigest())

"""
	Insert images to db
"""
def insert_imgs_to_db(list_of_images):
	with lock:
		try:
			for image in list_of_images:
				cur.execute("INSERT INTO crawldb.image (page_id, filename, content_type, accessed_time) VALUES (%s, %s, %s, NOW());", (image['page_id'], image['filename'], image['content_type']))
		except Exception as e:
			print(e)
"""
	Insert page_data to db and return id
"""
def insert_page_data_to_db(page_data_list):
	with lock:
		try:
			for page_data in page_data_list:
				cur.execute('INSERT INTO crawldb.page_data (page_id, data_type_code) VALUES (%s, %s) RETURNING id;', (page_data['page_id'], page_data['data_type_code']))
		except Exception as e:
			print(e)

"""
	Is there a duplicate of page
"""
def is_duplicate_page(url, html):
	
	with lock:
		try:
			cur.execute("SELECT * FROM crawldb.page WHERE url = %s", (url,))
			rows = cur.fetchall()
			if len(rows) > 1:
				return True
			else:
				cur.execute("SELECT * FROM crawldb.page WHERE html_content_md5 = %s", (html_md5(html),))
				rows = cur.fetchall()
				if rows:
					return True
			return False

		except Exception as e:
			print(e)
			return False

"""
	Get URLs from site map for domain
"""
def load_sitemap_urls_to_pages(domain):
	
	try:
		print("Adding sitemap to frontier from domain: " + domain)
		cur.execute("SELECT id, domain, sitemap_content FROM crawldb.site WHERE domain = %s", (domain,))
		rows = cur.fetchall()
		site_id = rows[0][0]

		parsed_sitemap = BeautifulSoup(rows[0][2], features="html.parser")
		sitemapindex = parsed_sitemap.find("sitemapindex")
		urlset = parsed_sitemap.find("urlset")

		if sitemapindex:
			for loc in parsed_sitemap.find_all("loc"):
				request = urllib.request.Request(loc.text, headers={'User-Agent': user_agent})
				with urllib.request.urlopen(request) as response:
					loc_data = response.read().decode("utf-8")
					parsed_sitemap_loc = BeautifulSoup(loc_data, features="html.parser")
					urls_loc = parsed_sitemap_loc.find_all("loc")
					for url in urls_loc:
						#with lock:
						cur.execute("SELECT * FROM crawldb.page WHERE url = %s", (url.text,))
						rows = cur.fetchall()
						if not rows:
							cur.execute("INSERT INTO crawldb.page(site_id, url) VALUES (%s, %s);", (site_id, url.text))
							frontier.add_page(url.text, domain)
							
							
		if urlset:
			for url in parsed_sitemap.find_all("url"):
				#with lock:
				cur.execute("SELECT * FROM crawldb.page WHERE url = %s", (url.text,))
				rows = cur.fetchall()
				if not rows:
					cur.execute("INSERT INTO crawldb.page(site_id, url) VALUES (%s, %s);", (site_id, url.text))
					frontier.add_page(url.text, domain)

	except Exception as e:
		print(e)

"""
	Is url allowed to be crawled?
"""
def can_crawl(domain, url):
	with lock:
		try:
			cur.execute("SELECT domain, robots_content FROM crawldb.site WHERE domain = %s", (domain,))
			rows = cur.fetchall()
			rp = urllib.robotparser.RobotFileParser()
			rp.parse(rows[0][1])
			return  rp.can_fetch(user_agent, url)
		except Exception as e:
			return True

"""
	Store site data in database in table crawldb.site, if it doesn't exist yet, and return its id 
"""
def get_site_id(domain):
	with lock:
		try:
			cur.execute("SELECT * FROM crawldb.site WHERE domain = %s", (domain,))
			rows = cur.fetchall()
			if rows:
				site_id = rows[0][0]
			if not rows:
				robots_sitemap_data = get_robots_sitemap_data(domain)
				cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s) RETURNING id", (domain, robots_sitemap_data[0], robots_sitemap_data[1]))
				site_id = cur.fetchone()[0]
				frontier.add_site(domain)
				#load_sitemap_urls_to_pages(domain)
			return site_id
		except Exception as e:
			print(e)

""" 
	Store page data in database in table crawldb.page, and return its id
"""
def put_page_in_db(page_object):
	site_id = page_object['site_id']
	page_type_code = page_object['page_type_code']
	url = page_object['url']
	html_content = page_object['html_content']
	http_status_code = page_object['http_status_code']
	html_content_md5 = page_object['html_content_md5']
	#accessed_time = page_object['accessed_time']
	with lock:
		try:
			cur.execute('SELECT * FROM crawldb.page WHERE url = %s', (url,))
			rows = cur.fetchall()
			if rows:
				page_id = rows[0][0]
			if not rows:
				#cur.execute('INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time) VALUES (%s, %s, %s, %s, %s) RETURNING id', (site_id, page_type_code, url, html_content, http_status_code, accessed_time))
				cur.execute('INSERT INTO crawldb.page (site_id, page_type_code, url, html_content, http_status_code, accessed_time, html_content_md5) VALUES (%s, %s, %s, %s, %s, NOW(), %s) RETURNING id', (site_id, page_type_code, url, html_content, http_status_code, html_content_md5))
				page_id = cur.fetchone()[0]
			return page_id
		except Exception as e:
			print(e)

"""
	Get page id
"""
def get_page_id(url):
	with lock:
		try:
			cur.execute("SELECT * FROM crawldb.page WHERE url = %s", (url,))
			rows = cur.fetchall()
			if rows:
				page_id = rows[0][0]
			return page_id
		except Exception as e:
			print(e)	

'''
	Creates empty page table in database. page_object must have parameters site_id and url. 
'''
def put_empty_page_in_db(page_object):
	site_id = page_object['site_id']
	url = page_object['url']
	#with lock: # TODO a gre with lock pred tem zgori al je tko ok, da je po tem?
	with lock:
		try:
			cur.execute('INSERT INTO crawldb.page (site_id, url) VALUES (%s, %s)', (site_id, url))
		except Exception as e:
			print(e)

"""
	Update page entry
"""
def update_page_entry(page_id, page_object):
	site_id = page_object['site_id']
	page_type_code = page_object['page_type_code']
	url = page_object['url']
	html_content = page_object['html_content']
	http_status_code = page_object['http_status_code']
	html_content_md5 = page_object['html_content_md5']
	accessed_time = page_object['accessed_time']
	with lock:
		try:
			#cur.execute('UPDATE crawldb.page SET (site_id = %s, page_type_code = %s, url = %s, html_content = %s, http_status_code = %s, html_content_md5 = %s, accessed_time = %s) WHERE (page_id = %s)', (site_id, page_type_code, url, html_content, http_status_code, html_content_md5, accessed_time, page_id))
			cur.execute('UPDATE crawldb.page SET site_id = %s WHERE id = %s', (site_id, page_id))
			cur.execute('UPDATE crawldb.page SET page_type_code = %s WHERE id = %s', (page_type_code, page_id))
			cur.execute('UPDATE crawldb.page SET url = %s WHERE id = %s', (url, page_id))
			cur.execute('UPDATE crawldb.page SET html_content = %s WHERE id = %s', (html_content, page_id))
			cur.execute('UPDATE crawldb.page SET http_status_code = %s WHERE id = %s', (http_status_code, page_id))
			cur.execute('UPDATE crawldb.page SET html_content_md5 = %s WHERE id = %s', (html_content_md5, page_id))
			cur.execute('UPDATE crawldb.page SET accessed_time = %s WHERE id = %s', (accessed_time, page_id))
		except Exception as e:
			print(e)
"""
	Insert link to db
"""
def put_link_in_db(link_object):
	from_page = link_object['from']
	to_page = link_object['to']
	with lock:
		try:
			cur.execute('INSERT INTO crawldb.link (from_page, to_page) VALUES (%s, %s)', (from_page, to_page))
		except Exception as e:
			print(e)
"""
	Get robots and sitemap data as tuple (robots_data, sitemap_data) if exists
"""
def get_robots_sitemap_data(domain):

	try:
		url = "http://{}/robots.txt".format(domain)
		rp = urllib.robotparser.RobotFileParser(url=url)
		rp.read()
		request = urllib.request.Request(url, headers={'User-Agent': user_agent})
		with urllib.request.urlopen(request) as response:
			robots_data = response.read().decode("utf-8")
	except Exception as e:
		robots_data = None

	try:
		s = rp.site_maps()
		if s:
			s = s[0]
			request = urllib.request.Request(s, headers={'User-Agent': user_agent})

			with urllib.request.urlopen(request) as response:
				sitemap_data = response.read().decode("utf-8")
		else:
			sitemap_data = None
	except Exception as e:
		sitemap_data = None

	return (robots_data, sitemap_data)

"""
	Detect images and next links
"""
def get_images_links(page_url, worker_id):
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('headless')
	driver = webdriver.Chrome(chrome_options = chrome_options)
	try:
		driver.get(page_url)
	except Exception as e:
		print(f"{Fore.RED} Exception za driver! {e} {Style.RESET_ALL}")
	#domain = urlparse(page_url).netloc # Če boš tole spodi s subdomainom odkomentiral, zamenjaj v tej vrstici domain z t
	#domain  = '.'.join(t.split('.')[-2:]) # Če želimo imeti samo main domain, ne pa tudi subdomain, npr. za www.e-vem.gov.si kot domain upoštevamo samo gov.si
	ext = extract(page_url) # prints abc, hostname, com
	domain = '.'.join(ext)
	print(worker_id + " Page url: ", page_url)
	print(worker_id + " Domain: ", domain)

	id_trenutnega_sitea = get_site_id(domain)
	id_trenutnega_pagea = get_page_id(page_url)
	page_content = driver.page_source
	page_cnt = BeautifulSoup(page_content, 'html.parser')
	# Create page object to be inserted to db table page
	page_type = get_content_type(page_url)#['page_type_code']
	page = {}
	if (page_type['page_type_code'] == 'html'):
		page = {
			'site_id' : id_trenutnega_sitea,
			'page_type_code' : 'html',
			'url' : page_url,
			'html_content' : page_cnt.prettify(),
			'http_status_code' : page_type['status_code'],
			'html_content_md5' : html_md5(page_cnt),
			'accessed_time' : datetime.datetime.now() # .strftime("%d. %m. %Y %H:%M:%S.%f") # TODO pustim brez formatiranja ali s formatiranjem?
		}
	elif (page_type['page_type_code'] != 'html'):
		page = {
			'site_id' : id_trenutnega_sitea,
			'page_type_code' : 'binary',
			'url' : page_url,
			'html_content' : None,
			'http_status_code' : page_type['status_code'],
			'html_content_md5' : None,
			'accessed_time' : datetime.datetime.now() #.strftime("%d. %m. %Y %H:%M:%S.%f") # TODO pustim brez formatiranja ali s formatiranjem?
		}
	if (is_duplicate_page(page_url, page_cnt) == True):
		page = {
			'site_id' : id_trenutnega_sitea,
			'page_type_code' : 'duplicate',
			'url' : page_url,
			'html_content' : '',
			'http_status_code' : page_type['status_code'],
			'html_content_md5' : html_md5(page_cnt),
			'accessed_time' : datetime.datetime.now() #.strftime("%d. %m. %Y %H:%M:%S.%f") # TODO pustim brez formatiranja ali s formatiranjem?
		}
		update_page_entry(id_trenutnega_pagea, page)
		return
	print("PAGE")
	print(page['page_type_code'], page['url'], page['http_status_code'], page['accessed_time'])

	images = []
	links = []

	imgs = page_cnt.findAll('img')
	for img in imgs:
		src = img['src']
		if src.startswith('data:image'):
			continue
		images.append(src)
	hyperlinks = page_cnt.findAll('a')
	for hyperlink in hyperlinks:
		try:
			href = hyperlink['href']
		except Exception as e:
			print("There is no href in this a.", e)
			continue
		if href == '':
			print("HREF is None, empty")
			continue
		if href.startswith('http') == False:
			if ('mailto:' in href) or  ('tel:' in href) or ('javascript:' in href) or (href[0] == '#') or (href == '/'):
				continue
			if href.startswith('www'):
				href = 'http://{}'.format(page_url).strip()
			if href.startswith('/'):
				href = '{}{}'.format(page_url, href).strip()
		links.append(href)
	# Links hidden in scripts
	scripts = page_cnt.findAll('script')
	for script in scripts:
		links_from_script = re.findall(r'(http://|https://)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?',
							   script.text)
		for link in links_from_script:
			link = ''.join(link)
			if link.startswith('http') == False:
				if ('mailto:' in link) or  ('tel:' in link) or ('javascript:' in link) or (link[0] == '#') or (link == '/'):
					continue
				if link.startswith('www'):
					link = 'http://{}'.format(page_url).strip()
				if link.startswith('/'):
					link = '{}{}'.format(page_url, link).strip()
			links.append(link)
	link_to_db = []
	page_data = []
	#link_to_frontier = []
	if len(links) > 0:
		myset = set(links) # remove duplicates
		links = list(myset)
		for i in links:
			ext_1 = extract(i) # prints abc, hostname, com
			domain_found_link = '.'.join(ext_1)
			if (allowed_domain in domain_found_link) and (page_url+'/' != i):
				pg_tp = get_content_type(i)
				if (pg_tp['page_type_code'] != 'html') and (pg_tp['page_type_code'] in type_codes.values()):
					page_data.append({
						'page_id' : id_trenutnega_pagea,
						'data_type_code' : pg_tp['page_type_code'],
						'data' : None
					})
				# if found link is not yet in table.page, add it to frontier (frontier.py, add_page()).
				if (is_link_in_table_page(i) == False):

					if (can_crawl(domain_found_link, i)):
						id_site = get_site_id(domain_found_link) # Če ni notr, lahk ful cajta traja.
						id_page = put_empty_page_in_db({'site_id':id_site, 'url':i})
						frontier.add_page(i, domain_found_link)
				link_to_db.append({ # TODO poberi id od trenutne strani in 'to' strani
					'from': id_trenutnega_pagea, # Tuki je id_trenutnega_pagea
					'to': get_page_id(i) # Kako pa dobit tole? Še ne obstaja v bazi, ne?
				})

	image_to_db = []
	if len(images) > 0:
		for i in images:
			filename = i.split('/')[-1].split('.')[0]
			image_to_db.append({
				'page_id' : id_trenutnega_pagea,
				'filename' : filename,
				'content_type' : 'img',
				'data' : None,
				'accessed_time' : datetime.datetime.now() #.strftime("%d. %m. %Y %H:%M:%S.%f") # TODO pustim brez formatiranja ali s formatiranjem?
			})

	print("PAGE_DATA:")
	print(page_data)
	driver.close()
	driver.quit()
	#UPDATE trenutni page (že more obstajat, ga samo updateaš - use razn url-ja pa id-ja) page putam notr.
	update_page_entry(id_trenutnega_pagea, page)
	#INSERT link_to_db v tabelo link
	for li in link_to_db:
		put_link_in_db(li)
	#INSERT image_to_db v tabelo image
	insert_imgs_to_db(image_to_db)
	#INSERT page_data v tabelo page_data
	insert_page_data_to_db(page_data)

"""
	Get page content type
"""
def get_content_type(url_link):
	res = ''
	status_code = 0
	page_type = {'page': url_link, 'status_code': status_code, 'page_type_code': 'other'}
	try:
		res = requests.get(url_link)
	except Exception as e:
		print(f"{Fore.RED} Requests error. (get_content_type)\n {e} {Style.RESET_ALL}")
	if res != '':
		try:
			status_code = res.status_code
			content_type = res.headers['Content-Type']
			if ';' in content_type:
				content_type = content_type.split(';')[0]
		except Exception as e:
			print(f"{Fore.RED} Content type error. (get_content_type)\n {e} {Style.RESET_ALL}")

		# doc, docx, pdf, ppt, pptx
		if content_type in type_codes:
			page_type = {'page': url_link, 'status_code': status_code, 'page_type_code': type_codes[content_type]}
		else:
			page_type = {'page': url_link, 'status_code': status_code, 'page_type_code': 'other'}
	return page_type

"""
	Check if link is already in db table page. Returns True if it is. Returns False if it is not. Used to add/not add found link to frontier.
"""
def is_link_in_table_page(url):
	with lock:
		cur.execute("SELECT * FROM crawldb.page WHERE url = %s", (url,))
		try:
			rows = cur.fetchall()
			if rows:
				print("URL ", url, " is already in.")
				return True
			return False
		except Exception as e:
			return False


def worker_loop(id):
	worker_id = threading.local
	worker_id = str(id)
	cur = threading.local
	cur = conn.cursor()
	print(worker_id + " Starting worker loop. ")
	while(True):
		if(frontier.has_page()):
			page = frontier.get_page()
			print(f"{Fore.GREEN}{worker_id} Working on: {page.url}{Style.RESET_ALL}")
			try:
				get_images_links(page.url, worker_id)
			except Exception as e:
				track = traceback.format_exc()
				print(f"{Fore.RED}{track}{Style.RESET_ALL}")


			print(f"{Fore.GREEN}{worker_id} Finished working on: {page.url}{Style.RESET_ALL}")
		else:
			print(f"{Fore.RED}{worker_id} Frontier has no more pages, waiting for 30 seconds. {Style.RESET_ALL}")
			time.sleep(30)
			if(not frontier.has_page()):
				break

	
	print(f"{Fore.RED}{worker_id} No more pages in frontier, shutting worker down. {Style.RESET_ALL}")


# base logika - najprej reset baze, pol dodamo domene in zacetne page na teh domenah v bazo, pol pa nardimo threadpool
reset_database()

for i in range(1, 4):
	print(i)
	site_id = get_site_id(domains[i]) # ustvarimo nov site za trenutno domeno

	# mormo se dodat frontpage te domene v tabelo page in frontier
	page_object = {}
	page_object['site_id'] = site_id
	page_object['url'] = urls[i]
	put_empty_page_in_db(page_object)
	frontier.add_site(domains[i])
	frontier.add_page(urls[i], domains[i])

# za single thread nej se spodnjo vrstico odkomentira, za multithread pa spodnji block
#worker_loop(0)

args = sys.argv
if len(args) >= 1:
	worker_count = int(args[1])
else:
	worker_count = 16

with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
	print(f"\n ... executing workers ...\n")
	for i in range(worker_count):
		executor.submit(worker_loop, i)
		time.sleep(10)



