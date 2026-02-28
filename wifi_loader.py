#!/usr/bin/env python3

import os
import subprocess

CONFIG_FILE = "/mnt/p3/wifi.conf"

def run(cmd):
    subprocess.run(cmd, shell=True)

def existing_connections():
    result = subprocess.run(
        "nmcli -t -f NAME connection show",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout.splitlines()

def add_or_update_wifi(ssid, psk, priority, hidden):
    connections = existing_connections()

    if ssid not in connections:
        print(f"Adding WiFi: {ssid}")
        run(f'nmcli connection add type wifi ifname wlan0 con-name "{ssid}" ssid "{ssid}"')

    print(f"Updating WiFi: {ssid}")

    run(f'nmcli connection modify "{ssid}" wifi-sec.key-mgmt wpa-psk')
    run(f'nmcli connection modify "{ssid}" wifi-sec.psk "{psk}"')
    run(f'nmcli connection modify "{ssid}" connection.autoconnect yes')
    run(f'nmcli connection modify "{ssid}" connection.autoconnect-priority {priority}')

    if hidden.lower() == "yes":
        run(f'nmcli connection modify "{ssid}" 802-11-wireless.hidden yes')
    else:
        run(f'nmcli connection modify "{ssid}" 802-11-wireless.hidden no')

def parse_config():
    if not os.path.exists(CONFIG_FILE):
        return []

    networks = []
    current = {}

    with open(CONFIG_FILE) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if line == "[WIFI]":
                if current:
                    networks.append(current)
                    current = {}
            elif "=" in line:
                k, v = line.split("=", 1)
                current[k.strip()] = v.strip()

        if current:
            networks.append(current)

    return networks

def main():
    networks = parse_config()

    for net in networks:
        ssid = net.get("SSID")
        psk = net.get("PSK")
        priority = net.get("PRIORITY", "0")
        hidden = net.get("HIDDEN", "no")

        if ssid and psk:
            add_or_update_wifi(ssid, psk, priority, hidden)

if __name__ == "__main__":
    main()
