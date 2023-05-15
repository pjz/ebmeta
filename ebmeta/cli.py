import sys
import logging

import click
from ebooklib import epub

from .model import MyBook

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

    for item in book.book.get_items():
        print(f'{filename} {item.get_name()} {item.media_type}')


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('key')
@click.argument('value')
def rawset(filename, key, value):
    '''set the value of one key

       KEY is of the form NAMESPACE:FIELD
       VALUE is eval'd by python
    '''

    val = eval(value)

    MyBook.set_and_save(filename, key, val)


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
def get_series(filename):
    MyBook.show_one_book_key(filename, 'calibre:series')


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('value')
def set_series(filename, value):
    key = 'calibre:series'
    val = [(None, {'name': key, 'content': str(value)})]

    MyBook.set_and_save(filename, key, val)


@cli.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False), required=True, nargs=1)
@click.argument('value', type=click.FLOAT)
def set_series_index(filename, value):
    key = 'calibre:series_index'
    val = [(None, {'name': key, 'content': str(value)})]

    MyBook.set_and_save(filename, key, val)




if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
