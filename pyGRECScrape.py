#!/usr/bin/env python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup

import rdflib
from rdflib import Graph, term, namespace
#from rdflib.Graph import Graph

import urllib2
import simplejson
import re
import math
import argparse

#GLOBAL VARS
pub_base_uri = "http://www.diei.udl.cat"
#END GLOBAL VARS

def clean_pub_title(string):
    if ":" in string:
        return string.strip()[:-1]
    return string.strip()


def clean_href(string):
    return string.split("'")[1]


def get_soup_from_url(url):
    return BeautifulSoup(urllib2.urlopen(url), "lxml", from_encoding="UTF8")


def get_links_in_row(soup, rowname):
    print u"Filtering data by row name: "+ rowname
    fila_pubs = soup.find("td", text=re.compile("^"+ rowname +"$")).find_parent("tr")
    link_list = [a["href"] for a in fila_pubs.find_all("a")]
    return link_list


def normalize_author_list(string):
    if ";" in string:
        stringn = re.split(";| and | i | amb | y ", string)
    elif "," in string:
        stringn = re.split(",| and | i | amb | y ", string)
    author_list = [nom.strip().replace(".", " ").replace(",", " ") for nom in stringn]
    # Copied and translated to python from the file PubsRDFizer.java at lines 344 to 414 from rogargon (Roberto García)
    # https://github.com/rogargon/GRECRDFizer/blob/master/src/main/java/net/rhizomik/grecrdfizer/PubsRDFizer.java#L344
    # TODO Complete this!
    for name in author_list:
        if re.match("(\\S\\S+)\\s+(\\S\\S?)(?:\\s+(\\S))?$", name): # Process authornames like Smith J, Doe J R or Frost RA
            print "1st: "+ name
        elif re.match("^(\\S\\S?)\\s+(:?(\\S)\\s+)?(\\S\\S+)", name): # Process authornames like J Smith, J R Doe or RA Frost
            print "2nd: "+ name
        elif re.match("^(\\S+)\\s+(:?(\\S+)\\s+)?(\\S+)", name): # Process authornames like John Smith or Ralph Albert Frost
            print "3rd: "+ name
        else:
            print "cap: "+ name
    # ENDTODO
    return [nom.strip() for nom in stringn]


def get_pubs_quantity(soup):
    max_posts = int(soup.find("p", {"class": "consultac"}).text.split(":")[1].strip())
    posts_per_page = len(soup.find_all("p", {"class": "llista"}))
    max_pages = int(math.ceil(max_posts / float(posts_per_page)))
    return max_posts, max_pages


def get_publication_dict(pub_url):
    pub_url = get_soup_from_url(pub_url)
    pub_data = pub_url.find_all("b")
    pub_dict = {}
    if pub_url.a("invest") != []:
        researchers = pub_url.a("invest")
        #TODO Complete this!
    for item in pub_data:
        if len(item.next_element) < 20:
            try:
                if clean_pub_title(item.next_element) == "Autors":
                    pub_dict[clean_pub_title(item.next_element)] = normalize_author_list(item.next_element.next_element.strip())
                else:
                    pub_dict[clean_pub_title(item.next_element)] = item.next_element.next_element.strip()
            except:
                pub_dict[clean_pub_title(item.next_element)] = None
    return pub_dict


def get_pub_list_from_link(link):
    max_posts, max_pages = get_pubs_quantity(get_soup_from_url(link))
    link = link+"&PAG=1"
    publication_list = []
    print str(max_pages)+u" pages and "+str(max_posts)+u" pubs. found"

    for page in range(1, max_pages+1):
        print u"Getting data from page "+ str(page)
        link = link.replace(re.findall("&PAG=.*", link).pop(), "&PAG="+ str(page))
        pub_page = get_soup_from_url(link)
        for pub in pub_page.find_all("p", {"class": "llista"}):
            publication_list.append(get_publication_dict(clean_href(pub.find("a")["href"])))
    return publication_list


def get_all_pubs_from_link_list(link_list):
    publication_list = []
    for link in link_list:
        print u"Getting data from", link
        pub_page = get_soup_from_url(link)
        publication_list.extend(get_pub_list_from_link(link))
    return publication_list


def get_pubs_by_row_name(row_name):
    url_obj = u'http://webgrec.udl.es/cgi-bin/DADREC/crcx1.cgi?PID=312186&IDI=CAT&FONT=3&QUE=CRXD&CRXDCODI=1605&CONSULTA=Fer+la+consulta'
    print "Getting DIEI data from GREC website"
    soup = get_soup_from_url(url_obj)
    link_list = get_links_in_row(soup, row_name)
    return get_all_pubs_from_link_list(link_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Little script for scraping data on DIEI GREC website")
    parser.add_argument("rowtitle",
        metavar = "\"title\"",
        help = "The row title (list) that you want to scrap data",
        type = str,
        nargs = "+")
    args = parser.parse_args()

    for row_title in args.rowtitle:
        pubs = get_pubs_by_row_name(row_title)
        print "Trobades", len(pubs), "publicacions"