#!/usr/bin/env python
# -*- coding: utf8 -*-

from rdflib.graph import ConjunctiveGraph
from rdflib import Namespace, URIRef, Literal, RDF

from bs4 import BeautifulSoup

import unicodedata

#GLOBAL VARS
pub_base_uri = "http://www.diei.udl.cat"
uri_person = "person"
uri_pub = "pub"
uri_sub = "subject"
DC = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SWRC = Namespace("http://swrc.ontoware.org/ontology#")
AIISO = Namespace("http://purl.org/vocab/aiiso/schema#")
TEACH = Namespace("http://linkedscience.org/teach/ns#")
#END GLOBAL VARS

# Create the RDF Graph
graph = ConjunctiveGraph()
graph.bind("dc", DC)
graph.bind("rdfs", RDFS)
graph.bind("swrc", SWRC)
graph.bind("aiiso", AIISO)
graph.bind("teach", TEACH)
# End create RDF Graph

def remove_accents(s):
    '''Quits accents and language specific characters of a string'''
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def htmlize_string(string):
    '''Make a HTML valid string (quits spaces, commas, dots and accents or language specific characters)'''
    return remove_accents(string.replace(",", "").replace(".", "").replace(" ", ""))

def get_teaching_soup(source):
    '''Return a BS4 object from a given URL'''
    # This funcion reads data from the output of the udl-xml-retriever project
    # https://github.com/davidkaste/udl-xml-retriever

    return BeautifulSoup(open(source), "lxml", from_encoding="UTF8")
    #return BeautifulSoup(urllib2.urlopen(source), "lxml", from_encoding="UTF8")

def build_career_graph(source_folder):
    import os
    file_list = os.listdir(os.path.abspath(source_folder))
    file_list.pop(file_list.index("dept.xml"))

    for fitxer in file_list:
        soup = BeautifulSoup(open(source_folder+fitxer), "lxml", from_encoding="iso-8859-1")

        nom_carrera = soup.find("pla").find("nom").text
        codi_carrera = soup.find("pla").find("codi").text

        carrera_uri = URIRef(pub_base_uri+"/programme/"+codi_carrera)
        graph.add((carrera_uri, RDF.type, AIISO.Programme))
        graph.add((carrera_uri, DC.identifier, Literal(nom_carrera)))
        graph.add((carrera_uri, RDFS.label, Literal(nom_carrera)))

        subject_list = soup.find_all("assignatura")
        for subject in subject_list:
            subject_uri = URIRef(pub_base_uri+"/"+uri_sub+"/"+subject.find("codi").text)
            graph.add((subject_uri, RDF.type, AIISO.Subject))
            graph.add((subject_uri, DC.identifier, Literal(subject.find("codi").text)))
            graph.add((subject_uri, RDFS.label, Literal(subject.find("nom").text)))

            if subject.find("tipus").text == "T":
                graph.add((subject_uri, DC.type, Literal("Troncal")))
            elif subject.find("tipus").text == "O":
                graph.add((subject_uri, DC.type, Literal("Optativa")))
            elif subject.find("tipus").text == "B":
                graph.add((subject_uri, DC.type, Literal("Obligatòria")))
            elif subject.find("tipus").text == "L":
                graph.add((subject_uri, DC.type, Literal("Lliure elecció")))

            graph.add((subject_uri, TEACH.module, Literal(subject.find("curs").text)))
            graph.add((subject_uri, TEACH.ects, Literal(subject.find("credits").text)))
            graph.add((subject_uri, TEACH.studyProgram, carrera_uri))

def build_graph(path):
    soup = BeautifulSoup(open(path+"dept.xml"), "lxml", from_encoding="iso-8859-1")

    dept_uri = URIRef(pub_base_uri+"/dept/"+soup.find("departament").find("codi").text)
    graph.add((dept_uri, RDF.type, AIISO.Department))
    graph.add((dept_uri, DC.identifier, Literal(soup.find("departament").find("codi").text)))
    graph.add((dept_uri, RDFS.label, Literal(soup.find("departament").find("nom").text)))

    prof_list = soup.find_all("professor")

    for professor in prof_list:
        if not professor.find("nom").text == "null":
            nom_sencer = professor.find("cognoms").text + ", " + professor.find("nom").text
            nom_n = "".join([nom[0]+"." for nom in professor.find("nom").text.strip().split(" ")])
            cognom_n = professor.find("cognoms").text.split(" ")[0]
            nom_complet =  cognom_n +", "+ nom_n
            nom_complet_html = htmlize_string(cognom_n +", "+ nom_n)
            profe_uri = URIRef(pub_base_uri +"/"+ uri_person +"/"+ nom_complet_html)
            graph.add((profe_uri, RDF.type, SWRC.AcademicStaff))
            graph.add((profe_uri, RDFS.label, Literal(nom_complet)))
            graph.add((profe_uri, SWRC.name, Literal(nom_sencer)))
            graph.add((profe_uri, DC.identifier, Literal(nom_complet_html)))
            graph.add((profe_uri, DC.initial, Literal(nom_complet_html[0])))
            graph.add((profe_uri, DC.LicenseDocument, Literal(professor.find("dni").text)))
            graph.add((profe_uri, DC.type, Literal(professor.find("categoria").text)))
            graph.add((profe_uri, DC.partOf, Literal(professor.find("area_coneixement").text)))
            if not professor.find("assignatures").text == "":
                for subject in professor.find_all("assignatura"):
                    subject_uri = URIRef(pub_base_uri +"/"+ uri_sub +"/"+ subject.find("codi").text)
                    graph.add((subject_uri, DC.identifier, Literal(subject.find("codi").text)))
                    graph.add((subject_uri, RDF.type, AIISO.Subject))
                    graph.add((subject_uri, RDFS.label, Literal(subject.find("nom").text)))
                    if subject.find("responsable").text == "N":
                        graph.add((profe_uri, AIISO.teaches, subject_uri))
                    else:
                        graph.add((subject_uri, AIISO.responsibilityOf, profe_uri))
                        graph.add((profe_uri, AIISO.responsibleFor, subject_uri))
                        graph.add((profe_uri, AIISO.teaches, subject_uri))

            if not professor.find("telefon").text == "":
                graph.add((profe_uri, DC.phone, Literal(professor.find("telefon").text)))

            if not professor.find("web").text == "":
                graph.add((profe_uri, DC.website, Literal(professor.find("web").text)))

            if not professor.find("ubicacio").text == "":
                graph.add((profe_uri, DC.office, Literal(professor.find("ubicacio").text)))


def get_graph(path):
    build_graph(path)
    build_career_graph(path)
    return graph

if __name__ == "__main__":
    build_graph()
    print graph.serialize(format="pretty-xml")
