#!/usr/bin/env python3

import argparse
import csv
import os
import re
import sqlite3

import matplotlib.pyplot as plt
import requests


def ssh_log_analyzer():
    print("SSH log analyzer")

    log_file = open("/var/log/auth.log", "r")

    successful_ip_addresses_country = {}
    successful_ip_addresses_timestamp = {}

    failed_ip_addresses_country = {}
    failed_ip_addresses_timestamp = {}

    ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    timestamp_pattern = re.compile(r'\[(\d{2}\/[a-zA-Z]{3}\/\d{4}:\d{2}:\d{2}:\d{2} \+\d{4})\]')

    for line in log_file:
        ip_match = re.search(ip_pattern, line)
        timestamp_match = re.search(timestamp_pattern, line)

        if ip_match and timestamp_match:
            ip_address = ip_match.group(1)
            timestamp = timestamp_match.group(1)
            country = get_country(ip_address)

            if "Accepted" in line:
                successful_ip_addresses_country[ip_address] = country
                successful_ip_addresses_timestamp[ip_address] = timestamp

            elif "Failed" in line:
                failed_ip_addresses_country[ip_address] = country
                failed_ip_addresses_timestamp[ip_address] = timestamp

    log_file.close()

    for ip_address, country in successful_ip_addresses_country.items():
        save_http_data(ip_address, str(country), str(
            successful_ip_addresses_timestamp[ip_address]), True)

    for ip_address, country in failed_ip_addresses_country.items():
        save_http_data(ip_address, str(country), str(
            failed_ip_addresses_timestamp[ip_address]), False)

    export_http_data_to_pdf()


def http_log_analyzer():
    print("Apache HTTP log analyzer")
    log_file = open("/var/log/apache2/access.log", "r")

    successful_ip_addresses_country = {}
    successful_ip_addresses_timestamp = {}

    failed_ip_addresses_country = {}
    failed_ip_addresses_timestamp = {}

    ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    status_code_pattern = re.compile(r'\"\d{3}')
    timestamp_pattern = re.compile(r'\[(.*?)\]')

    for line in log_file:
        ip_match = re.search(ip_pattern, line)
        status_code_match = re.search(status_code_pattern, line)
        timestamp_match = re.search(timestamp_pattern, line)

        if ip_match and status_code_match and timestamp_match:
            ip_address = ip_match.group(1)
            status_code = status_code_match.group(0)
            timestamp = timestamp_match.group(1)
            country = get_country(ip_address)

            if status_code.startswith("20") or status_code.startswith("30"):
                successful_ip_addresses_country[ip_address] = country
                successful_ip_addresses_timestamp[ip_address] = timestamp

            elif status_code.startswith("40") or status_code.startswith("50"):
                failed_ip_addresses_country[ip_address] = country
                failed_ip_addresses_timestamp[ip_address] = timestamp

    log_file.close()

    for ip_address, country in successful_ip_addresses_country.items():
        save_ssh_data(ip_address, str(country), str(successful_ip_addresses_timestamp[ip_address]), True)

    for ip_address, country in failed_ip_addresses_country.items():
        save_ssh_data(ip_address, str(country), str(failed_ip_addresses_timestamp[ip_address]), False)

    export_ssh_data_to_pdf()


