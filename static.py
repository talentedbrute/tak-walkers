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
import sys

from datetime import datetime, timedelta

callsign = "CALLSIGN"
altitude = 0
num_walkers = 4
# walker_type = "a-h-G-U-C-A"  # ARMOR
#walker_type = "a-f-S-X-M-C"  # CARGO SHIP
#  walker_type = "a-f-A-C-F"  # CIVILIAN AIRCRAFT
walker_type = "a-f-G-U-U-L-C"  # CIVILIAN LAW ENFORCEMENT

## For Remote
hostname = "r2tak.adeptus-cs.com"
port = 8089
serverPEM = "certs/server-r2.pem"
clientPEM = "certs/client-r2.pem"
serverCN = "RippleTwo"

walker_points = [[34.34734, -117.88357], 
                 [34.32600, -117.93791],
                 [34.37694, -117.96281],
                 [34.26852, -117.98668]]

# regarding socket.IP_MULTICAST_TTL
# ---------------------------------
# for all packets sent, after two hops on the network the packet will not 
# be re-sent/broadcast (see https://www.tldp.org/HOWTO/Multicast-HOWTO-6.html)
MULTICAST_TTL = 2

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.verify_mode = ssl.CERT_OPTIONAL
context.check_hostname = False
context.load_verify_locations(serverPEM)
context.load_cert_chain(certfile=clientPEM)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockConnection = context.wrap_socket(sock, server_hostname=serverCN)
sockConnection.connect((hostname, port))


def sendCoT(cotMessage):
    # For Python 3, change next line to 'sock.sendto(b"robot", ...' to avoid the
    # "bytes-like object is required" msg (https://stackoverflow.com/a/42612820)
    try:
        sockConnection.send(cotMessage.encode())
    except Exception as ex:
        print("Error: %s" % format(ex))

def startWalkers(uuids, callsigns, walker_points):
    while True:
        for w in range(num_walkers):
            print("Points for walker %d: %.8f:%.9f" % (w, walker_points[w][0], walker_points[w][1]))

            now = datetime.utcnow()
            startTime = now.strftime("%FT%T.%f")
            nowTime = now.strftime("%FT%T.%f")
            staleTime = (now + timedelta(minutes=120)).strftime("%FT%T.%f")
            xml = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><event version='2.0' uid='%s' type='%s' how='m-g' time='%sZ' start='%sZ' stale='%sZ'><detail><contact callsign='%s'/></detail><point lat='%.8f' lon='%.8f' hae='0.0' ce='1' le='1'/></event>" % (uuids[w], walker_type, nowTime, startTime, staleTime, callsigns[w], walker_points[w][0], walker_points[w][1])
            print("Sending XML: %s" % xml)
            sendCoT(xml)
        time.sleep(120)

def main():
    ## UUIDS for the walkers
    uuids = []
    callsigns = []
    for k in range(num_walkers):
        uuids.append(str(uuid.uuid4()))
        callsigns.append("%s-%d" % (callsign, (k+1)))

    while True:
        startWalkers(uuids, callsigns, walker_points)

def usage():
    print("usage: walkers.py ")
    sys.exit(2)

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(prog="walkers.py", description="Program generates requested number of walkers for ATAK")
        parser.add_argument('--type', nargs='?', help='CoT Type')
        parser.add_argument('--callsign', nargs='?', help='Callsign')

        args = parser.parse_args()
    
        if args.type:
            walker_type = args.type

        if args.callsign:
            callsign = args.callsign

        main()

    except Exception as ex:
        print("Error: %s" % format(ex))