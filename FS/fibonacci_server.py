import sys
from decimal import Decimal, getcontext
import socket
from flask import Flask, request




def send_udp(message, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    sock.sendto(message.encode(), (host, port))
    data, _ = sock.recvfrom(1024)  # buffer size is 1024 bytes
    sock.close()
    return data.decode()

app = Flask(__name__)


# {
# “hostname”: “fibonacci.com”,
# “ip”: “172.18.0.2”,
# “as_ip”: “10.9.10.2”,
# “as_port”: “30001”
# }

@app.route('/register', methods=['PUT'])
def register():
    body = request.get_json()

    if not body:
        return "Missing JSON body", 400
    hostname = body.get('hostname')
    ip = body.get('ip')
    as_ip = body.get('as_ip')
    as_port = body.get('as_port')
    if not hostname or not ip or not as_ip or not as_port or not as_port.isdigit():
        return "Missing fields in JSON body", 400

    # register to AS
    dns_massage = f"TYPE=A\nNAME={hostname} VALUE={ip} TTL=10\n"

    # send UDP packet to AS
    res = send_udp(dns_massage, as_ip, int(as_port))

    return res, 201


# calculate fibonacci number
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        getcontext().prec = int(n * 0.209) + 10

        sqrt5 = Decimal(5).sqrt()
        phi = (Decimal(1) + sqrt5) / Decimal(2)
        psi = (Decimal(1) - sqrt5) / Decimal(2)

        val = (phi ** n - psi ** n) / sqrt5
        return int(val.to_integral_value())




# /fibonacci?number=X
@app.route('/fibonacci', methods=['GET'])
def show_fibonacci():
    number = request.args.get('number')

    if not number or not number.isdigit():
        return "Bad format", 400

    fib = fibonacci(int(number))

    return f"{fib}", 200

if __name__ == '__main__':
    sys.set_int_max_str_digits(0)
    app.run(host='0.0.0.0', port=9090)

