from __future__ import annotations

import asyncio
from dataclasses import dataclass

from pymodbus.client import AsyncModbusTcpClient


@dataclass
class ModbusSettings:
    host: str
    port: int
    address_offset: int = 0
    word_order: str = "hi_lo"  # or "lo_hi"


class AnkerModbusClient:
    def __init__(self, settings: ModbusSettings):
        self._s = settings
        self._lock = asyncio.Lock()

    def _addr(self, register: int) -> int:
        return register + self._s.address_offset

    @staticmethod
    def _u32_from_words(words: list[int], word_order: str) -> int:
        w0, w1 = words[0] & 0xFFFF, words[1] & 0xFFFF
        if word_order == "hi_lo":
            hi, lo = w0, w1
        else:
            hi, lo = w1, w0
        return (hi << 16) | lo

    async def _with_client(self):
        client = AsyncModbusTcpClient(self._s.host, port=self._s.port, timeout=5)
        ok = await client.connect()
        if not ok:
            client.close()
            raise ConnectionError(f"Modbus TCP connect failed to {self._s.host}:{self._s.port}")
        return client

    async def read_u16(self, register: int) -> int:
        async with self._lock:
            client = await self._with_client()
            try:
                rr = await client.read_holding_registers(self._addr(register), count=1)
                if rr.isError():
                    raise RuntimeError(f"Modbus read_u16 error: {rr}")
                return int(rr.registers[0])
            finally:
                client.close()

    async def read_u32(self, register: int) -> int:
        async with self._lock:
            client = await self._with_client()
            try:
                rr = await client.read_holding_registers(self._addr(register), count=2)
                if rr.isError():
                    raise RuntimeError(f"Modbus read_u32 error: {rr}")
                return self._u32_from_words(rr.registers, self._s.word_order)
            finally:
                client.close()

    async def write_u16(self, register: int, value: int) -> None:
        async with self._lock:
            client = await self._with_client()
            try:
                rq = await client.write_register(self._addr(register), value & 0xFFFF)
                if rq.isError():
                    raise RuntimeError(f"Modbus write_u16 error: {rq}")
            finally:
                client.close()
