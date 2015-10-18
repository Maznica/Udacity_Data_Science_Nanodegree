# -*- coding: utf-8 -*-
"""
Created on Mon May 25 11:06:53 2015

@author: mmasika
"""


############################################################################
############################################################################

# P R O J E C T  2  :  D A T A  W R A N G L I N G  W I T H  M O N G O  D B

# Data Scrapping - all streets in Cheb
############################################################################
############################################################################

import urllib2
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re


#######################
# Get the started characters of the streets

page = u"http://www.psc.cz/cz/Karlovarsky-kraj/Cheb/Cheb/"
smallfile='cheb_cityboundary.osm'
                
# Extract all the possible starting of the streets - normal characters
def extract_startstreet(page):
    data = []
    response = urllib2.urlopen(page)
    html =response.read()
    soup = BeautifulSoup(html)
    street_list=soup.find('div',attrs={'class': 'abcUlic'})
    for item in street_list.findAll("a"):
        data.append(item.text)
    data=data[:-4]
    return data

listing = extract_startstreet(page)


# Prepare the list of parameters 
def create_param(l):
    paramlist=[]
    for item in l:
        item = 'ulice-od-'+item
        paramlist.append(item)
    return paramlist
    
create_param(listing)

# Extra Characters
list_extra=['ulice-od-%C3%9A',\
'ulice-od-%C4%8C',\
'ulice-od-%C5%A0',\
'ulice-od-%C5%BD']

# Union of two lists - helping function
def union(a,b):
    for item in b:
        if item not in a:
            a=a.append(item)
    return a
    
# Get the complete list of streets in Cheb
def extract_streets(page, listing):
    data = []
    newlist=create_param(listing)+list_extra
    for item in newlist:
        newpage=page+item
        #print newpage
        response = urllib2.urlopen(newpage)
        html =response.read()
        soup = BeautifulSoup(html)
        class_street=soup.find('div', attrs={'class': 'rightTree'})
        street_list=class_street.find('ul')
        for item in street_list.findAll('a'):
            #print item.text
            union(data,[item.text])
    return data

completelist_street=extract_streets(page,listing)


# Get streets in Cheb from Data
def get_street_dict(d):
    if 'city' in d and 'street' in d:
        if d['city']=='Cheb':
            if d['street']:
                return d['street']

get_street_dict({})

# Shape element such that streets in dictionary
startaddr = re.compile(r'(addr:)[a-z]*')

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        for tag in element.iter('tag'):
            if startaddr.search(tag.attrib['k']):
                if 'address' in node:
                    node['address'][tag.attrib['k'][5:]]=tag.attrib['v']
                else:
                    node['address']={}
                    node['address'][tag.attrib['k'][5:]]=tag.attrib['v']
            else:
                continue
        return node
    else:
        return None

  
    

def get_addr_map(file_in):
    data = []
    for _, element in ET.iterparse(file_in):
        el = shape_element(element)
        if el:
            street=get_street_dict(el['address'])
            if street!=None:
                union(data,[street])
    return data

streetlist_map=get_addr_map(smallfile)



def compare(list1,list2):
    l=[]
    for item in list1:
        if item not in list2:
            l.append(item)
    return l

print compare(completelist_street,streetlist_map)
print compare(streetlist_map,completelist_street)

            









