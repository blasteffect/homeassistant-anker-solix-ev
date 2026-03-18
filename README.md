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

## MVP entities
- Charging Status (20097)
- Total Active Power W (20068, UINT32)
- Session Duration s (20082, UINT32)
- Session Energy Wh (20084, UINT32)
- Buttons: Start/Stop (21000)
- Number: Max Current A (21004)
- Select: Phase Setting (21003)

## Notes
This integration is an MVP baseline intended for extension (more sensors, scaling, binary sensors, etc.).


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
