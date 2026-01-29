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
