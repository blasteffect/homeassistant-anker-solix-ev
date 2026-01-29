DOMAIN = "anker_solix_ev"
PLATFORMS = ["sensor", "number", "select", "button", "binary_sensor"]

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ADDRESS_OFFSET = "address_offset"
CONF_WORD_ORDER = "word_order"

DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 5  # seconds
DEFAULT_ADDRESS_OFFSET = 0  # works for you
DEFAULT_WORD_ORDER = "hi_lo"  # or "lo_hi"

# --- Key registers (Anker SOLIX V1 Modbus Protocol v1.0.0 30-11-2025) ---
REG_CHARGING_STATUS = 20097          # uint16 (0..8)
REG_TOTAL_ACTIVE_POWER = 20068       # uint32, W
REG_SESSION_DURATION = 20082         # uint32, s
REG_SESSION_ENERGY_WH = 20084        # uint32, Wh

# Voltages (gain 10)
REG_L1N_VOLTAGE = 20053              # uint16, V*10
REG_L2N_VOLTAGE = 20054
REG_L3N_VOLTAGE = 20055
REG_L12_VOLTAGE = 20056
REG_L23_VOLTAGE = 20057
REG_L31_VOLTAGE = 20058

# Currents (gain 100)
REG_L1_CURRENT = 20059              # uint16, A*100
REG_L2_CURRENT = 20060
REG_L3_CURRENT = 20061

# Powers (uint32)
REG_L1_ACTIVE_POWER = 20062          # uint32, W
REG_L2_ACTIVE_POWER = 20064
REG_L3_ACTIVE_POWER = 20066
# total = 20068

REG_L1_REACTIVE_POWER = 20070        # uint32, W
REG_L2_REACTIVE_POWER = 20072
REG_L3_REACTIVE_POWER = 20074

REG_L1_APPARENT_POWER = 20076        # uint32, W
REG_L2_APPARENT_POWER = 20078
REG_L3_APPARENT_POWER = 20080

# Modes / flags
REG_OPERATING_MODE = 20086           # uint16 (1 single-phase, 3 three-phase)
REG_PWM_ENABLED = 20089              # uint16 (0/1)
REG_CHARGING_MODE = 20090            # uint16 (0 solar+grid, 1 only solar)
REG_CP_SIGNAL_STATUS = 20092         # uint16 (0/1)
REG_LOAD_BALANCING_ENABLED = 20093   # uint16 (0/1)
REG_SOLAR_BALANCING_ENABLED = 20094  # uint16 (0/1)
REG_CP_ACQ_VOLTAGE = 20095           # uint16 enum
REG_LED_BRIGHTNESS = 20096           # uint16 (%)

# Temperatures
REG_RELAY1_TEMP = 20098              # uint16, °C
REG_RELAY2_TEMP = 20099              # uint16, °C

# Control (RW)
REG_COMMAND = 21000                  # uint16 write: 1 start, 2 stop
REG_BOOST = 21001                    # uint16 write: 1 on (once per session)
REG_TIMEOUT = 21002                  # uint16 write: seconds (>5)
REG_PHASE_SETTING = 21003            # uint16 write: 0 auto, 1 single, 2 three
REG_MAX_CURRENT = 21004              # uint16 write: A

CHARGING_STATUS_MAP = {
    0: "idle",
    1: "preparing",
    2: "charging",
    3: "charger_paused",
    4: "vehicle_paused",
    5: "charging_completed",
    6: "reserving",
    7: "disabled",
    8: "error",
}

OPERATING_MODE_MAP = {1: "single_phase", 3: "three_phase"}
CHARGING_MODE_MAP = {0: "solar+grid", 1: "only_solar"}

CP_ACQ_VOLTAGE_MAP = {
    0: "A (12V)",
    3: "B1 (9V)",
    4: "B2 (9V)",
    5: "C1 (6V)",
    6: "C2 (6V)",
    7: "Error",
    8: "D1 (3V)",
    9: "D2 (3V)",
    10: "E (0V)",
    11: "F (-12V)",
}

PHASE_MAP = {0: "auto", 1: "single_phase", 2: "three_phase"}
PHASE_REVERSE_MAP = {v: k for k, v in PHASE_MAP.items()}
