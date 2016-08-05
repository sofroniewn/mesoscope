import click

settings = dict(help_option_names=['-h', '--help'])
from .commands.convert import convert_command

@click.group(options_metavar='', subcommand_metavar='<command>', context_settings=settings)
def cli():
    """
    This is a tool for working with data from the two-photon random access mesoscope. 
    Check out the list of commands to see what you can do.
    """

cli.add_command(convert_command)