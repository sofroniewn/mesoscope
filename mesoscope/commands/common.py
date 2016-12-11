import click

def success(msg):
    click.echo('[' + click.style('success', fg='green') + '] ' + msg)

def status(msg):
    click.echo('[' + click.style('convert', fg='blue') + '] ' + msg)

def error(msg):
    click.echo('[' + click.style('error', fg='red') + '] ' + msg)

def warn(msg):
    click.echo('[' + click.style('warn', fg='yellow') + '] ' + msg)

def setup_spark(master):
    if master:
        status('configuring spark cluster')
        from pyspark import SparkContext
        context = SparkContext(master=master)
        return context
    else:
        return None