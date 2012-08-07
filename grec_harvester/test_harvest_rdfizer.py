#!/usr/bin/env python
# -*- coding: utf8 -*-

from unittest import TestCase, main
from mocker import *

import sys
import harvest_rdfizer as hr

class test_remove_accents(TestCase):
    def test_common_chars(self):
        string = u"àá ñ èé òó í ú"
        self.assertEqual(hr.remove_accents(string), "aa n ee oo i u")

class test_htmlize_string(TestCase):
    def test_complete_string(self):
        string = u"Hola, va tot correcte."
        self.assertEquals(hr.htmlize_string(string), "Holavatotcorrecte")


if __name__ == "__main__":
    main()
