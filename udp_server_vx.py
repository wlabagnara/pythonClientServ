"""@package udp_server_vx
A module to receive UDP/IPv4 or IPv6 packets over a Ethernet network interface.

USAGE: python udp_server_v6.py <server ip> <udp port>.
         if version is 4, use "localhost" for localhost or specific IPv4 notated address for server IP
         if version is 6, use "::1" for localhost or specific IPv6 notated address for server IP

The server will listen on IP Address::UDP Port socket interface.
A four-byte sequence number is expected at the beginning of the UDP payload.
"""

# Reference: https://gist.github.com/tuxmartin/e64d2132061ffef7e031#file-udp_ipv6_client-py

import socket
import time
import sys

# INPUT ARGS
num_args_exp = 4
usage = "usage: python " + sys.argv[0] + " <version> <server ip> <udp port>"

if len(sys.argv) != num_args_exp:
    sys.exit(usage)
else:
    cmd, version, srv_ip, udp_port = sys.argv  

if "4" in version and "." in srv_ip:
    print ("IPv4 detected")
    ip_version = 4
elif "4" in version and "localhost" in srv_ip:
    print ("IPv4 detected")
    ip_version = 4
elif "6" in version and "::" in srv_ip:
    print ("IPv6 detected")
    ip_version = 6
else:
    sys.exit(usage)
    
# INIT  
scale = 10000.0          # scale timers
avoid_div_zero = .000001 # very small delay time to avoid start_time=current_time
display_precision = 1

UDP_IP = srv_ip           # IP address
UDP_PORT = int(udp_port)  # UDP port number

hdr_size = 8  # bytes
buf_size = pow(2, 16) - 1 - hdr_size  # max udp packet size

if ip_version == 6:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) # IPv6 & UDP
elif ip_version == 4:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4 & UDP
                        
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow address/port reuse immediately                   
sock.bind((UDP_IP, UDP_PORT))

tot_bytes = 0
tot_packets = 0
lost_occurrence = 0
lost_packets = 0
expected_seq_num = 0
out_of_order = 0
seq_bytes_size = 4
client_restart_detected = ""

print("Server", UDP_IP, "listening on UDP port", UDP_PORT)
print("Key:\n\r",
      "   BPP=Bytes per Packet\n\r",
      "   BPS=Bytes per Second\n\r",
      "   PPS=Packets per Second\n\r",
      "   LIC=Loss Incidence Count\n\r",
      "   LPC=Lost Packet Count\n\r",
      "   OOP=Out of Order Packet Count\n\r"
      )
print("(Restart with a Control-C or Terminate with a Control-Break)\n\r")

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
            print ("Waiting for first receive packet...")

        data, addr = sock.recvfrom(buf_size)  # Receive a packet (blocking call)!

        if tot_packets == 0:  # synchronize on first received packet
            print ("Received first packet!\n\r")
            start_time = time.time() * scale
            time.sleep(avoid_div_zero)  # delay so that start_time != current_time

        tot_bytes = tot_bytes + len(data)
        tot_packets = tot_packets + 1
        seq_bytes = data[0:seq_bytes_size]
        seq_num = int.from_bytes(seq_bytes,'big')
        
        if expected_seq_num != seq_num:
            lost_occurrence = lost_occurrence + 1
            if seq_num > expected_seq_num:
                # dropped datagram
                lost_packets = lost_packets + (seq_num - expected_seq_num)
                expected_seq_num = seq_num + 1
            else:
                # out of order datagram
                out_of_order = out_of_order + 1
        else:
            # update to next expected sequence number
            expected_seq_num = seq_num + 1
            

            
        current_time = time.time() * scale
        run_time = current_time-start_time
        bps_time = (scale*tot_bytes/run_time)    
        pps_time = (scale*tot_packets/run_time)   
        
        _Print_Clear_Line()
        
        print("RX> ",
            "BPP:", round(tot_bytes/tot_packets, display_precision),
            "BPS:", round(bps_time, display_precision),
            "PPS:", round(pps_time, display_precision),
            "Runtime:", round(run_time/scale, display_precision),
            "Packets:", tot_packets,
            "Seq:", seq_num,
            "LIC:", lost_occurrence,
            "LPC:", lost_packets,
            client_restart_detected,
            "OOP:", out_of_order,
            end ="\r")

    except KeyboardInterrupt:
        print("\n\rControl-C detected")
        print("Program restarted!")
        tot_bytes = 0
        tot_packets = 0
        lost_packets = 0
        lost_occurrence = 0
        continue

    except Exception as e:
        print("Exception", e)
        break

