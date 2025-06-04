
# CAENels FAST-PS Multi-Device UDP Controller

This Python script allows you to control multiple CAENels FAST-PS power supplies over the network using the **SFP Fast Interface UDP protocol**.

It sends **UDP packets** to multiple devices, each identified by a unique IP address (Unicast) and Fast Address (Multicast, Broadcast).

- **Broadcast** (`fast-interface-broadcast.py`)
- **Multicast** (`fast-interface-multicast.py`)
- **Unicast** (`fast-interface-unicast.py`)

## 📦 Features

- Interactive setpoint entry for each power supply
- Sends IEEE754 floating-point setpoints using the Fast Interface UDP protocol
- Supports sending to multiple devices with different IP addresses (Unicast)
- One UDP packet per IP containing Fast Address-specific setpoints
- Gracefully handles user input and exit

All three scripts allow you to send setpoints (in amperes) to one or more power supply devices that support the FAST interface protocol. They generate UDP packets based on the protocol specification and send them over the network accordingly.

- Each script constructs UDP packets using the FAST protocol:
  - Protocol ID: `0x7631`
  - Optional 2-byte command
  - 8-byte nonce
  - Multiple device entries: `(2-byte address + 4-byte IEEE754 setpoint)`
- Users are prompted to enter setpoints for each device.
- Packets are sent using Python's `socket` module.

## 📦 File Descriptions

### 1. `fast-interface-broadcast.py`

- Sends control packets to all devices via UDP **broadcast**.
- Broadcast IP can be adjusted (e.g., `255.255.255.255` or `192.168.1.255`).
- Prompts user for setpoint values interactively.
- Sends one packet to all devices simultaneously.

### 2. `fast-interface-multicast.py`

- Sends control packets via **multicast** using a predefined group IP (default: `224.0.2.22`).
- Requires specifying the local interface IP to send from.
- Devices must be listening to the multicast address to receive packets.

### 3. `fast-interface-unicast.py`

- Sends individual packets to each device using **unicast**.
- Requires a list of target IP addresses and their respective FAST addresses.
- Sends one packet per IP with all associated device commands.

## 📦 Requirements

- Python 3.x
- No external libraries required (uses standard `socket`, `struct`, `time`)

## 📦 FAST-PS Configuration Requirements

Each FAST-PS unit must be configured with:

1. **Unique Fast Address** (e.g. `1001`, `1002`, etc.)
2. **Unique SFP IP address** (e.g. `172.16.144.111`, `172.16.144.112`, etc.)
3. **Update Mode set to `SFP`**  
   Set via standard interface:
   ```
   UPMODE:SFP
   ```

4. **Fast Address and IP Setup**  
   Example:
   ```
   PASSWORD:Admin
   MWG:129:1001                   # Set Fast Address
   MWG:123:172.16.144.111         # Set IP Address
   MSAVE   
   ```

## 🚀 How to Use

Run any script with:
   ```bash
   python3 fast-interface-*.py
   ```
Each script will prompt for setpoint values for each device. To exit, type q at any prompt.



## 📄 Packet Structure (per device)

Each UDP packet follows the format described in the FAST-PS Fast Interface Manual:

- Protocol ID: `0x7631`
- Command: `0x0000` (no readback)
- Nonce: 8-byte timestamp
- Repeated entries:
    - Fast Address (2 bytes)
    - Setpoint (IEEE754 float, 4 bytes)

## 📌 Notes

- Devices must be reachable on the same subnet or via routed network.
- Firewalls and switches must allow UDP traffic on port `30721`.
- Readback (feedback) is not implemented in this version.

## 🧾 License

This project is provided as-is under the MIT License.
