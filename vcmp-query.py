import asyncio
import socket
import struct
from dataclasses import dataclass


@dataclass
class Status:
    version: str
    passworded: bool
    num_players: int
    max_players: int
    server_name: str
    game_type: str
    language: str


@dataclass
class Player:
    name: str


class BinaryReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def byte(self):
        v = self.data[self.pos]
        self.pos += 1
        return v

    def short(self):
        v = struct.unpack_from("<H", self.data, self.pos)[0]
        self.pos += 2
        return v

    def long(self):
        v = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return v

    def bytes(self, n):
        v = self.data[self.pos:self.pos+n]
        self.pos += n
        return v


class VCMPQuery:
    REQUEST = b"VCMP"
    RESPONSE = b"MP04"

    def __init__(self, host: str, port: int, timeout: float = 3):
        self.host = host
        self.port = port
        self.timeout = timeout

    async def _query(self, opcode: bytes) -> bytes:
        loop = asyncio.get_running_loop()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)

        ip = list(map(int, socket.gethostbyname(self.host).split(".")))

        packet = self.REQUEST + struct.pack("<BBBBH", *ip, self.port) + opcode

        await loop.sock_sendto(sock, packet, (self.host, self.port))

        data, _ = await asyncio.wait_for(
            loop.sock_recvfrom(sock, 4096),
            timeout=self.timeout
        )

        if not data.startswith(self.RESPONSE):
            raise ValueError("Invalid VCMP response")

        return data[len(self.RESPONSE) + 7:]

    async def get_status(self) -> Status:
        data = await self._query(b"i")
        br = BinaryReader(data)

        version = br.bytes(12).split(b"\x00", 1)[0].decode("ascii", "ignore")
        passworded = bool(br.byte())
        num_players = br.short()
        max_players = br.short()

        return Status(
            version,
            passworded,
            num_players,
            max_players,
            self._string(br),
            self._string(br),
            self._string(br)
        )

    async def get_players(self) -> list[Player]:
        data = await self._query(b"c")
        br = BinaryReader(data)

        count = br.short()
        return [Player(self._string(br)) for _ in range(count)]

    def _string(self, br: BinaryReader) -> str:
        length = br.byte()
        return br.bytes(length).decode("utf-8", "ignore")
