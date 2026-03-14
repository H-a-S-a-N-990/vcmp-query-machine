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
# Installation

Clone the repository:
```
git clone https://github.com/H-a-S-a-N-990/vcmp-query-machine.git
cd vcmp-query-machine
```

# Example Usage 

Get Server status ( like vc-mp browser or game-state.com )

```
import asyncio
from vcmp-query import VCMPQuery

async def main():
    server = VcmpQuery("127.0.0.1", 8192)

    try:
        status = await server.get_status()
        print("=== SERVER STATUS ===")
        print("Name:", status.server_name)
        print("Version:", status.version)
        print("Gamemode:", status.game_mode)
        print("Map:", status.map_name)
        print("Players:", status.num_players, "/", status.max_players)
        print("Passworded:", status.passworded)

        players = await server.get_players()
        print("\n=== PLAYER LIST ===")
        if not players:
            print("No players online.")
        else:
            for p in players:
                print("-", p.name)

    except Exception as e:
        print("Error:", e)

asyncio.run(main())
```

- example output
```
===== SERVER STATUS =====
Name: My VCMP Server
Version: 04rel006
Gamemode: Freeroam
Language: English
Players: 3 / 100
Passworded: False

===== PLAYER LIST =====
- Player1
- Player2
- Player3
```

# Server Object 

| Field        | Type    | Description                |
|--------------|---------|----------------------------|
| version      | str     | VCMP server version        |
| passworded   | bool    | Password protection flag   |
| num_players  | int     | Current number of players  |
| max_players  | int     | Maximum number of players  |
| server_name  | str     | Server name                |
| game_type    | str     | Gamemode                   |
| language     | str     | Server language            |

# Player Object 
| Field | Type | Description       |
|-------|------|-----------------|
| name  | str  | Player nickname  |

# Protocol Notes

- Communication uses UDP packets.
- Requests contain the header:
```
VCMP
```

- Responses start with:
```
MP04
```

If the response header does not match, the client raises:
```
InvalidPacketException
```
