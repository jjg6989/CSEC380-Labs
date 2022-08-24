import requests
import sys
import lxml

def scan_website(url):
    scan = requests.get(url)
    print(scan.links)


def add_to_file(url):
    print()



def main():
    scan_website(sys.argv[1])


main()