# Anker SOLIX EV Charger (Modbus TCP) - Home Assistant

Custom integration (HACS) for Anker SOLIX V1 Smart EV Charger via Modbus TCP.

## Install (HACS)
1. HACS → Integrations → ⋮ → Custom repositories
2. Add your repo URL as **Integration**
3. Install
4. Restart Home Assistant

## Configure
Settings → Devices & services → Add integration → **Anker SOLIX EV Charger (Modbus TCP)**

Enter charger IP (LAN), port 502.

If sensors show nonsense, try:
- Address offset: -1
- Word order: lo_hi

The address offset is applied only to reads for compatibility with differing
register-number conventions. Control writes always use the canonical addresses
from the Anker protocol and cannot be redirected by this option.

## MVP entities
- Charging Status (20097)
- Total Active Power W (20068, UINT32)
- Session Duration s (20082, UINT32)
- Session Energy Wh (20084, UINT32)
- Buttons: Start/Stop (21000)
- Number: Max Current A (21001, tenths of an ampere)
- Select: Phase Setting (21005)

## Notes
This integration is an MVP baseline intended for extension (more sensors, scaling, binary sensors, etc.).

Home Assistant represents the charger as one **Anker EV Charger** device. Its
telemetry and controls are separate entities grouped beneath that device, which
is the native Home Assistant device model.

## Verified Modbus mapping

The register map was checked against the Anker SOLIX V1 Smart EV Charger
Modbus Protocol V1.0.0 and read-only values from an A5191 charger running
software `1.0.6.1`.

| Address | Signal | Conversion |
| --- | --- | --- |
| 20086 | PWM enabled | 0/1 |
| 20087 | Single/three-phase operating mode | 1 single, 3 three |
| 20088 | Charging mode | 0 solar + grid, 1 only solar |
| 20089 | Load balancing enabled | 0/1 |
| 20090 | Solar power balancing enabled | 0/1 |
| 20091 | CP acquisition voltage | observed as millivolts |
| 20092 | CP signal status | CP state enum |
| 20093-20094 | Relay temperatures | signed values observed in tenths of °C |
| 20095 | Boost mode status | 0/1 |
| 20096 | LED brightness | percent |
| 20097 | Charging status | status enum |
| 20099 | OCPP connection status | 0 disconnected, 1 connecting, 2 connected |
| 20100 | MQTT connection status | 0/1 |
| 21000 | Charging command | 1 start, 2 stop |
| 21001 | Maximum current | tenths of an ampere |
| 21002 | Boost command | 1 on |
| 21003 | Timeout | seconds, greater than 5 |
| 21004 | Reserved | do not use |
| 21005 | Number of charging phases | 0 auto, 1 single, 2 three |

The protocol PDF labels the units for several control registers incorrectly.
The conversions above use the signal descriptions and values observed on the
charger. No Modbus writes were used during verification.


## v0.1.1
- Relaxed pymodbus requirement to avoid dependency conflicts (uses >=3.11.2).


## v0.2.0
- Added per-phase voltage/current/power sensors, flags as binary_sensors, and readback for phase/max current.
- Removed pymodbus dependency (socket Modbus TCP).

## v0.2.4
- Improved Modbus communication reliability to reduce lost connection errors and long request expirations (including 120s timeout cases reported by apps).
- Reworked coordinator polling to use grouped block reads instead of many sequential single-register reads.
- Added bounded retry logic for Modbus TCP exchanges (read/write) to better handle transient network issues.
- Made TCP connect/response timeouts configurable in Modbus client settings.

## v0.2.5
- Fixed startup/configuration regression on control registers: `REG_PHASE_SETTING (21003)` and `REG_MAX_CURRENT (21004)` are now read directly (no `outside cached read blocks` error).
- Version metadata aligned for HACS upgrade detection (`manifest.json` bumped to `0.2.5`).

## v0.2.6
- Added a minimal/stable mode aligned with the compact dashboard: only 3 sensors (`Charging Status`, `Total Active Power`, `Session Energy`) and 2 actions (`Start/Stop Charging`).
- Reduced polling scope to the required registers only, lowering Modbus traffic and helping stability when communication is flaky.

## v0.2.7
- Switched Modbus TCP client to persistent socket mode (no connect/close on every request).
- Added automatic reconnect on communication errors and proper socket close on integration unload.
- Keeps the minimal polling profile from v0.2.6 while improving connection stability.


## v0.2.8
- Restored the full telemetry set (voltages, currents, per-phase powers, flags, temperatures, phase and max current).
- Kept the later communication/stability fixes from the minimal/stable branch.
- Kept the Home Assistant options-flow compatibility fix.

## v0.2.9
- Fix registre max current
