import socket
import struct
import time

def float_to_ieee754_bytes(value):
    """Convert a float to 4-byte IEEE754 format"""
    return struct.pack('>f', value)

def build_fast_packet(devices, command=0x0000):
    """
    Build a Fast Interface UDP packet for power supply devices.
    """
    FAST_PROTOCOL_ID = 0x7631
    nonce = int(time.time_ns()) & 0xFFFFFFFFFFFFFFFF

    packet = bytearray()
    packet += struct.pack('>H', FAST_PROTOCOL_ID)
    packet += struct.pack('>H', command)
    packet += struct.pack('>Q', nonce)

    for fast_addr, setpoint in devices:
        packet += struct.pack('>H', fast_addr)
        packet += float_to_ieee754_bytes(setpoint)

    return packet

def send_multicast_packet(multicast_ip, port, packet, interface_ip='0.0.0.0'):
    """Send a UDP packet to a multicast group."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(interface_ip))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    sock.sendto(packet, (multicast_ip, port))
    sock.close()

def main():
    multicast_ip = "224.0.2.22"
    multicast_port = 30721
    local_interface_ip = "172.16.144.4"

    # List of unique device addresses
    fast_addresses = [1001, 1002]  # Add more if needed

    print("Starting continuous FAST-PS setpoint control...\n")

    try:
        setpoint = 0
        direction = 1  # 1: increasing, -1: decreasing
        step = 1
        max_setpoint = 5
        min_setpoint = -5

        while True:
            devices = [(addr, float(round(setpoint, 4))) for addr in fast_addresses]
            packet = build_fast_packet(devices)
            send_multicast_packet(multicast_ip, multicast_port, packet, interface_ip=local_interface_ip)

            print(f"Sent setpoint {setpoint:.2f} A to devices: {[addr for addr in fast_addresses]}")
            time.sleep(0.5)

            # Change direction when reaching limits
            if direction == 1 and setpoint >= max_setpoint:
                direction = -1
            elif direction == -1 and setpoint <= min_setpoint:
                direction = 1

            setpoint += direction * step
            # Clamp to avoid small floating-point overshoots
            setpoint = min(max(setpoint, min_setpoint), max_setpoint)

    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    main()
