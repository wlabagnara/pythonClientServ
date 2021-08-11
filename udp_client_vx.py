"""@package udp_client_vx
A module to generate UDP/IPv4 or IPv6 packets over a Ethernet network interface.

USAGE: python udp_client_vx.py <version> <destination ip> <udp port> <packet gap> <message size>.
         if version is 4, use "localhost" for localhost or specific IPv4 notated address for destination IP
         if version is 6, use "::1" for localhost or specific IPv6 notated address for destination IP

The client will send on IP Address::UDP Port socket interface.
A four-byte sequence number will be inserted at the beginning of the UDP payload.
"""

# Reference: https://gist.github.com/tuxmartin/e64d2132061ffef7e031#file-udp_ipv6_client-py

import socket
import time
import sys

# INPUT ARGS
num_args_exp = 6
usage = "usage: python " + sys.argv[0] + " <version> <destination ip> <udp port> <packet gap> <message size>"

if len(sys.argv) != num_args_exp:
    sys.exit(usage)
else:
    cmd, version, dst_ip, udp_port, packet_gap, message_size = sys.argv

if "4" in version and "." in dst_ip:
    print ("IPv4 detected")
    ip_version = 4
elif "4" in version and "localhost" in dst_ip:
    print ("IPv4 detected")
    ip_version = 4
elif "6" in version and "::" in dst_ip:
    print ("IPv6 detected")
    ip_version = 6
else:
    sys.exit(usage)

# INIT  
scale = 10000.0          # scale timers
avoid_div_zero = .000001 # very small delay time to avoid start_time=current_time
display_precision = 1 

UDP_IP = dst_ip           # IP Address
UDP_PORT = int(udp_port)  # UDP port number

MESSAGE_DATA = "A"  # a message byte

MESSAGE = MESSAGE_DATA * int(message_size)

seq_num_size = 4 # sequence number of 4 bytes will be added to message

sleep_time = float(packet_gap)  # inter-packet time (seconds)

tot_bytes = 0
tot_packets = 0
packet_err = 0 # init generate packet error logic
                    
print("Client sending to", UDP_IP, "on UDP port", UDP_PORT)
print("Key:\n\r",
      "   BPP=Bytes per Packet\n\r",
      "   BPS=Bytes per Second\n\r",
      "   PPS=Packets per Second\n\r",
      )
print("Inter-packet-gap time:", sleep_time,"seconds")
print("A four-byte sequence number will be added to message\n\r")

print("(Create packet error with a Control-C or Terminate with a Control-Break)\n\r")

if ip_version == 6:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) # IPv6 UDP
    sock.bind(('::', UDP_PORT))                              # Source UDP Port (setting same as destination port)
elif ip_version == 4:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4 UDP
    sock.bind(('0.0.0.0', UDP_PORT))                        # Source UDP Port (setting same as destination port)

keep_running = True

# Helper functions
chars_per_line = 120
space_char = " "
clear_line = chars_per_line * space_char
reduce_flicker = 0
def _Print_Clear_Line():
    #  doing this b/c couldn't get delete to end of
    #  line escape sequence working!
    global reduce_flicker
    reduce_flicker = reduce_flicker + 1
    if reduce_flicker < 10:  # reduce line update flickering
        print(clear_line, end="\r")

# MAIN LOOP    
while keep_running:

    try:
    
        if tot_packets == 0:
            start_time = time.time() * scale
            time.sleep(avoid_div_zero)  # delay so that start_time != current_time
            
        seq_num = tot_packets.to_bytes(seq_num_size, 'big')
        msg_bytes = seq_num + bytes(MESSAGE, 'utf-8')  # convert message to bytes-like object

        sock.sendto(msg_bytes, (UDP_IP, UDP_PORT))  # Send a packet!

        tot_bytes = tot_bytes + len(msg_bytes)
        tot_packets = tot_packets + 1
    
        current_time = time.time() * scale
        run_time = current_time-start_time
        bps_time = (scale*tot_bytes/run_time)
        pps_time = (scale*tot_packets/run_time)
    
        _Print_Clear_Line()

        print("TX> ",
            "BPP:", round(tot_bytes/tot_packets, display_precision),
            "BPS:", round(bps_time, display_precision),
            "PPS:", round(pps_time, display_precision),
            "Runtime:", round(run_time/scale, display_precision),
            "Packets:", tot_packets,
            end="\r")

        time.sleep(sleep_time)  # sleep a little

    except KeyboardInterrupt:
        print("\n\rControl-C detected")

        if packet_err == 0:
            print("Generating 1 packet error!")
            tot_packets = tot_packets + 1
            packet_err = 1
        elif packet_err == 1:
            print("Generating 2 packet errors!")
            tot_packets = tot_packets + 2
            packet_err = 2
        elif packet_err == 2:
            print("Generating 3 packet errors!")
            tot_packets = tot_packets + 3
            packet_err = 0
            
        continue

    except Exception as e:
        print("Exception", e)
        break

    

