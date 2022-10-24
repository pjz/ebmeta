
import logging

import click
from ebooklib import epub


logger = logging.getLogger(__name__)

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
    if not keys:
        keys = (i.get_id() for i in book.get_items())
    for key in keys:
        if ':' in key:
            ns, k = key.split(':', 1)
        else:
            ns, k = None, key

        try:
            value = book.get_metadata(ns, k)
        except KeyError:
            value = None
        print(f'{filename} {key} {value}')



@cli.command()
@click.argument('key')
@click.argument('value')
def set(ctx, key, value):
    '''set the value of one key'''


if __name__ == '__main__':
    cli()
