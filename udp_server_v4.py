"""@package udp_server_v4
A module to receive UDP/IPv4 packets over a Ethernet network interface.

USAGE: python udp_server_v4.py <destination ip> <udp port>.

The server will listen on IP Address::UDP Port socket interface.
A four-byte sequence number is expected at the beginning of the UDP payload.

"""

# Reference: https://gist.github.com/tuxmartin/e64d2132061ffef7e031#file-udp_ipv6_client-py

import socket
import time
import sys

# INPUT ARGS
num_args_exp = 3
usage = "usage: python " + sys.argv[0] + " <destination ip> <udp port>"
if len(sys.argv) != num_args_exp:
    sys.exit(usage)
else:
    cmd, dst_ip, udp_port = sys.argv  
  
# INIT  
UDP_IP = dst_ip           # IP address
UDP_PORT = int(udp_port)  # UDP port number

hdr_size = 8  # bytes
buf_size = pow(2, 16) - 1 - hdr_size  # max udp packet size

display_precision = 1
scale = 1000.0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4 & UDP
                        
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address/port reuse immediately
                        
sock.bind((UDP_IP, UDP_PORT))

tot_bytes = 0
tot_packets = 0
lost_occurrence = 0
lost_packets = 0
lost_bytes = 0
seq_bytes_size = 4
client_restart_detected = ""

print("Server", UDP_IP, "listening on UDP port", UDP_PORT)
print("Key:\n\r",
      "   BPP=Bytes per Packet\n\r",
      "   BPS=Bytes per Second\n\r",
      "   PPS=Packets per Second\n\r",
      "   LIC=Loss Incidence Count\n\r",
      "   LPC=Loss Packet Count\n\r"
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
            start_time = time.time() * scale
            time.sleep(.00001)  # avoid startup div by zero if client already running

        data, addr = sock.recvfrom(buf_size)  # Receive a packet (blocking call)!

        tot_bytes = tot_bytes + len(data)
        tot_packets = tot_packets + 1
        seq_bytes = data[0:seq_bytes_size]
        seq_num = int.from_bytes(seq_bytes,'big')
        
        if seq_num != tot_packets -1 + lost_packets:
            if tot_packets <= seq_num:  # make sure client not restarted
                lost_occurrence = lost_occurrence + 1
                # lost_packets = lost_packets + (seq_num-tot_packets+1)
                lost_packets = seq_num - tot_packets + 1
                client_restart_detected = ""
            else:
                client_restart_detected = "(client restarted)"
            
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

