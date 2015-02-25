import os, sys
import subprocess

try:
    from sqlite3 import dbapi2 as sqlite  # python 2.5
except:
    try:
        from pysqlite2 import dbapi2 as sqlite
    except:
        print 'This program requires pysqlite2\n',\
            'http://initd.org/tracker/pysqlite/'
        sys.exit(1)

from csvdove.__main__ import to_str
from tempfile import SpooledTemporaryFile
 
def stream2fobj(stream):
    """Takes a data stream and returns a file object. Temporary, for use
    transitioning the way Restructure works.
    """
    max_size = 9900
    fobj = SpooledTemporaryFile(max_size=max_size)
    fobj.write(stream)
    fobj.seek(0)
    return fobj

class Dovetail(object):

    def __init__(self, schema, src_files, output_file):

        self.schema = schema
        self.source_files = src_files
        self.output_file = output_file

    def main(self):
        restructure = Restructure()
        db = DB()

        for each_file in self.source_files:
            try:
                keeper_data = restructure.prune(
                    each_file.schema_corr.keep, each_file.path)
                db.immigrate(keeper_data)

                db.add_cols(each_file.schema_corr.add)
                csv = db.emigrate()

                renamed = restructure.rename_cols(each_file.schema_corr.match, csv)
                ordered = restructure.order(self.schema.target.cols, renamed)

                db.clear()
                # db deletion should be in-loop: db is only used to process each
                # src file

                self.output_file.write(ordered)
                
            except AttributeError as err:
                sys.stderr.write('File "%s" has no match in the schema, and will be skipped.\n' % each_file.path)

class DB(object):

    def __init__(self):
        '''
        os.path.abspath(path)
        os.path.expanduser(path)
        os.path.join(path, *paths)

        dbf = os.tmpfile()
        dbfn = os.path.abspath(dbf)

        or use: import tmpfile ?
        '''
        # should change this to use: tempfile.SpooledTemporaryFile
        # complication: get it to persist between calls
        self.name = 'csvdove_tmp_db.db'
        self.path = 'sqlite:///' + self.name
        #self.path = 'sqlite:///' + ':memory:'

        # table* - derive for each sourcefile
        self.table = 'seamless'

    def clear(self):
        x = self.name
        if os.path.exists(x):
            os.remove(x)

    def immigrate(self, csv_data):
        self.clear()  # delete the db iff it already exists
        cmd = 'csvsql --no-inference --db %s --table %s --insert' % (self.path, self.table)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        p.communicate(input=csv_data)

    # def immigrateBetter(self, csv_data):
    #     """(1) Use CSVQL to get create table statement.  (2) Execute create
    #     table statement on a tmpf db.  (3) use sqlalchemy directly,
    #     and csvkit's Table, to execute insert statement on tmpf db.
    #     (4) Use SQL2CSV to export this tmpf db as CSV.

    #     """
    #     from tempfile import SpooledTemporaryFile
    #     from csvkit.utilities.csvsql import CSVSQL

    #     # get a create table statement
    #     tmpf = SpooledTemporaryFile(max_size=1000) #how much?
    #     csvsql = CSVSQL(output_file=tmpf)
    #     csvsql.main()
    #     # extract this statement from the file
    #     create_table_statement = tmpf.read()


    #     cmd = 'csvsql --db %s --table %s --insert' % (self.path, self.table)
    #     p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
    #                          stdin=subprocess.PIPE, shell=True)
    #     p.communicate(input=csv_data)

    def emigrate(self):
        #         from csvkit.utilities.sql2csv import SQL2CSV
        # db needs to persists between immigrate(), add_cols() and
        # emigrate(). Solution: add file_obj args to these
        # functions. (Better: have them operate on self.file_obj)
        cmd = 'sql2csv --db %s --query \"select * from %s\"' % (
            self.path, self.table)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        return p.stdout.read()

    def add_cols(self, col_names_to_add):
        connection = sqlite.connect(self.name)
        cursor = connection.cursor()
        for col_name in col_names_to_add:
            sql_add_col = 'ALTER TABLE %s ADD COLUMN \"%s\"' % (
                self.table, col_name)
            # syntax: ALTER TABLE name ADD COLUMN name type
            # type=text. Quotes around name to deal with whitespace...
            cursor.execute(sql_add_col)

    def get_salvage_cols(self, salvage_info):
        pass
    

