#!/usr/bin/env python
# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
from termcolor import colored

import rdflib
from rdflib import Graph, term, namespace
#from rdflib.Graph import Graph

import urllib2
import re
import math
import argparse


def get_soup_from_url(url):
    return BeautifulSoup(urllib2.urlopen(url))


def get_links_in_row(soup, rowname):
    print "Filtrant dades per fila..."
    fila_pubs = soup.find("td", text=re.compile("^"+ rowname +"$")).find_parent("tr")
    link_list = [a["href"] for a in fila_pubs.find_all("a")]
    return link_list


def get_pubs_quantity(soup):
    max_posts = int(soup.find("p", {"class": "consultac"}).text.split(":")[1].strip())
    posts_per_page = len(soup.find_all("p", {"class": "llista"}))
    max_pages = int(math.ceil(max_posts / float(posts_per_page)))
    return max_posts, max_pages


def get_pub_list_from_link(link):
    max_posts, max_pages = get_pubs_quantity(get_soup_from_url(link))
    link = link+"&PAG=1"
    publication_list = []
    print colored("Trobades "+str(max_pages)+" pàgines i "+str(max_posts)+" publicacions", "green")

    for page in range(1, max_pages+1):
        print colored("Agafant dades de la pàgina "+ str(page), "blue")
        link = link.replace(re.findall("&PAG=.*", link).pop(), "&PAG="+ str(page))
        pub_page = get_soup_from_url(link)
        publication_list.extend(pub_page.find_all("p", {"class": "llista"}))
    return publication_list


def get_all_pubs_from_link_list(link_list):
    publication_list = []
    for link in link_list:
        print "Agafant dades de", link
        pub_page = get_soup_from_url(link)
        publication_list.extend(get_pub_list_from_link(link))
    return publication_list


def get_pubs_by_row_name(row_name):
    url_obj = 'http://webgrec.udl.es/cgi-bin/DADREC/crcx1.cgi?PID=312186&IDI=CAT&FONT=3&QUE=CRXD&CRXDCODI=1605&CONSULTA=Fer+la+consulta'
    print colored("Agafant dades del DIEI a la web del GREC...", "green")
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