# VC-MP Query

Async Python client for querying Vice City Multiplayer servers using the Vice City Multiplayer Protocol (VC-MP).

This library allows you to retrieve:

Server status

List of players

Server metadata (name, gamemode, map, etc.)

# About

The Vice City Multiplayer protocol allows external tools to query game servers for information such as:

- Server version

- Number of players

- Maximum players

- Server name

- Game type

This library implements the query protocol using async UDP communication.

Protocol identifiers used:
```
Request header  : VCMP
Response header : MP04
```
