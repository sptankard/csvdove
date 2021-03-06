import os
import sys
import subprocess
#import six

from os.path import abspath, dirname, join

WHERE_AM_I = abspath(dirname(__file__))


class CSVDove(object):

    def __init__(self):
        import argparse

        desc = ''' CSV "dovetailing" utility.
        Dovetails CSV (comma-separated values) files according to
        custom-defined schema
        Schema configuration files must contain info on one or more
        source(s), and one target format.

        Mainly, it performs a realignment of the source columns:
        prunes, fills gaps, renames, and reorders.
        '''

        # extra
        '''
        It can also perform some extra cleanup operations on columns,
        including some built-in operations for dates etc., or
        applying any regexp.
        '''

        p = argparse.ArgumentParser(prog='csvdove', description=desc)

        #dove = parser.add_mutually_exclusive_group()

        # Maybe make --gen and --gui mutually exclusive. Also --gen
        # and -c. And -l vs everything else.

        p.add_argument(
            '-V, --version', action='version', version='%(prog)s 0.0.1')

        hgui = 'GUI mode'
        p.add_argument('--gui', action='store_true', help=hgui)

        hc = 'schema configuration file (.yml)'
        p.add_argument(
            '-c, --schema',
            metavar='SCHEMA',
            action='store',
            dest='schema',
            type=argparse.FileType('r'),
            help=hc)

        hs = ''' CSV file(s) to dovetail (or, if using --gen, to pattern as
        sources) '''
        p.add_argument('-s, --sources', metavar='SOURCE',
                       nargs='+', action='store', dest='sources', help=hs)
        # ? argparse.FileType('r')

        ho = 'file for CSV target output (on cli, defaults to STDOUT)'
        p.add_argument('-o', metavar='FILE', action='store',
                       dest='output', type=argparse.FileType('w'),
                       default=sys.stdout, help=ho)
        # filetype w +b?
        # or default=None, ?
        # CLI and GUI handle the default output differently. CLI sets
        # to sys.stdout, GUI generates a path.
        # But they should both accept the sysargs value if -o is
        # passed.

        # Note: -o should work with --gen and -l too.
        # as such, it is not just for CSV output

        hslvg = ''' file to output "salvaged", leftover data not carried over into
        target (default is to not produce) '''
        p.add_argument('--salvage', metavar='FILE', nargs=1,
                       action='store', dest='salvage',
                       type=argparse.FileType('w'),
                       # default should be NULL default=sys.stdout,
                       help=hslvg)

        hgen = ''' generate a starter schema from CSV files corresponding to desired
        source(s) and target format (requires -s and -t) '''
        p.add_argument('--gen', action='store_true',
                       help=hgen)

        ht = 'CSV file to pattern for target format (for use with --gen)'
        p.add_argument('-t, --target', metavar='TARGET',  # nargs=1,
                       action='store', dest='gen_t',
                       type=argparse.FileType('r'),
                       help=ht)

        hl = 'list the schemas that are cached for later use'
        p.add_argument('-l, --list-saved-schemas',
                       action='store_true', dest='list',
                       help=hl)

        self.args = p.parse_args()

    def main(self):
        if self.args.gui:
            print 'Starting in GUI mode'
            #from gui import GUI
            #GUI(c=self.args.schema, s=self.args.sources, t=self.args.target)
            # gui.main()

        elif self.args.gen:
            from worker import StarterSchemaGen
            gen = StarterSchemaGen(self.args.gen_t.name, self.args.sources)
            gen.dump()

        elif self.args.list:
            import data
            for fn in data.search_schemas_dir():
                print fn

        else:
            from cli import CLI
            cli = CLI(self.args.schema, self.args.sources, o=self.args.output)
            cli.main()


def to_str(a):
    str_enc = '\"'
    str_sep = '\",\"'  # sep is: ","
    result = str_enc + str_sep.join(a) + str_enc
    return result

if __name__ == '__main__':
    dove = CSVDove()
    dove.main()


# TODO
# use csvkit classes rather than cli utilities
# profile dir
# GUI

# detect input not conforming to source' schemas
