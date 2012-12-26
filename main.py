import argparse
import sys
import lib.parser as parser
import lib.types as types

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('file', nargs='*')
args = arg_parser.parse_args()

if not args.file:
    print "No file specified."
    sys.exit()

context = types.Graph()
for input_file in args.file:
    with open(input_file, 'r') as file_handle:
        parser.parse(file_handle)
