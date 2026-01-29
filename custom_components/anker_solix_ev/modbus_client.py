from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List, Tuple

# Modbus TCP constants
MBAP_HEADER_LEN = 7  # TID(2) + PID(2) + LEN(2) + UID(1)
PID_MODBUS = 0
UID_DEFAULT = 1


@dataclass
class ModbusSettings:
    host: str
    port: int
    address_offset: int = 0
    word_order: str = "hi_lo"  # or "lo_hi"


class AnkerModbusClient:
    """
    Minimal Modbus TCP client (asyncio) without pymodbus.
    Supports:
      - FC03 Read Holding Registers
      - FC06 Write Single Register
    """

    def __init__(self, settings: ModbusSettings):
        self._s = settings
        self._lock = asyncio.Lock()
        self._tid = 0

    def _addr(self, register: int) -> int:
        # Apply offset if device/tooling is 0-based vs 1-based mismatch
        return register + self._s.address_offset

    def _next_tid(self) -> int:
        self._tid = (self._tid + 1) & 0xFFFF
        return self._tid

    @staticmethod
    def _u32_from_words(words: list[int], word_order: str) -> int:
        if len(words) != 2:
            raise ValueError("Need exactly 2 words for uint32")
        w0, w1 = words[0] & 0xFFFF, words[1] & 0xFFFF
        if word_order == "hi_lo":
            hi, lo = w0, w1
        else:
            hi, lo = w1, w0
        return (hi << 16) | lo

    async def _open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        try:
            return await asyncio.wait_for(
                asyncio.open_connection(self._s.host, self._s.port),
                timeout=5,
            )
        except Exception as e:
            raise ConnectionError(
                f"TCP connect failed to {self._s.host}:{self._s.port} "
                f"({type(e).__name__}: {e})"
            ) from e

    @staticmethod
    def _build_mbap(tid: int, length: int, uid: int = UID_DEFAULT) -> bytes:
        # length = bytes following LEN field (UID + PDU)
        return (
            tid.to_bytes(2, "big")
            + PID_MODBUS.to_bytes(2, "big")
            + length.to_bytes(2, "big")
            + uid.to_bytes(1, "big")
        )

    async def _exchange(self, pdu: bytes) -> bytes:
        """
        Send one Modbus TCP request and return the raw PDU response (without MBAP).
        """
        reader, writer = await self._open()
        try:
            tid = self._next_tid()
            mbap = self._build_mbap(tid, 1 + len(pdu), UID_DEFAULT)

            writer.write(mbap + pdu)
            await writer.drain()

            # Read MBAP header
            hdr = await asyncio.wait_for(reader.readexactly(MBAP_HEADER_LEN), timeout=5)
            r_tid = int.from_bytes(hdr[0:2], "big")
            r_pid = int.from_bytes(hdr[2:4], "big")
            r_len = int.from_bytes(hdr[4:6], "big")
            # uid = hdr[6] (ignored)

            if r_pid != PID_MODBUS:
                raise RuntimeError(f"Invalid Modbus PID: {r_pid}")
            if r_tid != tid:
                raise RuntimeError(f"Transaction ID mismatch: sent {tid}, got {r_tid}")

            # r_len includes UID(1) + PDU(n). UID already consumed in header read.
            pdu_len = r_len - 1
            if pdu_len <= 0:
                raise RuntimeError(f"Invalid response length: {r_len}")

            resp_pdu = await asyncio.wait_for(reader.readexactly(pdu_len), timeout=5)
            return resp_pdu
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    @staticmethod
    def _check_exception(resp_pdu: bytes) -> None:
        # If FC has MSB set, it's an exception response.
        if not resp_pdu:
            raise RuntimeError("Empty response PDU")
        fc = resp_pdu[0]
        if fc & 0x80:
            exc = resp_pdu[1] if len(resp_pdu) > 1 else None
            raise RuntimeError(f"Modbus exception (fc=0x{fc:02X}, code={exc})")

    @staticmethod
    def _parse_fc03(resp_pdu: bytes) -> List[int]:
        # Response: fc(1) + byte_count(1) + data(2*N)
        AnkerModbusClient._check_exception(resp_pdu)
        if len(resp_pdu) < 2:
            raise RuntimeError("Short FC03 response")
        fc = resp_pdu[0]
        if fc != 0x03:
            raise RuntimeError(f"Unexpected function code in response: {fc}")
        byte_count = resp_pdu[1]
        data = resp_pdu[2:]
        if len(data) != byte_count:
            raise RuntimeError(f"Byte count mismatch: expected {byte_count}, got {len(data)}")
        if byte_count % 2 != 0:
            raise RuntimeError(f"Invalid byte_count (not even): {byte_count}")

        regs = []
        for i in range(0, byte_count, 2):
            regs.append(int.from_bytes(data[i : i + 2], "big"))
        return regs

    async def read_u16(self, register: int) -> int:
        async with self._lock:
            addr = self._addr(register)
            # FC03: 0x03 + start_addr(2) + quantity(2)
            pdu = b"\x03" + addr.to_bytes(2, "big") + (1).to_bytes(2, "big")
            resp = await self._exchange(pdu)
            regs = self._parse_fc03(resp)
            return int(regs[0])

    async def read_u32(self, register: int) -> int:
        async with self._lock:
            addr = self._addr(register)
            pdu = b"\x03" + addr.to_bytes(2, "big") + (2).to_bytes(2, "big")
            resp = await self._exchange(pdu)
            regs = self._parse_fc03(resp)
            return self._u32_from_words(regs[:2], self._s.word_order)

    async def write_u16(self, register: int, value: int) -> None:
        async with self._lock:
            addr = self._addr(register)
            val = int(value) & 0xFFFF
            # FC06: 0x06 + reg_addr(2) + value(2)
            pdu = b"\x06" + addr.to_bytes(2, "big") + val.to_bytes(2, "big")
            resp = await self._exchange(pdu)

            self._check_exception(resp)
            if len(resp) != 5:
                raise RuntimeError(f"Unexpected FC06 response length: {len(resp)}")
            if resp[0] != 0x06:
                raise RuntimeError(f"Unexpected function code for FC06: {resp[0]}")
            r_addr = int.from_bytes(resp[1:3], "big")
            r_val = int.from_bytes(resp[3:5], "big")
            if r_addr != addr or r_val != val:
                raise RuntimeError(f"FC06 echo mismatch (addr {r_addr} val {r_val})")
