#!/usr/bin/env python3

import json
import subprocess
import os
import time

JSON_FILE = "bluetooth_devices.json"

def load_existing_devices():
    """Laadt bestaande apparaten uit JSON als een lijst."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []  # Als er een fout is, begin met een lege lijst
    return []

def save_to_json(data):
    """Slaat ALLE gevonden apparaten op in JSON."""
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)
    print(f"📁 JSON bijgewerkt met {len(data)} apparaten.")

def scan_bluetooth():
    """Continu Bluetooth-apparaten scannen en opslaan in JSON."""
    try:
        print("🔍 Bluetooth scan gestart... Druk op CTRL+C om te stoppen.\n")

        devices = load_existing_devices()

        # Start de scan in de achtergrond
        scan_process = subprocess.Popen(["bluetoothctl", "scan", "on"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        while True:
            # Ophalen van alle gedetecteerde apparaten via scan uitvoer
            process = subprocess.Popen(["bluetoothctl", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, _ = process.communicate()

            for line in stdout.splitlines():
                print(line.strip())  # Live output van apparaten

                parts = line.split(" ")
                if len(parts) > 2:
                    mac_address = parts[1]
                    name = " ".join(parts[2:]).strip()

                    # Verzoek naar RSSI (signaalsterkte) via scanoutput (wordt automatisch gegeven bij scan on)
                    scan_rssi_process = subprocess.Popen(["bluetoothctl", "info", mac_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    scan_rssi_output, _ = scan_rssi_process.communicate()

                    rssi = None
                    for rssi_line in scan_rssi_output.splitlines():
                        if "RSSI" in rssi_line:
                            rssi = rssi_line.split(":")[1].strip()
                            break

                    if rssi is None:
                        rssi = "N/A"  # Als RSSI niet wordt gevonden

                    # Check of het MAC-adres al in de lijst staat
                    existing_device = next((d for d in devices if d["mac"] == mac_address), None)

                    if existing_device:
                        existing_device["rssi"] = rssi  # Update RSSI
                    else:
                        device_info = {"mac": mac_address, "name": name, "rssi": rssi}
                        devices.append(device_info)  # Voeg nieuw apparaat toe

                        print(f"📡 Nieuw apparaat gevonden: {mac_address} - {name} (RSSI: {rssi})")

                    # Direct opslaan na elke update
                    save_to_json(devices)

            time.sleep(3)  # Wacht een paar seconden voordat we opnieuw checken

    except KeyboardInterrupt:
        print("\n🚫 Scan gestopt door gebruiker.")

        # Bluetooth scanning stoppen
        subprocess.run(["bluetoothctl", "scan", "off"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("✅ Programma afgesloten.")

    except Exception as e:
        print(f"❌ Fout: {e}")

if __name__ == "__main__":
    scan_bluetooth()
