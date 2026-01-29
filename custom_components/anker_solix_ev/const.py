DOMAIN = "anker_solix_ev"
PLATFORMS = ["sensor", "number", "select", "button"]

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ADDRESS_OFFSET = "address_offset"
CONF_WORD_ORDER = "word_order"

DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 5  # seconds
DEFAULT_ADDRESS_OFFSET = 0  # 0 or -1
DEFAULT_WORD_ORDER = "hi_lo"  # or "lo_hi"

# Registers (from doc)
REG_CHARGING_STATUS = 20097          # uint16
REG_TOTAL_ACTIVE_POWER = 20068       # uint32, W
REG_SESSION_DURATION = 20082         # uint32, seconds
REG_SESSION_ENERGY_WH = 20084        # uint32, Wh

REG_COMMAND = 21000                 # uint16 write: 1 start, 2 stop
REG_PHASE_SETTING = 21003           # uint16 write: 0 auto, 1 single, 2 three
REG_MAX_CURRENT = 21004             # uint16 write: A

CHARGING_STATUS_MAP = {
    0: "idle",
    1: "preparing",
    2: "charging",
    3: "paused",
    4: "finishing",
    5: "reserved",
    6: "unavailable",
    7: "faulted",
    8: "offline",
}

PHASE_MAP = {0: "auto", 1: "single_phase", 2: "three_phase"}
PHASE_REVERSE_MAP = {v: k for k, v in PHASE_MAP.items()}

