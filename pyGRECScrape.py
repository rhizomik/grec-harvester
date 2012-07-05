# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
import rdflib

import urllib2
import re
import math

def get_soup(url):
    return BeautifulSoup(urllib2.urlopen(url))

def get_pubs_by_row_name(row_name):
    url_obj = 'http://webgrec.udl.es/cgi-bin/DADREC/crcx1.cgi?PID=312186&IDI=CAT&FONT=3&QUE=CRXD&CRXDCODI=1605&CONSULTA=Fer+la+consulta'
    print "Agafant dades del DIEI a la web del GREC..."
    soup = get_soup(url_obj)
    print "Filtrant dades per fila..."
    fila_pubs = soup.find("td", text=re.compile("^"+ row_name +"$")).find_parent("tr")
    link_list = [a["href"] for a in fila_pubs.find_all("a")]
    publication_list = []
    for link in link_list:
        print "Agafant dades de", link
        pub_page = get_soup(link)
        max_posts = int(pub_page.find("p", {"class": "consultac"}).text.split(":")[1].strip())
        posts_per_page = len(pub_page.find_all("p", {"class": "llista"}))
        max_pages = int(math.ceil(max_posts / float(posts_per_page)))
        link = link+"&PAG=1"
        print "Trobades", max_pages, "pàgines i ", max_posts, "publicacions"
        for page in range(1, max_pages+1):
            print "Agafant dades de la pàgina", page
            link = link.replace(re.findall("&PAG=.*", link).pop(), "&PAG="+ str(page))
            pub_page = get_soup(link)
            publication_list.extend(pub_page.find_all("p", {"class": "llista"}))
    return publication_list

pubs = get_pubs_by_row_name("Tesis.*")
print "Trobades", len(pubs), "publicacions"
#print [a.text for a in fila_pubs.find_all("a")]