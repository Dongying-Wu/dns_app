from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

def fib(n: int) -> int:
    if n < 0:
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def udp_send(host: str, port: int, message: str, timeout=2.0) -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(message.encode("utf-8"), (host, port))
        data, _ = sock.recvfrom(4096)
        return data.decode("utf-8", errors="replace").strip()
    finally:
        sock.close()

@app.get("/fibonacci")
def fibonacci():
    x = request.args.get("number")
    if x is None:
        return jsonify({"error": "missing number"}), 400
    try:
        n = int(x)
    except Exception:
        return jsonify({"error": "number must be int"}), 400

    try:
        return jsonify({"number": n, "fibonacci": fib(n)}), 200
    except Exception:
        return jsonify({"error": "invalid number"}), 400

@app.put("/register")
def register():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "bad json"}), 400

    hostname = body.get("hostname")
    ip = body.get("ip")
    as_ip = body.get("as_ip")
    as_port = body.get("as_port")

    if not (hostname and ip and as_ip and as_port):
        return jsonify({"error": "missing fields"}), 400

    try:
        as_port = int(as_port)
    except Exception:
        return jsonify({"error": "as_port must be int"}), 400

    msg = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL=10\n"
    try:
        resp = udp_send(as_ip, as_port, msg)
    except Exception as e:
        return jsonify({"error": f"udp failed: {e}"}), 500

    if resp != "OK":
        return jsonify({"error": f"AS returned: {resp}"}), 500

    return jsonify({"status": "registered"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)