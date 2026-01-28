DOMAIN = "evse_energy_star"
DEFAULT_SCAN_INTERVAL = 30
TITLE = "EVSE Energy Star"

STATUS_MAP = {
    0: "startup",
    1: "system_test",
    2: "waiting",
    3: "connected",
    4: "charging",
    5: "charge_complete",
    6: "suspended",
    7: "error",
}
