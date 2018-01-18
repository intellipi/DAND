#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import xml.etree.cElementTree as ET


OSMFILE = "rio-de-janeiro_brazil_sample.osm"

# Brazilian street types, unlike in the US, are the first word in the street name.
street_type_re = re.compile(r'^(.+?)\s', re.IGNORECASE)


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
            
            
            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")



def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    name = name.split(' ')
    for i in range(len(name)):
        if name[i] in mapping:
            name[i] = mapping[name[i]]
    name = ' '.join(name)
    name = name.title()
    return name


def test():
    st_types = audit(OSMFILE)
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
                   
            
if __name__ == '__main__':
    test()