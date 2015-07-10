#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Use pip or easy_install to install the mechanize library
import mechanize
import cookielib

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

def get_xml(user, passwd, path):
    br.open("http://www.udl.cat/generador_xml/validarusuari?usuari="+ user +"&contrasenya="+ passwd +"")
    for link in br.links():
        req = br.click_link(link)

        br.open(req)
        br.select_form(nr=0)

        if br.form.controls[0].type == "select":
            for item in br.form.controls[0].items:
                fitxer = open(path+"pla"+ item.attrs["value"] +".xml", "w")
                br.form["codi_pla"] = [item.attrs["value"]]
                r = br.submit()
                fitxer.write(r.read())
                # Go back and select the form
                br.back()
                br.select_form(nr=0)
            fitxer.close()
        else:
            fitxer = open(path+"dept.xml", "w")
            r = br.submit()
            fitxer.write(r.read())
            fitxer.close()
            br.back()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Little script for retrieving UdL data in XML format.")
    parser.add_argument("-u","--user",
        help="User name",
        type=str,
        required=True)
    parser.add_argument("-p", "--password",
        help="Password",
        type=str,
        required=True)
    parser.add_argument("-pt", "--path",
        help="Path to write the output files. (Has to be writable)",
        default="",
        type=str)
    args = parser.parse_args()

    if not args.path.endswith("/"):
        args.path = args.path + "/"

    get_xml(args.user, args.password, args.path)