#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint
import re

infile = "rio-de-janeiro_brazil_sample.osm"

def process_map(filename):
    users = set()
    for __, element in ET.iterparse(filename):
        for e in element:
            if 'uid' in e.attrib:
                users.add(e.attrib['uid'])
    return users

users = process_map(infile)
len(users)