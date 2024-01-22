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
