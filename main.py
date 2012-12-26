import argparse
import sys
from lib.graph import Graph

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('file', nargs='*', help='file to be interpreted')
arg_parser.add_argument('-d', '--draw', help='output an image of the resulting graph to the given image file')
arg_parser.add_argument('-i', '--interactive', help='enter interactive mode after interpreting file', action='store_true')
arg_parser.add_argument('-v', '--verbose', help='print each triple statement as evaluated', action='store_true')
args = arg_parser.parse_args()


graph = Graph(verbose=args.verbose)
for input_file in args.file:
    graph.parse(filename=input_file)
    
    
if not args.file or args.interactive:
    exit = False
    while not exit:
        try:
            next_line = raw_input('>> ').strip()
            if next_line:
                graph.parse(text=next_line)
        except EOFError:
            print
            exit = True
        except KeyboardInterrupt:
            print
            continue        
    
if args.draw:
    graph.draw(args.draw)
