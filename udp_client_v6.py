#
# Reference: https://gist.github.com/tuxmartin/e64d2132061ffef7e031#file-udp_ipv6_client-py
#

import socket
import time

UDP_IP = "::1"  # localhost
UDP_PORT = 5005
MESSAGE = "A" # a byte

tot_bytes = 0
tot_packets = 0
display_precision = 1
scale = 1000.0

start_time = time.time() * scale

max_size = pow(2,16) - 1 - 8 # max udp packet size based on 16 bits - size of udp header (8 bytes) 
min_size = 1 # min udp packet size is one byte

msg_size = max_size 

MESSAGE = MESSAGE * msg_size

print ("Client sending to ", UDP_IP, " on port ", UDP_PORT)

sock = socket.socket(socket.AF_INET6, # Internet
					socket.SOCK_DGRAM) # UDP
                    
msg_bytes = bytes(MESSAGE, 'utf-8') # convert message to bytes-like object

while True:
    sock.sendto(msg_bytes, (UDP_IP, UDP_PORT))
    tot_bytes = tot_bytes + len(msg_bytes)
    tot_packets = tot_packets + 1

    # print ("message bytes sent:", tot_bytes, end = "\n")
    time.sleep(.0001) # 100 us
    current_time = time.time() * scale
    run_time = current_time-start_time
    bps_time = (scale*tot_bytes/run_time)
    pps_time = (scale*tot_packets/run_time)
    print ("TX> ", 
        " BPS: ", round(bps_time, display_precision), 
        " PPS: ", round(pps_time, display_precision),
        " BPP: ", round(bps_time/pps_time, display_precision),        
        " Runtime: ", round(run_time/scale, display_precision),
        end = "\r", flush=True)    

