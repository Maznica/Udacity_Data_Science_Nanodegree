# -*- coding: utf-8 -*-
"""
Created on Sat May 23 17:55:49 2015

@author: mmasika
"""

############################################################################
############################################################################

# P R O J E C T  2  :  D A T A  W R A N G L I N G  W I T H  M O N G O  D B

# Keys and values
############################################################################
############################################################################


import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict


smallfile='cheb_cityboundary.osm'

##################################
# Examining the type of the key and value
# We are in particular interested whether there are bad characters in keys
# and/or values

####################################
# Cleaning data - how are the different key types structured

lower = re.compile(r'^([a-z]|_)*$', re.IGNORECASE) # lower letter
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$') #  if there is  a dopplepoint
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\.]') # e.g. question mark
startaddr=re.compile(r'(addr:)')
doppelpoints=re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
numbers=re.compile(r'\d')

# Key Type
def key_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            keys['lower_higher'] += 1
        elif lower_colon.search(element.attrib['k']):
            keys['lower_colon'] += 1
        elif problemchars.search(element.attrib['k']):
            keys['problemchars'] += 1
        elif doppelpoints.search(element.attrib['k']):
            keys['doublepoints'] += 1
        else:
            keys['other'] += 1
           
    return keys

# Value Type
def value_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['v']):
            keys['lower_higher'] += 1
        elif lower_colon.search(element.attrib['v']):
            keys['lower_colon'] += 1
        elif problemchars.search(element.attrib['v']):
            keys['problemchars'] += 1
            print element.attrib['v']
        elif doppelpoints.search(element.attrib['v']):
            keys['doublepoints'] += 1
        elif numbers.search(element.attrib['v']):
            keys['numbers'] +=1
        else:
            keys['other'] += 1
            
           
    return keys

