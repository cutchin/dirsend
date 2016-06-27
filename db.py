import os
import sqlite3
import args
from args import logger

global cursor
global connection

connection = None
cursor = None

def createDB():
    global logger
    logger.debug('Initializing new database at location {}'.format(args.dbFile))

    cursor.execute('''CREATE TABLE files
      (idx INTEGER PRIMARY KEY ASC,
      fileName TEXT NOT NULL)''')

    connection.commit()

def openDB():
    global connection
    global cursor

    needsInit = not os.path.isfile(args.dbFile)

    connection = sqlite3.connect(args.dbFile)
    cursor = connection.cursor()

    if needsInit:
        createDB()

    logger.debug('Database {} opened'.format(args.dbFile))

def findFile(fileName):
    cursor.execute('SELECT rowid FROM files WHERE fileName = ?', (fileName,))
    return cursor.fetchone() is not None;

def addFile(fileName):
    cursor.execute('INSERT INTO files (fileName) values ( ? )', (fileName,))
    connection.commit()

def deleteIndex(idx):
    logger.debug("Deleting entry {} from file database".format(idx))
    rslt = cursor.execute('DELETE FROM files WHERE rowid=?', (idx,))
    if (rslt.rowcount == 0):
        logger.error("No file with index {} was present".format(idx))
    connection.commit()

def listFiles():
    global cursor
    results = cursor.execute('SELECT rowid, fileName FROM files')

    print ' idx | fileName'
    print '-----|--------------------------------------'
    for result in results:
        print "{:3d}  | {}".format(result[0], result[1])

def selectAll():
    global cursor

    cursor.execute('SELECT rowid, fileName FROM files')
    return cursor.fetchmany()

def fetchNext():
    return cursor.fetchmany()

def deleteSet(deleteSet):
    global connection
    global cursor

    logger.debug('Removing {} entries from database'.format(len(deleteSet)))

    while len(deleteSet) > 0:
        currentSet = deleteSet[:100]
        deleteStr = ", ".join(map(str, currentSet));
        logger.debug('Removing batch of {} entries'.format(len(currentSet)))

        cursor.execute('DELETE FROM files WHERE rowid in ({})'.format(deleteStr))
        deleteSet = deleteSet[100:]
    connection.commit()

def closeDB():
    global connection
    global cursor

    cursor.close()
    connection.close()

