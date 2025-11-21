
import argparse


def main():
    """
    Handle main.
    """    
    parser = argparse.ArgumentParser(
        description="""
        Command line interface for defermi. Type "defermi -h" to view options.
        """
        )

    subparsers = parser.add_subparsers()

    # add setup functions here

    args = parser.parse_args()
    
    try:
        args.func
    except AttributeError:
        parser.print_help()
        raise SystemExit("Please specify a command.")
    return args.func(args)


if __name__ == '__main__':
    main()