
class WrapKits(object):
    '''
    csvkit vs csv
    
    csvkit replaces csv.reader():
    csvkit.py2.reader()
    csvkit.py3.reader()
    In csvkit.__init__, these are abstracted to csv.reader()
    (according to version).
    
    csvkit replaces csv.Sniffer().sniff:  
    csvkit.sniffer.sniff_dialect()
    
    But csvkit does not replace csv.Sniffer().has_header
    '''
    
    def __init__(self):
        import csv
        self.Sniffer = csv.Sniffer

        import csvkit
        self.reader = csvkit.__init__.__self__.reader

        # Also works:
        #from csvkit.__init__ import reader
        #self.reader = reader

# this is not pretty but it works
csv = WrapKits()

class CSV(object):
    '''
    Instantiate this on a (CSV-formatted) file object.
    Returns a data structure representing the CSV:
    CSV.header = list( name* ) or None
    CSV.data = list( list(cell_value*)* )
    CSV.has_header = bool

    WARNING: do not use on large files!
    (CSVData reads the whole file at once)
    but, CSVHeader is ok for large files
    '''

    def __init__(self, csvfile):
        self.header = CSVHeader(csvfile)
        
        if self.header == None:
            self.has_header = False
        else:
            self.has_header = True

        self.data = CSVData(csvfile, self.has_header)
        
class CSVHeader(object):
    '''csvdove uses this to grab header info from a file,
    for generating starter schemas'''
    def __init__(self, csvfile):
        pass
    
    def __new__(self, csvfile):
        if csv.Sniffer().has_header(csvfile.read(3050)):  #1024)):
            #need to handle non-csv input (raise error)
            #(could not determine delimiter errors)
            csvfile.seek(0)
            r = csv.reader(csvfile)
            return r.next() # first row
        else:
            return None
        
class CSVData(object):
    def __init__(self, csvfile):
        pass
    
    def __new__(self, csvfile, has_header):
        csvfile.seek(0)
        r = csv.reader(csvfile)

        if has_header:
            r.next()
            return [row for row in r]
        else:
            return [row for row in r]

        
# TESTING
test_time = False
if test_time:
    csvfile = open('../examples/seamless.csv')

    c = CSV(csvfile)
    print c.header
    print '\n'
    print c.data
    print '\n'

    nohead = open('../examples/seamless-headerless.csv')
    
    d = CSV(nohead)
    print d.header
    print '\n'
    print d.data

