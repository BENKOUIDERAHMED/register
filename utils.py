import sqlite3

def connectToDb(fileName):
    conn = sqlite3.connect(fileName)
    return conn ,conn.cursor()
    