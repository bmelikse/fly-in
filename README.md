# Fly-in project 42 curriculum.

## Map Parsing:
The general format of the Fly-in maps are as follows:
`<line_prefix> <name> <x> [optional_metadata]`

Example:
`start_hub: hub 0 0 [color=green]` — there's a zone named "hub" at (0,0) colored green and it's the start.

A class method was used after separating the main part and optional metadata for creating an object(?).