"""
The 'get_discoveries' module can be used to retrieve the discoveries on the fly
from the terminal. It supports both the Sqlite and Postgres clients.

NOTE: Postgres is used by default. Please make sure that the environment
variables are exported.

usage: credentialdigger get_discoveries [-h] [--dotenv DOTENV]
                                        [--sqlite SQLITE]
                                        [--filename FILENAME]
                                        [--state STATE]
                                        [--save SAVE]
                                        [--with_rules]
                                        repo_url

positional arguments:
    repo_url            The url of the repo we want to retrieve the discoveries
                        from. Please make sure it has been scanned beforehand.

optional arguments:
    -h, --help          Show this help message and exit
    --dotenv DOTENV     The path to the .env file which will be used in all
                        commands. If not specified, the one in the current
                        directory will be used (if present)
    --sqlite SQLITE     If specified, get the discoveries using the sqlite
                        client, passing as argument the path of the db.
                        Otherwise, use postgres (must be up and running)
    --filename FILENAME Show only the discoveries contained in this file
    --state STATE       The state to filter discoveries on. Possible options:
                        [new, false_positive, addressing, not_relevant, fixed]'
    --save SAVE         If specified, export the discoveries to the path passed
                        as an argument instead of showing them on the terminal
    --with_rules        If specified, add the rule details to the discoveries

"""

import csv
import io
import json
import logging
import sys

import pandas as pd
from rich.console import Console
from rich.table import Table

from ..export.sarif_exporter import export_to_sarif

# Maximum number of discoveries to print. If repo has more discoveries,
# the user will be given the option to export said discoveries.
MAX_NUMBER_DISCOVERIES = 30

logger = logging.getLogger(__name__)
console = Console()


def configure_parser(parser):
    """ Configure arguments for command line parser.

    Parameters
    ----------
    parser: `credentialdigger.cli.customParser`
        Command line parser
    """
    parser.set_defaults(func=run)
    parser.add_argument(
        'repo_url', type=str,
        help='The url of the repo we want to retrieve the discoveries from')
    parser.add_argument(
        '--filename', default=None, type=str,
        help='Show only the discoveries contained in this file')
    parser.add_argument(
        '--state', default=None, type=str,
        help='The state to filter discoveries on. Possible options: \
            [new, false_positive, addressing, not_relevant, fixed]')
    parser.add_argument(
        '--save', default=None, type=str,
        help='Path of the file to which we export the discoveries')
    parser.add_argument(
        '--format', default='csv', choices=['csv', 'sarif'], type=str,
        help='Format of the exported file (csv or sarif). Default is csv.')
    parser.add_argument(
        '--with_rules', action='store_true',
        help='Return for each discovery its associated rule details')


def print_discoveries(discoveries, repo_url, with_rules):
    """ Print discoveries on the terminal in a tabular format.

    Parameters
    ----------
    discoveries: list
        List of the discoveries to be printed.
    repo_url: str
        The url of the repo from which we retrieved the discoveries
    with_rules: bool
        Enhance list of discoveries with rule details
    """
    with console.status(f'[bold]Processing {len(discoveries)} discoveries...'):
        discoveries_df = pd.DataFrame(discoveries)
        # Remove the repo_url column since it has been passed as an argument
        del discoveries_df['repo_url']
        # Remove timestamp and rule_id columns because they are not
        # quite relevant
        del discoveries_df['timestamp']
        del discoveries_df['rule_id']

        # Convert `int` columns to `str` to be eventually rendered.
        discoveries_df['id'] = discoveries_df['id'].astype(str)
        discoveries_df['line_number'] = discoveries_df['line_number'].astype(
            str)

        # Convert to list and insert column names
        discoveries_list = discoveries_df.values.tolist()
        columns = ['id', 'file_name', 'commit_id', 'line_number',
                   'snippet', 'state']
        if with_rules:
            columns.append('rule_regex')
            columns.append('rule_category')
            columns.append('rule_description')

        table = Table(title=f'Discoveries found in "{repo_url}"',
                      pad_edge=False,
                      show_lines=True)

        for c in columns:
            table.add_column(c)
        for row in discoveries_list:
            table.add_row(*row)

        console.print(table)


