# csvdove

csvdove is a CSV "dovetailing" utility. Use it to merge several
datasets, which may have quite disparate structures.

It takes a "schema" file which you create, describing the format of
your datasets and how you would like them to be merged (what goes
where, what to leave out, etc.), and several source datasets, which it
processes and spits out in the desired format. (It can also be used on
a single file, to rename, delete and reorder columns.)

It can perform a realignment of the source columns: prune, fill
gaps, rename, reorder.

## I want to merge some data, but it's not in CSV format.

If it's tabular data, simply convert it into CSV, then use csvdove on
it. For conversion tools, check out csvkit's sql2csv, or google
around. 

If it's not tabular data, you will probably want to look into quite
different options.

## How is this different from tools like csvkit or csvmerge?

The names may confound, but csvdove actually does something quite
different from tools like csvmerge, or csvkit's csvjoin. (I started
csvdove because I tried to use those prexisting tools to accomplish
what I wanted to do, but they couldn't quite do it.) csvdove does a
different, smarter "merging".

csvmerge and csvjoin are ideal for combining data sets that say
different things about the same items (i.e., the columns are
different, and the rows are the same).
csvdove is ideal for combining data sets that say the same things
about different items (i.e., the columns are the same, but the rows
are different). However, csvdove goes a bit further: it can combine
data sets even when the format (column names, order, etc.) differs
radically between the different sources.

csvdove is a bit more like ffe (Flat File Extractor). However, csvdove
is simpler to use, and less powerful.

automating a repetitive, boring task

csvdove is ideal for merging

Imagine a non-profit that sells things on their website as one of
their main sources of funds. By historical happenstance, they have
three different plugins that they use for e-commerce on their website,
that each handle different things. (They would love to be using just
one, and a better one at that, but they are under-staffed and
over-worked as it is, and investing in revamping their website
infrastructure is off the table.) At the end of every month, they
export the data from these e-commerce plugins to combine it, sort it,
and import portions of it into a general-purpose database (their donor
database; their general recors). This is a long, monotonous,
error-prone process.

csvdove can help with this. Someone at the non-profit can create a
"schema" file describing the data that each e-commerce plugin exports,
and how they would like them to be combined. Then, they can simply
drop the files from each plugin into csvdove, which will spit them out
in the desired format. What used to mean hours of drudgery can now be
accomplished in seconds!

## Making a schema configuration file

Making a schema is not complicated, but it will require some critical
thinking about your data and how you want it to come out. If you have
already been manually merging your datasets, you will probably already
know everything you need to know.

First, run `csvdove --gen` on your source files and an example output
file, to create a starter schema:

csvdove --gen -t exampleTarget.csv -s source1.csv source2.csv ...

This will output a starter schema file, which you must then edit to
create a usable schema file. (Use `>` or the `-o` option to redirect
the output to a file.)

Note: use just one source file of each type, using more than one for a
given type is redundant.

`csvdove --gen` creates a file that describes what your source files
look like, and what your final target file should look like. You must
now edit the schema to describe how to match up the data from one to
the other.

A schema file has two main sections: `sources` and `target`. `sources`
contains a list of different sources. You must edit the entry for each
of these sources to describe whats bits of the source data should end
up where in the target file. This information is given in the `match`
section of each source description. 



If you don't want them to appear in the output file, simply leave them
out of `match`.