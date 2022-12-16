import click

from src.session import start_session


@click.command()
@click.argument('port')
def start(port):
    start_session(port)


if __name__ == '__main__':
    start()
