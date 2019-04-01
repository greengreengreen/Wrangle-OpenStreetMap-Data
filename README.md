# Wrangle-OpenStreetMap-Data
This goal of this project is to extract local cuisines in Seattle from openmap data. </br>
Steps are as below: </br>

• Corrected inconsistency problems like over-abbreviated street names, problematic postcode numbers and etc of a 1.6 GB OSM formatted Seattle area map dataset with the 're' package after parsing the dataset using ElementTree in Python.</br>

• Created a relational database, defined its schema in SQLite and imported the audited map data into the database.<./br>

• Queried the database in SQL and generated reports about local cuisines in Seattle.
