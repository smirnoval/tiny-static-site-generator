import argparse
import generator

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Tiny static site generator.")

    parser.add_argument('command', nargs='?', default='', help="'build', 'serve' or 'new'")

    parser.add_argument('-r', '--root', help='''The root folder wuth your source files.''', type=str, default='.')

    parser.add_argument('-o', '--output', help='''The folder where your files should be placed.''', type=str, default='site')

    parser.add_argument('-p', '--port', help='''The port to be used for the http server.''', type=int, default=8000)

    parser.add_argument('-w', '--watch', help='''Scan for changes.''', action='store_true')

    parser.add_argument('-f', '--force', help='''Build this site even if there already exists index.html.''', action='store_true')

    args = parser.parse_args()

    if args.command == 'build':
        generator.build_files(root=args.root,
                              dest=args.output,
                              force=args.force,
                              watch=args.watch)
    elif args.command == 'serve':
        generator.serve_files(root=args.root,
                              dest=args.output,
                              watch=args.watch,
                              port=args.port,
                              force=args.force)
    elif args.command == 'new':
        generator.new_site(root=args.root,
                           force=args.force)
    else:
        print("Please type a valid command, either 'build', 'serve' or 'new'.")
        parser.print_help()
