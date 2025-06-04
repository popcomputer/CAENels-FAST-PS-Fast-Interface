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

    # Device entries
    for fast_addr, setpoint in devices:
        packet += struct.pack('>H', fast_addr)
        packet += float_to_ieee754_bytes(setpoint)

    return packet

def send_multicast_packet(multicast_ip, port, packet, interface_ip='0.0.0.0'):
    """
    Send UDP packet to multicast group.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Set the outgoing interface (optional)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(interface_ip))

    # Set TTL if needed (default is 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

    # Enable loopback if needed (default: enabled)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    sock.sendto(packet, (multicast_ip, port))
    sock.close()

def main():
    # Multicast IP address & port for FAST-PS
    multicast_ip = "224.0.2.22"    # Must match what the devices are listening to
    multicast_port = 30721         # Standard Fast Interface port

    # Local network interface to send from
    local_interface_ip = "172.16.144.4"  # Replace with your PC's IP on the same LAN

    # Fast Addresses for all units (they are unique per device)
    fast_addresses = [1001, 1002]  # Add more as needed

    print("Multicast FAST-PS Control — type 'q' to quit.\n")

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
                        print("Invalid input. Try again.")

            packet = build_fast_packet(devices)
            send_multicast_packet(multicast_ip, multicast_port, packet, interface_ip=local_interface_ip)
            print(f"Multicast sent to devices: {[f'{a}: {s} A' for a, s in devices]}\n")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

if __name__ == "__main__":
    main()
