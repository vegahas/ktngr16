# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
from MessageParser import MessageParser
import json
import select

class client:
    """
    This is the chat client class
    """
    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """
        self.host = 'localhost'
        self.server_port = 9998
        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messageReciever = MessageReceiver()
        self.run()
        self.messageReciever.run()

    def run(self):
        self.connection.connect((self.host, self.server_port))
        while True:

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
    client = Client('localhost', 9998)
