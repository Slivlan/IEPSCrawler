import urllib
from selenium import webdriver
from urllib import robotparser
import psycopg2
import threading
import concurrent.futures
from bs4 import BeautifulSoup
import re

domains = ["gov.si", "evem.gov.si", "e-uprava.gov.si", "e-prostor.gov.si"]
allowed_domain = '.gov.si'
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
	cur.execute("DELETE FROM crawldb.site *")
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
            cur.execute("SELECT domain, sitemap_content FROM crawldb.site WHERE domain = %s", (domain,))
            rows = cur.fetchall()

            parsed_sitemap = BeautifulSoup(rows[0][1])
            sitemapindex = parsed_sitemap.find("sitemapindex")
            urlset = parsed_sitemap.find("urlset")


            if sitemapindex:
                locs = [loc.text for loc in parsed_sitemap.find_all("loc")]
                urls.extend(locs)

            if urlset:




            return urls
        except Exception as e:
            return None

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
def get_images_links(domain):
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('headless')
	driver = webdriver.Chrome(chrome_options = chrome_options)
	driver.get(domain)
	print("Domain: ", domain)
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
				href = '{}{}'.format(domain, href).strip()
		#href = '{}{}'.format(domain, href).strip()
		links.append(href)
	# Links hidden in scripts
	scripts = page.findAll('script')
	for script in scripts:
		print("SCRIPT: ")
		print(script.text)
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
					link = '{}{}'.format(domain, link).strip()
			links.append(link)
	link_to_frontier = []
	#links_images = images + links # doesn't remove duplicate links
	links_images = list(set(images + links)) # removes duplicate links
	for i in links_images:
		if (allowed_domain in i) and (domain+'/' != i):
			link_to_frontier.append({
				'from': domain+'/',
				'to': i
			})
	print("link_to_frontier: ")
	print(link_to_frontier)
	print("len(link_link): ", len(link_to_frontier))
	driver.close()
	driver.quit()
	print("-----KONECKONECKONEC-------")
	return link_to_frontier

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    print(f"\n ... executing workers ...\n")
    #reset_database()
    for domain in domains:
        get_urls_from_sitemap(domain)
        #executor.submit(put_site_in_db, domain)
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