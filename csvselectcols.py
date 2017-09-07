#!/usr/bin/env python

"""For usage see args_parser().
"""

import argparse
import csv
import numpy
import pandas
import sys


def args_parser(usage):
    """Parse command line arguments.

    Args:
      usage: str, program usage.
    Returns:
      ArgumentParser from the argparse module.
    """
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument(
        '--columns', default='',
        help='Columns to select/drop.')
    parser.add_argument(
        '--complement', type=str_to_bool, nargs='?', const=True,
        default=False,
        help='If true, the given columns will be dropped.')
    parser.add_argument(
        '--input-delimiter', default=',',
        help='Delimiter in the input csv file.')
    parser.add_argument(
        '--output-delimiter', default='',
        help='If empty, elimiter in the input csv file will be preserved in ' +
        'the output.')
    parser.add_argument(
        '--pandas', type=str_to_bool, nargs='?', const=True,
        default=True,
        help='Use pandas for the conversion. Faster than csv reader/writer, ' +
        'but reads the entire input in memory.')
    parser.add_argument(
        '--round', type=int, default=-1,
        help='If positive, number of decimal digits to round numeric values ' +
        'to.')
    return parser


def str_to_bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def header_indices(header, columns):
    """Find the indices in the header of the given columns.

    Args:
      header: List of all column names in the csv file.
      columns: List of columns to select/drop.

    Return:
      List of indices.
    """
    ret = []
    for i, v in enumerate(header):
        n = len(ret)
        if n >= len(columns):
            break
        if v == columns[n]:
            ret.append(i)
    return ret


def set_diff(univ, subs):
    """Compute univ - subs.

    Preserves the order.

    Args:
      univ: list, entire set
      subs: list, subset

    Return:
      list, univ - subs
    """
    return [c for c in univ if c not in set(subs)]


def check_columns(subs, columns):
    """Check if the given set of columns is available in the set of columns.

    Exit on error.

    Args:
      subs: list, columns to select/drop.
      columns: list, the columns in the csv file.

    Return:
      void. Exit on error.
    """
    diff = set_diff(subs, columns)
    if diff:
        print('The following columns are not present. Exiting.',
              file=sys.stderr)
        print(diff, file=sys.stderr)
        sys.exit(1)


def csv_select_cols_pandas(columns):
    """Select csv columns using pandas.

    Args:
      columns: list of columns to select/drop (based on args).

    Return:
      void
    """
    # Do not read a column as an index.
    df = pandas.read_csv(sys.stdin, sep=args.input_delimiter,
                         index_col=False)
    check_columns(columns, df.columns)
    if args.complement:
        columns = set_diff(df.columns, columns)
    df = df[columns]
    if args.round >= 0:
        df = df.round(args.round)
    df.to_csv(sys.stdout, sep=args.output_delimiter, index=False)


class unix_excel(csv.excel):
    """Define a dialect to prevent csv writer from writing '\r\n'.
    """
    lineterminator = '\n'


def round_row(row):
    """Round numeric entries of row.

    Modifies row in place.

    Args:
      row: array-like, row in the csv file.

    Return:
      void
    """
    for i in range(len(row)):
        try:
            int(row[i])
        except:
            try:
                f = float(row[i])
                row[i] = round(f, args.round)
            except:
                pass


def csv_select_cols(columns):
    """Select csv columns row by row.

    Args:
      columns: list of columns to select/drop (based on args).

    Return:
      void
    """
    writer = csv.writer(sys.stdout, delimiter=args.input_delimiter,
                        dialect=unix_excel)
    header = True
    indices = []
    for row in csv.reader(sys.stdin, delimiter=args.output_delimiter):
        if header:
            check_columns(columns, row)
            if args.complement:
                columns = set_diff(row, columns)
            indices = header_indices(row, columns)
            header = False
        row = numpy.array(row)[indices]
        round_row(row)
        writer.writerow(row)


def main(args):
    """Select columns from csv file.

    Args:
      args: args from argparse module.
    """
    if not args.output_delimiter:
        args.output_delimiter = args.input_delimiter
    columns = args.columns.strip().split(',')

    if args.pandas:
        csv_select_cols_pandas(columns)
    else:
        csv_select_cols(columns)


if __name__ == '__main__':
    usage = """Select columns from a csv file.
    Read from stdin and write to stdout.
    """
    args = args_parser(usage).parse_args()
    main(args)
