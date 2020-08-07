import argparse
from os import path, access, R_OK, W_OK
import sys
import pandas


def is_readable(input_path):
    if path.isfile(input_path) and access(input_path, R_OK):
        return path.realpath(input_path)
    raise argparse.ArgumentTypeError(
        'File %r does not exist or is not readable' % input_path
    )
# is_readable


def is_writeable(input_path):
    # STDOUT is writeable
    if input_path == sys.stdout:
        return sys.stdout

    input_path = path.realpath(input_path)

    # Path is a directory
    if path.isdir(input_path):
        raise argparse.ArgumentTypeError('Target path %r is a directory. File expected' % input_path)

    # Existing writeable file
    if path.isfile(input_path):
        if access(input_path, W_OK):
            return input_path
        raise argparse.ArgumentTypeError('Target file %r is not writeable' % input_path)

    # Non-existing file, check if dir is writable
    base_dir = path.dirname(input_path)
    base_name = path.basename(input_path)

    if access(base_dir, W_OK):
        return path.join(base_dir, base_name)
    else:
        raise argparse.ArgumentTypeError('Target directory %r is not writeable' % base_dir)
# is_writeable


def csv2json(input_file, output_file=sys.stdout):
    reader = pandas.read_csv(input_file)
    reader.to_json(output_file, orient="records")


def json2csv(input_file, output_file=sys.stdout):
    reader = pandas.read_json(input_file)
    reader.to_csv(output_file, index=False)


def main():
    parser = argparse.ArgumentParser(description='Convert CSV to JSON and vice versa')
    parser.add_argument('input_file', help='File to convert from (csv or json)', type=is_readable)
    parser.add_argument('output_file', help='File to save converted data to', type=is_writeable,
                        nargs='?', default=sys.stdout)

    args = parser.parse_args()
    input_extension = path.splitext(args.input_file)[1]

    if input_extension == '.csv':
        csv2json(args.input_file, args.output_file)
    elif input_extension == '.json':
        json2csv(args.input_file, args.output_file)
    else:
        raise argparse.ArgumentTypeError('Unsupported extension')


if __name__ == '__main__':
    main()
