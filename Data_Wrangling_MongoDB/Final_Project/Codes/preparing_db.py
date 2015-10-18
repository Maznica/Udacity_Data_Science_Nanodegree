# -*- coding: utf-8 -*-
"""
Created on Sat May 23 17:55:49 2015

@author: mmasika
"""

############################################################################
############################################################################

# P R O J E C T  2  :  D A T A  W R A N G L I N G  W I T H  M O N G O  D B

# Preparing for the DB import
############################################################################
############################################################################


import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import keys_values



smallfile='cheb_cityboundary.osm'


#################################################
# Preparing for DB

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
startaddr = re.compile(r'(addr:)[a-z]*')
doublepoint = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]



def shape_element(element):
    node = {"created":{}}
    if element.tag == "node" or element.tag == "way" :
        for key in element.attrib.keys():
            node["type"]=element.tag
            if key in CREATED:
                node['created'][key]=element.attrib[key]
            elif key=='lat':
                if 'pos' not in node:
                    node['pos']=[float(element.attrib[key])]
                else:
                    node['pos']=[float(element.attrib[key])]+node['pos']
            elif key=='lon':
                if 'pos' not in node:
                    node['pos']=[float(element.attrib[key])]
                else:
                    node['pos']=node['pos'].append(float(element.attrib[key]))
            else:
                node[key]=element.attrib[key]
        for tag in element.iter('tag'):
            if problemchars.search(tag.attrib['k']) or doublepoint.search(tag.attrib['k']):
                continue
            elif startaddr.search(tag.attrib['k']):
                if 'address' in node:
                    node['address'][tag.attrib['k'][5:]]=tag.attrib['v']
                else:
                    node['address']={}
                    node['address'][tag.attrib['k'][5:]]=tag.attrib['v']
            elif tag.attrib['k']=="type":
                node[tag.attrib['k']]=element.tag
            else:
                node[tag.attrib['k']]=tag.attrib['v']
        for tag in element.iter('nd'):
            if "node_refs" not in node:
                node["node_refs"]=[tag.attrib['ref']]
            else:
                node["node_refs"].append(tag.attrib['ref'])
        node['num_keys']=len(node)
      
        #element.clear()
        return node
    else:
        return None

  
    

def process_map_json(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in[:-4])
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                if 'address' in el:
                    el['address']=keys_values.update_city(el['address'])
                    el['address']=keys_values.update_strnumber(el['address'])
                if 'phone' in el:
                    if el['phone'].find('+420')!=-1:
                        el['phone']=keys_values.cz_updatephone(el['phone'])
                    else:
                        el['phone']=keys_values.de_updatephone(el['phone'])
                if 'is_in' in el:
                    el['is_in']=keys_values.update_name(el['is_in'],keys_values.mapping)
                    
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

process_map_json(smallfile, True)























    