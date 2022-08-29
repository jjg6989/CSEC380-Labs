import requests
import sys
from lxml import html
from lxml import etree
import threading
original_domain = ""
max_depth = 0
lock = threading.Lock()
threads = []


class Scanner (threading.Thread):
    def __init__(self, depth, url):
        threading.Thread.__init__(self)
        self.depth = depth
        self.url = url

    def run(self):
        global lock
        global threads
        lock.acquire()
        scan_website(self.url, self.depth)
        lock.release()
        for t in threads:
            #try:
            threads.remove(t)
            t.start()
            t.join()

            #except RuntimeError:
            #    pass


def scan_website(url, depth):
    global max_depth
    global threads
    global original_domain
    scan = requests.get(url)
    try:
        webpage = html.fromstring(scan.content)
        links = webpage.xpath('//a/@href')
        for link in links:
            if "http" in link:
                if original_domain == link[0:19]:
                    add_to_file(link, depth)
                    if not link[-4] == '.' and depth < max_depth:
                        thread = Scanner(depth + 1, link)
                        threads.append(thread)
        for link in links:
            if link[0:1] == "/":
                new_link = "https://" + original_domain + link
                add_to_file(new_link, depth)
                if not new_link[-4] == '.' and depth < max_depth:
                    thread = Scanner(depth + 1, new_link)
                    threads.append(thread)
        #for link in links:
        #    print(3)
        #    if link[0:1] == "#":
        #        add_to_file(link)
        #        if depth < max_depth:
        #            thread = Scanner(depth + 1, link)
        #            threads.append(thread)
    except etree.ParserError:
        pass


def add_to_file(url, depth):
    file = open("./Links", 'a')
    file.write(url + "," + str(depth) + '\n')
    file.close()


def separate_links_by_depth():
    f1 = open('./Links-depth-1', 'w')
    f2 = open('./Links-depth-2', 'w')
    f3 = open('./Links-depth-3', 'w')
    f1.close()
    f2.close()
    f3.close()
    file1 = open('./Links-depth-1', 'r+')
    file2 = open('./Links-depth-2', 'r+')
    file3 = open('./Links-depth-3', 'r+')
    with open('./Links', 'r') as links:
        d1 = []
        d2 = []
        d3 = []
        for link in links:
            link_arr = link.split(',')
            if len(link_arr) > 1 and link_arr[1] == '1\n':
                d1.append(link_arr[0] + '\n')
            elif len(link_arr) > 1 and link_arr[1] == '2\n':
                d2.append(link_arr[0] + '\n')
            elif len(link_arr) > 1 and link_arr[1] == '3\n':
                d3.append(link_arr[0] + '\n')
        uniq1 = set(d1)
        uniq2 = set(d2)
        uniq3 = set(d3)
        for i in uniq1:
            file1.write(i)
        for i in uniq2:
            file2.write(i)
        for i in uniq3:
            file3.write(i)
        file1.close()
        file2.close()
        file3.close()


def main():
    global max_depth
    global original_domain
    max_depth = int(sys.argv[2])
    original_domain = sys.argv[3]
    file = open('./Links', 'w')
    file.close()
    start = Scanner(1, sys.argv[1])
    start.run()
    separate_links_by_depth()


main()
