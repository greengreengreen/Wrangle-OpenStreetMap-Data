#OpenStreetMap Data of Case Study
##Map Area
Seattle, WA, United States

https://www.openstreetmap.org/relation/237385

https://mapzen.com/data/metro-extracts/metro/seattle_washington/ 

I chose Seattle because I have always been intersted in it for its multicultural environment, special coffee culture and so on.

##Problems Encountered in the Map
After checking the elements in the osm file, I found 4 problems:
1. Overabbreviated street names
2. Problematic postcode numbers
3. Unabbreviated name type
4. Ununified maxspeed format

###Overabbreviated street names
```sql
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
      UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='street'
GROUP BY tags.value
ORDER BY count DESC;
```
According to the results of the query, there exists overabbreviated street names like '251st Ave. SE' and 'Pacific Avenue S'. By creating a mapping dictionary, we could easily improve street names.

```python
mapping_direction = { 'NE': 'Northeast', 'SE': 'Southeast', 'NW': 'Northwest', 'SW': 'Southwest',
            		'N': 'North', 'W': 'West', 'S': 'South', 'E': 'East'}
mapping_way = {'Ave.': 'Avenue', 'Rd': 'Road', 'Ln': 'Lane'}

def audit_street(street): 
	street_names = street.split()
	for i,name in enumerate(street_names):
		if name in mapping_direction.keys():
			street_names[i] = mapping_direction[name]
		elif name in mapping_way.keys():
			street_names[i] = mapping_way[name]
	street = ' '.join(street_names)
	return street
```

