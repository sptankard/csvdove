"""all changeable during GUI runtime:
1 schema file
* source files
1 target file
...this happens below the DataWrapper level

GUI table view:
welcome_text = 'Drag or drop CSV files here to dovetail them.'

fields: file name, source type; remove button
"""
class GUI(object):
    # GUI needs to have optional args (-c, -s, -o)
    # def __init__(self, **kwargs):

    def __init__(self, c=None, s=None, o=autogen_output_path()):
        # or s=[] ??

        # N.B. should GUI expect c = str or file object? (or
        # datastruct?)

        # collect the sysargs if they got explicitly passed on cli
        # If args were not provided on cli, define defaults for them.

        self.file_output_path = o
        self.target_file = self.file_output_path

        # default schema:
        # (1) if started with -c, use that path
        # otherwise, call default_schema_file()

    def main(self):
        # GUI.main() DOES NOT call a DataWrapper -- you don't
        # necessarily have all the args (output file is always
        # defined, but there may be no source files or schema files
        # yet). Rather, it interacts with the files more directly.

        # selected_schema_file is a str leading to the schema file we
        # want to work with.
        self.selected_schema_file = None

        # GUI needs to create SchemaFile objs for all the file paths
        # it finds. Then, activate the selected one.
        #
        pass

    def process(self):
        '''Gets called when 'Process' button is clicked.'''
        # you can only call process if you have all the args (means
        # have to check for SourceFiles and active SchemaFile)
        data = DataWrapper(
            self.selected_schema_file,
            self.target_file,
            self.source_files_list)
        from csvdove.worker import Dovetail
        d = Dovetail(data)
        d.main()

    def add_source_file(self):
        '''Gets called when a source file is added to the window's list. Needs
        to create a SourceFile object for the file.

        '''
        pass

    def rm_source_file(self):
        '''Gets called when user clicks 'Remove this file'. Needs to destroy
        the corresponding SourceFile object as well as remove from list.
        '''
        pass

    def change_schema(self):
        '''Changes which schema is active. Destroys Schema object for the
        prior active SchemaFile, and creates a Schema for the newly
        active SchemaFile.
        '''
        self.selected_schema_file = self.get_file_path_from_widget()
        from csvdove import data
        data.schema_from_file_path(self.selected_schema_file)

        # Everytime you change a schema, it should reevaluate the
        # source files wrt the new schema file.
        # SourceFile implements this checking. So, on every schema
        # change, must reiterate through source file paths and make
        # new SourceFile objects for them.

        # return Schema(s)  #where am i form???

    def add_schema_file(self):
        '''Called when user selects 'Add schema file...' (Schema selector
        drop-down.)
        '''
        # gui needs to:
        # data.schema_from_file_path()
        # set schema to active
        # reevaluate src files wrt new schema

        pass

    def rm_schema_file(self):
        '''Called when user selects 'Delete schema file from cache'. (In
        dialog window/preferences.)'''
        pass

    def change_output_file_path(self):
        '''Called when user changes the path for output file. GUI handles
        output file like so: (1) use autogenerated path, or (2)
        manually enter custom path and name.

        '''
        pass
