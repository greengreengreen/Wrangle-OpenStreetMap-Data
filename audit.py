import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSM_FILE = 'SAMPLE.OSM'

mapping_direction = { 'NE': 'Northeast', 'SE': 'Southeast', 'NW': 'Northwest', 'SW': 'Southwest',
                'N': 'North', 'W': 'West', 'S': 'South', 'E': 'East'}
mapping_way = {'Ave.': 'Avenue', 'Rd': 'Road', 'Ln': 'Lane'}
mapping_way_inverse = {'Avenue': 'Ave', 'Road': 'Rd', 'Lane': 'Ln'}

def audit_street(street): 
    street_names = street.split()
    for i,name in enumerate(street_names):
        if name in mapping_direction.keys():
            street_names[i] = mapping_direction[name]
        elif name in mapping_way.keys():
            street_names[i] = mapping_way[name]
    street = ' '.join(street_names)
    return street

def audit_nametype(nametype):
    names = nametype.split()
    for i, name in enumerate(names):
    	if name in mapping_way_inverse.keys():
      		names[i] = mapping_way_inverse[name]
    nametype = ';'.join(names)
    return nametype

#dump the data when return False
def audit_postcode(postcode):
    if len(postcode) != 5:
        return ''
    elif postcode[0:2] != '98':
        return ''
    else:   
        return postcode

def audit_maxspeed(speed):
    names = speed.split()
    if len(names) == 1 and names[0].isdigit() == True:
        names.append('mph')
        speed = ' '.join(names)
    return speed



def audit(element):
	if element.tag == 'way' or 'node':
		for tag in element.iter('tag'):
			tag_key = tag.attrib['k']
			tag_value = tag.attrib['v']
			if element.tag == 'way':
				if tag_key == 'name_type':
					tag.attrib['v'] = audit_nametype(tag_value)
				elif tag_key == 'maxspeed':
					tag.attrib['v'] = audit_maxspeed(tag_value)


			if tag_key == 'street':
				tag.attrib['v'] = audit_street(tag_value)
			elif tag_key == 'postcode':
				tag.attrib['v'] = audit_postcode(tag_value)
	return element

























