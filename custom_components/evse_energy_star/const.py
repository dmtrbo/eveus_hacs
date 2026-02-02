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

LIMIT_STATUS_MAP = {
    0: "no_limits",
    1: "limited_by_user",
    2: "limited_by_schedule",
    3: "limited_by_time",
    4: "limited_by_energy",
    5: "limited_by_money",
}
