# dirsend

This is a relatively simple Python script that runs a specified command on all files in a given directory and persistently tracks which files have been processed, ensuring the command won't be run on a file more than once with further invocations.

It is intended to be run via cron or some other triggering mechanism.  It uses a lock to ensure invocations won't overlap.

## Uses

The general principal is that you need one-way file synchronization from a source machine to a destination, but don't want those files to be re-transmitted if you subsequently delete them from the destination.  One possible use case is pushing files from a seedbox to a home server.  This was originally developed to move EDI batch files from a customer's server to my own to allow offline handling, when I had shell access to their server but read-only access to the source directory.

```dirsend``` uses a sqlite3 database to store the path of each file once it's been processed to ensure they are not processed more than once. Rows are deleted from this database if the source file no longer exists.
Files won't be added to the directory if the command invocation returns a non-zero exit code.  If an invocation failes it will return immediately.

## Usage

A typical invocation might look like this:
```sh
./dirsend.py -c 'rsync -a "{}" user@myhose:/dest_directory' /source_directory
```

This would run the above ```rsync``` command, substituting ```{}``` with the full filename of each unprocessed file or directory in ```/source_directory```.

### Getting up and running quickly

Get the source:
```sh
git clone https://github.com/cutchin/dirsend.git
```

Optionally mark all files are processed if the existing files don't need to be processed:
```sh
./dirsend.py /src_dir --store-only
```

Make a cron job to run it:
```
crontab -e

...

# Attempt to sync /src_dir to remote location every five minutes
*/5    *    *    *    *    ~/??/dirsend/dirsend.py /src_dir -c 'rsync -a "{}" user@host:/dest_dir'
```

### Other Options

#### Listing files in the file database:
This shows the current known entries in the database, indicating all files (and their index) which will be skipped when the command is run:

```sh
./dirsend.py --list-entries
```
#### Deleting a file entry from the database:
__This does not delete files!__ All it does is removes the relevant entry from the file database.  This is useful if you want a file to be re-transmitted.  Use the ```--list-entries``` option to determine the index of a given file.

```sh
./dirsend.py --delete-entry 17
```

#### Adding files to the database without actually running a command on them
This would be useful the first time ```dirsend``` is used or if your database is deleted.  It "pretends" the files in the directory have been processed, marking them as such in the database, so they won't be processed in subsequent runs:

```sh
./dirsend.py --store-only /source_dir
```
#### Dealing with more than one directory
By default, the database and lock files go in your home directory.  That's fine, but if you are tracking files in more than
one directory this will cause the whole process to fall apart.  Files from directory one will be purged from the database
when it is run on directory two, etc.  Everything will be sent every time, etc.

To avoid this, use the ```--data-dir``` parameter.  For example:

```sh
./dirsend.py --data-dir ~/tmp -c 'rsync etc...' ~/tmp
./dirsend.py --data-dir ~/another_dir -c 'rsync etc...' ~/another_dir
```

### Alternatives
There are a lot of alternatives!

Rsync is an obvious choice but of course it would re-transmit files deleted from the destination directory each time it was run.

Triggering file transmission as soon as the files arrived would probably work fine but you would need to be notified of new files, 
a way to retry if transmission failed, potentially a queuing mechanism to avoid sending too many files at once, etc.

If you have write access to the server and can freely move or delete files, a simple shell script may well suffice:

```sh
for f in /source_dir/*; do
    rsync -a "${f}" user@host:/dest_dir && mv "${f}" /moved_files
done
```

If you need to keep the files in place but still have write access to the directory, it's still not hard.  For example:
```sh
sudo groupadd -f processed

for f in $(find /source_dir -not -gid processed); do
    rsync -a "${f}" user@host:/dest_dir && chgrp processed "${f}"
done
```
That last example will fail on files with spaces in their name, but you get the idea.

In both cases, you will need to take care to avoid the shell script overlapping, which ```dirsend``` deals with.  ```flock``` can be
used for this.


## Supported Platforms
This has been tested on linux and OSX.  It's more or less guaranteed to fail on Windows currently because of its reliance on 
```fcntl.flock```, which is unix-only as far as I know.

## Todo
  - With my usage, file names are guaranteed to be unique, but for cases where it's not the database could probably track mtime/file
  size to re-send files which have changed.
  - A flag for a modification time theshold might be useful - if the file was changed in the last few seconds it's possibly still
  being generated/transmitted and shouldn't be processed yet.

## Known Limitations
It's a fairly simple script and seems to do its job well enough.  Offhand, I can think of a few potential enhancements:
  - Support Windows, or at least remove the flock requirement.
  - Support an alternate way of tracking files than sqlite, in case it's unavailable.
  - Allowing of a configurable number of files to be processed simultaneously, maybe?
  - Python is not generally my language of choice - the code may benefit from a legit Python person giving it a once-over.
