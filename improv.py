import xml.etree.cElementTree as ET
from test_osm import get_element
OSM_PATH = "seattle_washington.osm"

name0 = {'name': None, 'name_base':None, 'name_type':None, 'name_direction_prefix':None, 
		'name_direction_suffix':None} 
name1 = {'name_1': None, 'name_base_1':None, 'name_type_1':None, 'name_direction_prefix_1':None, 
		'name_direction_suffix_1':None} 
name2 = {'name_2': None, 'name_base_2':None, 'name_type_2':None, 'name_direction_prefix_2':None, 
		'name_direction_suffix_2':None} 
name3 = {'name_3': None, 'name_base_3':None, 'name_type_3':None, 'name_direction_prefix_3':None, 
		'name_direction_suffix_3':None} 
name4 = {'name_4': None, 'name_base_4':None, 'name_type_4':None, 'name_direction_prefix_4':None, 
		'name_direction_suffix_4':None} 
names = [name0, name1, name2, name3, name4]


seq0 = ('name','name_base', 'name_type', 'name_direction_prefix', 'name_direction_suffix')
seq1 = ('name_1','name_base_1', 'name_type_1', 'name_direction_prefix_1', 'name_direction_suffix_1')
seq2 = ('name_2','name_base_2', 'name_type_2', 'name_direction_prefix_2', 'name_direction_suffix_2')
seq3 = ('name_3','name_base_3', 'name_type_3', 'name_direction_prefix_3', 'name_direction_suffix_3')
seq4 = ('name_4','name_base_4', 'name_type_4', 'name_direction_prefix_4', 'name_direction_suffix_4')
seqs = [seq0,seq1,seq2,seq3,seq4]

def name_ornot(name1, name2):
	return len(set(name1.items()).intersection(name2.items())) <=3
	
def improv(element):
	if element.tag == 'way':
		#create a new name list
		names_temp = []
		name_temp = {}
		for i in range(0,5):
			name_temp = {}
			name_temp = name_temp.fromkeys(seqs[i])
			names_temp.append(name_temp)
		del name_temp

		#Fill names_temp list with expected values
		for tag in element.iter('tag'):
			tag_key = tag.attrib['k']
			tag_value = tag.attrib['v']
			for i in range(0,5):
				if tag_key in seqs[i]:
					names_temp[i][tag_key] = tag_value

		#Find the names and print them out
		for i in range(0,5):
			name_temp = names_temp[i]
			name_ori = names[i]

			if name_ornot(name_temp, name_ori) == True: 
			# if a tag contains name or name_base and so on
				if name_temp[seqs[i][0]] != None:#Name != None
					whole_name = name_temp[seqs[i][0]]
					if name_temp[seqs[i][1]] != None and name_temp[seqs[i][1]] not in whole_name:
						#name_temp[seqs[i][1]] is the value of name_base
						print name_temp
										
				# print '\n'
		del names_temp

	
	# return element
if __name__ == '__main__':
	for element in get_element(OSM_PATH, tags=('node', 'way')):
		improv(element)
	





