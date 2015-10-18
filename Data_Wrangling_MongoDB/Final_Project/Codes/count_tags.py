# -*- coding: utf-8 -*-
"""
Created on Sat May 23 17:55:49 2015

@author: mmasika
"""

############################################################################
############################################################################

# P R O J E C T  2  :  D A T A  W R A N G L I N G  W I T H  M O N G O  D B

# data cleaning: tag exercises
############################################################################
############################################################################


import xml.etree.cElementTree as ET
import pprint


smallfile='cheb_cityboundary.osm'


##################################
# Find all top level tags

def count_toptags(filename):
        tag_dic={}
        for event, elem in ET.iterparse(filename, events=('start',)):
            if elem.tag in tag_dic:
                tag_dic[elem.tag]=tag_dic[elem.tag]+1
            else:
                tag_dic[elem.tag]=1
        return tag_dic

tags = count_toptags(smallfile)
pprint.pprint(tags)
print tags

#second level tags

def tags_secondlevel(filename):
    tag_attrib={}
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag in tag_attrib:
            for item in elem.iter():
                if elem.tag==item.tag:
                    continue
                tag_attrib[elem.tag].add(item.tag)
        else:
            for item in elem.iter():
                if elem.tag==item.tag:
                    continue
                tag_attrib[elem.tag]=set()
                tag_attrib[elem.tag].add(item.tag)
    return tag_attrib
 
               
tag_secondlevel=tags_secondlevel(smallfile)              
pprint.pprint(tag_secondlevel)