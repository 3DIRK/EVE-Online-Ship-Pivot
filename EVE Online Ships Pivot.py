import sqlite3
import pandas as pd
import requests
import bz2


# Link to SDE on Fuzzworks
link = "https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2"

# Handcrafted SQL
sql = """
SELECT 
	invGroups.groupName AS "Ship Group",
	chrRaces.raceName AS "Race Name",
	invTypes.typeName AS "Ship Name",
	invTypes.mass AS "Mass",
	invTypes.volume AS "Volume",
	invTypes.capacity AS "Cargo Capacity",
	invMarketGroups.marketGroupName AS "Market Group Name",
	dgmAttributeTypes.attributeName AS "Attribute Name",
    COALESCE(dgmTypeAttributes.valueInt,dgmTypeAttributes.valueFloat) AS "Attribute Value"
FROM 
	invGroups 
LEFT JOIN 
	invTypes ON invGroups.groupID = invTypes.groupID	
LEFT JOIN
	chrRaces ON invTypes.raceID = chrRaces.raceID	
LEFT JOIN
	dgmTypeAttributes ON invTypes.typeID = dgmTypeAttributes.typeID	
LEFT JOIN
	dgmAttributeTypes ON dgmTypeAttributes.attributeID = dgmAttributeTypes.attributeID
LEFT JOIN
	 invMarketGroups ON invTypes.marketGroupID =  invMarketGroups.marketGroupID
WHERE 
	invGroups.categoryID = 6 AND 
	invGroups.published = 1 AND 
	invTypes.published = 1 AND
	dgmAttributeTypes.published = 1 AND
	dgmAttributeTypes.attributeName IS NOT NULL
ORDER BY
	chrRaces.raceID,
	invGroups.groupID,
	dgmAttributeTypes.attributeID,
	invTypes.typeID,
	dgmAttributeTypes.attributeID
    """

# Download and store the SDE locally (for testing and debugging)
r = requests.get(link, allow_redirects=True)
open("sqlite-latest.sqlite", "wb").write(bz2.decompress(r.content))

# SQLite connection
conn = sqlite3.connect("sqlite-latest.sqlite")

# SQL Query in Panda Dataframe
sde_ships = pd.read_sql_query(sql, conn)

# Create the Pivot Table
index_pivot = ['Ship Group', 'Race Name', 'Ship Name', 'Mass', 'Volume', 'Cargo Capacity', "Market Group Name"] # Create the index, in order to avoid using these columns
columns_pivot = ['Attribute Name']  # Column with  the attributes --> will be transposed to columns
values_pivot = 'Attribute Value'  # Column with the values
ships = pd.pivot_table(sde_ships, values=values_pivot, columns=columns_pivot, index=index_pivot, fill_value=0)

# Create new index
ships.reset_index(inplace=True)
ships.set_index(['Ship Group', 'Race Name', "Market Group Name", 'Ship Name'], inplace=True)

# Add shield, armor, hull resistances as percentage value for convenience
for z in ["Armor EM Damage Resistance",
          "Armor Explosive Damage Resistance",
          "Armor Kinetic Damage Resistance",
          "Armor Thermal Damage Resistance",
          "Shield EM Damage Resistance",
          "Shield Explosive Damage Resistance",
          "Shield Kinetic Damage Resistance",
          "Shield Thermal Damage Resistance",
          "Structure EM Damage Resistance",
          "Structure Explosive Damage Resistance",
          "Structure Kinetic Damage Resistance",
          "Structure Thermal Damage Resistance"]:
    ships["_".join([z, "%"])] = ships[z].apply(lambda x: (1 - x)*100)

# Add Hit-Point (Raw)
ships["Raw Hitpoints"] = ships["Shield Capacity"] + ships["Armor Hitpoints"] + ships["Structure Hitpoints"]

# EHP calculation: Armor
ships["Armor EHP"] = round( \
					1/ \
					((ships["Armor EM Damage Resistance"] + \
					ships["Armor Explosive Damage Resistance"] + \
					ships["Armor Kinetic Damage Resistance"] + \
					ships["Armor Thermal Damage Resistance"]) \
                    / 4) \
                    *ships["Armor Hitpoints"], 0)

# EHP calculation: Shield
ships["Shield EHP"] = round( \
					1/ \
                    ((ships["Shield EM Damage Resistance"] + \
                    ships["Shield Explosive Damage Resistance"] + \
                    ships["Shield Kinetic Damage Resistance"] + \
                    ships["Shield Thermal Damage Resistance"]) \
                    / 4) \
                    * ships["Shield Capacity"], 0)
                    
# EHP calculation: Structure
ships["Structure EHP"] = round(  \
    				1/ \
					((ships["Structure EM Damage Resistance"] + \
					ships["Structure Explosive Damage Resistance"] + \
					ships["Structure Kinetic Damage Resistance"] + \
					ships["Structure Thermal Damage Resistance"]) \
                    / 4)
                    *ships["Structure Hitpoints"], 0)

# Overall EHP 
ships["Total EHP"] = ships["Armor EHP"] + ships["Shield EHP"] + ships["Structure EHP"]

# Add mass in tons for convenience 
ships["Mass Tons"] = ships["Mass"].apply(lambda x: x/1000)
ships.rename(columns={"Mass": "Mass Kilos"}, inplace=True)

# Calculate In-Agility (= Mass_Kilos * Inertia Modifier) --> Lower is better
ships["In-Agility"] = round(ships["Mass Kilos"] * ships["Inertia Modifier"] / 1000 / 1000, 2)

# Finally, save as CSV to import in Excel or Google Sheets
ships.to_csv("EVE Online Ships Pivot.csv", decimal=",", index=True, float_format='%g')

