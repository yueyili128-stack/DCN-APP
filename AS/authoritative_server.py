import socketserver
import re
import os

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

class DNSRecorder:
    def __init__(self):
        self.records = {}

    def add_record(self, type, name, value, ttl,filename='dns_records.txt'):
        self.records[name] = {
            "TYPE": type,
            "NAME": name,
            "VALUE": value,
            "TTL": ttl
        }
        with open(filename, 'a') as f:
            f.write(f"TYPE={type}\nNAME={name} VALUE={value} TTL={ttl}\n\n")


    def load_record(self, filename='dns_records.txt'):
        if not os.path.exists(filename):
            return
        with open(filename, 'r') as f:
            content = f.read()
            entries = content.strip().split('\n\n')
            for entry in entries:
                record = parse_record(entry)
                if record and 'VALUE' in record and 'TTL' in record:
                    self.add_record(record['TYPE'], record['NAME'], record['VALUE'], record['TTL'])

        # rewrite file to remove duplicates
        with open(filename, 'w') as f:
            for record in self.records.values():
                f.write(f"TYPE={record['TYPE']}\nNAME={record['NAME']} VALUE={record['VALUE']} TTL={record['TTL']}\n\n")

        print(f"Loaded {len(self.records)} records from {filename}")

    def get_record(self, name):
        return self.records.get(name, None)




class MyRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        raw_message = data.decode()
        message = parse_record(raw_message)
        # case 0: unformatted message
        if not message:
            response = "Unformatted message"
            socket.sendto(response.encode(), self.client_address)
            return
        # case 1: query
        if not message['VALUE'] and not message['TTL']:
            record = self.server.dns_recorder.get_record(message['NAME'])
            if record:
                response = f"TYPE={record['TYPE']}\nNAME={record['NAME']} VALUE={record['VALUE']} TTL={record['TTL']}\n"
            else:
                response = "Not found"
            socket.sendto(response.encode(), self.client_address)
            return
        # case 2: register
        if message['VALUE'] and message['TTL']:
            self.server.dns_recorder.add_record(message['TYPE'], message['NAME'], message['VALUE'], message['TTL'])
            response = f"Registered: {message['NAME']} -> {message['VALUE']}"
            socket.sendto(response.encode(), self.client_address)
            return




if __name__ == "__main__":
    HOST = '0.0.0.0'
    PORT = 53533

    with socketserver.UDPServer((HOST, PORT), MyRequestHandler) as server:
        print(f"Starting UDP server on {HOST}:{PORT}")
        server.dns_recorder = DNSRecorder()
        server.dns_recorder.load_record()
        server.serve_forever()