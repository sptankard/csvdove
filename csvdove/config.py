
file_name = 'seamless.csv'
# NOTE: file names will need to be gotten as arguments on CLI or from GUI
db_name = 'csvdove_csv_tmp.db'


#SCHEMA FILE FORMAT
def format():
    s = ''
    s_name = ''
    t = ''
    t_name = ''
    
    schema = dict(

        sources = list(
            dict(
                name = str(s_name),
                cols = list(str(s)),
                primary_keys = list(str(s)),
                match = list(
                    list( str(s), str(t) )
                )
                #match = list( tuple(str(s), str(t)) )
            )
        ),
        
        target = dict(
            name = str(t_name),
            cols = list(str(t))
        )
    )

#EXAMPLE REFERENCES
'''
class Schema(object):
    def __init__(self, schema):
        self.target = Target( schema['target'] )

        self.sources = []        
        for src in schema['sources']:
            s = Source( src, self.target )
            self.sources.append(s)
 
class Source(object):
    # instantiate source on a dict()
    def __init__(self, s, t):
            self.name = s['name']
            self.cols = s['cols']
            self.match = s['match']
            self.primary_keys = s['primary_keys']



class Target(object):
    def __init__(self, t):
        self.name = t['name']
        self.cols = t['cols']
'''    
# schema['sources'][0]['name']
# schema['sources'][0]['name']

sources = [
    
    dict(
        name = 'seamless',
        cols = [
            'Date',
            'Time',
            'First Name',
            'Last Name',
            'Amount',
            'Currency',
            'Repeating',
            'Designated Fund',
            'Gift Item',
            'Phone',
            'Email',
            'Address',
            'Address 2',
            'City',
            'State/Prov',
            'Postal Code',
            'Country',
            'Employer',
            'Occupation',
            'OK to Add to Mailing List'
        ],
    
        match = [
        # [source, target]
            ['Date', 'Date'],
            ['First Name', 'Billing First Name'],
            ['Last Name', 'Billing Last Name'],
            ['Employer', 'Organization'],
            ['Amount', 'Amount'],
            ['Repeating', 'Repeating?'],
            ['Email', 'Email'],
            ['Designated Fund', 'Designated Fund'],
            ['Address', 'Shipping Address'],
            ['Address 2', 'Shipping Address 2'],
            ['City', 'Shipping City'],
            ['State/Prov', 'Shipping State/Prov'],
            ['Postal Code', 'Shipping Postal Code'],
            ['Country', 'Shipping Country'],
            ['Phone', 'Phone'],
            ['OK to Add to Mailing List', 'OK to Add to Mailing List']
        ],
        
        primary_keys = [
            'Date',
            'First Name',
            'Last Name',
            'Amount'
        ]
    )
    
    # room for more sources: dict()...
]
    
target = dict(
    name = 'gdoc',
    cols = [
        'source',
        'Contact IPK',
        'donation entered to DS?',
        'sent in mail?',
        'Date',
        'Title',
        'Billing First Name',
        'Billing Middle Name',
        'Billing Last Name',
        'Partner First',
        'Partner Middle',
        'Partner Last',
        'Organization',
        'Shipping First Name',
        'Shipping Last Name',
        'Amount',
        'Repeating?',
        'Email',
        'Designated Fund',
        'Specific',
        'Renewal foster?',
        'Shipping Address',
        'Shipping Address 2',
        'Shipping City',
        'Shipping State/Prov',
        'Shipping Postal Code',
        'Shipping Country',
        'Phone',
        'OK to Add to Mailing List',
        'Billing Address 1',
        'Billing Address 2',
        'Billing City',
        'Billing State',
        'Billing Postal Code',
        'Billing Country',
        'H/F First',
        'H/F Last',
        'H/F Address 1',
        'H/F Address 2',
        'H/F City',
        'H/F State',
        'H/F Postal Code',
        'H/F Country',
        'H/F Phone',
        'H/F Email'
    ]
)
