#!/usr/bin/env python

"""Unittests for csvwidesplity.py.
"""

import os
import tempfile
import unittest

from csvwidesplit import CsvWideSplit
from namedlist import namedlist

class CsvWideSplitTest(unittest.TestCase):

    # Number of columns per chunk is set to negative.
    def test_compute_splits_ncols_negative(self):
        # Create mock args.
        Args = namedlist('Args', ['file', 'ncols'])
        args = Args(file='base.csv', ncols=-1)

        csvwidesplit = CsvWideSplit(args)

        # Test.
        header = ['field1', 'field2', 'field3']
        split = csvwidesplit.compute_splits(header)
        self.assertEqual(1, len(split))


    # Number of columns per chunk is set to 0.
    def test_compute_splits_ncols_0(self):
        # Create mock args.
        Args = namedlist('Args', ['file', 'ncols'])
        args = Args(file='base.csv', ncols=0)

        csvwidesplit = CsvWideSplit(args)

        # Test.
        header = ['field1', 'field2', 'field3']
        split = csvwidesplit.compute_splits(header)
        self.assertEqual(1, len(split))


    # The first column is carried in every split.
    def test_compute_splits_col1_carry(self):
        # Create mock args.
        Args = namedlist('Args', ['file', 'ncols'])
        args = Args(file='base.csv', ncols=2)

        csvwidesplit = CsvWideSplit(args)

        # Test.
        header = ['field1', 'field2', 'field3']
        split = csvwidesplit.compute_splits(header)
        self.assertEqual(1, len(split))


    # Split results in more than 1 chunk.
    def test_compute_splits_multiple_chunks(self):
        # Create mock args.
        Args = namedlist('Args', ['file', 'ncols'])
        args = Args(file='base.csv', ncols=1)

        csvwidesplit = CsvWideSplit(args)

        # Test.
        header = ['field1', 'field2', 'field3']
        split = csvwidesplit.compute_splits(header)
        self.assertEqual(2, len(split))


    # Test file naming of csv chunks. Single digit in name suffices.
    def test_compute_splits_name_single_digit(self):
        # Create mock args.
        Args = namedlist('Args', ['file', 'ncols'])
        args = Args(file='base.csv', ncols=1)

        csvwidesplit = CsvWideSplit(args)

        # Test.
        header = ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
                  'f11']
        split = csvwidesplit.compute_splits(header)
        self.assertEqual(10, len(split))
        self.assertEqual('base0.csv', split[0])


    # Test file naming of csv chunks. Two digits in name necessary.
    def test_compute_splits_name_two_digits(self):
        # Create mock args.
        Args = namedlist('Args', ['file', 'ncols'])
        args = Args(file='base.csv', ncols=1)

        csvwidesplit = CsvWideSplit(args)

        # Test.
        header = ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
                  'f11', 'f12']
        split = csvwidesplit.compute_splits(header)
        self.assertEqual(11, len(split))
        self.assertEqual('base00.csv', split[0])
        self.assertEqual('base10.csv', split[10])


    # Test splitting a simple csv file.
    def test_run(self):
        # Write test data.
        icsv_path  = tempfile.mkstemp(suffix='.csv')[1]
        with open(icsv_path, 'w') as icsv:
            icsv.write('# Some comment\n')
            icsv.write(',f1,f2\n')
            icsv.write('sim1,1,2\n')

        # Create mock args.
        Args = namedlist('Args', ['file', 'ncols', 'delimiter', 'tex'])
        args = Args(file=icsv_path, ncols=1, delimiter=',', tex=False)

        # Test.
        csvwidesplit = CsvWideSplit(args)
        csvwidesplit.run()
        csv1_file = args.file.replace('.csv', '0.csv')
        with open(csv1_file, 'r') as csv1:
            self.assertEqual(',f1', csv1.readline()[:-1])
            self.assertEqual('sim1,1', csv1.readline()[:-1])
        csv2_file = args.file.replace('.csv', '1.csv')
        with open(csv2_file, 'r') as csv2:
            self.assertEqual(',f2', csv2.readline()[:-1])
            self.assertEqual('sim1,2', csv2.readline()[:-1])


    def test_csv2latex(self):
        # Write test data.
        icsv_path  = tempfile.mkstemp(suffix='.csv')[1]
        with open(icsv_path, 'w') as icsv:
            icsv.write('# Some comment\n')
            icsv.write(',f1,f2\n')
            icsv.write('sim1,1,2\n')

        # Create mock args.
        Args = namedlist('Args', ['delimiter'])
        args = Args(delimiter=',')

        # Test.
        csvwidesplit = CsvWideSplit(args)
        csvwidesplit.csv2latex([icsv_path])
        otex_path = icsv_path.replace('.csv', '.tex')
        self.assertTrue(os.path.isfile(otex_path))


if __name__ == '__main__':
    unittest.main()
