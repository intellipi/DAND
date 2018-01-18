#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import unicodecsv as csv
import codecs
import cerberus
import schema
import pprint

OSMFILE = "rio-de-janeiro_brazil_sample.osm"


NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'^(.+?)\s', re.IGNORECASE)
zipcode_re = re.compile(u'^2(\d{4})-(\d{3})')
zipcode_missing_sign = re.compile(u'^(\d{8})')


expected = ["Rua", "Avenida", "Estrada", "Praia", "Parque", "Ladeira", "Praça", "Travessa", 
            "Largo", "Caminho", "Alameda", "Rodovia", "Via", "Acesso", "Servidão", "Calçadão", "Terminal"
           "Boulevard", "Condomínio", "Quadra", "Beco", "Ilha", "Campo"]


mapping = {"Est": "Estrada",
           "Estr": "Estrada",
           "Ruas": "Rua",
           "Rue": "Rua",
           "R": "Rua",
           "R.": "Rua",
           "Av": "Avenida",
           "Av.": "Avenida",
           "Praca": "Praça",
           "Pca": "Praça",
           "Pça": "Praça",
           "Rod": "Rodovia",
           "Rod.": "Rodovia",
           "Trav": "Travessa"
          }




def audit_street_type(street_types, street_name):
    street_name = street_name.replace(".", "")
    street_name = street_name.encode("utf-8")
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group(1)
        if street_type not in expected:
            street_types[street_type].add(street_name)


def audit_zipcode(errors, zipcode):
    zipcode = zipcode.encode("utf-8")
    m = zipcode_re.match(zipcode)
    
    if not m:    
        errors[m].add(zipcode)
            
            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def is_zipcode(elem):
    return (elem.attrib['k'] == "addr:postcode")



def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    invalid_zipcodes = defaultdict(set)
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                elif is_zipcode(tag):
                    audit_zipcode(invalid_zipcodes, tag.attrib['v'])
    osm_file.close()
    return [street_types, invalid_zipcodes]



def update_name(name, mapping):
    name = name.split(' ')
    for i in range(len(name)):
        if name[i] in mapping:
            name[i] = mapping[name[i]]
    name = ' '.join(name)
    name = name.title()
    
    return name


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

    if len(zipcode)==5:
        zipcode = zipcode + '-000'
    
    if zipcode_missing_sign.match(zipcode):
        zipcode = zipcode[:5] + '-' + zipcode[5:]
        
    return zipcode






def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=problemchars, default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
    
    


    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in NODE_FIELDS:
                node_attribs[attrib] = element.attrib[attrib]
        
        for child in element:
            node_tag = {}    
                
            if lower_colon.search(child.attrib['k']):
                node_tag['type'] = child.attrib['k'].split(':',1)[0]                
                node_tag['key'] = child.attrib['k'].split(':',1)[1]
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
                
                # fix street types
                if node_tag['key'] == 'street':
                    node_tag['value'] = update_name(node_tag['value'], mapping)
                        
                # fix zipcodes
                if node_tag['key'] == 'postcode':
                    node_tag['value'] = update_zipcode(node_tag['value']) 
                
                tags.append(node_tag)
            elif problemchars.search(child.attrib['k']):
                continue
            else:
                node_tag['type'] = 'regular'
                node_tag['key'] = child.attrib['k']
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
                
                # fix street types
                if node_tag['key'] == 'street':
                    node_tag['value'] = update_name(node_tag['value'], mapping)
                        
                # fix zipcodes
                if node_tag['key'] == 'postcode':
                    node_tag['value'] = update_zipcode(node_tag['value']) 
                    
                tags.append(node_tag)
        
        return {'node': node_attribs, 'node_tags': tags}


        
        
        
        
    elif element.tag == 'way':
        for attrib in element.attrib:
            if attrib in WAY_FIELDS:
                way_attribs[attrib] = element.attrib[attrib]
        
        position = 0
        
        
        for child in element:
            way_tag = {}
            way_node = {}
            
                    
            if child.tag == 'tag':
                if lower_colon.search(child.attrib['k']):
                    way_tag['type'] = child.attrib['k'].split(':',1)[0]
                    way_tag['key'] = child.attrib['k'].split(':',1)[1]
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']
                    
                    # fix street types
                    if way_tag['key'] == 'street':
                        way_tag['value'] = update_name(way_tag['value'], mapping)
                        
                    # fix zipcodes
                    if way_tag['key'] == 'postcode':
                        way_tag['value'] = update_zipcode(way_tag['value']) 
                    
                    tags.append(way_tag)
                    
                elif problemchars.search(child.attrib['k']):
                    continue
                    
                else:
                    way_tag['type'] = 'regular'
                    way_tag['key'] = child.attrib['k']
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']

                    # fix street types
                    if way_tag['key'] == 'street':
                        way_tag['value'] = update_name(way_tag['value'], mapping)
                        
                    # fix zipcodes
                    if way_tag['key'] == 'postcode':
                        way_tag['value'] = update_zipcode(way_tag['value'])               
                    
                    tags.append(way_tag)                    
                    
  
                    
            elif child.tag == 'nd':
                way_node['id'] = element.attrib['id']
                way_node['node_id'] = child.attrib['ref']
                way_node['position'] = position
                position += 1
                way_nodes.append(way_node)
                
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags} 
    


    

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
                 


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        
        error_string = pprint.pformat(errors)
        raise Exception(message_string.format(field, error_string))
        


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


            
            



# ================================================== #
#               Main Function                        #
# ================================================== #




def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    #process_map(OSMFILE, validate=True) --> done once, OK. Takes a long time to validate.
    process_map(OSMFILE, validate=False)