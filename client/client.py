# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
from MessageParser import MessageParser
import json
import select

class Client:
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
        self.messageParser = MessageParser()
        self.run()

    def run(self):
        # Initiate the connection to the server
        self.connection.connect((self.host, self.server_port))
        while True:
            while True:
                self.connection.setblocking(0)
                ready = select.select([self.connection], [], [], 0.4)
                if ready[0]:
                    data = self.connection.recv(1024)
                    self.receive_message(data)
                else:
                    break
            userInput = str(raw_input("Request: "))
            content = str(raw_input("Content: "))
            dictObject = {"request":userInput, "content":content}
            jsonObject = json.dumps(dictObject, ensure_ascii=False)
            self.send_payload(jsonObject)


    def receive_message(self, message):
        msg = self.messageParser.parse(message)
        print msg

    def send_payload(self, data):
        self.connection.send(data)

    # More methods may be needed!


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    client = Client('localhost', 9998)
