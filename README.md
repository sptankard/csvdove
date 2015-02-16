# csvdove

**NOTE: csvdove is in active development -- not all of these features
  are implemented yet, and if you use it, it will fail in unexpected
  ways**

csvdove is a CSV "dovetailing" tool -- it combines CSV
(comma-separated value) files that are organized differently. Use it
to merge several datasets, which may have quite disparate
structures. You tell it what columns the input documents have, what
columns should be in the output document, and how the columns match up
between the two. Then, it does the dirty work for you.

It takes a "schema" file which you create, describing the format of
your datasets and how you would like them to be merged (what goes
where, what to leave out, etc.), and several source datasets, which it
processes and spits out in the desired format. (It can also be used on
a single file, to rename, delete and reorder columns.)

### What to use it for?

csvdove is ideal for automating a repetitive, boring data-merging task
that you have been doing manually.

Imagine a non-profit that sells things on their website as one of
their main sources of funds. By historical happenstance, they have
three different website plugins that they use for e-commerce, that
each handle different things. (They would love to be using just one,
and a better one at that, but they are under-staffed and over-worked
as it is, and investing in revamping their website infrastructure is
off the table…) At the end of every month, they export the data from
these e-commerce plugins to combine it, sort it, and import portions
of it into a general-purpose database. This is a long, monotonous,
error-prone process.

csvdove can help with this. Someone at the non-profit can create a
"schema" file describing the data that each e-commerce plugin exports,
and how they would like them to be combined. Then, whenever they need
to merge some data, they can simply drop the files into csvdove, which
will spit them out in the desired format. What used to mean hours of
drudgery can now be done in seconds!

#### How is this different from tools like csvkit or csvmerge?

The names may confound, but csvdove actually does something quite
different from tools like [csvmerge]
(https://github.com/defcube/csvmerge), or [csvkit's]
(http://csvkit.rtfd.org/) [csvjoin]
(http://csvkit.readthedocs.org/en/latest/scripts/csvjoin.html).

csvdove does a different, smarter "merging" -- it actually uses (the
totally awesome) csvkit on the backend.
(I started csvdove because I tried to use those pre-existing tools to
accomplish what I wanted to do, but they couldn't quite do it.)

csvmerge and csvjoin are ideal for combining data sets that say
*different things* about the **same** items (i.e., the columns are
different, and the rows are the same).
csvdove is ideal for combining data sets that say the *same things*
about **different** items (i.e., the columns are the same, but the
rows are different).

As such, it's a bit more like csvkit's [csvstack]
(http://csvkit.readthedocs.org/en/latest/scripts/csvstack.html).
However, csvdove goes a bit further: it can combine data sets even
when the organization (column names, order, etc.)
differs radically between the different sources.

csvdove does much the same thing as [ffe (Flat File Extractor)]
(http://ff-extractor.sourceforge.net/). However, csvdove is simpler to
use (and much less powerful).

Also take a look at [mcm] (https://pypi.python.org/pypi/mcm/).

#### I want to merge some data, but it's not in CSV format.

If it's tabular data, simply convert it into CSV, then use csvdove on
it.
For conversion tools, check out csvkit's [sql2csv]
(http://csvkit.readthedocs.org/en/latest/scripts/sql2csv.html) and
[in2csv]
(http://csvkit.readthedocs.org/en/latest/scripts/in2csv.html).
For the technically oriented, there might be what you're looking for
at [PyPI (search 'csv')]
(https://pypi.python.org/pypi?%3Aaction=search&term=csv&submit=search).

If it's not tabular data, you will probably want to look into quite
different options.

### Making a schema configuration file

Making a schema is not complicated, but it will require some critical
thinking about your data and how you want it to come out. If you have
already been manually merging your datasets, you will probably already
know everything you need to know.

If you haven't already been merging your datasets, then you should
first figure out what you want your output CSV file to look like.

Schema files are stored in the [YAML]
(https://en.wikipedia.org/wiki/YAML) (`.yml`) format.
They look like this:
```yaml
EXAMPLE
```

#### Generate a starter schema

To get started, run `csvdove --gen` on your source files and an
example output file, to create a starter schema:

```shell
csvdove --gen -t exampleTarget.csv -s source1.csv source2.csv ...
```

This will output a starter schema file, which you must then edit to
create a usable schema file. (Use `>` or the `-o` option to redirect
the output to a file.)

Note: use just one source file of each type, using more than one for a
given type is redundant.

#### Edit the starter schema to make a usable schema

`csvdove --gen` creates a file that describes what your source files
look like, and what your final target file should look like. You must
now edit this starter schema to describe how to match up the data from
one to the other.

A schema file has two main sections: `sources` and `target`. `sources`
contains a list of different sources. You must edit the entry for each
of these sources to describe whats bits of the source data should end
up where in the target file. This information is given in the `match`
section of each source description. 

Within `match`, ...

If you don't want certain columns to appear in the output file, simply
leave them out of `match`. These columns can optionally be found later
in the "salvage" file.

You can also edit the `primary_keys` section, adding some column names
that can identify which row is which. This is only for use in the
"salvage" file, which would be difficult to use if there was no link
between the info there and the info in the target file.

There is no need to touch the `cols` for any of the sources, or for the
target.