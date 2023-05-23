import sys
import json
import logging

import click
from ebooklib import epub

from . import logger
from .model import MyBook


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
    '''
    get the value of the specified key, or all keys if unspecified
    '''
    book = MyBook.orExit(filename)

    if not keys:
        keys = book.all_meta_keys()

    for key in keys:
        book.show_key(key)


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def ls(filename):
    '''
    List interior files of the specified epub
    '''
    book = MyBook.orExit(filename)

    items = list(book.book.get_items())

    max_media_type_len = 0
    for item in items:
        max_media_type_len = max(max_media_type_len, len(item.media_type))

    for item in sorted(items, key=lambda i: i.get_name()):
        print(f'{filename} {item.media_type:<{max_media_type_len}} {item.get_name()}')


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def metadata(filename):
    '''
    List metadata of the specified epub
    '''

    book = MyBook.orExit(filename)
    print(json.dumps(book.metadata, sort_keys=True, indent=4))


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('key')
@click.argument('value')
def set_any(filename, key, value):
    '''set the value of one key

       KEY is of the form NAMESPACE:FIELD
       VALUE is eval'd by python
    '''
    val = eval(value)

    MyBook.set_and_save(filename, key, val)


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def get_series(filename):
    '''show the series'''
    MyBook.show_one_book_key(filename, 'calibre:series')


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('value')
def set_series(filename, value):
    '''set the series'''
    book = MyBook.orExit(filename)
    book.book.set_unique_metadata('calibre', 'series', str(value))
    book.save()

@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('value', type=click.FLOAT)
def set_series_index(filename, value):
    '''set the series index'''
    book = MyBook.orExit(filename)
    book.book.set_unique_metadata('calibre', 'series_index', str(value))
    book.save()


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def rewrite(filename):
    '''load and save the book in order to upgrade the metadata to EPUB3'''
    MyBook(filename).save()


def cli_wrapper():
    try:
        return cli()  # pylint: disable=no-value-for-parameter
    except Exception as e:
        logging.debug("Crash! when called with args %r :", sys.argv, exc_info=e)
        print("Exception thrown.  Re-run with --debugall for details")


if __name__ == '__main__':
    cli_wrapper()
