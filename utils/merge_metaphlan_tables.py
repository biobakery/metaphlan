#!/usr/bin/env python

import argparse
import os
import sys
import re
import pandas as pd
from itertools import takewhile

def merge( aaastrIn, ostm ):
    """
    Outputs the table join of the given pre-split string collection.

    :param  aaastrIn:   One or more split lines from which data are read.
    :type   aaastrIn:   collection of collections of string collections
    :param  iCol:       Data column in which IDs are matched (zero-indexed).
    :type   iCol:       int
    :param  ostm:       Output stream to which matched rows are written.
    :type   ostm:       output stream
    """

    listmpaVersion = set()
    merged_tables = pd.DataFrame()

    for f in aaastrIn:
        with open(f) as fin:
            headers = [x.strip() for x in takewhile(lambda x: x.startswith('#'), fin)]
     
        mpaVersion = list(filter(re.compile('#mpa_v[0-9]{2,}_CHOCOPhlAn_[0-9]{0,}').match, headers))
        if len(mpaVersion):
            listmpaVersion.add(mpaVersion[0])

        if len(listmpaVersion) > 1:
            print('merge_metaphlan_tables found tables made with different versions of the MetaPhlAn2 database.\nPlease re-run MetaPhlAn2 with the same database.\n')
            return

        iIn = pd.read_csv(f, 
                          sep='\t',
                          skiprows=len(headers),
                          names = headers[-1].split('#')[1].strip().split('\t'),
                          index_col=0
                        )

        merged_tables = pd.merge(merged_tables,
                                 iIn.iloc[:,0].rename(os.path.splitext(os.path.basename(f))[0]), 
                                 how='outer', 
                                 left_index=True, 
                                 right_index=True
                                )
        merged_tables.index.names = ['ID']

    if listmpaVersion:
        ostm.write(list(listmpaVersion)[0])

    ostm.write(merged_tables.fillna('0').reset_index().to_string(index=False))

argp = argparse.ArgumentParser( prog = "merge_metaphlan_tables.py",
    description = """Performs a table join on one or more metaphlan output files.""")
argp.add_argument( "aistms",    metavar = "input.txt", nargs = "+",
    help = "One or more tab-delimited text tables to join" )
argp.add_argument( '-o',    metavar = "output.txt", nargs = 1,
    help = "Name of output file in which joined tables are saved" )

__doc__ = "::\n\n\t" + argp.format_help( ).replace( "\n", "\n\t" )

argp.usage = argp.format_usage()[7:]+"\n\n\tPlease make sure to supply file paths to the files to combine. If combining 3 files (Table1.txt, Table2.txt, and Table3.txt) the call should be:\n\n\t\tpython merge_metaphlan_tables.py Table1.txt Table2.txt Table3.txt > output.txt\n\n\tA wildcard to indicate all .txt files that start with Table can be used as follows:\n\n\t\tpython merge_metaphlan_tables.py Table*.txt > output.txt"


def _main( ):
    args = argp.parse_args( )
    merge(args.aistms, sys.stdout)


if __name__ == "__main__":
    _main( )
