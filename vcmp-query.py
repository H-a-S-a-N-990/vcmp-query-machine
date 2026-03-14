import asyncio        
import socket        
import struct        
from dataclasses import dataclass        
        
# ======================        
# Data classes        
# ======================        
        
@dataclass        
class Status:        
    version: str        
    passworded: bool        
    num_players: int        
    max_players: int        
    server_name: str        
    game_mode: str        
    map_name: str        
        
        
@dataclass        
class Player:        
    name: str        
        
        
# ======================        
# Binary reader        
# ======================        
        
class BinaryReader:        
    def __init__(self, data: bytes):        
        self.data = data        
        self.pos = 0        
        
    def read_byte(self):        
        if self.pos >= len(self.data):        
            return 0        
        val = self.data[self.pos]        
        self.pos += 1        
        return val        
        
    def read_short(self):        
        if self.pos + 2 > len(self.data):        
            return 0        
        val = struct.unpack_from("<H", self.data, self.pos)[0]        
        self.pos += 2        
        return val        
        
    def read_long(self):        
        if self.pos + 4 > len(self.data):        
            return 0        
        val = struct.unpack_from("<I", self.data, self.pos)[0]        
        self.pos += 4        
        return val        
        
    def read_bytes(self, n):        
        if self.pos + n > len(self.data):        
            n = len(self.data) - self.pos        
        val = self.data[self.pos:self.pos + n]        
        self.pos += n        
        return val        
        
        
# ======================        
# VCMP Query Client        
# ======================        
        
class VcmpQuery:        
    REQUEST_HEADER = b"VCMP"        
    RESPONSE_HEADER = b"MP04"        
        
    def __init__(self, host: str, port: int, timeout=3.0):        
        self.host = host        
        self.port = port        
        self.timeout = timeout        
        
    # ----------------------        
    # Send & receive packets        
    # ----------------------        
    async def _send_and_receive(self, opcode: bytes) -> bytes:        
        loop = asyncio.get_running_loop()        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        
        sock.setblocking(False)        
        
        ip_parts = list(map(int, socket.gethostbyname(self.host).split(".")))        
        packet = (        
            self.REQUEST_HEADER +        
            struct.pack("<BBBBH", *ip_parts, self.port) +        
            opcode        
        )        
        
        await loop.sock_sendto(sock, packet, (self.host, self.port))        
        
        try:        
            data, _ = await asyncio.wait_for(        
                loop.sock_recvfrom(sock, 4096),        
                timeout=self.timeout        
            )        
        except asyncio.TimeoutError:        
            raise TimeoutError("Server did not respond")        
        
        if not data.startswith(self.RESPONSE_HEADER):        
            raise ValueError("Invalid VCMP response")        
        
        header_len = len(self.RESPONSE_HEADER) + 7  # MP04 + IP + port        
        return data[header_len:]        
        
    # ----------------------        
    # Safe string reader        
    # ----------------------        
    def _read_string(self, br: BinaryReader, use_long_length=False) -> str:        
        if br.pos >= len(br.data):        
            return ""        
        length = br.read_long() if use_long_length else br.read_byte()        
        if br.pos + length > len(br.data):        
            return ""        
        return br.read_bytes(length).decode("utf-8", "ignore")        
        
    # ----------------------        
    # Get server status        
    # ----------------------        
    async def get_status(self) -> Status:        
        data = await self._send_and_receive(b"i")        
        br = BinaryReader(data)        
        
        version = br.read_bytes(12).split(b"\x00", 1)[0].decode("ascii", "ignore")        
        passworded = bool(br.read_byte())        
        num_players = br.read_short()        
        max_players = br.read_short()        
        
        server_name = self._read_string(br, use_long_length=True) or "Unknown Server"        
        game_mode = self._read_string(br, use_long_length=True) or "Unknown Mode"        
        map_name = self._read_string(br, use_long_length=True) or "Unknown Map"        
        
        return Status(version, passworded, num_players, max_players, server_name, game_mode, map_name)        
        
    # ----------------------        
    # Get player list        
    # ----------------------        
    async def get_players(self) -> list[Player]:        
        data = await self._send_and_receive(b"c")        
        br = BinaryReader(data)        
        
        count = br.read_short()        
        players = []        
        
        for _ in range(count):        
            players.append(Player(self._read_string(br) or "Unknown Player"))        
        
        return players
