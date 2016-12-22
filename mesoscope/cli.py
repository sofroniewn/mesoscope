import click

settings = dict(help_option_names=['-h', '--help'])
from .commands.convert import convert_command
from .commands.summarize import summarize_command
from .commands.register import register_command
from .commands.regions import regions_command
from .commands.extract import extract_command
from .commands.bidi import bidi_command

@click.group(options_metavar='', subcommand_metavar='<command>', context_settings=settings)
def cli():
    """
    This is a tool for working with data from the two-photon random access mesoscope.
    Check out the list of commands to see what you can do.
    """

cli.add_command(convert_command)
cli.add_command(summarize_command)
cli.add_command(register_command)
cli.add_command(regions_command)
cli.add_command(extract_command)
cli.add_command(bidi_command)
