# -*- coding: utf-8 -*-
import socket
import time
from MessageReceiver import MessageReceiver
import json


class Client:

    def __init__(self, host, server_port):
        self.host = host
        self.server_port = server_port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.server_port))
        self.messageReceiver = MessageReceiver(self, self.connection)
        self.run()

    def run(self):
        while True:
            time.sleep(0.2)
            user_input = str(raw_input("Request: "))
            content = str(raw_input("Content: "))
            dict_object = {"request": user_input, "content": content}
            json_object = json.dumps(dict_object, ensure_ascii=False)
            self.send_payload(json_object)

    def receive_message(self, message):
        print message

    def send_payload(self, data):
        self.connection.send(data)

if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    client = Client('10.20.78.29', 9998)
