# -*- coding: utf-8 -*-
from threading import Thread
import select
import time
from messageParser import MessageParser


class MessageReceiver(Thread):
    """
    This is the message receiver class. The class inherits Thread, something that
    is necessary to make the MessageReceiver start a new thread, and it allows
    the chat client to both send and receive messages at the same time
    """

    def __init__(self, client, connection):
        print 'run receiver'
        self.client = client
        self.connection = connection
        Thread.__init__(self)
        """
        This method is executed when creating a new MessageReceiver object
        """

        # Flag to run thread as a deamon
        self.daemon = True
        self.messageParser = MessageParser()
        self.run()
        # TODO: Finish initialization of MessageReceiver

    def run(self):
        print 'runrun'
        time.sleep(0.1)
        while True:
            print 'runrun'
            self.connection.setblocking(0)
            ready = select.select([self.connection], [], [], 0.4)
            if ready[0]:
                data = self.connection.recv(1024)
                msg = self.messageParser.parse(data)
                self.client.receive_message(msg)
            else:
                break
