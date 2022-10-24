import os
import sys
import logging
import tempfile

import click
from ebooklib import epub

REVNAMESPACE = { url:ns for ns, url in epub.NAMESPACES.items() }

logger = logging.getLogger(__name__)

def stderr_handler():
    handler = logging.StreamHandler(stream=sys.stderr)
    formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    return handler

logger.addHandler(stderr_handler())

@click.group()
@click.option('--debug', is_flag=True, default=False, help='enable debug output for ebmeta')
@click.option('--debugall', is_flag=True, default=False, help='enable debug output for everything')
def cli(debug, debugall):
    if debug:
        logger.setLevel(logging.DEBUG)
    if debugall:
        logging.getLogger('').setLevel(logging.DEBUG)






@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('keys', nargs=-1)
def get(filename, keys):
    '''get the value of one key'''

    book = epub.read_epub(filename)
    logger.debug(f'Book {filename} {book.metadata!r}')

    if not keys:
        keys = []
        for url, kv in book.metadata.items():
            ns = REVNAMESPACE.get(url, url)
            for k in kv:
                keys.append(f'{ns}:{k}')

    for key in keys:
        if ':' in key:
            ns, k = key.rsplit(':', 1)
        else:
            ns, k = None, key

        show_one_key(filename, book, key, ns, k)


def show_one_key(filename, book, key, ns, k):
    try:
        value = book.get_metadata(ns, k)
    except KeyError as e:
        value = 'Key Not Found'
        logger.exception(e)
    print(f'{filename} {key} {value}')


def show_one_book_key(filename, key, ns, k):
    book = epub.read_epub(filename)
    show_one_key(filename, book, key, ns, k)
    

@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def ls(filename):

    book = epub.read_epub(filename)
    for item in book.get_items():
        print(f'{filename} {item.get_name()} {item.media_type}')


def set_raw_bookmeta(book, ns, k, val):
    book.metadata[ns] = book.metadata.get(ns, {})
    book.metadata[ns][k] = val


def update_book(filename, book):
    tempfh = tempfile.NamedTemporaryFile()
    tempname = tempfh.name
    tempfh.close()

    epub.write_epub(tempname, book)
    try:
        os.rename(tempname, filename)
    except PermissionError:
        print(f"PermissionError: can't write to {filename}")


def update_book_metadata(filename, ns, k, val):
    book = epub.read_epub(filename)
    set_raw_bookmeta(book, ns, k, val)
    update_book(filename, book)





@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('key')
@click.argument('value')
def rawset(filename, key, value):
    '''set the value of one key

       KEY is of the form NAMESPACE:FIELD
       VALUE is eval'd by python
    '''

    if ':' in key:
        ns, k = key.split(':', 1)
    else:
        ns, k = None, key

    ns = epub.NAMESPACES.get(ns, ns)
    val = eval(value)
    
    update_book_metadata(filename, ns, k, val)



@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def get_series(filename):
    ns, k = 'calibre', 'series'
    show_one_book_key(filename, k, ns, k)


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('value')
def set_series(filename, value):
    ns, k = 'calibre', 'series'
    val = [(None, {'name': f'{ns}:{k}', 'content': str(value)})]

    update_book_metadata(filename, ns, k, val)


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('value', type=click.FLOAT)
def set_series_index(filename, value):
    ns, k = 'calibre', 'series_index'
    val = [(None, {'name': f'{ns}:{k}', 'content': str(value)})]

    update_book_metadata(filename, ns, k, val)






if __name__ == '__main__':
    cli()
