#!/usr/local/bin/python3.9
#----------------------------------------------------------------------------------------
# Copyright 2024 Adeptus Cyber Solutions, LLC. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#    https://www.apache.org/licenses/LICENSE-2.0.html
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
#----------------------------------------------------------------------------------------
import socket
import time
import uuid
import ssl
import argparse

from datetime import datetime, timedelta
from pyproj import Geod

num_walkers = 3
# walker_type = "a-h-G-U-C-A"  # ARMOR
walker_type = "a-f-S-X-M-C"  # CARGO SHIP
#  walker_type = "a-f-A-C-F"  # CIVILIAN AIRCRAFT

latitude=1
longitude=0

lat1=41.793
lon1=-70.377

lat2=42.391
lon2=-70.33372

lat3=42.490
lon3=-69.449

num_points=100

## For Local
MCAST_GRP = '239.2.3.1'
MCAST_PORT = 6969

## For Remote
hostname = "tak.adeptus-cs.com"
port = 8089
serverPEM = "certs/server.pem"
clientPEM = "certs/client.pem"
serverCN = "tak.adeptuscybersolutions.com"

# regarding socket.IP_MULTICAST_TTL
# ---------------------------------
# for all packets sent, after two hops on the network the packet will not 
# be re-sent/broadcast (see https://www.tldp.org/HOWTO/Multicast-HOWTO-6.html)
MULTICAST_TTL = 2

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations(serverPEM)
context.load_cert_chain(certfile=clientPEM)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockConnection = context.wrap_socket(sock, server_hostname=serverCN)
sockConnection.connect((hostname, port))

### LOCAL
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

def sendCoT(cotMessage):
    # For Python 3, change next line to 'sock.sendto(b"robot", ...' to avoid the
    # "bytes-like object is required" msg (https://stackoverflow.com/a/42612820)
    # LOCAL 
    # sock.sendto(cotMessage.encode(), (MCAST_GRP, MCAST_PORT))
    try:
        sockConnection.send(cotMessage.encode())
    except Exception as ex:
        print("Error: %s" % format(ex))

def startWalkers(uuids, walker_points):
    for k in range(len(walker_points[0])):
        for w in range(num_walkers):
            print("Points for walker %d: %.8f:%.9f" % (w, walker_points[w][k][latitude], walker_points[w][k][longitude]))

            now = datetime.utcnow()
            startTime = now.strftime("%FT%T.%f")
            nowTime = now.strftime("%FT%T.%f")
            staleTime = (now + timedelta(minutes=1)).strftime("%FT%T.%f")
            xml = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><event version='2.0' uid='%s' type='%s' how='m-g' time='%sZ' start='%sZ' stale='%sZ'><detail></detail><point lat='%.8f' lon='%.8f' hae='0' ce='1' le='1'/></event>" % (uuids[w], walker_type, nowTime, startTime, staleTime, walker_points[w][k][latitude], walker_points[w][k][longitude])
            print("Sending XML: %s" % xml)
            sendCoT(xml)
        time.sleep(1)

def main():
    ## UUIDS for the walkers
    uuids = []
    for k in range(num_walkers):
        uuids.append(str(uuid.uuid4()))

    geoid = Geod(ellps="WGS84")

    walker_points = []
    if num_walkers == 2:
        walker_points.append(geoid.npts(lon1, lat1, lon2, lat2, num_points) + geoid.npts(lon2, lat2, lon1, lat1, num_points))
        walker_points.append(geoid.npts(lon2, lat2, lon1, lat1, num_points) + geoid.npts(lon1, lat1, lon2, lat2, num_points))
    else:
        walker_points.append(geoid.npts(lon1, lat1, lon2, lat2, num_points) + geoid.npts(lon2, lat2, lon3, lat3, num_points) + geoid.npts(lon3, lat3, lon1, lat1, num_points))
        walker_points.append(geoid.npts(lon2, lat2, lon3, lat3, num_points) + geoid.npts(lon3, lat3, lon1, lat1, num_points) + geoid.npts(lon1, lat1, lon2, lat2, num_points))
        walker_points.append(geoid.npts(lon3, lat3, lon1, lat1, num_points) + geoid.npts(lon1, lat1, lon2, lat2, num_points) + geoid.npts(lon2, lat2, lon3, lat3, num_points))

    while True:
        startWalkers(uuids, walker_points)

def usage():
    print("usage: walkers.py ")
    sys.exit(2)
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(prog="walkers.py", description="Program generates requested number of walkers for ATAK")
        parser.add_argument('--num_walkers', nargs='?', help='Number of Walkers')
        parser.add_argument('--type', nargs='?', help='CoT Type')
        parser.add_argument('--pos1_lat', nargs='?', help='Position 1 Latitude')
        parser.add_argument('--pos1_lon', nargs='?', help='Position 1 Longitude')
        parser.add_argument('--pos2_lat', nargs='?', help='Position 2 Latitude')
        parser.add_argument('--pos2_lon', nargs='?', help='Position 2 Longitude')
        parser.add_argument('--pos3_lat', nargs='?', help='Position 3 Latitude')
        parser.add_argument('--pos3_lon', nargs='?', help='Position 3 Longitude')

        args = parser.parse_args()

        if args.pos1_lat and args.pos1_lon:
            lat1 = float(args.pos1_lat)
            lon1 = float(args.pos1_lon)

        if args.pos2_lat and args.pos2_lon:
            lat2 = float(args.pos2_lat)
            lon2 = float(args.pos2_lon)
        
        if args.pos3_lat and args.pos3_lon:
            lat3 = float(args.pos3_lat)
            lon3 = float(args.pos3_lon)

        if args.num_walkers:
            num_walkers = int(args.num_walkers)
    
        if args.type:
            walker_type = args.type

        main()

    except Exception as ex:
        print("Error: %s" % format(ex))
