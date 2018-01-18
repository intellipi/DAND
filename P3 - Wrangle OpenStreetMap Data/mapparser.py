#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

infile = "rio-de-janeiro_brazil_sample.osm"

def count_tags(filename):
    tags = {}
    for event , element in ET.iterparse(filename):
        tag = element.tag
        if tag not in tags.keys():
            tags[tag] = 1
        else:
            tags[tag]+=1
    return tags

def test():
    tags = count_tags(infile)
    pprint.pprint(tags) 


if __name__ == "__main__":
    test()
