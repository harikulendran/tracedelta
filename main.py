from io import StringIO
import click
import pyperclip
import csv
import sys
from rich.console import Console
from rich.table import Table

READ = [ 'STDIN', 'CLIPBOARD' ]
WRITE = [ 'STDOUT', 'CLIPBOARD' ]
FORMAT = [ 'PRETTY', 'CSV', 'TSV' ]

def get_clipboard():
    data = pyperclip.paste()
    return csv.reader(StringIO(data), delimiter=',')

def get_stdin(data):
    return csv.reader(StringIO(data), delimiter=',')


def calculate_deltas(reader):
    # skip header
    next(reader, None)
    output_data = []

    previous_ts = 0
    cumulative_ts = 0
    for row in reader:
        tsr, msg = row
        ts = float(tsr)

        delta = 0 if previous_ts == 0 else ts - previous_ts
        cumulative_ts += delta
        output_data.append([delta, cumulative_ts, msg])
        previous_ts = ts

    return output_data


def write_csv(name, data):
    with open(name, "w+") as csv_out:
        writer = csv.writer(csv_out,delimiter=',')
        writer.writerow([ "duration(ms)", "cumulative duration(ms)", "message" ])
        writer.writerows(data)


def get_input(ctx, param, value):
    if value == 'STDIN':
        return get_stdin(click.get_text_stream('stdin').read())
    if value == 'CLIPBOARD':
        return get_clipboard()
    sys.exit('unsupported option')

@click.command()
@click.option('--read', default='clipboard', type=click.Choice(READ, case_sensitive=False),callback=get_input, help='Where to read input from')
@click.option('--write', default='stdout', type=click.Choice(WRITE, case_sensitive=False), help='Where to write output to')
@click.option('--format', default='pretty', type=click.Choice(FORMAT, case_sensitive=False), help='output format')
def run(read, write, format):
    delta_arr = calculate_deltas(read)

    if write == 'STDOUT':
        if format == 'PRETTY':
            pretty_print(delta_arr)
        else:
            delimiter = ',' if format == 'CSV' else '\t'
            output = get_csv(delta_arr, delimiter)
            print(output)
        sys.exit()

    if write == 'CLIPBOARD':
        delimiter = ',' if format == 'CSV' else '\t'
        output = get_csv(delta_arr, delimiter)
        pyperclip.copy(output)

def get_csv(arr, delimiter):
    r_out = StringIO()
    writer = csv.writer(r_out, delimiter=delimiter)
    writer.writerow([ "duration(ms)", "cumulative duration(ms)", "message" ])
    writer.writerows(arr)
    return r_out.getvalue()[:-2]

def pretty_print(arr):
    console = Console()
    table = Table()
    table.add_column("duration", no_wrap=True, min_width=10)
    table.add_column("cumulative", no_wrap=True, min_width=12)
    table.add_column("message", no_wrap=True)
    

    [ table.add_row(str(t),str(c),m, style=style(t)) for [t,c,m] in arr ]
    console.print(table)

def style(n):
    n = float(n)
    if n > 200:
        return 'red'
    if n > 100:
        return 'yellow'
    return ''

if __name__ == '__main__':
    run()
