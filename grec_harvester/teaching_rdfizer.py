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
uri_sub = "subject"
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

def remove_accents(s):
    '''Quits accents and language specific characters of a string'''
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def htmlize_string(string):
    '''Make a HTML valid string (quits spaces, commas, dots and accents or language specific characters)'''
    return remove_accents(string.replace(",", "").replace(".", "").replace(" ", ""))

def get_teaching_soup(source):
    '''Return a BS4 object from a given URL'''
    # This method is temporary until we have a web service to get this data.
    # At that moment, switch comments between the following lines.

    return BeautifulSoup(open("docencia.xml"), "lxml", from_encoding="UTF8")
    #return BeautifulSoup(urllib2.urlopen(source), "lxml", from_encoding="UTF8")


def build_graph():
    soup = get_teaching_soup("nothing")

    prof_list = soup.find_all("professor")

    for professor in prof_list:
        if not professor.find("nom").text == "null":
            nom_n = " ".join([nom[0]+"." for nom in professor.find("nom").text.split(" ")])
            cognom_n = professor.find("cognoms").text.split(" ")[0]
            nom_complet =  cognom_n +", "+ nom_n
            nom_complet_html = htmlize_string(cognom_n +", "+ nom_n)
            profe_uri = URIRef(pub_base_uri +"/"+ uri_person +"/"+ nom_complet_html)
            graph.add((profe_uri, RDF.type, UNI.Professor))
            graph.add((profe_uri, RDFS.label, Literal(nom_complet)))
            graph.add((profe_uri, DC.identifier, Literal(professor.find("dni").text)))
            if not professor.find("assignatures").text == "":
                for subject in professor.find_all("assignatura"):
                    subject_uri = URIRef(pub_base_uri +"/"+ uri_sub +"/"+ subject.find("codi").text)
                    graph.add((subject_uri, RDF.type, UNI.Subject))
                    graph.add((subject_uri, RDFS.label, Literal(subject.find("nom").text)))
                    graph.add((subject_uri, SWRC.CarriedOutBy, profe_uri))

            if not professor.find("telefon").text == "":
                graph.add((profe_uri, DC.phone, Literal(professor.find("telefon").text)))

            if not professor.find("web").text == "":
                graph.add((profe_uri, DC.website, Literal(professor.find("web").text)))

            if not professor.find("ubicacio").text == "":
                graph.add((profe_uri, DC.office, Literal(professor.find("ubicacio").text)))


def get_graph():
    build_graph()
    return graph