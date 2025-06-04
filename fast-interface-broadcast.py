import socket
import struct
import time

def float_to_ieee754_bytes(value):
    """Convert a float to 4-byte IEEE754 format"""
    return struct.pack('>f', value)

def build_fast_packet(devices, command=0x0000):
    """
    Build a Fast Interface UDP packet for n power supplies.

    :param devices: List of tuples (fast_address, setpoint)
    :param command: 2-byte command (readback enable/disable, default: 0x0000)
    :return: UDP packet as bytes
    """
    FAST_PROTOCOL_ID = 0x7631
    nonce = int(time.time_ns()) & 0xFFFFFFFFFFFFFFFF  # 8-byte unique nonce

    packet = bytearray()

    # Header
    packet += struct.pack('>H', FAST_PROTOCOL_ID)
    packet += struct.pack('>H', command)
    packet += struct.pack('>Q', nonce)

    # Each device: Fast Address (2 bytes) + Setpoint (4 bytes)
    for fast_addr, setpoint in devices:
        packet += struct.pack('>H', fast_addr)
        packet += float_to_ieee754_bytes(setpoint)

    return packet

def send_broadcast_packet(broadcast_ip, port, packet):
    """
    Send a UDP broadcast packet to the specified IP and port.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast
    sock.sendto(packet, (broadcast_ip, port))
    sock.close()

def main():
    # Broadcast IP address for your subnet
    broadcast_ip = "255.255.255.255"   # Or use e.g. "192.168.0.255" depending on your network
    broadcast_port = 30721             # FAST-PS default Fast Interface UDP port

    # List of power supply Fast Addresses
    fast_addresses = [1001, 1002]  # Modify to match your setup

    print("Broadcast FAST-PS Control — type 'q' to quit.\n")

    try:
        while True:
            devices = []
            for addr in fast_addresses:
                while True:
                    user_input = input(f"Setpoint for device {addr} (A): ")
                    if user_input.lower() == 'q':
                        print("Exiting.")
                        return
                    try:
                        setpoint = float(user_input)
                        devices.append((addr, setpoint))
                        break
                    except ValueError:
                        print("Invalid input. Enter a number or 'q' to quit.")

            packet = build_fast_packet(devices)
            send_broadcast_packet(broadcast_ip, broadcast_port, packet)
            print(f"Broadcast sent to devices: {[f'{a}: {s} A' for a, s in devices]}\n")

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")

if __name__ == "__main__":
    main()
