import requests
import sys
from lxml import html
from lxml import etree
import threading
original_domain = ""
max_depth = 0
lock = threading.Lock()
threads = []


#The class for the scanner thread
class Scanner (threading.Thread):
    def __init__(self, depth, url):
        threading.Thread.__init__(self)
        self.depth = depth
        self.url = url

    #The functionality of the thread
    def run(self):
        global lock
        global threads
        #Acquires the lock so it can access scan_website function which accesses a file
        lock.acquire()
        scan_website(self.url, self.depth)
        lock.release()
        #Runs all new threads added to the thread list and removes them
        for t in threads:
            threads.remove(t)
            t.start()
            t.join()


#The function for scanning the website
def scan_website(url, depth):
    global max_depth
    global threads
    global original_domain
    #Ensures that a proper schema for the request is provided
    if not url[0:8] == "https://":
        url = "https://" + url
    try:
        #Scans the provided url, parses the request into html, then pulls out all the href fields
        scan = requests.get(url)
        webpage = html.fromstring(scan.content)
        links = webpage.xpath('//a/@href')
        #Takes the 2 conditions for links, full links starting with http or subdirectories starting with /
        #For http links it confirms that the original domain is the domain in the link
        #If it doesn't match, it won't be added to the file
        #If it does match, it is checked for a file extension
        #If it has a file extension or has too high depth it will be added to the file but not added as a thread
        #If there is no file extension and low enough depth it will be added to the file and added as a thread with increased depth
        for link in links:
            if "http" in link:
                if original_domain == link[0:19]:
                    add_to_file(link)
                    if not link[-4] == '.' and depth < max_depth:
                        thread = Scanner(depth + 1, link)
                        threads.append(thread)
        #For subdirectories it is appended to the end of the original domain and added to the file
        #If there is no file extension and it is below max depth it is added as a thread with increased depth and eventually run
        for link in links:
            if link[0:1] == "/":
                new_link = "https://" + original_domain + link
                add_to_file(new_link)
                if not new_link[-4] == '.' and depth < max_depth:
                    thread = Scanner(depth + 1, new_link)
                    threads.append(thread)
    #In some cases a ParseError is thrown. The except block just suppresses it and continues on
    except etree.ParserError:
        pass
    #If an invalid url is provided at the beginning, this exception will be raised
    #It is unlikely this will be run during runtime
    except requests.ConnectionError:
        print("Error: Please enter a valid URL")
        sys.exit(0)


#Adds the provided url to the links file
def add_to_file(url):
    file = open("./Links", 'a')
    file.write(url + '\n')
    file.close()


#Writes all links to the unique_links file
def write_to_file():
    with open('./Links', 'r') as links:
        unfiltered = []
        #Adds all links from the unfiltered links file to a list
        for link in links:
            unfiltered.append(link)
        #Converts the list of links into a set, deleting all duplicates
        uniq = set(unfiltered)
        uniq_links = open('./unique_links', 'w')
        #Adds all of the unique links from the uniq set to the unique_links file
        for i in uniq:
            uniq_links.write(i)
        links.close()


def main():
    global max_depth
    global original_domain
    #Ensures the depth provided is a number
    try:
        int(sys.argv[3])
    except ValueError:
        print("Error: Please enter a valid number for depth")
        sys.exit(0)
    #Initializes all global variables
    max_depth = int(sys.argv[3])
    original_domain = sys.argv[1]
    #Clears the unfiltered links file
    file = open('./Links', 'w')
    file.close()
    #Runs the main functions of the scraper
    start = Scanner(1, sys.argv[2])
    start.run()
    write_to_file()





main()
