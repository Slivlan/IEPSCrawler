import urllib
from selenium import webdriver
from urllib import robotparser
import psycopg2
import threading
import concurrent.futures
from bs4 import BeautifulSoup
import re
import requests
from operator import itemgetter
import datetime 

domains = ["gov.si", "evem.gov.si", "e-uprava.gov.si", "e-prostor.gov.si"]
#domains = ['www.e-prostor.gov.si/fileadmin/DPKS/Transformacija_v_novi_KS/Aplikacije/3tra.zip']
allowed_domain = '.gov.si'
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
	#cur.execute("DELETE FROM crawldb.site *")
	cur.execute("DELETE FROM crawldb.page *")
	cur.execute("DELETE FROM crawldb.image *")
	cur.execute("DELETE FROM crawldb.page_data *")
	cur.execute("DELETE FROM crawldb.data_type *")
	cur.execute("DELETE FROM crawldb.page_type *")
	cur.execute("DELETE FROM crawldb.link *")
	cur.execute("DELETE FROM Frontier *")
	cur.execute("INSERT INTO Frontier (next_page_id) VALUES (1)")

def get_next_page_id():
	with lock:
		cur.execute("SELECT next_page_id FROM Frontier")
		rows = cur.fetchone()
		return rows[0]

def increment_next_page_id():
	with lock:
		cur.execute("UPDATE Frontier SET next_page_id = next_page_id + 1")

#test
#print(get_next_page_id())
#increment_next_page_id()
#print(get_next_page_id())
#exit()

"""
	Get URLs from site map for domain
"""
def get_urls_from_sitemap(domain):
	urls = []
	with lock:
		try:
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
						urls.extend([url.text for url in urls_loc])

			if urlset:
				sitemap_urls = [url.text for url in parsed_sitemap.find_all("url")]
				urls.extend(sitemap_urls)

			for url in urls:

				#temporeray ker še ni funkcije za duplikate
				cur.execute("SELECT * FROM crawldb.page WHERE url = %s", (url,))
				rows = cur.fetchall()
				###
				if not rows:
					cur.execute("INSERT INTO crawldb.page(site_id, url) VALUES (%s, %s);", (site_id, url))

			#return urls

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
	Store site data in database in table crawldb.site
"""
def put_site_in_db(domain):
	with lock:
		try:
			robots_sitemap_data = get_robots_sitemap_data(domain)
			cur.execute("SELECT domain FROM crawldb.site WHERE domain = %s", (domain,))
			rows = cur.fetchall()
			if not rows:
				cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s)", (domain, robots_sitemap_data[0], robots_sitemap_data[1]))

		except Exception as e:
			print(e)

"""
	Get robots and sitemap data as tuple (robots_data, sitemap_data) if exists
