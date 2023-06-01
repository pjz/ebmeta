import sys
import json
import logging

import click

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
@click.argument('ebookname', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('keys', nargs=-1)
def get(ebookname, keys):
    '''
    get the value of the specified key, or all keys if unspecified
    '''
    book = MyBook.orExit(ebookname)

    if not keys:
        keys = book.all_meta_keys()

    for key in keys:
        book.show_key(key)


@cli.command()
@click.argument('ebookname', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def ls(ebookname):
    '''
    List interior files of the specified epub
    '''
    book = MyBook.orExit(ebookname)

    items = list(book.book.get_items())

    max_media_type_len = 0
    for item in items:
        max_media_type_len = max(max_media_type_len, len(item.media_type))

    for item in sorted(items, key=lambda i: i.get_name()):
        print(f'{ebookname} {item.media_type:<{max_media_type_len}} {item.get_name()}')


@cli.command()
@click.argument('ebookname', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def metadata(ebookname):
    '''
    List metadata of the specified epub
    '''
    book = MyBook.orExit(ebookname)
    print(json.dumps(book.metadata, sort_keys=True, indent=4))


@cli.command()
@click.argument('ebookname', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('key')
@click.argument('value')
def set_any(ebookname, key, value):
    '''set the value of one key

       KEY is of the form NAMESPACE:FIELD
       VALUE is eval'd by python
    '''
    val = eval(value)
    MyBook.set_and_save(ebookname, key, val)


@cli.command()
@click.argument('ebookname', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def get_series(ebookname):
    '''show the series'''
    MyBook.show_one_book_key(ebookname, 'calibre:series')


@cli.command()
@click.argument('ebookname', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('value')
def set_series(ebookname, value):
    '''set the series'''
    book = MyBook.orExit(ebookname)
    book.book.set_unique_metadata('calibre', 'series', str(value))
    book.save()

@cli.command()
@click.argument('ebookname', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('value', type=click.FLOAT)
def set_series_index(ebookname, value):
    '''set the series index'''
    book = MyBook.orExit(ebookname)
    book.book.set_unique_metadata('calibre', 'series_index', str(value))
    book.save()


@cli.command()
@click.argument('ebookname', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def rewrite(ebookname):
    '''load and save the book in order to upgrade the metadata to EPUB3'''
    MyBook(ebookname).save()


@cli.command()
@click.argument('ebookname', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('itemname')
def set_cover(ebookname, itemname):
    '''
    Set the cover to be the specified item inside the ebook. Item names can be seen with 'ebmeta ls'
    '''
    book = MyBook.orExit(ebookname)

    item = book.item_named(itemname)
    if item is None:
        print("No item found named {itemname!r}.  Nothing done.")
        sys.exit(1)

    book.set_cover_id(item.id)
    book.save()
    print(f"Cover set to {itemname!r}.")


def cli_wrapper():
    try:
        cli()  # pylint: disable=no-value-for-parameter
    except Exception as e:
        logging.debug("Crash! when called with args %r :", sys.argv, exc_info=e)
        print("Exception thrown.  Re-run with --debugall for details")


if __name__ == '__main__':
    cli_wrapper()
