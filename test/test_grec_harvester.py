#!/usr/bin/env python
# -*- coding: utf8 -*-

from unittest import TestCase, main
from mocker import *

from bs4 import BeautifulSoup

import sys
sys.path.append("../src")
import grec_harvester as gh

from time import time

class test_clean_pub_title(TestCase):
    def test_with_colon_at_end_of_string(self):
        string = "test:"
        string2 = " test: "
        self.assertEqual(gh.clean_pub_title(string), "test")
        self.assertEqual(gh.clean_pub_title(string2), "test")

    def test_without_colon_at_end_of_string(self):
        string = "test"
        string2 = " test "
        self.assertEqual(gh.clean_pub_title(string), "test")
        self.assertEqual(gh.clean_pub_title(string2), "test")

    def test_with_colon_middle_string(self):
        string = "te:st"
        string2 = " te:st "
        self.assertEqual(gh.clean_pub_title(string), "te:st")
        self.assertEqual(gh.clean_pub_title(string2), "te:st")


class test_remove_accents(TestCase):
    def test_common_chars(self):
        string = u"àá ñ èé òó í ú"
        self.assertEqual(gh.remove_accents(string), "aa n ee oo i u")


class test_get_soup_from_url(TestCase):
    def test_inexistent_url(self):
        try:
            gh.get_soup_from_url("invalid_url")
            self.fail("URL not valid")
        except ValueError:
            self.assertTrue(True)

    def test_existing_url(self):
        mocker = Mocker()
        mock_url = mocker.replace("urllib2.urlopen")
        mock_url(ANY)
        mocker.result("<b>proves</b>")
        mocker.replay()

        soup = gh.get_soup_from_url("http://www.google.com")

        self.assertEquals(type(soup), type(BeautifulSoup()))
        self.assertEquals(soup, BeautifulSoup("<b>proves</b>", "lxml", from_encoding="UTF8"))

        mocker.restore()
        mocker.verify()


class test_htmlize_string(TestCase):
    def test_complete_string(self):
        string = u"Hola, va tot correcte."
        self.assertEquals(gh.htmlize_string(string), "Holavatotcorrecte")


class test_normalize_author_name(TestCase):
    def test_common_strings(self):
        name1 = "Lastname N"
        name2 = "N Lastname"
        name3 = "Name Lastname"

        expected = "Lastname, N."

        self.assertEquals(gh.normalize_author_name(name1), expected)
        self.assertEquals(gh.normalize_author_name(name2), expected)
        self.assertEquals(gh.normalize_author_name(name3), expected)

    def test_double_name_strings(self):
        name1 = "Lastname NA"
        name2 = "NA Lastname"
        name3 = "Name Are Lastname"
        name4 = "Lastname N A"
        name5 = "N A Lastname"

        expected = "Lastname, N.A."

        self.assertEquals(gh.normalize_author_name(name1), expected)
        self.assertEquals(gh.normalize_author_name(name2), expected)
        self.assertEquals(gh.normalize_author_name(name3), expected)
        self.assertEquals(gh.normalize_author_name(name4), expected)
        self.assertEquals(gh.normalize_author_name(name5), expected)

    def test_unexpected_string_form(self):
        name1 = "Ponsarnau Caste D"
        print gh.normalize_author_name(name1)


if __name__ == "__main__":
    main()