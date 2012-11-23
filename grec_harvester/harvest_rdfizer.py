#!/usr/bin/env python
# -*- coding: utf8 -*-

from rdflib import Namespace, URIRef, Literal, RDF

import teaching_rdfizer

import unicodedata

#GLOBAL VARS
pub_base_uri = "http://www.diei.udl.cat"
uri_person = "person"
uri_pub = "pub"
DC = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SWRC = Namespace("http://swrc.ontoware.org/ontology#")
AIISO = Namespace("http://purl.org/vocab/aiiso/schema#")
TEACH = Namespace("http://linkedscience.org/teach/ns#")
#END GLOBAL VARS

# Create the RDF Graph
graph = teaching_rdfizer.get_graph("xmls/")
graph.bind("dc", DC)
graph.bind("rdfs", RDFS)
graph.bind("swrc", SWRC)
graph.bind("aiiso", AIISO)
graph.bind("teach", TEACH)
# End create RDF Graph


def remove_accents(s):
    '''
    Quits accents and language specific characters of a string
    '''
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def htmlize_string(string):
    '''
    Make a HTML valid string (quits spaces, commas, dots and accents or language specific characters)
    '''
    return remove_accents(string.replace(",", "").replace(".", "").replace(" ", ""))


def rdfize_output_common(pub_dict, puburi):
    '''
    Adds common fields for outputs un the RDF Graph.
    '''
    pub_uriref = URIRef(pub_base_uri+"/"+puburi+"/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, DC.year, Literal(pub_dict[u"Any"])))
    graph.add((pub_uriref, DC.title, Literal(pub_dict[u"Títol"])))

    graph.add((pub_uriref, RDF.type, SWRC.Publication))

    if pub_dict.has_key(u"Autors"):
        graph.add((pub_uriref, SWRC.authors, Literal("; ".join(pub_dict[u"Autors"]))))
        for autor in pub_dict[u"Autors"]:
            autor_uriref = URIRef(pub_base_uri+"/"+uri_person+"/"+htmlize_string(autor))
            graph.add((autor_uriref, RDF.type, SWRC.Person))
            graph.add((pub_uriref, DC.author, autor_uriref))
            graph.add((autor_uriref, RDFS.label, Literal(autor)))
            graph.add((autor_uriref, DC.identifier, Literal(htmlize_string(autor))))


def rdfize_pages(pub_dict, puburi):
    '''
    Adds pages fields in RDF Graph
    '''
    pub_uriref = URIRef(pub_base_uri+"/"+puburi+"/"+pub_dict["Id. GREC"])
    if pub_dict[u"Pàgina inicial"] != "" or pub_dict[u"Pàgina final"] != "":
        graph.add((pub_uriref, SWRC.pages, Literal(pub_dict[u"Pàgina inicial"] +"-"+ pub_dict[u"Pàgina final"])))
    if pub_dict["Volum"] != "":
        graph.add((pub_uriref, SWRC.volume, Literal(pub_dict["Volum"])))


def rdfize_journal_article(pub_dict):
    '''
    Add common article fields into the RDF graph.
    '''
    if "docent" in pub_dict["Clau"].split(" ") or "docents" in pub_dict["Clau"].split(" "): return
    rdfize_output_common(pub_dict, "article")
    pub_uriref = URIRef(pub_base_uri+"/article/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, SWRC.Article))
    rdfize_pages(pub_dict, "article")

    if pub_dict["ISSN"] != "":
        journal_uriref = URIRef(pub_base_uri+"/journal/"+pub_dict["ISSN"])
        graph.add((pub_uriref, SWRC.isPartOf, journal_uriref))
        graph.add((journal_uriref, RDF.type, SWRC.Journal))
        graph.add((journal_uriref, RDFS.label, Literal(pub_dict["Revista"])))
        graph.add((journal_uriref, SWRC.ISSN, Literal(pub_dict["ISSN"])))


def rdfize_book_article(pub_dict):
    '''
    Add common inbook fields into the RDF graph.
    '''
    if "docent" in pub_dict["Clau"].split(" ") or "docents" in pub_dict["Clau"].split(" "): return
    rdfize_output_common(pub_dict, "inbook")
    pub_uriref = URIRef(pub_base_uri+"/inbook/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, SWRC.InBook))
    rdfize_pages(pub_dict, "inbook")

    if pub_dict["ISBN"] != "":
        book_uriref = URIRef(pub_base_uri+"/book/"+pub_dict["ISBN"])
        graph.add((pub_uriref, SWRC.isPartOf, book_uriref))
        graph.add((book_uriref, RDF.type, SWRC.Book))
        if pub_dict[u"Referència"] != "":
            graph.add((book_uriref, RDFS.label, Literal(pub_dict[u"Referència"])))
        graph.add((book_uriref, SWRC.ISBN, Literal(pub_dict["ISBN"])))
        if pub_dict[u"Editorial"] != "": 
            graph.add((book_uriref, SWRC.editor, Literal(pub_dict[u"Editorial"])))


def rdfize_thesis(pub_dict):
    '''
    Add common PhD Thesis fields into the RDF graph.
    '''
    if pub_dict[u"Clau"] != "Tesi Doctoral" and pub_dict[u"Clau"] != "Tesi Doctoral Europea": return
    rdfize_output_common(pub_dict, "phdthesis")
    pub_uriref = URIRef(pub_base_uri+"/phdthesis/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, SWRC.PhDThesis))
    for autor in pub_dict[u"Autor"]:
        autor_uriref = URIRef(pub_base_uri+"/"+uri_person+"/"+htmlize_string(autor))
        graph.add((autor_uriref, RDF.type, SWRC.Person))
        graph.add((pub_uriref, DC.author, autor_uriref))
        graph.add((autor_uriref, RDFS.label, Literal(autor)))

    for director in pub_dict[u"Director"]:
        director_uriref = URIRef(pub_base_uri+"/"+uri_person+"/"+htmlize_string(director))
        graph.add((director_uriref, RDF.type, SWRC.Person))
        graph.add((pub_uriref, SWRC.supervisor, director_uriref))
        graph.add((director_uriref, RDFS.label, Literal(director)))

    graph.add((pub_uriref, SWRC.school, Literal(pub_dict[u"Facultat"])))
    graph.add((pub_uriref, DC.University, Literal(pub_dict[u"Universitat"])))


def rdfize_congress_paper(pub_dict):
    '''
    Add common InProceedings fields into the RDF graph.
    '''
    rdfize_output_common(pub_dict, "inproceedings")
    pub_uriref = URIRef(pub_base_uri+"/inproceedings/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, SWRC.InProceedings))
    graph.add((pub_uriref, SWRC.atEvent, Literal(pub_dict[u"Congrés"])))


def rdfize_patent(pub_dict):
    '''
    Add common patent fields into the RDF graph.
    '''
    rdfize_output_common(pub_dict, "patent")
    pub_uriref = URIRef(pub_base_uri+"/patent/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, SWRC.Patent))
    graph.add((pub_uriref, SWRC.location, Literal(pub_dict[u"Països"])))
    graph.add((pub_uriref, SWRC.organization, Literal(pub_dict["Organismes"])))


def rdfize_input_common(pub_dict):
    '''
    Add common fields for inputs into the RDF graph.
    '''
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])

    director_uriref = URIRef(pub_base_uri+"/"+uri_person+"/"+htmlize_string(pub_dict["Investigador principal"]))
    graph.add((pub_uriref, SWRC.head, director_uriref))
    graph.add((director_uriref, RDF.type, SWRC.Person))
    graph.add((director_uriref, RDFS.label, Literal(pub_dict["Investigador principal"])))
    graph.add((director_uriref, DC.identifier, Literal(htmlize_string(pub_dict["Investigador principal"]))))

    graph.add((pub_uriref, DC.title, Literal(pub_dict[u"Títol"])))

    graph.add((pub_uriref, DC.isPartOf, Literal(pub_dict[u"Convocatòria"])))

    graph.add((pub_uriref, SWRC.financedBy, Literal(pub_dict[u"Organisme"])))

    graph.add((pub_uriref, SWRC.carriedOutBy, Literal(pub_dict[u"Institució"])))

    if pub_dict["Data d'inici"] != "":
        data = "-".join(pub_dict["Data d'inici"].split("/")[::-1])
        graph.add((pub_uriref, DC.beginDate, Literal(data)))
        graph.add((pub_uriref, DC.year, Literal(data.split("-")[0])))

    if pub_dict["Data Fi"] != "":
        data = "-".join(pub_dict["Data Fi"].split("/")[::-1])
        graph.add((pub_uriref, DC.endDate, Literal(data)))

    if pub_dict["Data"] != "":
        data = "-".join(pub_dict["Data"].split("/")[::-1])
        graph.add((pub_uriref, DC.date, Literal(data)))

    if pub_dict["Investigadors secundaris"] != []:
        graph.add((pub_uriref, SWRC.authors, Literal(pub_dict["Investigador principal"]+"; "+"; ".join(pub_dict["Investigadors secundaris"]))))
        for researcher in pub_dict["Investigadors secundaris"]:
            researcher_uriref = URIRef(pub_base_uri+"/"+uri_person+"/"+htmlize_string(researcher))
            graph.add((pub_uriref, SWRC.member, researcher_uriref))
            graph.add((researcher_uriref, RDF.type, SWRC.Person))
            graph.add((researcher_uriref, RDFS.label, Literal(researcher)))
            graph.add((researcher_uriref, SWRC.note, Literal(htmlize_string(researcher))))


def rdfize_research_project(pub_dict):
    '''
    Add common research project fields into the RDF graph.
    '''
    rdfize_input_common(pub_dict)
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, SWRC.Project))
    graph.add((pub_uriref, DC.identifier, Literal(pub_dict["Codi oficial"])))
    graph.add((pub_uriref, DC.isPartOf, Literal(pub_dict[u"Programa"])))


def rdfize_european_project(pub_dict):
    '''
    Add common European project fields into the RDF graph.
    '''
    rdfize_input_common(pub_dict)
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, SWRC.Project))
    graph.add((pub_uriref, DC.identifier, Literal(pub_dict["Codi UE"])))
    graph.add((pub_uriref, DC.isPartOf, Literal(pub_dict[u"Programa"])))


def rdfize_contract(pub_dict):
    '''
    Add common contract fields into the RDF graph.
    '''
    rdfize_input_common(pub_dict)
    pub_uriref = URIRef(pub_base_uri+"/"+uri_pub+"/"+pub_dict["Id. GREC"])

    graph.add((pub_uriref, RDF.type, SWRC.Contract))
    graph.add((pub_uriref, DC.identifier, Literal(pub_dict["Codi oficial"])))

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
        elif pub_dict.has_key(u"Número de registre"):
            rdfize_patent(pub_dict)
        else:
            rdfize_contract(pub_dict)

    return graph.serialize(format="n3")