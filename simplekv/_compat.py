# -*- coding: utf-8 -*-
"""Helpers for python 2/3 compatibility"""

import sys

PY2 = sys.version_info[0] == 2


if not PY2:
    import configparser as ConfigParser
else:
    import ConfigParser


if not PY2:
    from urllib.parse import quote as url_quote
else:
    from urllib import quote as url_quote


if not PY2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


if not PY2:
    imap = map
else:
    from itertools import imap


xrange = range if not PY2 else xrange
