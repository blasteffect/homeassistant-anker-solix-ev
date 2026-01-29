# Anker SOLIX EV Charger (Modbus TCP) - Home Assistant

Custom integration (HACS) for Anker SOLIX V1 Smart EV Charger via Modbus TCP.

## Install
Add this repository to HACS (Custom repositories) as **Integration**, then install.

## Configure
Settings → Devices & services → Add integration → "Anker SOLIX EV Charger"
Enter charger IP (LAN), port 502.

If sensors show nonsense, try:
- Address offset: -1
- Word order: lo_hi

