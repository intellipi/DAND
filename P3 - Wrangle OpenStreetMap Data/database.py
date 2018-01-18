#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unicodecsv as csv
import sqlite3

db = sqlite3.connect("rio_de_janeiro_sample.db")
cur = db.cursor()




# Create nodes table

cur.execute("CREATE TABLE nodes (id, lat, lon, user, uid, version, changeset, timestamp);")

with open('nodes.csv','rb') as f:
    d = csv.DictReader(f)
    output = [(i['id'], i['lat'], i['lon'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in d]
    
cur.executemany("INSERT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", output)

db.commit()




# Create ways table


cur.execute("CREATE TABLE ways (id, user, uid, version, changeset, timestamp);")

with open('ways.csv','rb') as f:
    d = csv.DictReader(f) 
    output = [(i['id'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in d]

cur.executemany("INSERT INTO ways (id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", output)

db.commit()





# Create nodes_tags table


cur.execute("CREATE TABLE nodes_tags (id, key, value, type);")

with open('nodes_tags.csv','rb') as f:
    d = csv.DictReader(f) 
    output = [(i['id'], i['key'], i['value'], i['type']) for i in d]

cur.executemany("INSERT INTO nodes_tags (id, key, value, type) VALUES (?, ?, ?, ?);", output)

db.commit()







# Create ways_tags table


cur.execute("CREATE TABLE ways_tags (id, key, value, type);")

with open('ways_tags.csv','rb') as f:
    d = csv.DictReader(f) 
    output = [(i['id'], i['key'], i['value'], i['type']) for i in d]

cur.executemany("INSERT INTO ways_tags (id, key, value, type) VALUES (?, ?, ?, ?);", output)

db.commit()



# Create ways_nodes table
cur.execute("CREATE TABLE ways_nodes (id, node_id, position);")

with open('ways_nodes.csv','rb') as f:
    d = csv.DictReader(f) 
    output = [(i['id'], i['node_id'], i['position']) for i in d]

cur.executemany("INSERT INTO ways_nodes (id, node_id, position) VALUES (?, ?, ?);", output)

db.commit()
