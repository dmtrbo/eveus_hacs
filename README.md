# ⚡ EVSE Energy Star

**English** | [Українська](README.uk.md)

---

Home Assistant integration for local control of **Energy Star Pro** and **Eveus Pro** EV charging stations via their built-in web interface (JSON API).

---

## 🆕 Changes from Original Version 1.2.0

### Bug Fixes:
- ✅ Fixed incorrect current sensor values
- ✅ Fixed incorrect power sensor values

---

## 🔧 Features

- Display charging station status
- Sensors for power, voltage, current, temperature
- Control charging current, start/stop charging
- Charge scheduling, timers
- Time synchronization support
- Full local operation without cloud
- UI configuration via Config Flow
- Support for **Energy Star Pro** and **Eveus Pro**

---

## 🚀 Installation

### Option 1: via HACS (recommended)

1. Open HACS → "Integrations" → "Custom repositories"
2. Add repository:
   ```
   https://github.com/d-primikirio/eveus_hacs
   ```
3. Select category: `Integration`
4. Install the integration
5. Restart Home Assistant

### Option 2: Manual

1. Download ZIP archive or clone the repository
2. Copy the `evse_energy_star` folder to:
   ```
   config/custom_components/evse_energy_star
   ```
3. Restart Home Assistant

---

## ⚙️ Configuration

1. Go to `Settings` → `Devices & Services` → `Add Integration`
2. Search for "Eveus Chargers"
3. Enter:
   - Charging station IP address
   - Username (optional)
   - Password (optional)

---

## 🛠️ Requirements

- Home Assistant 2023.0 or newer
- Energy Star Pro or Eveus Pro charging station with active web interface

---

## 👤 Author

**[@d-primikirio](https://github.com/d-primikirio)**  
Pull requests, issues, and stars are welcome!

### Acknowledgment

This project is a fork of the original work by **[@V-Plum](https://github.com/V-Plum/evse_energy_star)**. 
Thank you for the great integration!

---

## 📝 License

[MIT License](LICENSE)
