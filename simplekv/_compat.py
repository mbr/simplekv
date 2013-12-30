# -*- coding: utf-8 -*-
"""Helpers for python 2/3 compatibility"""

import sys

PY3 = sys.version_info[0] == 3


if PY3:
    import configparser as ConfigParser
else:
    import ConfigParser


if PY3:
    from urllib.parse import quote as url_quote
else:
    from urllib import quote as url_quote


if PY3:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


if PY3:
    imap = map
else:
    from itertools import imap


xrange = range if PY3 else xrange
