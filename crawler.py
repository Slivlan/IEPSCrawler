import urllib
from selenium import webdriver
from urllib import robotparser
import psycopg2
import threading
import concurrent.futures
from bs4 import BeautifulSoup
import re

domains = ["gov.si", "evem.gov.si", "e-uprava.gov.si", "e-prostor.gov.si"]
request_rate_sec = 5
user_agent = "fri-ieps-nasagrupa"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
driver = webdriver.Chrome(chrome_options = chrome_options)

"""
	Store site data in database in table crawldb.site
"""
def put_site_in_db(domain):
    try:
        robots_sitemap_data = get_robots_sitemap_data(domain)

        conn = psycopg2.connect("host=167.71.67.220 dbname=crawler user=crawler password=tojegeslo")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT domain FROM crawldb.site WHERE domain = %s", (domain,))
        rows = cur.fetchall()
        if not rows:
            cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s, %s, %s)", (domain, robots_sitemap_data[0], robots_sitemap_data[1]))

    except Exception as e:
        print(e)

    finally:
        cur.close()
        conn.close()

"""
	Get robots and sitemap data as tuple (robots_data, sitemap_data) if exists
"""
def get_robots_sitemap_data(domain):
    url = "http://{}/robots.txt".format(domain)
    rp = urllib.robotparser.RobotFileParser(url=url)
    rp.read()

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
		#print("SRC2: ", src2)
		if src.startswith('data:image'):
			#print("OH YES.")
			continue
		images.append(src)
	hyperlinks = page.findAll('a')
	#print("HYPERLINKS: ", hyperlinks)
	#print("HYPERLINKS len: ", len(hyperlinks))
	for hyperlink in hyperlinks:
		print("HYPERLINK", hyperlink)
		href = hyperlink['href']
		#print("HREF: ", href)
		links.append(href)
	# Links hidden in scripts
	scripts = page.findAll('script')
	for script in scripts:
		print("SCRIPT: ")
		print(script.text)
		links_from_script = re.findall(r'(http://|https://)([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?',
                               script.text)
		for link in links_from_script:
			links.append(link)
	print("IMAGES: ")
	print(images)
	print("LINKS: ")
	print(links)
	print("-----KONECKONECKONEC-------")
	
	driver.close()
	driver.quit()

lock = threading.Lock()

# with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
#     print(f"\n ... executing workers ...\n")
#     for domain in domains:
#         executor.submit(put_site_in_db, domain)
#         executor.submit(get_images_links, 'https://'+domain)
for domain in domains:
        #executor.submit(put_site_in_db, domain)
        #executor.submit(get_images_links, 'https://'+domain)
        try:
        	get_images_links('https://'+domain)
        except Exception as e:
        	print("ERROR: ", e)