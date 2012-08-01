#!/usr/bin/env python
# -*- coding: utf8 -*-

from unittest import TestCase, main
from mocker import *

from bs4 import BeautifulSoup

import sys
import grec_harvester as gh

class test_clean_pub_title(TestCase):
    def test_returns_correct_object(self):
        self.assertEqual(type(gh.clean_pub_title("test")), str)

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


class test_has_one_element_character(TestCase):
    def test_returns_correct_value(self):
        test_list = ["test1", "test2"]
        self.assertFalse(gh.has_one_element_character(test_list))

        test_list.append("a")
        self.assertTrue(gh.has_one_element_character(test_list))


class test_clean_href(TestCase):
    def test_returns_correct_value(self):
        string = "alert('http://www.google.com');"
        expected = "http://www.google.com"
        self.assertEquals(gh.clean_href(string), expected)


#class test_remove_accents(TestCase):
#    def test_common_chars(self):
#        string = u"àá ñ èé òó í ú"
#        self.assertEqual(gh.remove_accents(string), "aa n ee oo i u")


class test_get_soup_from_url(TestCase):
    def test_inexistent_url(self):
        try:
            gh.get_soup_from_url("invalid_url")
            self.fail("URL not valid") # pragma: no cover
        except ValueError:
            self.assertTrue(True)

    def test_returns_correct_object(self):
        soup = gh.get_soup_from_url("http://www.google.com")
        self.assertEquals(type(soup), type(BeautifulSoup()))

    def test_existing_url(self):
        mocker = Mocker()
        mock_url = mocker.replace("urllib2.urlopen")
        mock_url(ANY)
        mocker.result("<b>proves</b>")
        mocker.replay()

        soup = gh.get_soup_from_url("http://www.google.com")
        self.assertEquals(soup, BeautifulSoup("<b>proves</b>", "lxml", from_encoding="UTF8"))

        mocker.restore()
        mocker.verify()


class test_get_links_in_row(TestCase):
    def test_returns_correct_value(self):
        soup = BeautifulSoup('''<tr>
            <td>Row name</td>
            <td><a href="localhost">test</a></td>
            <td><a href="localhost">test</a></td>
            <td><a href="localhost">test</a></td>
            </tr>''', "lxml", from_encoding="UTF8")

        expected = ["localhost", "localhost", "localhost"]
        self.assertEquals(gh.get_links_in_row(soup, "Row name"), expected)


#class test_htmlize_string(TestCase):
#    def test_complete_string(self):
#        string = u"Hola, va tot correcte."
#        self.assertEquals(gh.htmlize_string(string), "Holavatotcorrecte")


class test_normalize_author_name(TestCase):
    def test_returns_correct_object(self):
        self.assertEquals(type(gh.normalize_author_name("Test T")), str)

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
        name1 = "Abla1 Bbla2 C"
        self.assertEquals(gh.normalize_author_name(name1), "Bbla2, C.")

        name2 = "Abla1 Bbla2 Cbla3"
        self.assertEquals(gh.normalize_author_name(name2), "Cbla3, A.B.")

        name3 = "ABLA1 BBLA2 CBLA3 DBLA4"
        self.assertEquals(gh.normalize_author_name(name3), "Cbla3, A.B.")

        name4 = "ABLA1 BBLA2 CBLA3"
        self.assertEquals(gh.normalize_author_name(name4), "Bbla2, A.")


class test_normalize_author_list(TestCase):
    def setUp(self):
        self.mocker = Mocker()

    def setUpMock(self, calls):
        self.mock_name = self.mocker.replace("grec_harvester.normalize_author_name")
        for i in range(calls):
            self.mock_name(ANY)
            self.mocker.result("Doe, J.")
        self.mocker.replay()

    def tearDownMock(self):
        self.mocker.restore()
        self.mocker.verify()

    def test_returns_correct_object(self):
        test = "Lastname F, Lastname F, Lastname F"
        self.assertEquals(type(gh.normalize_author_list(test)), list)

    def test_simple_list_comma(self):
        self.setUpMock(3)

        expected = ["Doe, J.", "Doe, J.", "Doe, J."]
        test = "Lastname F, Lastname F, Lastname F"
        self.assertEquals(gh.normalize_author_list(test), expected)

        self.tearDownMock()


    def test_simple_list_semicolon(self):
        self.setUpMock(3)

        expected = ["Doe, J.", "Doe, J.", "Doe, J."]
        test = "Lastname, F.; Lastname, F.; Lastname, F."
        self.assertEquals(gh.normalize_author_list(test), expected)

        self.tearDownMock()


    def test_list_conjunction_list_comma(self):
        self.setUpMock(3)

        expected = ["Doe, J.", "Doe, J.", "Doe, J."]
        test = "Lastname F, Lastname D and Lastname E"

        self.assertEquals(gh.normalize_author_list(test), expected)

        self.tearDownMock()

    def test_list_conjunction_list_semicolon(self):
        self.setUpMock(3)

        expected = ["Doe, J.", "Doe, J.", "Doe, J."]
        test = "Lastname, F; Lastname, D and Lastname, E"

        self.assertEquals(gh.normalize_author_list(test), expected)

        self.tearDownMock()

    def test_list_conjunction_pair(self):
        self.setUpMock(2)

        expected = ["Doe, J.", "Doe, J."]
        test = "Lastname D and Lastname E"

        self.assertEquals(gh.normalize_author_list(test), expected)

        self.tearDownMock()

    def test_list_conjunction_pair_comma(self):
        self.setUpMock(2)

        expected = ["Doe, J.", "Doe, J."]
        test = "Lastname, D. and Lastname, E."
        #print gh.normalize_author_list(test)
        self.assertEquals(gh.normalize_author_list(test), expected)

        self.tearDownMock()

    def test_one_author_comma(self):
        self.setUpMock(1)

        expected = ["Doe, J."]
        test = "Lastname, D"
        #print gh.normalize_author_list(test)
        self.assertEquals(gh.normalize_author_list(test), expected)

        self.tearDownMock()


