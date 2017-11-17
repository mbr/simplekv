# coding=utf-8
from simplekv.transform.transformer import Pipe
from util import gen_random_bytes
import pytest


try:
    from simplekv.transform.encrypt import Encrypt, \
        _KeepNLast, MAC_NBYTES, NONCE_NBYTES, InvalidSignature
except ImportError:
    pytestmark = pytest.mark.skip(reason='needs cryptography')


def test_keep_nlast():
    t = _KeepNLast(5)
    testdata = b'1234567890'
    assert t.transform(testdata) == b'12345'
    assert t.finalize() == b'67890'


def test_keep_nlast2():
    t = _KeepNLast(5)
    testdata = gen_random_bytes(100)
    assert t.transform(testdata) == testdata[:-5]
    assert t.finalize() == testdata[-5:]


def test_keep_nlast3():
    t = _KeepNLast(5)
    testdata = gen_random_bytes(100)
    output = b''
    for i in range(len(testdata)):
        output += t.transform(testdata[i:i + 1])
    assert output == testdata[:-5]
    assert t.finalize() == testdata[-5:]


def test_str():
    assert str(Encrypt('')) == 'Encrypt'


def test_roundtrip():
    key = Encrypt.generate_encryption_key()
    p = Encrypt(key)
    pipe = Pipe([p.transformer(), p.inverse()])
    testdata = b'ldgroijgr'
    assert pipe.transform(testdata) + pipe.finalize() == testdata


def test_roundtrip_segments():
    key = Encrypt.generate_encryption_key()
    p = Encrypt(key)
    pipe = Pipe([p.transformer(), p.inverse()])
    testdata = b'ldgroijgr'
    output = b''
    for _ in range(10):
        output += pipe.transform(testdata)
    output += pipe.finalize()
    assert output == testdata * 10


def test_roundtrip_empty():
    key = Encrypt.generate_encryption_key()
    p = Encrypt(key)
    pipe = Pipe([p.transformer(), p.inverse()])
    testdata = b''
    assert pipe.transform(testdata) + pipe.finalize() == testdata


def test_structure():
    key = Encrypt.generate_encryption_key()
    p = Encrypt(key)
    enc = p.transformer()
    testdata = b'ldgroijgr'
    encrypted = enc.transform(testdata) + enc.finalize()
    assert len(encrypted) == 4 + NONCE_NBYTES + len(testdata) + MAC_NBYTES
    assert encrypted[:4] == b'SCR\0'


def test_wrong_header():
    key = Encrypt.generate_encryption_key()
    p = Encrypt(key)
    enc = p.transformer()
    testdata = b'ldgroijgr'
    encrypted = enc.transform(testdata) + enc.finalize()
    encrypted = b'X' + encrypted[1:]
    dec = p.inverse()
    with pytest.raises(ValueError) as ex:
        dec.transform(encrypted) + dec.finalize()
    assert 'header' in str(ex.value)


def test_message_too_short():
    key = Encrypt.generate_encryption_key()
    p = Encrypt(key)
    enc = p.transformer()
    testdata = b''
    encrypted = enc.transform(testdata) + enc.finalize()
    encrypted = encrypted[:-1]
    dec = p.inverse()
    with pytest.raises(ValueError) as ex:
        dec.transform(encrypted) + dec.finalize()
    assert 'eof' in str(ex.value)


def _bitflip(c):
    return bytes([ord(c) ^ 1])


def test_tamper_nonce():
    key = Encrypt.generate_encryption_key()
    p = Encrypt(key)
    enc = p.transformer()
    testdata = b'ldgroijgr'
    encrypted = enc.transform(testdata) + enc.finalize()
    encrypted = encrypted[:4] + _bitflip(encrypted[4:5]) + encrypted[5:]
    dec = p.inverse()
    with pytest.raises(InvalidSignature):
        dec.transform(encrypted) + dec.finalize()


def test_tamper_data():
    key = Encrypt.generate_encryption_key()
    p = Encrypt(key)
    enc = p.transformer()
    testdata = b'ldgroijgr'
    encrypted = enc.transform(testdata) + enc.finalize()
    pos = 4 + NONCE_NBYTES + 2
    encrypted = (
        encrypted[:pos] + _bitflip(encrypted[pos:pos + 1]) +
        encrypted[pos + 1:])
    dec = p.inverse()
    with pytest.raises(InvalidSignature):
        dec.transform(encrypted) + dec.finalize()


def test_tamper_mac():
    key = Encrypt.generate_encryption_key()
    p = Encrypt(key)
    enc = p.transformer()
    testdata = b'ldgroijgr'
    encrypted = enc.transform(testdata) + enc.finalize()
    encrypted = encrypted[:-1] + _bitflip(encrypted[-1:])
    dec = p.inverse()
    with pytest.raises(InvalidSignature):
        dec.transform(encrypted) + dec.finalize()
