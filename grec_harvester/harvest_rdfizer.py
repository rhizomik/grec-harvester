#!/usr/bin/env python
# -*- coding: utf8 -*-

from rdflib.graph import ConjunctiveGraph
from rdflib import Namespace, URIRef, Literal, RDF, BNode
from rdflib.collection import Collection

import unicodedata

#GLOBAL VARS
pub_base_uri = "http://www.diei.udl.cat"
uri_person = "person"
uri_pub = "pub"
swrc = "http://swrc.ontoware.org/ontology#"
DC = Namespace("http://purl.org/dc/elements/1.1/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
UNI = Namespace("http://swrc.ontoware.org/ontology#")

#END GLOBAL VARS

# Create the RDF Graph
graph = ConjunctiveGraph()
graph.bind("dc", DC)
graph.bind("rdfs", RDFS)
graph.bind("uni", UNI)
# End create RDF Graph


def remove_accents(s):
    '''Quits accents and language specific characters of a string'''
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def htmlize_string(string):
    '''Make a HTML valid string (quits spaces, commas, dots and accents or language specific characters)'''
    return remove_accents(string.replace(",", "").replace(".", "").replace(" ", ""))


def rdfize_output_common(pub_dict):
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, DC.year, Literal(pub_dict[u"Any"])))
    graph.add((pub_uriref, DC.title, Literal(pub_dict[u"Títol"])))

    if pub_dict.has_key(u"Autors"):
        graph.add((pub_uriref, UNI.authors, Literal("; ".join(pub_dict[u"Autors"]))))
        for autor in pub_dict[u"Autors"]:
            autor_uriref = URIRef(pub_base_uri+"/"+uri_person+"/"+htmlize_string(autor))
            graph.add((pub_uriref, DC.author, autor_uriref))
            graph.add((autor_uriref, RDFS.label, Literal(autor)))


def rdfize_pages(pub_dict):
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])
    if pub_dict[u"Pàgina inicial"] != "" or pub_dict[u"Pàgina final"] != "":
        graph.add((pub_uriref, UNI.pages, Literal(pub_dict[u"Pàgina inicial"] +"-"+ pub_dict[u"Pàgina final"])))
    if pub_dict["Volum"] != "":
        graph.add((pub_uriref, UNI.volume, Literal(pub_dict["Volum"])))


def rdfize_journal_article(pub_dict):
    rdfize_output_common(pub_dict)
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, UNI.Article))
    rdfize_pages(pub_dict)

    if pub_dict["ISSN"] != "":
        journal_uriref = URIRef(pub_base_uri+"/journal/"+pub_dict["ISSN"])
        graph.add((pub_uriref, UNI.isPartOf, journal_uriref))
        graph.add((journal_uriref, RDF.type, UNI.Journal))
        graph.add((journal_uriref, RDFS.label, Literal(pub_dict["Revista"])))
        graph.add((journal_uriref, UNI.ISSN, Literal(pub_dict["ISSN"])))


def rdfize_book_article(pub_dict):
    rdfize_output_common(pub_dict)
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, UNI.Article))
    rdfize_pages(pub_dict)

    if pub_dict["ISBN"] != "":
        book_uriref = URIRef(pub_base_uri+"/book/"+pub_dict["ISBN"])
        graph.add((pub_uriref, UNI.isPartOf, book_uriref))
        graph.add((book_uriref, RDF.type, UNI.Book))
        if pub_dict[u"Referència"] != "":
            graph.add((book_uriref, RDFS.label, Literal(pub_dict[u"Referència"])))
        graph.add((book_uriref, UNI.ISBN, Literal(pub_dict["ISBN"])))
        if pub_dict[u"Editorial"] != "": 
            graph.add((book_uriref, UNI.editor, Literal(pub_dict[u"Editorial"])))


def rdfize_thesis(pub_dict):
    rdfize_output_common(pub_dict)
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, UNI.Thesis))
    for autor in pub_dict[u"Autor"]:
        autor_uriref = URIRef(pub_base_uri+"/"+uri_person+"/"+htmlize_string(autor))
        graph.add((pub_uriref, DC.author, autor_uriref))
        graph.add((autor_uriref, RDFS.label, Literal(autor)))

    for director in pub_dict[u"Director"]:
        director_uriref = URIRef(pub_base_uri+"/"+uri_person+"/"+htmlize_string(director))
        graph.add((pub_uriref, UNI.supervisor, director_uriref))
        graph.add((director_uriref, RDFS.label, Literal(director)))

    graph.add((pub_uriref, UNI.school, Literal(pub_dict[u"Facultat"])))
    graph.add((pub_uriref, DC.University, Literal(pub_dict[u"Universitat"])))


def rdfize_congress_paper(pub_dict):
    rdfize_output_common(pub_dict)
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, UNI.Article))
    graph.add((pub_uriref, UNI.Meeting, Literal(pub_dict[u"Congrés"])))


def rdfize_research_project(pub_dict):
    pass


def rdfize_european_project(pub_dict):
    pass


def rdfize_contract(pub_dict):
    pass


def rdfize_pub_list(pub_list):
    '''Translate the publication list structure to a RDF Graph structure'''
    for pub_dict in pub_list:
        if pub_dict.has_key(u"ISSN"):
            rdfize_journal_article(pub_dict)
        elif pub_dict.has_key(u"ISBN"):
            rdfize_book_article(pub_dict)
        elif pub_dict.has_key(u"Qualificació"):
            rdfize_thesis(pub_dict)
        elif pub_dict.has_key(u"Congrés"):
            rdfize_congress_paper(pub_dict)
        elif pub_dict.has_key(u"Unesco"):
            rdfize_research_project(pub_dict)
        elif pub_dict.has_key(u"Codi UE"):
            rdfize_european_project(pub_dict)
        else:
            rdfize_contract(pub_dict)
    return graph.serialize(format="pretty-xml")