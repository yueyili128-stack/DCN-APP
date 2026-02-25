import re
import socket
import requests

from flask import Flask, request

def parse_record(s: str):
    s = s.strip()
    pattern = (
        r"^TYPE=([^\s]+)\n"                 # line 1: TYPE=xxx
        r"NAME=([^\s]+)"                    # line 2: NAME=xxx
        r"(?:\s+VALUE=([^\s]+)\s+TTL=(\d+))?$"  # line 2: VALUE / TTL
    )
    match = re.match(pattern, s)
    if not match:
        return None

    type_val, name_val, value_val, ttl_val = match.groups()

    result = {"TYPE": type_val, "NAME": name_val,"VALUE" : None, "TTL": None}
    if value_val is not None:
        result["VALUE"] = value_val
    if ttl_val is not None:
        result["TTL"] = ttl_val

    return result

def send_udp(message, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    sock.sendto(message.encode(), (host, port))
    data, _ = sock.recvfrom(1024)  # buffer size is 1024 bytes
    sock.close()
    return data.decode()
app = Flask(__name__)


# /fibonacci?hostname=fibonacci.com&fs_port=K&number=X&as_ip=Y&as_port=Z
@app.route('/fibonacci', methods=['GET'])
def show_fibonacci():
    # parse query parameters
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')
    if not hostname or not fs_port or not number or not as_ip or not as_port or not as_port.isdigit() or not fs_port.isdigit() or not number.isdigit():
        return "Missing query parameters", 400

    as_port = int(as_port)
    # send query to AS
    dns_massage = f"TYPE=A\nNAME={hostname}\n"
    res = send_udp(dns_massage, as_ip, as_port)
    if not res or res == "Not found":
        return "Not found", 404

    record = parse_record(res)

    fs_ip = record.get('VALUE')

    url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"
    response = requests.get(url)
    if response.status_code != 200:
        return response.text, response.status_code
    return response.text, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

