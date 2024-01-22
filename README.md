# EVE Online Ship Pivot

The aim of this Python script is to download and extract static data (EVE SDE) of EVE Online ships and convert it to CSV file. The CSV file can easily imported into any spreadsheet app like Excel or Google Sheets.

Python enthusiasts might love the possibility to work with Pandas to reach the same goal.

## Example analytics whith Pandas

### Find certain columns per name

``` python
[col for col in ships.columns if "Name" in col]
```

### Analyse maximum speed per ship group and race

``` python
ships.groupby(level=["Ship Group", "Race Name"])["Maximum Velocity"].max()
```

## Analyse highest agility

``` python
ships.groupby(level=["Ship Group", "Race Name", "Market Group Name", "Ship Name"])["In-Agility"].min()
```

## Analyse highest agility with hitpoints

``` python
ships["Agility Raw Hitpoints"] = round(ships["Raw Hitpoints"] / ships["In-Agility"], 0)
ships["Agility EHP Hitpoints"] = round(ships["Total EHP"] / ships["In-Agility"], 0)
ships.loc["Frigate"][["Mass Tons", "Inertia Modifier", "In-Agility", "Raw Hitpoints", "Agility Raw Hitpoints", "Total EHP", "Agility EHP Hitpoints"]].sort_values(by="Agility EHP Hitpoints", ascending=False)
```



# CCP Copyright Notice
EVE Online, the EVE logo, EVE and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf. EVE Online and the EVE logo are the registered trademarks of CCP hf. All rights are reserved worldwide. All other trademarks are the property of their respective owners. CCP is in no way responsible for the content on or functioning of this program, nor can it be liable for any damage arising from the use of this program.