###Problematic postcode numbers
```sql
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags 
      UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key='postcode'
GROUP BY tags.value
ORDER BY count DESC;
```
Part of the results are as follows:
```sql
98034,50
98033,42
98115,40
98103,37
98118,28
98125,27
98133,21
98273,19
98108,18
98271,1
98408,1
98447,1
98466,1
98501,1
"V9B 0J8",1
```
From the query result, most postcodes start from '98', however, there exists a 'V9B 0J8', which apparently is not a standard postcode of Seattle area according to google search.( http://postalcode.globefeed.com/us_postal_code.asp?dt1=ChIJVTPokywQkFQRmtVEaUZlJRA&pl=Seattle,%20WA,%20United%20States ) 
Therefore, we need to dump the problematic postcodes by regulate the postcode data format to start from '98' and be a 5-digit number.

```python
#dump the data when return False
def audit_postcode(postcode):
	if len(postcode) != 5:
		return False
	elif postcode[0:2] != '98':
		return False
	else:		
		return True

```

###Unabbreviated name type
```sql
SELECT ways_tags.key, ways_tags.value, COUNT(*) as count 
FROM  ways_tags
WHERE ways_tags.key='name_type'
GROUP BY ways_tags.value
ORDER BY count DESC;
```
```sql
St,36
Ave,28
Rd,20
Ct,12
Dr,11
Ln,11
Pl,5
Way,2
"Ave; St",1
Avenue,1
Blvd,1
Hwy,1
```
'name_type' key generally has a value that is well abbreviated, like 'St', 'Ave', 'Rd'. But there exists some values that are not. We need to fix this by applying map dictionary here. 
```python
mapping_way_inverse = {'Avenue': 'Ave', 'Road': 'Rd', 'Lane': 'Ln'}
def audit_nametype(nametype):
	names = nametype.split()
	for i, name in enumerate(names):
		if name in mapping_way_inverse.keys():
			names[i] = mapping_way_inverse[name]
	nametype = ';'.join(names)
	return nametype
```
###Ununified maxspeed format
```sql
SELECT ways_tags.key, ways_tags.value, COUNT(*) as count 
FROM  ways_tags
WHERE ways_tags.key='maxspeed'
GROUP BY ways_tags.value
ORDER BY count DESC;
```
```sql
maxspeed,"25 mph",15
maxspeed,"35 mph",12
maxspeed,"30 mph",6
maxspeed,"15 mph",5
maxspeed,"40 mph",4
maxspeed,"55 mph",3
maxspeed,30,2
maxspeed,"70 mph",2
maxspeed,sign,2
maxspeed,"20 mph",1
maxspeed,40,1
maxspeed,"45 mph",1
maxspeed,50,1
maxspeed,"50 mph",1
maxspeed,"60 mph",1
```
Some values have unit while others don't. 'sign' means signal here. 
I will add unit 'mph' to those who don't. Since it's in Seattle, WA, the units will all be 'mph'.
```python
def audit_maxspeed(speed):
	names = speed.split()
	if len(names) == 1 and names[0].isdigit() == True:
		names.append('mph')
	speed = ' '.join(names)
	return speed
``` 
##Data Overview And Additional Ideas
This sections includes basic information about the size of files and some 

###File Sizes
```
seattle_washington.osm     ...  1.63 GB
seattle_washington.db      ... 935.7 MB
nodes.csv                  ...   622 MB
nodes_tags.csv             ...  41.7 MB
ways.csv                   ...  43.1 MB   
ways_nodes.csv             ... 191.8 MB
ways_tags.csv              ... 128.6 MB

sample_seattle.osm         ...   8.2 MB
sample_seattle.db          ...   4.6 MB
nodes_sample.csv           ...   3.1 MB
nodes_tags_sample.csv      ...   205 KB
ways_sample.csv            ...   216 KB   
ways_nodes_sample.csv      ...   928 KB
ways_tags_sample.csv       ...   645 KB



```
###Number of Nodes
```sql
SELECT COUNT(*) FROM nodes;
```
```
7301290
```

###Number of Ways
```sql
SELECT COUNT(*) FROM ways;
```
```
716561
```

###Number of Unique Users
```sql
SELECT COUNT(DISTINCT(e.uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;
```
```
3075
```

###Top 10 Contributing Users
```sql
SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;
```
The top 10 Contributing Users are as below:
```
Glassman,1230411
SeattleImport,741414
tylerritchie,659782
woodpeck_fixbot,598816
alester,355405
Omnific,230272
Glassman_Import,227583
STBrenden,219754
"Brad Meteor",178062
Amoebabadass,164776
```
The following code gets the total contribution of the top 10 contributing users.

```sql
SELECT sum(top10users.num) as sum
FROM 
(SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10) top10users
```
```
4606275
```
The following code gets the total number of contribution made by all users.
```sql
SELECT count(e.user) as sum 
FROM 
(SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
```
```
8017850
```
Therefore, the top 10 cntributing users make up 4606275/8017850 = 57.450% of the whole data. 

###Top 10 Sources

```sql
SELECT e.key, e.value, COUNT(*) as num
FROM (SELECT key,value FROM nodes_tags UNION ALL SELECT key,value FROM ways_tags) e
WHERE e.key = 'source'
GROUP BY e.value
ORDER BY num DESC
LIMIT 10;
```
```
source,"King County GIS;data.seattle.gov",183117
source,tiger_import_dch_v0.6_20070830,59024
source,data.seattle.gov,56568
source,Bing,39366
source,NRCan-CanVec-10.0,38249
source,"King County GIS",33705
source,http://www.fs.fed.us/r6/data-library/gis/olympic/hydronet_meta.htm,32328
source,US-NPS_import_b2a6c900-5dcc-11de-8509-001e2a3ffcd7,29764
source,PGS,21531
source,bing,12167
```
Seems that lots of data are from 'King Country GIS;data.seattle.gov'.

###The Specific Area of the Map 
```
SELECT e.key, e.value, COUNT(*) as num
FROM (SELECT key,value FROM nodes_tags UNION ALL SELECT key,value FROM ways_tags) e
WHERE e.key = 'city'
GROUP BY e.value
ORDER BY num DESC
LIMIT 10;
```
```
city,Seattle,203388
city,Kirkland,42285
city,"Mount Vernon",11725
city,Saanich,11617
city,Langford,2807
city,"Oak Bay",2298
city,Colwood,1985
city,Sooke,1601
city,Esquimalt,1495
city,"View Royal",1000
```
Apparantly, the region of the map includes not only Seattle City, but also other cities. Therefore, the map contains the wide range of Seattle area.

###Top 10 Appearing Cuisine
```sql
SELECT key, value, COUNT(*) as num
FROM nodes_tags
WHERE key = 'cuisine'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```
```
cuisine,coffee_shop,547
cuisine,pizza,335
cuisine,sandwich,321
cuisine,mexican,301
cuisine,burger,281
cuisine,american,164
cuisine,asian,152
cuisine,chinese,136
cuisine,japanese,131
cuisine,thai,128
```
Seems like there are many coffee shops in Seattle. According to wikipeida, 
>Seattle is a world center for coffee roasting and coffee supply chain management. Related to this, many Seattle-area people are coffee enthusiasts and they maintain a coffee culture in Seattle's many coffeehouses.

### 
```sql
SELECT e.value, COUNT(*) AS num
FROM (SELECT key,value FROM nodes_tags UNION ALL SELECT key,value FROM ways_tags) e
WHERE e.key = 'created'
GROUP BY e.value
ORDER BY num
DESC;
```
```
09/10/1979,1379
07/15/2008,955
03/01/1993,414
11/01/1991,355
12/31/1992,194
03/01/1990,130
11/03/2008,130
05/01/1992,119
07/01/1994,105
09/01/1990,92
08/01/1990,82
11/01/1992,59
01/01/1995,42
12/01/1990,41
04/01/1991,40
07/01/1990,20
06/01/1992,17
01/01/1992,14
10/01/1990,10
08/01/1993,9
11/01/1990,9
05/01/1991,8
11/17/2008,7
02/05/2004,6
12/01/1991,6
07/01/1989,5
07/15/2003,5
09/01/1993,5
02/01/1991,3
10/01/1989,3
01/01/1991,2
02/01/1992,2
03/01/1991,2
04/01/1990,2
10/01/1991,2
03/01/1933,1
04/14/1999,1
04/20/2006,1
05/01/1989,1
05/01/1995,1
06/01/1995,1
07/01/1992,1
07/15/1998,1
09/15/2010,1
09/20/2000,1
10/01/1992,1
10/01/1994,1
11/06/2000,1
```
According to the data, the data are mostly created on 09/10/1979. And the earliest created date is 03/01/1933.

```sql
SELECT nodes_tags.key, nodes_tags.value, COUNT(nodes_tags.key) AS num
FROM nodes_tags
LEFT JOIN
(SELECT id, key, value 
FROM nodes_tags
WHERE value = '09/10/1979') e
ON nodes_tags.id = e.id
GROUP BY nodes_tags.key
ORDER BY num
DESC;
```

###Non-English Tags 
```python
def isEnglishString(s):
    for s_value in s.split(' '):
        if isEnglishWord(s_value) == True:
            return True
    return False        

def isEnglishWord(w):
    try:
        w.decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def print_non_English():
    total_no = 0
    non_English_no = 0
    with open("nodes_tags.csv", "rb") as f:
        for line in f:
            values = line.split(',')
            total_no += 1
            if isEnglishString(values[2]) == False:
                non_English_no+=1
                print values[1], values[2]

    print 'total tag number = ', total_no
    print 'non_English tag number = ', non_English_no
print_non_English
```
Part of the results are as follows:
```
arz صب واى
name 西雅圖下車
name 港口
ru Каса Эль Дорадо
name Freshëns
zh 西雅圖雷藏寺
name Denny’s
name O’Char
name Métier Café
operator Métier
de Brücke
artist_name Ćakwasap
zh 碧近山駕駛學校
zh 西雅圖華人駕校筆試路考中心
name Aéropostale
vi Phở tái
total tag number =  1076753
non_English tag number =  228
[Finished in 1.8s]
```
According to the result, there are many non-English tags, making up 228/1076753 = 00.02117% of the total tags. The non-English tags contain languages like Chinese, Korean, Japanese, Russian etc. 
Seattle is a very international area referring to the result. 

###Suggestions

By exploring the key value of the tags, I found that many of them indicate similar concepts. For instance, 'name', 'name_base', 'name_type' all contain the name information. According the 
osm document on wiki(https://wiki.openstreetmap.org/wiki/TIGER_to_OSM_Attribute_Map#Feature_Name):
>OSM Key|TIGER Field|Example
>-------|-----------|-------
>name|"#{fedirp} #{fename} #{fetype} #{fedirs}".strip|"NW Chester St S"
>name_direction_prefix|fedirp|"NW", "Southwest"
>name_base|fename|"Chester"
>name_type|fetype|"Street", "Ave"
>name_direction_suffix|fedirs|"S"

Refer to the imformation above, a cross-validation could be built among 'name', 'name_direction_prefix', 'name_base', 'name_type' and 'name_direction', since 'name' is supposed to
contain the information that other name-related tags offer. If not, the name-related tags are problematic.

```python

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
										
			
		del names_temp

```
Part of the results are as follow:
```
{'name_base': 'Davidson', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Kulshan View Road', 'name_type': 'Blvd'}
{'name_base': 'Decatur Head', 'name_direction_prefix': None, 'name_direction_suffix': 'N', 'name': 'Davis Beach Road', 'name_type': 'Dr'}
{'name_base': 'Runway View', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Airport Perimeter Way', 'name_type': None}
{'name_base': 'Sylvan Cove', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Reed Bay Road', 'name_type': 'Rd'}
{'name_base': 'Decatur Head', 'name_direction_prefix': None, 'name_direction_suffix': 'S', 'name': 'Davis Beach Road', 'name_type': 'Dr'}
{'name_base': 'Appletree', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Apple Tree Lane', 'name_type': 'Ln'}
{'name_base': 'Johanson-Crosby', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Bowers Road', 'name_type': 'Rd'}
{'name_base': 'Johanson-Crosby', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Bowers Road', 'name_type': 'Rd'}
{'name_base': 'Pear Point', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Whiteley Way', 'name_type': 'Rd'}
{'name_base': 'Armitage', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Decatur Head Drive', 'name_type': 'Rd'}
{'name_base': 'Decatur Head', 'name_direction_prefix': None, 'name_direction_suffix': 'N', 'name': 'Kulshan View Road', 'name_type': 'Dr'}
{'name_base': 'Ocean Spray', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Shearwater Lane', 'name_type': 'Ln'}
{'name_base': 'Haidah;Wishah', 'name_direction_prefix': None, 'name_direction_suffix': None, 'name': 'Haidah Street', 'name_type': 'St;Ln'}

```
Every dictionary above contains name information of a way and the items in each dictionary ought to be in accordance with each other. However, the above dictionaries are
problematic since the 'name_base' is not included in the 'name' tags. It is hard to explain why these information contradicts with each other. 
They need to be further surveyed. Since OSM documents use 'fixme' tags to store the information that is temporarily uncertain, a possible solution is to dump the problematic data
and create new 'fixme' tags, listing the problematic dictionary above. 



#Conclusion
In general, the openstreetmap of Seattle is clean after auditing the data following the steps mentioned in this report. 
By importing the data into sql and querying the results, I get information about Seattle area
like cuisines, date when the data was created, amenities and so on. The tags show that Seattle is a multicultural and international area with many languages in use.
To further improve the data, I think cross-validation could be in use, since some information really need to be further surveyed. Also, gamification the contributing process may
increase the user's willingess to contribute to the map community. 