def discoveries_to_csv(discoveries):
    """ Generate CSV from list of discoveries.

    Parameters
    ----------
    discoveries: list
        List of discoveries from which to generate the CSV

    Returns
    -------
    str
        A string containing CSV obtained from the original list of discoveries
    """
    try:
        stringIO = io.StringIO()
        csv_writer = csv.DictWriter(stringIO, discoveries[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(discoveries)
        csv_data = stringIO.getvalue()
        return csv_data
    except IndexError as error:
        logger.error(error)
    except Exception as exception:
        logger.exception(exception)


def export_discoveries(discoveries, client, save=False, export_format='csv'):
    """ Export discoveries as a CSV or SARIF file.

    Parameters
    ----------
    discoveries: list
        List of discoveries to export
    client: `credentialdigger.Client`
        Instance of the client from which we retrieve rules
    save: bool or str
        If set, path to which export the file. Otherwise prompt the user.
    export_format: str
        Format to export ('csv' or 'sarif'). Default is 'csv'.
    """
    # If there were no discoveries, handle empty export gracefully
    if not save:
        path = ''
        while path == '':
            path = console.input(f'Path to export {export_format.upper()}:')
    else:
        path = save

    try:
        out_file = open(path, mode='w', encoding='utf-8')
    except IOError as e:
        console.print(f'[red]{e}\n'
                      '[bold][!] Failed to export discoveries.[/]')
    else:
        with out_file:
            with console.status(f'[bold]Exporting discoveries as {export_format.upper()}...'):
                if export_format.lower() == 'sarif':
                    rules = client.get_rules() if hasattr(client, 'get_rules') else None
                    sarif_dict = export_to_sarif(discoveries, rules=rules)
                    out_file.write(json.dumps(sarif_dict, indent=2))
                else:
                    data = discoveries_to_csv(discoveries) if discoveries else ''
                    out_file.write(data)
                console.print(
                    f'[bold][!] {len(discoveries)} discoveries have been '
                    f'exported successfully to {path}.')


def export_csv(discoveries, client, save=False):
    """ Backwards compatibility wrapper for export_csv. """
    export_discoveries(discoveries, client, save=save, export_format='csv')


def filter_discoveries(discoveries, state=None):
    """ Filter discoveries based on state.

    Parameters
    ----------
    discoveries: list
        List of discoveries to be filtered
    state: str, optional
        Consider only the discoveries to the specified state. Keep all the
        discoveries if the state is not specified

    Returns
    -------
    list
        The discoveries
    """
    if not state:
        return discoveries

    return list(filter(lambda d: d.get('state') == state, discoveries))


def run(client, args):
    """ Retrieve discoveries of a git repository and export them if needed.

    Parameters
    ----------
    client: `credentialdigger.Client`
        Instance of the client from which we retrieve results
    args: `argparse.Namespace`
        Arguments from command line parser.
    """
    discoveries = []
    try:
        discoveries = client.get_discoveries(
            repo_url=args.repo_url, file_name=args.filename, with_rules=args.with_rules)
    except Exception as e:
        console.print(f'[red]{e}[/]')

    # If --state is specified, filter the discoveries based on it
    if args.state is not None:
        discoveries = filter_discoveries(discoveries, args.state)

    export_format = getattr(args, 'format', 'csv')

    # if --save is specified, export the discoveries and exit
    if args.save is not None:
        export_discoveries(discoveries, client, save=args.save, export_format=export_format)
        sys.exit(len(discoveries))

    if len(discoveries) == 0:
        # if repo has no discoveries, exit
        console.print(f'[bold] {args.repo_url} has 0 discoveries.')
    elif len(discoveries) > MAX_NUMBER_DISCOVERIES:
        response = ''
        while response.upper() not in ['Y', 'N', 'YES', 'NO']:
            response = console.input(
                f'[bold]This repository has more than {MAX_NUMBER_DISCOVERIES}'
                ' discoveries, export them instead? (Y/N) ')
        if response.upper() in ['N', 'NO']:
            print_discoveries(discoveries, args.repo_url, args.with_rules)
        else:
            export_discoveries(discoveries, client, export_format=export_format)
    else:
        print_discoveries(discoveries, args.repo_url, args.with_rules)
        console.print(
            f'[bold] {args.repo_url} has {len(discoveries)} discoveries.')

    sys.exit(len(discoveries))
