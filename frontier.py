import time
import queue

class Frontier:
    
    def __init__(self):
        self.sites = queue.SimpleQueue()
        self.sitesDictionary = {}

    '''
    Doda domain v dictionary sites. Ce ze obstaja, vrne false, drugace vrne true.
    '''
    def add_site(self, domain):
        if(domain in self.sitesDictionary):
            return False

        s = Site(domain)
        self.sites.put(s)
        self.sitesDictionary[domain] = s

        return True


    '''
    Doda page z danim urljem in domeno v dictionary pagov
    Domain (torej site) more bit obstojec, drgac returna false, sicer pa true
    Also, ni nobenga checkinga, da page ze obstaja itd. Naceloma bi mogu exception vrzt, ce hoces dodat neki na key, ki ze obstaja. 
    '''
    def add_page(self, url, domain):
        s = self.sitesDictionary[domain]
        if (s == None):
            return False
        p = Page(url, self.sitesDictionary[domain])
        self.sitesDictionary[domain].add_page(p)
        return True


    '''
    Vrne url naslova, ki je naslednji na listi za pogledat. Ce ni nobenga sita, za katerga nam ni treba cakat, se thread tuki ustavi, dokler ne potece dovolj casa
    '''
    def get_page(self):
        s = self.sites.get()
        s.halt_till_allowed(5)
        s.accessed()
        self.sites.put(s)
        return s.pages.get()

class Site:
    
    #domain #string
    #last_accessed #struct_time al whatever - v sekundah
    #pages = queue.Queue() #queue page classov

    def __init__(self, dom):
        self.domain = dom
        self.pages = queue.Queue()
        self.last_accessed = time.time()

    def accessed(self):
        self.last_accessed = time.time()

    def next_allowed_access(self, seconds):
        return (time.time() - self.last_accessed) > seconds

    def halt_till_allowed(self, seconds):
        waitTime = self.last_accessed - time.time() + seconds
        if(waitTime > 0):
            print("Sleeping for: " + str(waitTime))
            time.sleep(waitTime)
        

    def add_page(self, p):
        self.pages.put(p)

class Page:
    #site #pointer na Site object
    #url #string

    def __init__(self, u, s):
        self.url = u
        self.site = s

'''
f = Frontier()
f.add_site("www.site.si")
f.add_site("www.site2.si")
f.add_site("3")
f.add_page("3/1", "3")
f.add_page("www.site.si/123", "www.site.si")
f.add_page("www.site.si/456", "www.site.si")
f.add_page("www.site2.si/123", "www.site2.si")
f.add_page("www.site2.si/456", "www.site2.si")
page = f.get_page()
print(page.url)
page = f.get_page()
print(page.url)
page = f.get_page()
print(page.url)
page = f.get_page()
print(page.url)
'''
