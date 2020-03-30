import urllib
from selenium import webdriver
from urllib import robotparser
import psycopg2
import threading
import concurrent.futures
from bs4 import BeautifulSoup

domains = ["gov.si", "evem.gov.si", "e-uprava.gov.si", "e-prostor.gov.si"]
request_rate_sec = 5
user_agent = "fri-ieps-nasagrupa"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('headless')
driver = webdriver.Chrome(chrome_options = chrome_options)

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
def get_images_links(driver, domain):
	driver.get(domain)
	print("Domain: ", domain)
	#print(driver.page_source)
	page_content = driver.page_source
	# Html_file= open("tmp_{}".format(domain),"w")
	# Html_file.write(page_content)
	# Html_file.close()
	images = []
	links = []
	page = BeautifulSoup(page_content, 'html.parser')
	imgs = page.findAll('img')
	for img in imgs:
		src = img.get_attribute('src')
		images.append(src)
	hyperlinks = page.findAll('a')
	for hyperlink in hyperlinks:
		href = hyperlink.get_attribute('href')
		links.append(href)
	print("------------")
	driver.quit()

lock = threading.Lock()

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    print(f"\n ... executing workers ...\n")
    for domain in domains:
        executor.submit(put_site_in_db, domain)
        executor.submit(get_images_links, driver, 'https://'+domain)
    # for domain in domains:
    #     put_site_in_db(domain)
    #     get_images_links(driver, 'https://' + domain)