class test_get_pubs_quantity(TestCase):
    def setUp(self):
        soup = BeautifulSoup('''<p class="consultac">Numero: 100</p>
            <p class="llista"></p>
            <p class="llista"></p>
            <p class="llista"></p>
            <p class="llista"></p>
            <p class="llista"></p>''', "lxml", from_encoding="UTF8")
        self.result = gh.get_pubs_quantity(soup)

    def test_returns_correct_object(self):
        self.assertEquals(type(self.result), tuple)
        self.assertEquals(len(self.result), 2)

    def test_correct_return_values(self):
        self.assertEquals(self.result, (100, 20))


class test_get_publication_dict(TestCase):
    def test_returns_correct_value(self):
        self.soup = BeautifulSoup('''<b>TestTitle</b>title
            <b>TestTitle2</b>title2
            <b>TestTitle3</b>title3
            <b>Autors</b>Test, T.;Test, T.
            <b>NullTitle</b>
            ''')
        self.mocker = Mocker()
        mocker_get_soup = self.mocker.replace("grec_harvester.get_soup_from_url")
        mocker_get_soup(ANY)
        self.mocker.result(self.soup)
        self.mocker.replay()

        result = gh.get_publication_dict("nothing")
        expected = {u'TestTitle2': u'title2',
            u'TestTitle3': u'title3',
            u'TestTitle': u'title',
            u'Autors': [u'Test, T.', u'Test, T.'],
            u'NullTitle': u''}

        self.assertEquals(result, expected)
        self.assertEquals(type(result), dict)

        self.mocker.restore()
        self.mocker.verify()


class test_get_pub_list_from_link(TestCase):
    def setUp(self):
        self.mocker_soup = Mocker()
        self.mocker_pubs = Mocker()
        self.mocker_dict = Mocker()
        self.mocker_href = Mocker()

    def setUpMocks(self):
        mocker_p = self.mocker_pubs.replace("grec_harvester.get_pubs_quantity")
        mocker_p(ANY)
        self.mocker_pubs.result(tuple([3, 1]))

        soup = BeautifulSoup('''<p class="llista"><a href="nothing">test1</a></p>
            <p class="llista"><a href="nothing">test2</a></p>
            <p class="llista"><a href="nothing">test3</a></p>''', "lxml", from_encoding="UTF8")
        mocker_s = self.mocker_soup.replace("grec_harvester.get_soup_from_url")
        mocker_s(ANY)
        self.mocker_soup.result("nothing")
        mocker_s(ANY)
        self.mocker_soup.result(soup)

        mocker_d = self.mocker_dict.replace("grec_harvester.get_publication_dict")
        for count in range(3):
            mocker_d(ANY)
            self.mocker_dict.result({"Test1": "test1"})

        mocker_h = self.mocker_href.replace("grec_harvester.clean_href")
        for count in range(3):
            mocker_h(ANY)
            self.mocker_href.result("url")

        self.mocker_soup.replay()
        self.mocker_pubs.replay()
        self.mocker_dict.replay()
        self.mocker_href.replay()

    def tearDownMocks(self):
        self.mocker_soup.restore()
        self.mocker_pubs.restore()
        self.mocker_dict.restore()
        self.mocker_href.restore()

        self.mocker_soup.verify()
        self.mocker_pubs.verify()
        self.mocker_dict.verify()
        self.mocker_href.verify()

    def test_returns_correct_object(self):
        self.setUpMocks()

        result = gh.get_pub_list_from_link("nothing")
        self.assertEquals(type(result), list)

        self.tearDownMocks()

    def test_returns_correct_value(self):
        self.setUpMocks()

        result = gh.get_pub_list_from_link("nothing")
        expected = [{'Test1': 'test1'}, {'Test1': 'test1'}, {'Test1': 'test1'}]
        self.assertEquals(result, expected)

        self.tearDownMocks()


if __name__ == "__main__":
    main()