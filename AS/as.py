import os
import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 53533
DB_FILE = "dns_records.txt"

def parse_lines(msg: str) -> dict:
    lines = [ln.strip() for ln in msg.splitlines() if ln.strip()]
    out = {}
    for ln in lines:
        if "=" not in ln:
            continue
        key, rest = ln.split("=", 1)
        out[key.strip().upper()] = rest.strip()
    return out

def parse_name_line(name_line: str):
    parts = name_line.split()
    name = parts[0]
    kv = {}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            kv[k.upper()] = v
    return name, kv

def save_record(name, value, ttl):
    with open(DB_FILE, "a") as f:
        f.write(f"TYPE=A NAME={name} VALUE={value} TTL={ttl}\n")

def lookup(name):
    if not os.path.exists(DB_FILE):
        return None
    with open(DB_FILE, "r") as f:
        for line in f:
            if f"NAME={name}" in line:
                return line.strip()
    return None

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Authoritative Server running...")

    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode().strip()
        print("Received:", msg)

        parsed = parse_lines(msg)

        if "VALUE" in msg:
            # registration
            name, kv = parse_name_line(parsed["NAME"])
            save_record(name, kv["VALUE"], kv["TTL"])
            sock.sendto(b"OK", addr)
        else:
            # query
            name = parsed["NAME"]
            result = lookup(name)
            if result:
                sock.sendto(result.encode(), addr)
            else:
                sock.sendto(b"NOTFOUND", addr)

if __name__ == "__main__":
    main()