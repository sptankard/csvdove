
'''This setup reduces the basic data needed to:
- full target list
- full source list
- matching matrix [source, target]
- 'primary keys' for source (to make a 'salvage' file)
- also, 'name' for target and source (~type)

As such, making schema config files is easier. The rest of the needed
data is then derived from computing on this base info.
'''

from main import to_str
# can prob move to_str into data for good

def subtract_lists(x, y):
    #alt but different: z = list(set(x) - set(y))
    z = [item for item in x if item not in y]
    return z

def schema_from_file_path(file_path):
    import yaml
    c = yaml.load(file(file_path))
    return Schema(c) 

def search_schemas_dir():
    '''Returns a list of .yml files in ~/.csvdove/saved_schemas
    
    Should this be in data or in worker?
    '''
    # consider using ~/.config/ 
    import os

    # This first block should be abstracted out to code for
    # config. (Doesn't have to do with schemas_dir per se.)
    appn = 'csvdove' # get this val from an app-wide var
    cfgdir = '.' + appn # also get this from app-wide var for config
                      # location
    cfgpath = os.path.expanduser( os.path.join('~', cfgdir) )
    # need to make this work better for Windows. os settings for
    # appdata/config dirs... Right now it works for *nix.
    
    # here's the start of what should actually be dealt with in this
    # function. Well, schemas_dir should be maybe gotten from
    # somewhere... (where?)
    schemas_dir = os.path.join(cfgpath, 'saved_schemas')
    file_names = [fn for fn in os.listdir(schemas_dir) if fn.endswith('.yml')]

    file_paths = [os.path.join(schemas_dir, fn) for fn in file_names]    

    return file_paths

'''NOTE: need to differentiate better between output file path, 
and 'target file'.
Really, output file path does not need to be dealt with in data at all:
it's a job for Worker

True "input" target files, however, need to be parsed by data.Target.
This only concernes --gen.
'''
     
class DataWrapper(object):
    '''Wraps up the data for use: 
    (1) a schema (with source and target description), and
    (2) files (schema file, source files, and target file location).
    
    A DataWrapper instance is provided as the arg to a Worker instance.
    '''
    def __init__(self, schema_file, target_file, list_of_source_files):
        self.schema = Schema(schema_file)
        self.schema_file_path = schema_file # is this actually a path,
                                            # or a file object?
        
        self.target_file = target_file
        
        self.source_files = []
        for each_source_file in list_of_source_files:
            sf = SourceFile(each_source_file, self.schema)
            self.source_files.append(sf)

#each of the things that Schema is getting fed in  are
#schema.sources is a list
#it should be a list of dicts,
#not a list of lists

class Schema(object):
    '''Jumper point for Target and Source* classes.
    Loads a schema and instantiates a Target and a list of Sources.
    '''
    def __init__(self, schema_data):
        # need to overhaul the dot notation vs dict access. ATM, it
        # works in Target and Source but not in Schema. Wait for
        # loading from yaml first...
        
        self.target = Target(schema_data.target)
        #self.target = Target(schema_data['target'])
        self.sources = []
        for each_source in schema_data.sources:        
        #for each_source in schema_data['sources']:
            s = Source(each_source, self.target)
            self.sources.append(s)

#        self.s = self.sources[0] #hack to make it function for now

class Target(object):
    '''Represents the target description from a schema.
    instantiate on a dict()
    '''
    def __init__(self, target):
        self.name = target['name']
        #self.name = target[0]
        self.cols = target['cols']
        #self.cols = target[1]
        
class Source(object):
    '''Represents a source description from a schema.
    Derives useful info above and beyond the data stored in the schema
    configuration file. (What to keep, what to add, what gets left out,
    what to put in the salvage file, how to id a source.)

    s: source dict taken from schema
    t: a Target object instance
    '''
    def __init__(self, s, t):
        # defined in schema file
        self.name = s['name']
        self.cols = s['cols']
        self.match = s['match']
        self.primary_keys = s['primary_keys']

        # here's where the real magic happens
        self.keep = [ i[0] for i in self.match ]
        
        t_match =  [ i[1] for i in self.match ]
        self.add = subtract_lists(t.cols, t_match)
        
        self.forsaken = subtract_lists(self.cols, self.keep)
        self.salvage = self.primary_keys + self.forsaken

        # string that allows to id file as a type of source
        # can abstract this task to use CSVHeader...
        self.jisser = to_str(self.cols)

class SourceFile(object):
    def __init__(self, file_path, schema_obj):
        '''Represents a source *input file*.
        Read the file and find some stuff out about it.
        Compare it to the source descriptions in the schema and find
        its matching definition.

        The GUI keeps and updates (add/remove, disactivate if no match
        in schema) a list of SourceFile objects.

        '''
        self.path = file_path

        with open(file_path, 'r') as f:
            first_line = f.readline().rstrip() #rstrip() removes \n
            # can use CSVHeader here instead

        schema = schema_obj
        for src in schema.sources:
            if src.jisser == first_line:
                self.schema_corr = src
            else:
                self.is_in_schema = False

        # i think this var isn't being used enough yet
        self.src_type = self.schema_corr.name

class SchemaFile(object):
    '''Represents a schema *configuration file*.
    Mainly for use by the GUI. (ATM, CLI only works with one schema
    file at a time. Maybe for -l, it will need.)
    The GUI will maintain a list of these objects, which can be active
    or not. The active schema file will have a Schema object loaded in
    memory.

    '''
    def __init__(self, file_path):
        #self.path = 'somewhere' + self.name
        
        # When the GUI starts, it should create a bunch of SchemaFile
        # objects, one from each schema file path it has access to.
        # To start with, they should be inactive -- and the GUI
        # should then activate one of them.
        self.active = False
         