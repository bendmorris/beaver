import argparse
import sys
from lib.graph import Graph
from lib.types import BeaverException
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from __init__ import __version__


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('file', nargs='*', help='file to be interpreted')
arg_parser.add_argument('-d', '--draw', help='output an image of the resulting graph to the given image file')
arg_parser.add_argument('-i', '--interactive', help='enter interactive mode after interpreting file', action='store_true')
arg_parser.add_argument('-e', '--eval', help='string to be evaluated')
arg_parser.add_argument('-v', '--verbose', help='print each triple statement as evaluated', action='store_true')
arg_parser.add_argument('--version', help='print version and exit', action='store_true')
arg_parser.add_argument('--test', help='run unit tests and exit', action='store_true')
args = arg_parser.parse_args()

if args.version:
    print __version__
    sys.exit()

if args.test:
    import tests
    tests.run_tests(verbose=args.verbose)
    sys.exit()

if not sys.stdin.isatty():
    # read and evaluate piped input
    if args.eval is None: args.eval = ''
    args.eval = sys.stdin.read() + args.eval


interactive = (not args.file and not args.eval) or args.interactive


def run():
    if interactive: print '''Beaver %s''' % __version__

    graph = Graph(verbose=args.verbose)
    for input_file in args.file:
        try:
            graph.parse(filename=input_file)
        except KeyboardInterrupt:
            sys.exit()
        
    if args.eval:
        try:
            graph.parse(text=args.eval)
        except KeyboardInterrupt:
            sys.exit()
    
    if interactive:
        import readline

        exit = False
        while not exit:
            graph.verbose = args.verbose
        
            try:
                next_line = raw_input('>> ').strip()
                
                if not next_line: continue
                
                if next_line[0] == '-' and next_line.split(' ')[0] in arg_parser._option_string_actions:
                    command = next_line.split(' ')[0]
                    action = arg_parser._option_string_actions[command].dest
                    
                    if len(next_line.split(' ')) > 1:
                        arg = ' '.join(next_line.split(' ')[1:])
                        try: arg = eval(arg)
                        except: pass
                    else: 
                        arg = not getattr(args, action)
                    
                    try: 
                        setattr(args, action, arg)
                    except:
                        print 'Illegal argument: %s %s' % (command, arg)
                
                elif next_line in ('exit', 'quit'):
                    exit = True
                else:
                    stmts = graph.parse(text=next_line)
                    if stmts == 0:
                        raise BeaverException('Failed to parse line: %s' % next_line)
                    
            except EOFError:
                print
                exit = True
                
            except KeyboardInterrupt:
                print
                continue
                
            except Exception as e:
                print e
                continue
            
        
    if args.draw:
        graph.draw(args.draw)
    
    
if __name__ == '__main__': run()
