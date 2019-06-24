"""Helpers for python 2/3 compatibility"""

import sys

PY2 = sys.version_info[0] == 2


if not PY2:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser

if not PY2:
    from urllib.parse import quote as url_quote, unquote as url_unquote
    from urllib.parse import quote_plus, unquote_plus

else:
    from urllib import quote as url_quote
    from urllib import unquote as url_unquote
    from urllib import quote_plus, unquote_plus

if not PY2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

if not PY2:
    imap = map
    ifilter = filter
else:
    from itertools import imap
    from itertools import ifilter


if not PY2:
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

if not PY2:
    import pickle
else:
    try:
        import cPickle as pickle
    except ImportError:
        import pickle

xrange = range if not PY2 else xrange

if not PY2:
    text_type = str
    key_type = str
    unichr = chr
    binary_type = bytes
else:
    text_type = unicode
    key_type = basestring
    unichr = unichr
    binary_type = str
