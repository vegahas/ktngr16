# -*- coding: utf-8 -*-
import socket
import time
from MessageReceiver import MessageReceiver
import json
import select

class client:

    def __init__(self, host, server_port):
        self.host = 'localhost'
        self.server_port = 9998
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.server_port))
        self.messageReceiver = MessageReceiver(self, self.connection)
        self.run()

    def run(self):
        while True:
            time.sleep(0.2)
            userInput = str(raw_input("Request: "))
            content = str(raw_input("Content: "))
            dictObject = {"request":userInput, "content":content}
            jsonObject = json.dumps(dictObject, ensure_ascii=False)
            self.send_payload(jsonObject)


    def receive_message(self, message):
        print message

    def send_payload(self, data):
        self.connection.send(data)

    # More methods may be needed!


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python client.py"
    in your terminal.

    No alterations are necessary
    """
    client = client('localhost', 9998)