def process_map(filename):
    keys = {"lower_higher": 0, "lower_colon": 0, "problemchars": 0, \
    "doublepoints":0, "other": 0}
    values = {"lower_higher": 0, "lower_colon": 0, "problemchars": 0, \
    "doublepoints":0, "other": 0, "numbers":0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
        values=value_type(element, values)

    return keys,values

key_types,value_types=process_map(smallfile)
pprint.pprint(key_types)
pprint.pprint(value_types)

# Keys which values have problematic characters

def problem_values(filename):
    d={}
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            if problemchars.search(element.attrib['v']):
                if element.attrib['k'] in d:
                    d[element.attrib['k']] +=1
                else:
                    d[element.attrib['k']]=1
    sorted_list= sorted(d.items(),key=lambda x:x[1], reverse=True)
    return sorted_list

problemvalues = problem_values(smallfile)
print problemvalues[:10]

    
####################################
# What are the most used keys stored in each tag

def count_keys(filename):
    dictionary={}
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag=='tag':
            if elem.attrib['k'] in dictionary:
                dictionary[elem.attrib['k']]=dictionary[elem.attrib['k']]+1
            else:
                dictionary[elem.attrib['k']]=1
    return dictionary

keys=count_keys(smallfile)
pprint.pprint(keys)
sorted_list= sorted(keys.items(),key=lambda x:x[1], reverse=True)
print len(sorted_list)
print sorted_list[:10]

# Source: http://stackoverflow.com/questions/16772071/sort-dict-by-value-python


#################################################
# C O U N T R Y 

# There should be only two countries in our Data: 'CZ' and 'DE'

def country_check(filename):
    listing=set()
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag=='tag':
            if elem.attrib['k']=="addr:country":
                listing.add(elem.attrib['v'])
    return listing

country_check(smallfile)

###############################################
# H O U S E  N U M B E R , 
# Speciality for Czech Republic - house number=conscriptionnumber/streetnumber

# Analyzing of the problems with the different street and house numbers   
def addr_numbers(filename):
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag=="node" or elem.tag=="way":
            d={}
            for item in elem.iter("tag"):
                if item.attrib['k']=="addr:conscriptionnumber":
                    d[item.attrib['k']]=item.attrib['v']
                elif item.attrib['k']=="addr:housenumber":
                    d[item.attrib['k']]=item.attrib['v']
                elif item.attrib['k']=="addr:streetnumber":
                    d[item.attrib['k']]=item.attrib['v']
            if len(d)==3:
                if d['addr:housenumber']!=d['addr:conscriptionnumber']+"/"+d['addr:streetnumber']:
                    print "Problem with hn!=cn/sn:\n",elem.attrib['id']
            elif len(d)==2 and 'addr:housenumber' in d and 'addr:streetnumber' in d:
                if d['addr:housenumber']!=d['addr:streetnumber']:
                    print "Problem with missing cn:\n",elem.attrib['id'], d
            elif len(d)==2 and 'addr:housenumber' in d and 'addr:conscriptionnumber' in d:
                if d['addr:housenumber']!=d['addr:conscriptionnumber']:
                    print "Problem with missing sn:\n",elem.attrib['id'], d
            elif len(d)==2 and 'addr:streetnumber' in d and 'addr:conscriptionnumber' in d:
                print "Problem with missing hn:\n",elem.attrib['id'], d
            elif len(d)==1 and 'addr:housenumber' in d and '/' in d['addr:housenumber']:
                print "Problem with missing both cn and sn:\n",elem.attrib['id'], d
                
print addr_numbers(smallfile)   

# Updating of the conscription or street number
def update_strnumber(d):
    if 'housenumber' in d and 'conscriptionnumber' in d and 'streetnumber' not in d:
        position=d['housenumber'].find('/')
        if d['housenumber'][:position]==d['conscriptionnumber']:
            d['streetnumber']=d['housenumber'][position+1:]
    elif 'housenumber' in d and 'conscriptionnumber' not in d and 'streetnumber' in d:
        position=d['housenumber'].find('/')
        if d['housenumber'][position+1:]==d['streetnumber']:
            d['conscriptionnumber']=d['housenumber'][:position]     
    elif 'housenumber' in d and d['housenumber'].find('/')!=-1:
        position=d['housenumber'].find('/')
        d['streetnumber']=d['housenumber'][position+1:]
        d['conscriptionnumber']=d['housenumber'][:position]
    return d


def test():
    dictionary1={'housenumber': '89/4'}
    dictionary2={'housenumber': '89'}
    dictionary3={'housenumber': '418/12', 'conscriptionnumber': '418'}
    dictionary4={'housenumber': '417/12', 'conscriptionnumber': '418'}
    dictionary5={'housenumber': 'ev.8/7', 'streetnumber': '7'}
    dictionary6={'housenumber': 'ev.8/7', 'streetnumber': '71'}
    update_strnumber(dictionary1)
    assert update_strnumber(dictionary1)=={'conscriptionnumber': '89', \
    'housenumber': '89/4', 'streetnumber': '4'}
    assert update_strnumber(dictionary2)=={'housenumber': '89'}
    assert update_strnumber(dictionary3)=={'conscriptionnumber': '418', \
    'housenumber': '418/12', 'streetnumber': '12'}
    assert update_strnumber(dictionary4)=={'conscriptionnumber': '418', \
    'housenumber': '417/12'}
    assert update_strnumber(dictionary5)=={'conscriptionnumber': 'ev.8', \
    'housenumber': 'ev.8/7', 'streetnumber': '7'}
    assert update_strnumber(dictionary6)=={'housenumber': 'ev.8/7', \
    'streetnumber': '71'}

test()    
      
    
#############################
# C I T I E S
    
# Checking Cities
def city_check(filename):
    listing=set()
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag=='tag':
            if elem.attrib['k']=="addr:city":
                listing.add(elem.attrib['v'])
    return listing

city_check(smallfile)

# Update city
def update_city(d):
    if 'city' in d and d['city']=='Hohenberg a.d.Eger':
        d['city']='Hohenberg an der Eger'
    return d
    
##########################
# P O S T  C O D E
    
# Checking the postal codes

def count_postalcodes(filename):
    dictionary={}
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag=='tag':
            if elem.attrib['k']=='addr:postcode':
                if elem.attrib['v'] in dictionary:
                    dictionary[elem.attrib['v']]=dictionary[elem.attrib['v']]+1
                else:
                    dictionary[elem.attrib['v']]=1
    return dictionary

count_postalcodes(smallfile)

# Updating postcodes requires only removing the non-number characters - only in 
# 1 case. (e.g. postcode = re.sub('\D','',postcode))


######################################
# P H O N E S

# Checking phones

def count_phones(filename):
    dictionary={}
    listing=[]
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag=='tag':
            if elem.attrib['k']=='phone':
                if elem.attrib['k'] in dictionary:
                    dictionary[elem.attrib['k']]=dictionary[elem.attrib['k']]+1
                    listing.append(elem.attrib['v'])
                else:
                    dictionary[elem.attrib['k']]=1
                    listing.append(elem.attrib['v'])
    return dictionary,listing

count_phones(smallfile)

# update Czech phones

def cz_updatephone(phone):
    if phone.find(',')!=-1:
        phone=phone.split(',')
    elif phone.find(';')!=-1:
        phone=phone.split(';')
    elif len(phone)<20:
        # remove all non-number charactes
        phone = re.sub('\D','',phone)
        phone="+" + phone[:3] +" "+ phone[3:6] +" "+ phone[6:9] +" "+ phone[9:12]
        phone=[phone]
    elif phone=='112':
        phone=[phone]
    return phone

        
cz_updatephone('+420 606 681 824, +420 606 681 823')
cz_updatephone('+420354595081')
cz_updatephone('+420 354 595081')
cz_updatephone('+420 354 595 081')

    
# update German phones
    
def de_updatephone(phone):
    # remove all non-number charactes
    phone = re.sub('\D','',phone)
    if phone.find('0')==0:
        phone = ['+49 ' + phone[1:5] + " " + phone[5:]]
    elif len(phone)>=10:
        phone = ['+' + phone[:2] + " " + phone[2:6] + " " + phone[6:]]
    elif phone=="112":
        phone = [phone]
    return phone

de_updatephone('09231/9624-0')
de_updatephone('+49 9235 981020')
de_updatephone('+49 9235 98102')
de_updatephone('+49 -92 35 - 98 11 0')


################################################
# R E G I O N

# What kind of regions are there
def region_check(filename):
    listing=set()
    for event, elem in ET.iterparse(filename, events=('start',)):
        if elem.tag=='node' or elem.tag=='way':
            for item in elem.iter("tag"):
                if item.attrib['k']=="is_in":
                    listing.add(item.attrib['v'])
    return listing


listing=region_check(smallfile)
print listing
# Filter out the problematic regions
for item in listing:
    l=item.split(',')
    if len(l)!=4 and l[-2:]!=[u' Karlovarský kraj', u' CZ']:
        print item


mapping={'Selb': 'Selb, Wunsiedel im Fichtelgebirge, Oberfranken, Bayern, DE', \
'Marktredwitz': 'Marktredwitz, Wunsiedel im Fichtelgebirge, Oberfranken, Bayern, DE', \
'Poustka': u'Poustka, Karlovarský kraj, CZ', \
'Neualbenreuth': 'Neualbenreuth, Tirschenreuth, Oberpfalz, Bayern, DE', \
'Arzberg': 'Arzberg, Wunsiedel im Fichtelgebirge, Oberfranken, Bayern, DE', \
'Hohenberg an der Eger': 'Hohenberg a.d.Eger, Wunsiedel im Fichtelgebirge, Oberfranken, Bayern, DE', \
u'Lipová u Chebu': u'Lipová u Chebu, Karlovarský kraj, CZ', \
'Waldershof': 'Waldershof, Tirschenreuth, Oberpfalz, Bayern, DE', \
u'Höchstädt i.Fichtelgebirge': u'Höchstädt i.Fichtelgebirge, Wunsiedel im Fichtelgebirge, Oberfranken, Bayern, DE', \
'Tirschenreuth': 'Tirschenreuth, Tirschenreuth, Oberpfalz, Bayern, DE', \
'Pechbrunn': 'Pechbrunn, Tirschenreuth, Oberpfalz, Bayern, DE', \
'Wunsiedel im Fichtelgebirge': 'Wunsiedel im Fichtelgebirge, Wunsiedel im Fichtelgebirge, Oberfranken, Bayern, DE', \
'Thierstein': 'Thierstein, Wunsiedel im Fichtelgebirge, Oberfranken, Bayern, DE', \
u'Libá': u'Libá, Karlovarský kraj, CZ', \
'Konnersreuth': 'Konnersreuth, Tirschenreuth, Oberpfalz, Bayern, DE', \
'Thiersheim': 'Thiersheim, Wunsiedel im Fichtelgebirge, Oberfranken, Bayern, DE', \
'Schirnding': 'Schirnding, Wunsiedel im Fichtelgebirge, Oberfranken, Bayern, DE', \
'Hazlov': u'Hazlov, Karlovarský kraj, CZ', \
'Waldsassen': 'Waldsassen, Tirschenreuth, Oberpfalz, Bayern, DE'}
    

# update region
def update_name(name, mapping):
    keys = mapping.keys()
    listing = name.split(",")
    for item in keys:
        if item==listing[0]:
            name=mapping[item]
    return name

# Tests
update_name('Selb', mapping)
update_name('Arzberg,Kreis Wunsiedel', mapping)
update_name(u'Höchstädt i.Fichtelgebirge', mapping)
update_name("Bukovany, Karlovarský kraj, CZ",mapping)





#############################################
# STREET 

street_types=""
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
gasse_re =re.compile(r'(gasse)$', re.IGNORECASE)
strasse_re =re.compile(r'(stra\xdfe)$', re.IGNORECASE)
weg_re = re.compile(r'(weg)$',re.IGNORECASE)
platz_re = re.compile(r'(platz)$',re.IGNORECASE)
street_types = defaultdict(set)


m=strasse_re.search(u'Siedlungsstra\xdfe')
if m:
    print m.group()

expected=[u"Náměstí",u"Straße", "Platz", "Ulice", "Weg", "Gasse", \
"gasse", u"straße", "weg", "platz"]

# Searching for more patterns
def search_more(street_name):
    m = gasse_re.search(street_name)
    n = strasse_re.search(street_name)
    o = weg_re.search(street_name)
    p = platz_re.search(street_name)
    if m:
        return m.group()
    elif n:
        return n.group()
    elif o:
        return o.group()
    elif p:
        return p.group()
    else:
        return street_name

    

def audit_street_type(street_types, street_name):
    listing=street_name.split(" ")
    if len(listing)>1:
        m=street_type_re.search(street_name)
        if m:
            street_type=m.group()
            if street_type not in expected:
                street_types[street_type].add(street_name)
    else:
        street_type=search_more(street_name)
        if street_type not in expected:
            street_types[street_type].add(street_name)


def print_sorted_dict(d):
    keys = d.keys()
    keys =sorted(keys,key=lambda s: s.lower())
    for k in keys:
        v=d[k]
        print "%s: %d" % (k,v)

def is_street_name(elem):
    return (elem.attrib['k']=="addr:street")

def audit():
    for event, elem in ET.iterparse(smallfile,events=("start",)):
        if elem.tag=="way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    pprint.pprint(dict(street_types))
    #print_sorted_dict(street_types)

if __name__=='__main__':
    audit()
    result1=audit()
    print result1



def problem_values_str(filename):
    d={}
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            if element.attrib['k']=='addr:street':
                if problemchars.search(element.attrib['v']):
                    if element.attrib['v'] in d:
                        d[element.attrib['v']] +=1
                    else:
                        d[element.attrib['v']]=1
    sorted_list= sorted(d.items(),key=lambda x:x[1], reverse=True)
    return sorted_list

problemvalues_str = problem_values_str(smallfile)
print problemvalues_str
for item in problemvalues_str:
    print item[0], item[1]


























    