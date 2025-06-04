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
    nonce = int(time.time_ns()) & 0xFFFFFFFFFFFFFFFF  # 8-byte nonce

    packet = bytearray()
    packet += struct.pack('>H', FAST_PROTOCOL_ID)
    packet += struct.pack('>H', command)
    packet += struct.pack('>Q', nonce)

    for fast_addr, setpoint in devices:
        packet += struct.pack('>H', fast_addr)
        packet += float_to_ieee754_bytes(setpoint)

    return packet

def send_udp_packet(ip, port, packet):
    """Send UDP packet to a specific IP address and port."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(packet, (ip, port))

def main():
    # List of tuples: (target IP, Fast Address)
    power_supplies = [
        ("172.16.144.111", 1001),
        ("172.16.144.112", 1002),
    ]

    target_port = 30721  # Default FAST-PS UDP port

    print("FAST-PS Unicast Control to Multiple IPs")
    print("Enter current setpoints for each power supply (or 'q' to quit).\n")

    try:
        while True:
            devices_by_ip = {}  # { ip: [(fast_address, setpoint), ...] }

            for ip, addr in power_supplies:
                while True:
                    user_input = input(f"Setpoint for device {addr} at {ip} (A): ")
                    if user_input.lower() == 'q':
                        print("Exiting...")
                        return
                    try:
                        setpoint = float(user_input)
                        if ip not in devices_by_ip:
                            devices_by_ip[ip] = []
                        devices_by_ip[ip].append((addr, setpoint))
                        break
                    except ValueError:
                        print("Invalid input. Please enter a valid float or 'q'.")

            # Send one packet per IP with its respective fast addresses
            for ip, device_list in devices_by_ip.items():
                packet = build_fast_packet(device_list)
                send_udp_packet(ip, target_port, packet)
                print(f"Sent to {ip}: {[f'{a}: {s} A' for a, s in device_list]}")

            print()

    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")

if __name__ == "__main__":
    main()
