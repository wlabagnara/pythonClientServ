#
# Reference: https://gist.github.com/tuxmartin/e64d2132061ffef7e031#file-udp_ipv6_client-py
#

import socket
import time
  
UDP_IP = "::" # = 0.0.0.0 u IPv4
UDP_PORT = 5005
buf_size = pow(2,16) - 1 - 8 # max udp packet size based on 16 bits - size of udp header (8 bytes) 
display_precision = 1
scale = 1000.0

start_time = time.time() * scale

sock = socket.socket(socket.AF_INET6, # Internet
						socket.SOCK_DGRAM) # UDP
                        
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow address/port reuse immediately
                        
sock.bind((UDP_IP, UDP_PORT))

tot_bytes = 0
tot_packets = 0

print ("Server listening on", UDP_PORT)

while True:
    data, addr = sock.recvfrom(buf_size) # buffer size in bytes
    tot_bytes = tot_bytes + len(data)
    tot_packets = tot_packets + 1
    
#    print ("received message:", data)
#    print ("received message length:", len(data))
    current_time = time.time() * scale
    run_time = current_time-start_time
    bps_time = (scale*tot_bytes/run_time)
    pps_time = (scale*tot_packets/run_time)
    print ("RX> ", 
        " BPS: ", round(bps_time, display_precision), 
        " PPS: ", round(pps_time, display_precision),
        " BPP: ", round(bps_time/pps_time, display_precision),        
        " Runtime: ", round(run_time/scale, display_precision),
        end = "\r", flush=True)  
 