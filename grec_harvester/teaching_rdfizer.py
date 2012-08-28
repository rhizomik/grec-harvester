#!/usr/bin/env python
# -*- coding: utf8 -*-

from rdflib.graph import ConjunctiveGraph
from rdflib import Namespace, URIRef, Literal, RDF, BNode
from rdflib.collection import Collection

from bs4 import BeautifulSoup
import urllib2

import unicodedata

#GLOBAL VARS
pub_base_uri = "http://www.diei.udl.cat"
uri_person = "person"
uri_pub = "pub"
DC = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SWRC = Namespace("http://swrc.ontoware.org/ontology#")
UNI = Namespace("http://purl.org/weso/uni/uni.html#")

#END GLOBAL VARS

# Create the RDF Graph
graph = ConjunctiveGraph()
graph.bind("dc", DC)
graph.bind("rdfs", RDFS)
graph.bind("swrc", SWRC)
graph.bind("uni", UNI)
# End create RDF Graph

def get_teaching_soup(source):
    '''Return a BS4 object from a given URL'''
    # This method is temporary until we have a web service to get this data.
    # At that moment, switch comments between the following lines.

    return BeautifulSoup(open("docencia.xml"), "lxml", from_encoding="UTF8")
    #return BeautifulSoup(urllib2.urlopen(source), "lxml", from_encoding="UTF8")

