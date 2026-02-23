from flask import Flask, request, jsonify
import socket
import requests

app = Flask(__name__)

def query_as(as_ip: str, as_port: int, hostname: str, timeout=2.0) -> str:
    msg = f"TYPE=A\nNAME={hostname}\n"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(msg.encode(), (as_ip, as_port))
        data, _ = s.recvfrom(4096)
        return data.decode().strip()
    finally:
        s.close()

def parse_value(resp: str):
    # Expected format: TYPE=A NAME=... VALUE=IP TTL=10
    parts = resp.split()
    for p in parts:
        if p.startswith("VALUE="):
            return p.split("=", 1)[1]
    return None

@app.get("/fibonacci")
def fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return jsonify({"error": "missing parameters"}), 400

    try:
        fs_port = int(fs_port)
        as_port = int(as_port)
        n = int(number)
    except:
        return jsonify({"error": "bad parameter format"}), 400

    # 1) Ask AS for the IP of hostname
    try:
        dns_resp = query_as(as_ip, as_port, hostname)
        ip = parse_value(dns_resp)
        if not ip:
            return jsonify({"error": f"bad DNS response: {dns_resp}"}), 500
    except Exception as e:
        return jsonify({"error": f"DNS query failed: {e}"}), 500

    # 2) Call FS Fibonacci endpoint
    try:
        r = requests.get(f"http://{ip}:{fs_port}/fibonacci", params={"number": n}, timeout=3)
        return r.text, r.status_code
    except Exception as e:
        return jsonify({"error": f"FS request failed: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)