def save_ssh_data(ip_address, country, timestamp, success):
    if not os.path.exists("ssh_log.csv"):
        with open("ssh_log.csv", "w") as f:
            fieldnames = ["ip_address", "country", "timestamp", "success"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    with open("ssh_log.csv", "a") as f:
        fieldnames = ["ip_address", "country", "timestamp", "success"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow({"ip_address": ip_address, "country": country, "timestamp": timestamp, "success": success})

    if not os.path.exists("ssh_log.db"):
        conn = sqlite3.connect("ssh_log.db")
        c = conn.cursor()
        c.execute("CREATE TABLE ssh_log (ip_address text, country text, timestamp text, success text)")
        conn.commit()
        conn.close()

    conn = sqlite3.connect("ssh_log.db")
    c = conn.cursor()
    c.execute("INSERT INTO ssh_log VALUES (?, ?, ?, ?)", (ip_address, country, timestamp, success))
    conn.commit()
    conn.close()


def save_http_data(ip_address, country, timestamp, success):
    if not os.path.exists("http_log.csv"):
        with open("http_log.csv", "w") as f:
            fieldnames = ["ip_address", "country", "timestamp", "success"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    with open("http_log.csv", "a") as f:
        fieldnames = ["ip_address", "country", "timestamp", "success"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow({"ip_address": ip_address, "country": country, "timestamp": timestamp, "success": success})

    if not os.path.exists("http_log.db"):
        conn = sqlite3.connect("http_log.db")
        c = conn.cursor()
        c.execute("CREATE TABLE http_log (ip_address text, country text, timestamp text, success text)")
        conn.commit()
        conn.close()

    conn = sqlite3.connect("http_log.db")
    c = conn.cursor()
    c.execute("INSERT INTO http_log VALUES (?, ?, ?, ?)", (ip_address, country, timestamp, success))
    conn.commit()
    conn.close()


def export_ssh_data_to_pdf():
    plt.style.use("ggplot")
    plt.rcParams["figure.figsize"] = (20, 10)
    plt.rcParams["font.size"] = 20
    plt.rcParams["axes.labelsize"] = 20
    plt.rcParams["axes.titlesize"] = 20
    plt.rcParams["xtick.labelsize"] = 20
    plt.rcParams["ytick.labelsize"] = 20
    plt.rcParams["legend.fontsize"] = 20
    plt.rcParams["figure.titlesize"] = 20

    conn = sqlite3.connect("ssh_log.db")
    c = conn.cursor()
    c.execute("SELECT * FROM ssh_log")
    data = c.fetchall()
    conn.close()

    ip_addresses = []
    countries = []
    timestamps = []
    success = []

    for row in data:
        ip_addresses.append(row[0])
        countries.append(row[1])
        timestamps.append(row[2])
        success.append(row[3])

    successful_ip_addresses = []
    successful_countries = []

    failed_ip_addresses = []
    failed_countries = []

    for i in range(len(success)):
        if success[i] == "True":
            successful_ip_addresses.append(ip_addresses[i])
            successful_countries.append(countries[i])
        else:
            failed_ip_addresses.append(ip_addresses[i])
            failed_countries.append(countries[i])

    plt.plot(successful_countries, successful_ip_addresses, "o", color="green", label="Successful")
    plt.plot(failed_countries, failed_ip_addresses, "o", color="red", label="Failed")

    plt.title("SSH Log Analysis")
    plt.xlabel("Country")
    plt.ylabel("IP Address")
    plt.legend()

    plt.savefig("ssh_log_analysis.pdf")


def export_http_data_to_pdf():
    plt.style.use("ggplot")
    plt.rcParams["figure.figsize"] = (20, 10)
    plt.rcParams["font.size"] = 20
    plt.rcParams["axes.labelsize"] = 20
    plt.rcParams["axes.titlesize"] = 20
    plt.rcParams["xtick.labelsize"] = 20
    plt.rcParams["ytick.labelsize"] = 20
    plt.rcParams["legend.fontsize"] = 20
    plt.rcParams["figure.titlesize"] = 20

    conn = sqlite3.connect("http_log.db")
    c = conn.cursor()
    c.execute("SELECT * FROM http_log")
    data = c.fetchall()
    conn.close()

    ip_addresses = []
    countries = []
    timestamps = []
    success = []

    for row in data:
        ip_addresses.append(row[0])
        countries.append(row[1])
        timestamps.append(row[2])
        success.append(row[3])

    successful_ip_addresses = []
    successful_countries = []

    failed_ip_addresses = []
    failed_countries = []

    for i in range(len(success)):
        if success[i] == "True":
            successful_ip_addresses.append(ip_addresses[i])
            successful_countries.append(countries[i])
        else:
            failed_ip_addresses.append(ip_addresses[i])
            failed_countries.append(countries[i])

    plt.plot(successful_countries, successful_ip_addresses, "o", color="green", label="Successful")
    plt.plot(failed_countries, failed_ip_addresses, "o", color="red", label="Failed")

    plt.title("HTTP Log Analysis")
    plt.xlabel("Country")
    plt.ylabel("IP Address")
    plt.legend()

    plt.savefig("http_log_analysis.pdf")


def get_country(ip_address):
    response = requests.get("http://ip-api.com/json/" + ip_address)
    json_response = response.json()
    country = json_response["country"]

    return country


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--help", help="Help")
    parser.add_argument("-l", "--log", help="Log file to analyze")
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        exit()

    if args.log == "all":
        ssh_log_analyzer()
        http_log_analyzer()
    elif args.log == "ssh":
        ssh_log_analyzer()
    elif args.log == "http":
        http_log_analyzer()
    else:
        print("Invalid log file specified")
        exit()


if __name__ == "__main__":
    main()
