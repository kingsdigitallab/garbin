# Garbin

A python command line toolbox to validate input files.

Features:
* **legible**: a command to quantify the legibility of plain text and PDF document 
  by counting the proportion of token found in an English vocabulary. 
  The text is extracted from the PDFs using tesseract library.

# Setup

Create a python virtual environment and activate it.

```commandline
pip install pip-tools
pip-sync
```

# Usage

Process:
* Place your input files into the data/in folder.
* Use garbin.py to check them (see available actions below).
* Look at the result table returned by garbin (default is a table, use -f
  for other formats)

## Example

```commandline
(venv) $ python garbin.py legible
100%|██████████████████████████████████████████| 23/23 [01:31<00:00,  3.97s/it]
                           file    extraction  legibility
0     data/in/penn-1789-516.pdf           PDF       0.767
1       data/in/penn-1810-5.txt         ascii       0.892
2       data/in/penn-1830-5.pdf           PDF       0.859

(venv) $ python garbin.py legible -f csv > data/out/legibility.csv
```

# Interface

```commandline
$ python garbin.py -h

usage: garbin.py [-h] [-f [{table,json,csv}]] action

Data validator toolbox.

positional arguments:
  action                help, legible, test

optional arguments:
  -h, --help            show this help message and exit
  -f [{table,json,csv}], --format [{table,json,csv}]
                        output format

Actions:
  help: Show help
  legible: Check English legibility of documents in input folder.
        Returns a list of dictionary. One entry per file.
        Keys:
            file (PosixPath),
            legibility (from 0 to 1),
            extraction (e.g. tesseract)
        
  test: Dummy action for testing purpose.
```