from csvkit import table

class Restructure(object):

    def __init__(self):
        pass

    def salvage(self):
        # implement salvage with csvcut (not db)
        pass

    def prune(self, keeper_list, file_name):
        '''get keepers
        Things of the sort: csvcut -c "Date","First Name" ./seamless.csv
        cmd = 'csvcut -c ' + keeper_list + ' ' + file_name
        '''
        keeper_list = to_str(keeper_list)
        # NOTE: i can move this operation to SQL
        cmd = 'csvcut -c %s %s' % (keeper_list, file_name)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        return p.stdout.read()

    def complement(self):
        # add missing (fill)
        pass

    def rename_cols(self, match, csv_text):
        """This function takes a match-list and a Table object. It returns a
        Table object with the column names changed.

        """

        tab = table.Table.from_csv(stream2fobj(csv_text))

        # don't bother renaming the cols that are already the same,
        # just the ones that differ.
        differing = [(src, tar) for src, tar in match if src != tar]
        
        # rename each column object in the table
        for (src, tar) in differing:
            for col in tab:
                if col.name == src:
                    col.name = tar

        #return tab

        with SpooledTemporaryFile(max_size=9900) as out_f:        
            # write out the header, and the text
            tab.to_csv(out_f)

            # return the both (header and data-text) together
            out_f.seek(0)
            return out_f.read()
        
    def order(self, ordering, data):
        # expects csv input with all requisite columns, in any order
        # returns csv data in desired order

        target_list = to_str(ordering)
        # fix this, prob use jisser
        cmd_cut_for_target = 'csvcut -c %s' % (target_list)
        p = subprocess.Popen(cmd_cut_for_target, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        output = p.communicate(input=data)[0]  # first element is stdoutdata
        return output


class Clean(object):

    '''
    cleanup
    case, bool
    split first last names etc
    lookup states?
    '''

    def __init__(self):
        pass

import yaml


class StarterSchemaGen(object):

    '''Generate a starter schema from CSV files --
    pattern one or more source files, and a target file.'''

    def __init__(self, target, sources):
        # get headers out of the CSV files...
        from csvdove import handler

        # first, the target file
        t_header = handler.CSVHeader(open(target))
        if t_header is None:
            exit('Your target file needs to have some structure...')
        else:
            # make a target dict

            # derive the name attribute from the file name
            tn = os.path.splitext(os.path.basename(target))[0]

            tar = dict(
                name=tn,
                cols=t_header
            )

        # next, make a list of src dicts
        src_list = []
        for src_file_path in sources:
            # for each source file:
            # (1) grab the header
            # (2) bundle up (in a dict) the header with other properties
            #     (other properties will have default values)
            csvfile = open(src_file_path)
            header = handler.CSVHeader(csvfile)

            # need to disambiguate names
            #s_num = 1
            n = os.path.splitext(os.path.basename(src_file_path))[0]
            #n = 'source_' + str(s_num)
            # s_num = s_num + 1  #not working...

            pk = [
                'A FEW COLUMNS FOR REFERENCE IN THE SALVAGE FILE',
                'Date',
                'First Name',
                'Last Name',
                'etc.'
            ]
            ms = 'NAME OF COLUMN IN SOURCE FILE'
            mt = 'NAME FOR CORRESPONDING COLUMN IN TARGET FORMAT'

            src = dict(
                name=n,
                cols=header,
                primary_keys=pk,
                match=[[ms, mt]]
            )

            src_list.append(src)

        # make a dict combining that list with a target
        self.schema = dict(sources=src_list, target=tar)

    def dump(self):

        yaml.safe_dump(self.schema, os.sys.stdout, default_flow_style=False)
