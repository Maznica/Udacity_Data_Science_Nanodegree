# -*- coding: utf-8 -*-
"""
Created on Sat May 23 17:55:49 2015

@author: mmasika
"""

############################################################################
############################################################################

# P R O J E C T  2  :  D A T A  W R A N G L I N G  W I T H  M O N G O  D B

# DATA ANALYZIS
############################################################################
############################################################################

import os
from pymongo import MongoClient
import pprint


osmfile="cheb_cityboundary.osm"
jsonfile="cheb_cityboundary.json"

# Size of the imported file
print "The osm file is {} MB".format(os.path.getsize(osmfile)/1.0e6)

# Size of the imported file
print "The json file is {} MB".format(os.path.getsize(jsonfile)/1.0e6)

##############
# Analyzis

client=MongoClient('localhost:27017')
db = client['project2']
collection = db.cheb

#######################
# Documents, Ways and Nodes
##########################

# Number of documents
count=collection.find().count()
print 'There are ' + str(count) + ' documents.'

# Number of ways and nodes

count_node = collection.find({"type": "node"}).count()
count_way = collection.find({"type": "way"}).count()
percentage_node=100.*count_node/count

print count_node, count_way, percentage_node

# alternatively

types=collection.aggregate([{"$group" : {"_id" : "$type", "count" : {"$sum" : 1}}}, \
                           {"$sort" : {"count" : -1}}])['result']

print types


# Nodes only with basic information

nodes_created= collection.find({"num_keys": 4, "type": "node"}).count()

print nodes_created

# Nodes and Ways with country info:

docu_country=collection.aggregate([{"$group": {"_id": \
{"type":"$type","address.country":"$address.country"},"count":{"$sum":1}}}])

print docu_country


############################
# Users
############################

# Situations with uid but not with user and vice versa

uidnouser= collection.find({"created.uid":{"$exists":1},"created.user":{"$exists":0}}).count()
usernouid= collection.find({"created.uid":{"$exists":0},"created.user":{"$exists":1}}).count()

print "Situations with uid but no user: " + str(uidnouser)
print "Situations with uid but no user: " + str(usernouid)

# Unique user

unique_user=len(collection.distinct("created.user"))

print unique_user

# Unique user with address information

unique_useraddr=collection.aggregate([{"$match":{"address.country":{"$exists": 1}}}, \
{"$group": {"_id": 'All together', "uset":{"$addToSet": "$created.user"}}}, \
{"$project":{"uniques": {"$size": "$uset"}}}])

print unique_useraddr

# Unique use by country:

unique_usercountry=collection.aggregate([{"$match": {"address.country":{"$exists":1}}}, \
{"$group": {"_id": "$address.country", \
"uset": {"$addToSet": "$created.user"}}}, \
{"$project": {"uniqueusers": {"$size": "$uset"}}}])

print unique_usercountry



# The most contributed user

most_user=collection.aggregate([{"$group": {"_id": "$created.user","count": \
{"$sum": 1}}},{"$sort":{"count":-1}},{"$limit":1}])

print most_user

# Share of documents added by most contributed user 

share_mostdoc=100.*most_user['result'][0]['count']/count

print share_mostdoc

# Most contributed user by country

most_user_c=collection.aggregate([{"$match": {"address.country": {"$exists": 1}}}, \
{"$group": {"_id": {"created.user":"$created.user", \
"address.country": "$address.country"},"count":{"$sum": 1}}}, \
{"$sort":{"count":-1}}])

print most_user_c

# Distribution of documents by user

def contr_share():
    contributors=collection.aggregate([{"$group": {"_id": "$created.user","count": \
    {"$sum": 1}}},{"$sort":{"count":-1}}])['result']
    contshare=0
    for item in contributors:
        item['share']=100.*item['count']/count
        item['contshare']=item['share']+contshare
        contshare=item['contshare']
    return contributors

print contr_share()[:10]

# by country
def contr_share_c(country):
    contributors=collection.aggregate([{"$match":{"address.country": country}}, \
    {"$group": {"_id": "$created.user","count": \
    {"$sum": 1}}},{"$sort":{"count":-1}}])['result']
    count_c=collection.find({"address.country": country}).count()
    contshare=0
    for item in contributors:
        item['share']=100.*item['count']/count_c
        item['contshare']=item['share']+contshare
        contshare=item['contshare']
    return contributors

print contr_share_c('CZ')[:10]
print contr_share_c('DE')[:10]


###########################
# N O D E S
##########################


################################
# Node References - what is the most refered node - with duplicates

most_noderefs=collection.aggregate([{"$match":{"type": "way"}},\
{"$unwind": "$node_refs"},\
{"$group": {"_id":"$node_refs","count":{"$sum":1}}},\
{"$sort": {"count":-1}},\
{"$limit":1}])

print most_noderefs, collection.find_one({"id": most_noderefs})

####################
# Nodes which are most refered to (without duplicates)

most_unique_noderefs = collection.aggregate([{"$unwind": "$node_refs"}, \
{"$group": {"_id": "$id", "nset": {"$addToSet": "$node_refs"}}}, \
{"$unwind": "$nset"},\
{"$group": {"_id": "$nset", "count": {"$sum":1}}},\
{"$sort": {"count":-1}},\
{"$limit": 1}])

print most_unique_noderefs

###############################
# A M E N I T I E S
###############################

most_amenities = collection.aggregate([{"$match": {"amenity": {"$exists": 1}}}, \
{"$group":{"_id": "$amenity", "count": {"$sum": 1}}}, \
{"$sort": {"count": -1}}, {"$limit": 10}])



print most_amenities


################################
# Cities by region
################################

#######################
# Updating Regions

regions=['Karlovarský kraj', 'Oberfranken', 'Oberpfalz']

def multi_update_1():
    for item in regions:
        collection.update({"is_in": {"$regex": item}}, \
        {"$set": {"address.region": item }}, multi=True)

multi_update_1()

# List Cities
list_cities=collection.aggregate([{"$match":{"address.city":{"$exists": 1}}}, \
{"$group":{"_id": "List of cities", \
"cityset":{"$addToSet": "$address.city"}}}])['result'][0]['cityset']

def mapping_c_r():
    d={}
    for item in list_cities:
        dict_reg=collection.find_one({"is_in": {"$regex": item}})
        if dict_reg:
            region=dict_reg["address"]["region"]
            d[item]=region
    return d
    
mapping_c_r=mapping_c_r()

def multi_update_2():
    keys=mapping_c_r.keys()
    for item in keys:
        collection.update({"address.city": item}, \
    {"$set": {"address.region": mapping_c_r[item]}}, multi=True)

multi_update_2()

#######################
# Cities by region
 
cities_by_reg= collection.aggregate([{"$match": {"address.city": {"$exists": 1}}}, \
{"$group": {"_id":"$address.region", "cset": {"$addToSet": "$address.city"}}}, \
{"$project":{"uniquecities":{"$size": "$cset"}}}])

print cities_by_reg






























