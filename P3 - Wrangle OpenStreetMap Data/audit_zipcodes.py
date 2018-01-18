#!/usr/bin/env python
# -*- coding: utf-8 -*-


from collections import defaultdict
import xml.etree.cElementTree as ET
import re
import pprint

OSMFILE = "rio-de-janeiro_brazil_sample.osm"


'''
regex syntax: 
- must start with an integer = 2
- followed by 4x an integer [0-9]
- followed by a minus sign '-'
- followed by 3x an integer [0-9]
'''
zipcode_re = re.compile(u'^2(\d{4})-(\d{3})')



''' 
regex syntax:
- 8 integers [0-9]
- no minus sign
'''
zipcode_missing_sign = re.compile(u'^(\d{8})')




def is_zipcode(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit_zipcode(errors, zipcode):
    zipcode = zipcode.encode("utf-8")
    m = zipcode_re.match(zipcode)
    
    if not m:    
        errors[m].add(zipcode) # all zipcodes before correction
        
        

def audit(osmfile):
    osm_file = open(osmfile, "r")
    errors = defaultdict(set)
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zipcode(tag):
                    audit_zipcode(errors, tag.attrib['v'])
    osm_file.close()
    return dict(errors)


'''
The check below prints a dict of zipcode errors to be fixed. 
Values will be corrected in 'update_zipcode'function.
'''
#check = audit(OSMFILE)
#pprint.pprint(dict(check))


def update_zipcode(zipcode):
   
    # correct odd errors:
    zipcode = zipcode.replace(".", "")
    zipcode = zipcode.replace(" ", "")
    zipcode = zipcode.replace("20090-00", "20090-000")
    zipcode = zipcode.replace("2261001", "22610-001")
    zipcode = zipcode.replace("2246-000", "22460-000")
    zipcode = zipcode.replace("2695307", "26953-070")
    zipcode = zipcode.replace("35953060", "25953-060")
    zipcode = zipcode.replace("52645100", "22645-100")

    # correct valid zipcodes with 5 digits (the last 3 digits were added about a decade ago)
    if len(zipcode)==5:
        zipcode = zipcode + '-000'
    
    
    # correct valid zipcodes with missing minus sign:
    if zipcode_missing_sign.match(zipcode):
        zipcode = zipcode[:5] + '-' + zipcode[5:]
        
    return zipcode

            
# Function 'test' below checks if the 'update_zipcode' function works on errors found in 'audit' function.

def test():
    a = audit(OSMFILE)
    for i, j in a.iteritems():
        for x in j:
            new_zipcode = update_zipcode(x)
            print x, "=>", new_zipcode
                   
            
if __name__ == '__main__':
    test()