"""
def get_robots_sitemap_data(domain):
	url = "http://{}/robots.txt".format(domain)
	rp = urllib.robotparser.RobotFileParser(url=url)
	rp.read()

	# crawl_delay_sec_t = rp.crawl_delay(user_agent)
	# if crawl_delay_sec_t:
	#     crawl_delay_sec = crawl_delay_sec_t

	try:
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
def get_images_links(page_url): # TODO dodaj with lock. Ne znam točno, upraš za pomoč (je treba samo na začetku te funkcije? ali tudi na začetku get_content_type?)
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('headless')
	driver = webdriver.Chrome(chrome_options = chrome_options)
	driver.get(page_url)
	print("Domain: ", page_url)
	page_content = driver.page_source
	images = []
	links = []
	page = BeautifulSoup(page_content, 'html.parser')
	imgs = page.findAll('img')
	#print("IMGS len: ", len(imgs))
	for img in imgs:
		#print("IMG ", img)
		src = img['src']
		#print("SRC: ", src)
		if src.startswith('data:image'):
			#print("OH YES.")
			continue
		images.append(src)
	hyperlinks = page.findAll('a')
	#print("HYPERLINKS: ", hyperlinks)
	#print("HYPERLINKS len: ", len(hyperlinks))
	for hyperlink in hyperlinks:
		#print("HYPERLINK", hyperlink)
		try:
			href = hyperlink['href']
		except Exception as e:
			print("There is no href in this a.", e)
			continue
		#print("HREF: ", href)
		if href == '':
			print("HREF is None, empty")
			continue
		if href.startswith('http') == False:
			if ('mailto:' in href) or  ('tel:' in href) or ('javascript:' in href) or (href[0] == '#') or (href == '/'):
				#print("FOUND inappropriate: ", href)
				continue
			if href.startswith('www'):
				href = 'http://{}'.format(url).strip()
			if href.startswith('/'):
				href = '{}{}'.format(page_url, href).strip()
		links.append(href)
	# Links hidden in scripts
	scripts = page.findAll('script')
	for script in scripts:
		links_from_script = re.findall(r'(http://|https://)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?',
							   script.text)
		for link in links_from_script:
			link = ''.join(link)
			if link.startswith('http') == False:
				if ('mailto:' in link) or  ('tel:' in link) or ('javascript:' in link) or (link[0] == '#') or (link == '/'):
					#print("FOUND inappropriate: ", link)
					continue
				if link.startswith('www'):
					link = 'http://{}'.format(url).strip()
				if link.startswith('/'):
					link = '{}{}'.format(page_url, link).strip()
			links.append(link)
	link_to_db = []
	page_data = []
	if len(links) > 0:
		myset = set(links) # remove duplicates
		links = list(myset)
		for i in links:
			if (allowed_domain in i) and (page_url+'/' != i):
				link_to_db.append({
					'from': page_url+'/',
					'to': i
				})
				pg_tp = get_content_type(i)
				print("PG_TP")
				print(pg_tp)
				if (pg_tp['page_type_code'] != 'html') and (pg_tp['page_type_code'] in type_codes.values()):
					page_data.append({
						'data_type_code' : pg_tp['page_type_code'],
						'data' : None
					})
				# if found link is not yet in table.page, add it to frontier (frontier.py, add_page()). # TODO function to connect to db and check if link (url) is already in table.page
	print("link_to_db: ")
	print(link_to_db)
	print("len(link_link): ", len(link_to_db))
	image_to_db = []
	if len(images) > 0:
		for i in images:
			filename = i.split('/')[-1].split('.')[0]
			image_to_db.append({
				'filename' : filename,
				'content_type' : 'img',
				'data' : None,
				'accessed_time' : datetime.datetime.now().strftime("%d. %m. %Y %H:%M:%S.%f") # TODO pustim brez formatiranja ali s formatiranjem?
			})
	#print("image_to_db: ")
	#print(image_to_db)
	#print("len(image_to_db): ", len(image_to_db))
	page_type = get_content_type(page_url)#['page_type_code']
	page = {}
	if (page_type['page_type_code'] == 'html'): # TODO inside of this if has to be check if it is html or binary or duplicate (create function is_duplicate?)
		page = {
			'page_type_code' : 'html', # TODO change later to html/binary/duplicate
			'url' : page_url,
			'html_content' : page_content,
			'http_status_code' : page_type['status_code'],
			'accessed_time' : datetime.datetime.now().strftime("%d. %m. %Y %H:%M:%S.%f") # TODO pustim brez formatiranja ali s formatiranjem?
		}
		# TODO tle je vse neki narobe. zgori: page = link_url, to kar je trenutno. page_type_code = get_content_type(page_url)..
		# page_data pa for links (vsi "to" linki, ki si jih zgori naštel), vzameš content type, če niso html (= other, pptx, docx,...) grejo v page_data.append({kar je treba})
	elif (page_type['page_type_code'] != 'html'):
		page = {
			'page_type_code' : 'binary', # TODO change later to html/binary/duplicate
			'url' : page_url,
			'html_content' : page_content,
			'http_status_code' : page_type['status_code'],
			'accessed_time' : datetime.datetime.now().strftime("%d. %m. %Y %H:%M:%S.%f") # TODO pustim brez formatiranja ali s formatiranjem?
		}
	print("PAGE")
	print(page['page_type_code'], page['url'], page['http_status_code'], page['accessed_time'])
	print("PAGE_DATA:")
	print(page_data)
	driver.close()
	driver.quit()
	print("-----KONECKONECKONEC-------")
	return (link_to_db, image_to_db, page, page_data)

"""
	Get page content type
"""
def get_content_type(url_link):
	res = ''
	status_code = 0
	page_type = {'page': url_link, 'status_code': status_code, 'page_type_code': 'other'}
	try:
		res = requests.get(url_link)
		#print("res: ", res)
	except Exception as e:
		print("Requests error: ", e)
	if res != '':
		try:
			status_code = res.status_code
			content_type = res.headers['Content-Type']
			if ';' in content_type:
				content_type = content_type.split(';')[0]
			#print("CONTENT TYPE: ", content_type)
		except Exception as e:
			print("Content type error: ", e)

		# doc, docx, pdf, ppt, pptx 
		if content_type in type_codes:
			page_type = {'page': url_link, 'status_code': status_code, 'page_type_code': type_codes[content_type]}
		else:
			page_type = {'page': url_link, 'status_code': status_code, 'page_type_code': 'other'}
	#print(page_type)
	return page_type
lock = threading.Lock() # TODO tole mamo zdj na dveh mestih v kodi, narobe vrjetno?

# with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
#     print(f"\n ... executing workers ...\n")
#     reset_database()
#     for domain in domains:
#         executor.submit(put_site_in_db, domain)
        #put_site_in_db(domain)
        #can_crawl(domain, "https://www.gov.si/podrocja/druzina-otroci-in-zakonska-zveza/")
        #executor.submit(get_images_links, 'https://'+domain)
for domain in domains:
        #executor.submit(put_site_in_db, domain)
        #executor.submit(get_images_links, 'https://'+domain)
        try:
        	get_images_links('https://'+domain)
        except Exception as e:
        	print("ERROR: ", e)
