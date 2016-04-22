__author__ = 'jaemin'
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
class Ant:
    Name = ""
    # They need to have its own analyzer strings
    # Call the Bee analyzer with string inputs and current team information and get picks
    # Ant has its own Bank roll.
    # Ant can also test their analyzer string with created database.
    def __init__(self):
        pass
    def votes_odds(self,db_name):
        conn = sql.connect(self,db_name)
        cur = conn.cursor()
        cur.execute("select * from MLB_V1")

        for fetch in cur.fetchall():
            print fetch[31],fetch[32],fetch[33],fetch[34]
            pass
        pass



