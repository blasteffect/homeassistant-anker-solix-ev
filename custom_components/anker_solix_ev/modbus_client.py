from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List, Tuple

MBAP_HEADER_LEN = 7  # TID(2) + PID(2) + LEN(2) + UID(1)
PID_MODBUS = 0
UID_DEFAULT = 1


class ModbusException(Exception):
    def __init__(self, fc: int, code: int | None):
        self.fc = fc
        self.code = code
        super().__init__(f"Modbus exception (fc=0x{fc:02X}, code={code})")


@dataclass
class ModbusSettings:
    host: str
    port: int
    address_offset: int = 0
    word_order: str = "hi_lo"  # or "lo_hi"


class AnkerModbusClient:
    """
    Minimal Modbus TCP client (asyncio), no pymodbus.
    Reads: FC03 (holding) with auto-fallback to FC04 (input) on Illegal Data Address (code=2).
    Writes: FC06 (write single register).
    """

    def __init__(self, settings: ModbusSettings):
        self._s = settings
        self._lock = asyncio.Lock()
        self._tid = 0

    def _addr(self, register: int) -> int:
        return register + self._s.address_offset

    def _next_tid(self) -> int:
        self._tid = (self._tid + 1) & 0xFFFF
        return self._tid

    @staticmethod
    def _u32_from_words(words: list[int], word_order: str) -> int:
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
        return (
            tid.to_bytes(2, "big")
            + PID_MODBUS.to_bytes(2, "big")
            + length.to_bytes(2, "big")
            + uid.to_bytes(1, "big")
        )

    async def _exchange(self, pdu: bytes) -> bytes:
        reader, writer = await self._open()
        try:
            tid = self._next_tid()
            mbap = self._build_mbap(tid, 1 + len(pdu), UID_DEFAULT)

            writer.write(mbap + pdu)
            await writer.drain()

            hdr = await asyncio.wait_for(reader.readexactly(MBAP_HEADER_LEN), timeout=5)
            r_tid = int.from_bytes(hdr[0:2], "big")
            r_pid = int.from_bytes(hdr[2:4], "big")
            r_len = int.from_bytes(hdr[4:6], "big")

            if r_pid != PID_MODBUS:
                raise RuntimeError(f"Invalid Modbus PID: {r_pid}")
            if r_tid != tid:
                raise RuntimeError(f"Transaction ID mismatch: sent {tid}, got {r_tid}")

            pdu_len = r_len - 1
            if pdu_len <= 0:
                raise RuntimeError(f"Invalid response length: {r_len}")

            return await asyncio.wait_for(reader.readexactly(pdu_len), timeout=5)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    @staticmethod
    def _raise_if_exception(resp_pdu: bytes) -> None:
        if not resp_pdu:
            raise RuntimeError("Empty response PDU")
        fc = resp_pdu[0]
        if fc & 0x80:
            code = resp_pdu[1] if len(resp_pdu) > 1 else None
            raise ModbusException(fc=fc, code=code)

    @staticmethod
    def _parse_read_response(expected_fc: int, resp_pdu: bytes) -> List[int]:
        AnkerModbusClient._raise_if_exception(resp_pdu)
        if len(resp_pdu) < 2:
            raise RuntimeError("Short read response")
        fc = resp_pdu[0]
        if fc != expected_fc:
            raise RuntimeError(f"Unexpected function code in response: {fc}")
        byte_count = resp_pdu[1]
        data = resp_pdu[2:]
        if len(data) != byte_count:
            raise RuntimeError(f"Byte count mismatch: expected {byte_count}, got {len(data)}")
        if byte_count % 2 != 0:
            raise RuntimeError(f"Invalid byte_count (not even): {byte_count}")

        regs: List[int] = []
        for i in range(0, byte_count, 2):
            regs.append(int.from_bytes(data[i : i + 2], "big"))
        return regs

    async def _read_regs(self, fc: int, start_addr: int, quantity: int) -> List[int]:
        # FC03 or FC04: fc + start(2) + qty(2)
        pdu = bytes([fc]) + start_addr.to_bytes(2, "big") + quantity.to_bytes(2, "big")
        resp = await self._exchange(pdu)
        return self._parse_read_response(fc, resp)

    async def read_u16(self, register: int) -> int:
        async with self._lock:
            addr = self._addr(register)
            try:
                regs = await self._read_regs(0x03, addr, 1)  # holding
            except ModbusException as e:
                # 0x83/code=2 => illegal address: try input registers (FC04)
                if e.code == 2:
                    regs = await self._read_regs(0x04, addr, 1)
                else:
                    raise
            return int(regs[0])

    async def read_u32(self, register: int) -> int:
        async with self._lock:
            addr = self._addr(register)
            try:
                regs = await self._read_regs(0x03, addr, 2)
            except ModbusException as e:
                if e.code == 2:
                    regs = await self._read_regs(0x04, addr, 2)
                else:
                    raise
            return self._u32_from_words(regs[:2], self._s.word_order)

    async def write_u16(self, register: int, value: int) -> None:
        async with self._lock:
            addr = self._addr(register)
            val = int(value) & 0xFFFF
            # FC06: 0x06 + reg(2) + value(2)
            pdu = b"\x06" + addr.to_bytes(2, "big") + val.to_bytes(2, "big")
            resp = await self._exchange(pdu)

            self._raise_if_exception(resp)
            if len(resp) != 5:
                raise RuntimeError(f"Unexpected FC06 response length: {len(resp)}")
            if resp[0] != 0x06:
                raise RuntimeError(f"Unexpected function code for FC06: {resp[0]}")
            r_addr = int.from_bytes(resp[1:3], "big")
            r_val = int.from_bytes(resp[3:5], "big")
            if r_addr != addr or r_val != val:
                raise RuntimeError(f"FC06 echo mismatch (addr {r_addr} val {r_val})")
