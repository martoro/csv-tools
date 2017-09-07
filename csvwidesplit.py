#!/usr/bin/env python

"""Splits a wide csv file into several files. Each new file will have
a specified number of columns (a command line switch) except the last
file if the number of columns in the original file minus one is not
evenly divisible. Each new file will carry the header and first column.

For usage, run the program with the -h switch.
"""

import argparse
import csv
import os.path
import subprocess

class CsvWideSplit(object):

    def __init__(self, args):
        """Initialize csv split with commandline arguments.

        Args:
            args: command-line arguments from argparse.
        """
        self.args = args


    def compute_splits(self, header):
        """Compute number of chunks to split file into.
        The first column is carried in every split.

        Args:
            header: list, first row of csv file

        Returns:
            list of filenames for the split based on basename,
            e.g. base01.csv, base02.csv, etc.
        """
        ncols = (len(header)-1)
        if self.args.ncols <= 0:
            self.args.ncols = ncols
        quot = ncols // self.args.ncols
        nsplits =    quot if ncols % self.args.ncols == 0 else quot + 1
        basename = os.path.splitext(self.args.file)[0]
        ndigits = len(str(nsplits-1))
        splits = [basename + ("{0:0>%d}" % ndigits).format(i) + '.csv'
                for i in range(nsplits)]
        return splits


    def run(self):
        """Split input csv file into column groups.
        """
        rows = []
        with open(self.args.file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=self.args.delimiter)
            rows = [row for row in reader if not row[0].startswith('#')]

        # Write splits out.
        header = rows.pop(0)
        splits = self.compute_splits(header)
        for i, filename in enumerate(splits):
            l = i*self.args.ncols + 1
            r = l + self.args.ncols
            with open(filename, 'w') as ofile:
                writer = csv.writer(ofile, delimiter=self.args.delimiter)
                writer.writerow([''] + header[l:r])
                for row in rows:
                    writer.writerow(row[0:1] + row[l:r])

        if self.args.tex:
            self.csv2latex(splits)


    def csv2latex(self, splits):
        """Run csv2tex on the splits.

        Args:
            splits: list of files to run csv2latex on.
        """
        separator = {
            ','  : 'c',
            ';'  : 's',
            '\t' : 't',
            ' '  : 'p',
            ':'  : 'l'
        }[self.args.delimiter]
        for ifname in splits:
            ofname = os.path.splitext(ifname)[0] + '.tex'
            with open(ofname, 'w') as of:
                subprocess.check_call(
                    ['csv2latex', '-s', separator, '-n', '-r', '2', '-p', 'r',
                     '-e', '-c', '0.75', ifname],
                    stdout=of)


def main():
    """Parses command line arguments and runs csvwidesplit.
    """
    parser = argparse.ArgumentParser(description='Split csv in column groups.')
    parser.add_argument("file", help='csv file to split')
    parser.add_argument('-n', '--ncols', type=int, default=0,
                        help='number of columns per chunk')
    parser.add_argument('-d', '--delimiter', help='csv delimiter', default=',')
    parser.add_argument('-t', '--tex', action='store_true',
                        help='convert output chunks to .tex')
    args = parser.parse_args()
    CsvWideSplit(args).run()


if __name__ == "__main__":
        main()
