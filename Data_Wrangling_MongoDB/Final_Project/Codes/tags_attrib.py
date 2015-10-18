# -*- coding: utf-8 -*-
"""
Created on Sat May 23 17:55:49 2015

@author: mmasika
"""

############################################################################
############################################################################

# P R O J E C T  2  :  D A T A  W R A N G L I N G  W I T H  M O N G O  D B

# data cleaning: attributes exercises
############################################################################
############################################################################

import xml.etree.cElementTree as ET
import pprint


smallfile='cheb_cityboundary.osm'

##################################
# The attributes for the tag


def tags_attribute(filename):
    tag_attrib={}
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag in tag_attrib:
            for item in elem.attrib:
                tag_attrib[elem.tag].add(item)
        else:
            tag_attrib[elem.tag]=set()
            for item in elem.attrib:
                tag_attrib[elem.tag].add(item)
    return tag_attrib
 

# most used attributes
def count_attribute(filename):
    d_attrib={}
    for event, elem in ET.iterparse(filename, events=('start',)):
        for attribute in elem.attrib:
            if attribute in d_attrib:
                d_attrib[attribute] += 1
            else:
                d_attrib[attribute]=1
    return d_attrib
               
tag_attrib=tags_attribute(smallfile)              
pprint.pprint(tag_attrib)
count_attrib=count_attribute(smallfile)
pprint.pprint(count_attrib)