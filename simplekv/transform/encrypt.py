# coding=utf-8
from .transformer import Transformer, TransformerPair
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend

import os
import io

MAC_NBYTES = 32
KEY_NBYTES = 32
NONCE_NBYTES = 16


_FILE_HEADER = b'SCR\0'


# re-export exception raised in case of validation failure (meke flake8 happy)
InvalidSignature = InvalidSignature


class EncryptingTransformer(Transformer):

    def __init__(self, nonce, encryptor, hmac):
        """

        :param encryptor: the cryptography CipherContext to use for encryption
        :param hmac: the cryptography hmac to use for hashinh
        """
        self.encryptor = encryptor
        self.hmac = hmac
        self.nonce = nonce
        self._header_sent = False

    def transform(self, data):
        encrypted = self.encryptor.update(data)
        if not self._header_sent:
            self._header_sent = True
            retval = _FILE_HEADER + self.nonce + encrypted
        else:
            retval = encrypted
        self.hmac.update(retval)
        return retval

    def finalize(self):
        encrypted = self.encryptor.finalize()
        self.hmac.update(encrypted)
        mac = self.hmac.finalize()
        return encrypted + mac


class _KeepNLast(Transformer):
    """
    A transformer that does not change data, but always keeps the
    trailing n bytes, which are emitted by finalize.

    This is a useful helper transformer for formats that use a
    fixed-size trailer that requires special handling.
    """

    def __init__(self, n):
        self.n = n
        self._buffer = b''

    def transform(self, data):
        self._buffer += data
        # retval will be empty if buffer is too small, which is OK
        retval = self._buffer[:-self.n]
        self._buffer = self._buffer[-self.n:]
        return retval

    def finalize(self):
        rv = self._buffer
        # remove self._buffer so use-after-finalize can be easier detected
        del self._buffer
        return rv


class DecryptingTransformer(Transformer):

    def __init__(self, dec_factory, hmac):
        """

        :param dec_factory: a callable that, when called with the
           nonce, yields a decrypting CipherContext
        :param hmac: the cryptography hmac to use for hashing
        """
        self.dec_factory = dec_factory
        self.hmac = hmac
        self._header_buffer = io.BytesIO()
        self._header_complete = False
        self._mac_buffer = None
        self._dec = None
        self._keeper = _KeepNLast(MAC_NBYTES)

    def transform(self, data):
        if not self._header_complete:
            self._header_buffer.write(data)
            if self._header_buffer.tell() >= len(_FILE_HEADER) + NONCE_NBYTES:
                self._header_complete = True
                self._header_buffer.seek(0)
                file_header = self._header_buffer.read(len(_FILE_HEADER))
                if file_header != _FILE_HEADER:
                    raise ValueError("data does not start with "
                                     "expected file header {!r}".
                                     format(_FILE_HEADER))
                nonce = self._header_buffer.read(NONCE_NBYTES)
                self._dec = self.dec_factory(nonce)
                self.hmac.update(file_header + nonce)
                # the data after the header:
                data = self._header_buffer.read()
        # note that the 'not self._header_complete' block can set
        # this flag (and modify 'data'), so this is not the same as 'else'
        if self._header_complete:
            # `data` could include (part of) the mac, so feed
            # everything through the keeper:
            data = self._keeper.transform(data)
            self.hmac.update(data)
            return self._dec.update(data)

    def finalize(self):
        trailing_mac = self._keeper.finalize()
        if len(trailing_mac) < MAC_NBYTES:
            raise ValueError("unexpected eof (not enough for trailing mac)")
        self.hmac.verify(trailing_mac)
        decrypted = self._dec.finalize()
        return decrypted


class Encrypt(TransformerPair):
    """
    Encrypt/Decrypt data

    This class requires the
    `cryptography <https://pypi.python.org/pypi/cryptography>`_ package,
    which has to be installed separately (it is not a requirement
    of the ``simplekv`` package).

    Algorithm: AES with 256bit key in CTR mode for encryption,
    HMAC with sha256 for authentication, using encrypt-then-mac.

    Data structure of encrypted data:

     1. 4 bytes: file header; to be used for versioning. Right now,
        there is only one version which uses ``b'SCR\\0'``
     2. NONCE_NBYTES (16) the nonce, randomly generated for each
        stored key
     3. n bytes of encrypted data, using AES256 with the ``encryption_key``
        provided in the initializer using the CTR mode with the nonce
     4. MAC_NBYTES (32) the HMAC: sha256-based, computed over 1.-3.

    :param encryption_key: the key to use for encryption / decryption. Must
       be a ``bytes`` object of length ``KEY_NBYTES`` (32), ideally completely
       random. You can use
       :meth:`~simplekv.transform.Encrypt.generate_encryption_key` to generate
       a suitable new key.
    """

    def __init__(self, encryption_key):
        backend = default_backend()

        def cipher_factory(nonce):
            return Cipher(algorithms.AES(encryption_key),
                          modes.CTR(nonce),
                          backend=backend
                          )

        def hmac_factory():
            return hmac.HMAC(encryption_key, hashes.SHA256(), backend=backend)

        self.cipher_factory = cipher_factory
        self.hmac_factory = hmac_factory

    @staticmethod
    def generate_encryption_key():
        """
        Generate a random key suitable as ``encryption_key``
        """
        return os.urandom(KEY_NBYTES)

    def transformer(self):
        nonce = os.urandom(NONCE_NBYTES)
        enc = self.cipher_factory(nonce).encryptor()
        hmac = self.hmac_factory()
        return EncryptingTransformer(nonce, enc, hmac)

    def inverse(self):
        def decryptor_factory(nonce):
            return self.cipher_factory(nonce).decryptor()
        hmac = self.hmac_factory()
        return DecryptingTransformer(decryptor_factory, hmac)

    def __str__(self):
        return 'Encrypt'
