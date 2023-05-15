import os
import sys
import logging
import zipfile
import tempfile
from typing import NamedTuple, List

from ebooklib import epub
from lxml.etree import XMLSyntaxError

logger = logging.getLogger(__name__)

REVNAMESPACE = {url: ns for ns, url in epub.NAMESPACES.items()}


class NSKey(NamedTuple):
    ns: str
    key: str

    @classmethod
    def fromKey(cls, key: str):
        '''normalize a key into an NSKey'''
        if ':' in key:
            return cls(*key.rsplit(':', 1))
        else:
            return cls(None, key)

    def asKey(self):
        ns: str = '' if self.ns is None else epub.NAMESPACES.get(self.ns, self.ns)
        return f'{ns}:{self.key}'


class MyBook:

    def __init__(self, filename: str):
        self.filename = filename
        self.book = epub.read_epub(self.filename)
        logger.debug(f'Book {filename} {self.book.metadata!r}')

    @property
    def metadata(self):
        return self.book.metadata

    @classmethod
    def orExit(cls, filename: str, exitmsg: str = None, exitcode: int = 1) -> "MyBook":
        '''
        Open the file successfully as an epub, or exit
        '''
        err = None
        try:
            return cls(filename)
        except (epub.EpubException, zipfile.BadZipFile) as e:
            msg, err = f'Cannot open {filename}', e
        except XMLSyntaxError as e:
            msg, err = f'{filename} has malformed XML', e

        # success returned from inside the try:, so this is only on exceptions

        logger.debug('%s: ', msg, exc_info=err)
        if exitmsg is None:
            exitmsg = f'{msg}. Exiting.'
        print(exitmsg)
        sys.exit(exitcode)

    @classmethod
    def show_one_book_key(cls, filename: str, key: str, ns: str = None, k: str = None) -> "MyBook":
        book = cls.orExit(filename)
        book.show_key(key, ns, k)
        return book

    def save(self) -> None:
        tempfh = tempfile.NamedTemporaryFile()
        tempname = tempfh.name
        tempfh.close()

        epub.write_epub(tempname, self.book)
        try:
            os.rename(tempname, self.filename)
        except PermissionError:
            print(f"PermissionError: can't write to {self.filename}")

    def rawset_meta(self, ns: str, k: str, val) -> None:
        self.book.metadata[ns] = self.book.metadata.get(ns, {})
        self.book.metadata[ns][k] = val

    @classmethod
    def rawset_and_save(cls, filename: str, ns: str, k: str, val) -> None:
        book = cls.orExit(filename)
        book.rawset_meta(ns, k, val)
        book.save()

    @classmethod
    def set_and_save(cls, filename: str, key: str, val) -> None:
        book = cls.orExit(filename)
        nsk = NSKey.fromKey(key)
        book.rawset_meta(nsk.ns, nsk.key, val)
        book.save()

    def all_meta_keys(self) -> List[str]:
        keys = []
        for url, kv in self.book.metadata.items():
            ns = REVNAMESPACE.get(url, url)
            for k in kv:
                keys.append(f'{ns}:{k}')
        return keys

    def show_key(self, key: str, ns: str = None, k: str = None) -> None:
        if k is None:
            nsk = NSKey.fromKey(key)
        else:
            nsk = NSKey(ns, k)
        try:
            value = self.book.get_metadata(*nsk)
        except KeyError as e:
            value = '<Key Not Found>'
            logger.debug("File: %s has no key %s:%s - ", self.filename, nsk.ns, nsk.key, exc_info=e)
        print(f'{self.filename} {key} {value}')
