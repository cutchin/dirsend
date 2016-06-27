
import argparse
import logging
import os

commandDesc = "Executes a provided command once on every file or " \
              "subdirectory in a particular directory. Can be used, " \
              "for example, for pushing files from one location to " \
              "another via a cron job."



parser = argparse.ArgumentParser(description=commandDesc)

parser.add_argument('directory', help='The directory with source files', nargs='?')
parser.add_argument('--list-entries', help='List current known processed file entries', action='store_true')
parser.add_argument('--delete-entry', help='Delete a file entry by its index', metavar='index', type=int)
parser.add_argument('-c', '--command', help='Command to be run on each file.  The string "{}" (without the quotes) will be replaced by the full path of the filename.', metavar='command', action='store')
parser.add_argument('-v', '--verbose', help='Enable verbose output', action='store_true')
parser.add_argument('--store-only', help='Mark all files as processed but don\'t exexecute a command', action='store_true')
parser.add_argument('--data-dir', help='Directory to store database and lock files.  (Defaults to user home.)', default='~', metavar='directory')

args = parser.parse_args();

if not (args.directory or args.list_entries or args.delete_entry):
    parser.error('Either a directory, --list-entries or --delete-entry required.')

if args.directory and not (args.command or args.store_only):
    parser.error('A directory was specified but no command provided with -c or --command')

# configure runtime parameter based on arguments
command = args.command

listFiles = args.list_entries
deleteEntry = args.delete_entry
directory = args.directory
dataDir = os.path.expanduser(args.data_dir)
storeOnly = args.store_only

skipDotFiles = True

dbFile = os.path.abspath(dataDir + '/' + '.dirsend.db')
lockFile = os.path.abspath(dataDir + '/' + '.dirsend.lock')

# Confgure logging

logger = logging.getLogger()

_handler = logging.StreamHandler()
logger.addHandler(_handler)

if (args.verbose):
    logger.setLevel(logging.DEBUG)
    logger.debug('Debug output enabled')

