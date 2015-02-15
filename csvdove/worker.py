import os, subprocess

try:
    from sqlite3 import dbapi2 as sqlite # python 2.5
except:
    try:
        from pysqlite2 import dbapi2 as sqlite
    except:
        print 'This program requires pysqlite2\n',\
            'http://initd.org/tracker/pysqlite/'
        sys.exit(1)

from main import to_str
        
class Worker(object):
    def __init__(self, data):
        self.data = data

    def main(self):
        restructure = Restructure()
        db = DB()

        for each_file in self.data.source_files:
            keeper_data = restructure.prune(each_file.schema_corr.keep, each_file.path)
            db.immigrate(keeper_data)
            
            db.add_cols( each_file.schema_corr.add )
            
            csv = db.emigrate().encode()
            
            renamed = restructure.rename_cols( each_file.schema_corr.match, csv )
            ordered = restructure.order(self.data.schema.target.cols, renamed)

            db.clear()
            # should the db deletion be in or out the loop? If it is
            # out-loop, there could be data mixing (db would not
            # simply be written over, but appended to etc?)
            
            # Need to figure out how to deal with multiple source
            # files of the same type. As it is, DB is created, used
            # and deleted for each file. This is probably simpler, but
            # might there be some benefit to grouping files of the
            # same src type together, and using one db table for them?
            # Also, i can use one DB for all the data, and separate
            # src types by table (or by file...), but is this desirable?
            
            # ...would use more disk space, for the db (but possibly
            # less RAM.) However, would require more RAM for the final
            # step, because writing operations could have to deal with
            # the output of several src files at once. As such, I
            # think each file should use a separate db file.

            # (Note this is doable only for sqlite, if another db
            # backend is used, there is only one db per system?)

            self.data.target_file.write(ordered)
            # Note. For stdout: putting this in-loop works, but
            # nothing is actually written out until all the loops have
            # finished. (Then the output for all the files shows up at
            # once.) This means that the entire output has to be held in memory.

            # Writing to sys.stdout must implement some sort of
            # buffer. Q: does writing to a file implement a buffer
            # too? But for a file, would this append like for stdout, or overwrite each time?

            # Conclusion: write (at least for stdout) in python
            # automatically implements a sequential process. So it
            # doesn't get overwritten.

            # This works for now; it is simpler to implement. However,
            # since it takes more RAM, it may be better to implement a
            # truly sequential process, write, process, write/append, etc

            # Also. I don't think using csvstack would make it any
            # simpler. It probably just implements a file write-append
            # that would be a python one-liner. However, look at the csvstack code for reference.

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
        self.name = 'csvdove_tmp_db.db'
        self.path = 'sqlite:///' + self.name

        #table* - derive for each sourcefile
        self.table = 'seamless'
    
    def clear(self):
        x = self.name
        if os.path.exists(x):
            os.remove(x)
        
    def immigrate(self, csv_data):
        self.clear() # delete the db iff it already exists
        cmd = 'csvsql --db %s --table %s --insert' % (self.path, self.table)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        p.communicate(input = csv_data)
        
    def emigrate(self):
        cmd = 'sql2csv --db %s --query \"select * from %s\"' % (self.path, self.table)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        return p.stdout.read()

    def add_cols(self, col_names_to_add):
        connection = sqlite.connect(self.name)
        cursor = connection.cursor()
        for col_name in col_names_to_add:
            sql_add_col = 'ALTER TABLE %s ADD COLUMN \"%s\"' % (self.table, col_name)
            # syntax: ALTER TABLE name ADD COLUMN name type
            # type=text. Quotes around name to deal with whitespace...
            cursor.execute(sql_add_col)

    def get_salvage_cols(self, salvage_info):
        pass
            
    def rename_cols(self, columns):
        # goddamn sqlite don't support this shit. So for now it's
        # implemented with python replace(), in Restructure
        '''connection = sqlite.connect(db.name)
        cursor = connection.cursor()
        ...
        #syntax: ALTER TABLE table_name RENAME COLUMN old_name to new_name;
        sql_rename_cols = 'ALTER TABLE %s RENAME COLUMN \"%s\" to \"%s\"' % (table, key, val)
        #cursor.execute(sql_rename_cols)
        '''
        pass

class Restructure(object):
    def __init__(self):
        pass

    def salvage(self):
        #implement salvage with csvcut (not db)
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
        #add missing (fill)
        pass

    def rename_cols(self, matching, data):
        '''rename the discrepancy headers
        matching: a list of lists that match [source, target] cols
        data: the csv-text data to operate on
        '''
        pairs = matching # i have to get a list of tuples from the list
        # prune out the ones that are already the same
        pruned = [ (key, val) for key, val in pairs if key != val ]
        header = data # maybe restrict this to just first line
        for key, val in pruned:
            # problem: replacing with commas like this means it will
            # not work on first or last column. Solution: use CSVHeader instead.
            k = ',' + key + ','
            v = ',' + val + ','
            header = header.replace(k, v, 1) # just replace once
        return header

    def order(self, ordering, data):
        # expects csv input with all requisite columns, in any order
        # returns csv data in desired order
        
        target_list = to_str(ordering)
        # fix this, prob use jisser
        cmd_cut_for_target = 'csvcut -c %s' % (target_list)
        p = subprocess.Popen(cmd_cut_for_target, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        output = p.communicate(input = data)[0] # first element is stdoutdata
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
        import handler

        # first, the target file
        t_header = handler.CSVHeader(open(target))
        if t_header == None:
            exit('Your target file needs to have some structure...')
        else:
            #make a target dict

            # derive the name attribute from the file name
            tn = os.path.splitext(os.path.basename(target))[0]
            
            tar = dict(
                name = tn,
                cols = t_header
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
            #s_num = s_num + 1  #not working...
            
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
                name = n,
                cols = header,
                primary_keys = pk,
                match =  [ [ms,mt] ] 
            )
            
            src_list.append(src)

        #make a dict combining that list with a target
        self.schema = dict(sources=src_list, target=tar)

    def dump(self):

        yaml.safe_dump(self.schema, os.sys.stdout, default_flow_style=False)




    
    
