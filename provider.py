import os
import socket
import struct
import select
from multiprocessing import Process, Lock
from msgpack import packb, unpackb
from datetime import datetime

THINKNODE_HOST = os.getenv("THINKNODE_HOST")
THINKNODE_PORT = int(os.getenv("THINKNODE_PORT"))
THINKNODE_PID  = os.getenv("THINKNODE_PID")
BUFFER_SIZE = 4096

def ext_hook(code, data):
    if code == 1:
        length = len(data)
        if length == 1:
            data = struct.unpack_from(">b", data)[0]
        elif length == 2:
            data = struct.unpack_from(">h", data)[0]
        elif length == 4:
            data = struct.unpack_from(">i", data)[0]
        else: # length == 8
            data = struct.unpack_from(">q", data)[0]
        return datetime.utcfromtimestamp(data / 1000.0)
    raise ValueError("Cannot decode extension type " + str(code))

class Client(object):
    versions = {
        "1": 0
    }

    actions = {
        "REGISTER": 0,
        "FUNCTION": 1,
        "PROGRESS": 2,
        "RESULT": 3,
        "FAILURE": 4,
        "PING": 5,
        "PONG": 6
    }

    protocols = {
        "MsgPack": 0
    }

    def __init__(self, provider):
        self.messages = []
        self.write_lock = Lock()
        self.provider = provider
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.sock.close()

    # Public Methods

    def connect(self):
        print "Connecting"
        self.sock.connect((THINKNODE_HOST, THINKNODE_PORT))

    def loop(self):
        print "Receiving Messages"
        while True:
            self._receive_message()

    def register(self):
        print "Registering"
        header = Client._get_header("1", "REGISTER", 34)
        protocol = bytearray(2)
        struct.pack_into(">H", protocol, 0, Client.protocols["MsgPack"])
        pid = bytearray(unicode(THINKNODE_PID), "utf-8")
        message = header + protocol + pid
        self.sock.send(message)

    # Private Methods

    def _receive_message(self):
        print "Reading Header"
        header = Client._receive(self.sock, 8)
        v, r1, c, r2, length = struct.unpack_from(">BBBBI", header)
        print "Reading Body"
        body = Client._receive(self.sock, length)
        if c == Client.actions["FUNCTION"]:
            p = Process(target=Client._handle_function, args=(self, body))
            p.start()
        elif c == Client.actions["PING"]:
            p = Process(target=Client._handle_ping, args=(self, body))
            p.start()

    def _send_message(self, action, body):
        print "Sending Message", action
        self.write_lock.acquire()
        length = len(body)
        header = Client._get_header("1", action, length)
        message = header + body
        self.sock.send(message)
        self.write_lock.release()

    # Static methods

    @staticmethod
    def _get_failure_reporter(client):
        def fail(code, message):
            Client._handle_failure(client, code, message)
            # Kill Process because we don't want to send anything after a failure.
            pid = os.getpid()
            os.kill(pid, 1)
        return fail

    @staticmethod
    def _get_header(version, action, length):
        v = Client.versions[version]
        a = Client.actions[action]
        header = bytearray(8)
        struct.pack_into(">BBBBI", header, 0, v, 0, a, 0, length)
        return header

    @staticmethod
    def _get_progress_updater(client):
        def update_progress(progress, message=""):
            Client._handle_progress(client, progress, message)
        return update_progress

    @staticmethod
    def _handle_failure(client, code, message):
        code_length = len(code)
        raw_code_length = bytearray(1)
        struct.pack_into(">B", raw_code_length, 0, code_length)

        raw_code = bytearray(unicode(code), "utf-8")

        message_length = len(message)
        raw_message_length = bytearray(2)
        struct.pack_into(">H", raw_message_length, 0, message_length)

        raw_message = bytearray(unicode(message), "utf-8")

        body = raw_code_length + raw_code + raw_message_length + raw_message

        client._send_message("FAILURE", body)

    @staticmethod
    def _handle_ping(client, body):
        client._send_message("PONG", body)

    @staticmethod
    def _handle_progress(client, progress, message):
        pre = bytearray(6)
        msg = bytearray(unicode(message), "utf-8")
        length = len(msg)
        struct.pack_into(">fH", pre, 0, progress, length)
        body = pre + msg
        client._send_message("PROGRESS", body)

    @staticmethod
    def _handle_function(client, body):
        try:
            index = 0

            raw_name_length = body[:index+1]
            name_length = struct.unpack_from(">B", raw_name_length)[0]
            index += 1

            raw_name = body[index:index+name_length]
            name = raw_name.decode("utf-8")
            index += name_length

            raw_count = body[index:index+2]
            count = struct.unpack_from(">H", raw_count)[0]
            index += 2

            args = []
            for i in range(count):
                raw_arg_length = body[index:index+4]
                arg_length = struct.unpack_from(">I", raw_arg_length)[0]
                index += 4
                arg = body[index:index+arg_length]
                args.append(unpackb(arg, ext_hook=ext_hook))
                index += arg_length

            args.append(Client._get_progress_updater(client))
            args.append(Client._get_failure_reporter(client))

            result = packb(getattr(client.provider, name)(*args))
            client._send_message("RESULT", result)
        except Exception as e:
            Client._handle_failure(client, e.__class__.__name__, e.message)

    @staticmethod
    def _receive(socket, length):
        msg = bytearray()
        remaining = length
        while remaining > 0:
            chunk = socket.recv(min(BUFFER_SIZE, remaining))
            msg.extend(chunk)
            remaining -= len(chunk)
        return buffer(msg)

class Provider(object):

    def __init__(self):
        self._client = Client(self)

    def run(self):
        self._client.connect()
        self._client.register()
        self._client.loop()