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
    '''Clear de name for the dictionary keys'''
    if ":" in string:
        return string.strip()[:-1]
    return string.strip()


def clean_href(string):
    '''Clean the javascript stuff from the given content of href property of an anchor'''
    return string.split("'")[1]


def get_soup_from_url(url):
    '''Return a BS4 object from a given URL'''
    return BeautifulSoup(urllib2.urlopen(url), "lxml", from_encoding="UTF8")


def get_links_in_row(soup, rowname):
    '''Get a list of links from a BS4 object and a row name'''
    print u"Filtering data by row name: "+ rowname
    fila_pubs = soup.find("td", text=re.compile("^"+ rowname +"$")).find_parent("tr")
    link_list = [a["href"] for a in fila_pubs.find_all("a")]
    return link_list

def normalize_author_name(name):
    # Copied and translated to python from the file PubsRDFizer.java at lines 344 to 414 from rogargon (Roberto García)
    # https://github.com/rogargon/GRECRDFizer/blob/master/src/main/java/net/rhizomik/grecrdfizer/PubsRDFizer.java#L344
    if re.match(".*?(\S\S+)\s+(\S\S?)(?:\s+(\S))?$", name): # Process authornames like Smith J, Doe J R or Frost RA
        match = re.match(".*?(\S\S+)\s+(\S\S?)(?:\s+(\S))?$", name)
        name = match.group(1)+", "
        if None not in match.groups():
            name = name+match.group(2)+"."+match.group(3)+"."
        else:
            if len(match.group(2)) == 1:
                name = name +match.group(2)+"."
            else:
                name = name +match.group(2)[0]+"."+match.group(2)[1]+"."
    elif re.match("^(\S\S?)\s+(:?(\S)\s+)?(\S\S+)", name): # Process authornames like J Smith, J R Doe or RA Frost
        match = re.match("^(\S\S?)\s+(:?(\S)\s+)?(\S\S+)", name)
        name = match.group(4)+", "
        if None not in match.groups():
            name = name+match.group(1)+"."+match.group(3)+"."
        else:
            if len(match.group(1)) == 1:
                name = name +match.group(1)+"."
            else:
                name = name +match.group(1)[0]+"."+match.group(1)[1]+"."
    elif re.match("^(\S+)\s+(:?(\S+)\s+)?(\S+)", name): # Process authornames like John Smith or Ralph Albert Frost
        match = re.match("^(\S+)\s+(:?(\S+)\s+)?(\S+)", name)
        name = match.group(1)[0]+"."
        if None not in match.groups():
            name = match.group(4)+", "+name+match.group(3)[0]+"."
        else:
            name = match.group(4)+", "+name
    return name

def normalize_author_list(string):
    if ";" in string:
        stringn = re.split(";| and | i | amb | y ", string)
    elif "," in string:
        if re.match("(\S\S+)\s+(\S\S?)(?:\s+(\S))?$", string.replace(".", " ").replace(",", " ").strip()):
            stringn = re.split(" and | amb | y ", string.replace(".", " ").replace(",", " ").strip())
        else:
            stringn = re.split(",| and | i | amb | y ", string)
    else:
        stringn = re.split(" and | amb | y ", string)
    author_list = [nom.replace(".", " ").replace(",", " ").strip() for nom in stringn]
    final_author_list = []
    for name in author_list:
        final_author_list.append(normalize_author_name(name))
    print final_author_list
    return final_author_list


def get_pubs_quantity(soup):
    '''Get the number of publications and pages in a BS4 object'''
    max_posts = int(soup.find("p", {"class": "consultac"}).text.split(":")[1].strip())
    posts_per_page = len(soup.find_all("p", {"class": "llista"}))
    max_pages = int(math.ceil(max_posts / float(posts_per_page)))
    return max_posts, max_pages


def get_publication_dict(pub_url):
    ''''''
    pub_url = get_soup_from_url(pub_url)
    pub_data = pub_url.find_all("b")
    pub_dict = {}
    for item in pub_data:
        if len(item.next_element) < 25:
            titol = clean_pub_title(item.next_element)
            try:
                if titol == "Autors":
                    pub_dict[titol] = normalize_author_list(item.next_element.next_element.strip())
                else:
                    pub_dict[titol] = item.next_element.next_element.strip()
            except Error:
                print (Error)
                pub_dict[titol] = None
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