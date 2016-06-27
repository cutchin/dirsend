#!/usr/bin/python

import args
import db
from args import logger

import os
from subprocess import call
import sys
import fcntl


global fileDesc
def acquireLock():
    global fileDesc
    fileDesc = os.open(args.lockFile, os.O_CREAT)

    logger.debug("Acquiring lock using file {}".format(args.lockFile))
    try:
        fcntl.flock(fileDesc, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except:
        logger.error("Error - unable to acquire lock.  (Is another instance running?)")
        sys.exit()

def releaseLock():
    global fileDesc

    logger.debug("Releasing lock")
    fcntl.flock(fileDesc, fcntl.LOCK_UN)
    os.close(fileDesc)
    os.unlink(args.lockFile)


def processDir():
    fileList = os.listdir(args.directory)

    for fileName in fileList:
        absPath = os.path.abspath(args.directory + '/' + fileName)

        if args.skipDotFiles and fileName.startswith('.'):
            continue

        if db.findFile(absPath):
            logger.debug("File {} already processed".format(absPath))
            continue

        if args.storeOnly:
            print "Marking {} as processed".format(absPath)
            db.addFile(absPath)
            continue

        print "Processing file {}".format(absPath)
        cmd = args.command.format(absPath)
        logger.debug("Executing command \"{}\"".format(cmd))
        returnCode = call(cmd, shell=True)

        if (returnCode == 0):
            logger.debug("Processing file {}".format(absPath))
            db.addFile(absPath)
        else:
            logger.error("Error synchronizing file {}".format(absPath))
            return False
    
    return True

def cleanDB():
    logger.debug("Purging missing files from database")
    
    files = [ os.path.abspath(args.directory + '/' + f) for f in os.listdir(args.directory)]
    
    deleteFiles = []

    entries = db.selectAll()

    while len(entries) > 0:
        for nextEntry in entries:
            if not nextEntry[1] in files:
                logger.debug("Marking file {} for removal from database".format(nextEntry[1]))
                deleteFiles.append(nextEntry[0])

        entries = db.fetchNext()

    db.deleteSet(deleteFiles)

acquireLock()
db.openDB()

try:
    if args.listFiles:
        db.listFiles()

    if args.deleteEntry:
        db.deleteIndex(args.deleteEntry)

    if args.directory:
    
        processDir()
        cleanDB()
finally:
    releaseLock()
    db.closeDB()
