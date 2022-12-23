import click
import colorama

from . import bridge

colorama.init()


@click.group()
def main():
    pass


@main.command()
@click.argument('port')
def start(port):
    bridge.start(port)
