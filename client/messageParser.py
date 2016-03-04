import json

class MessageParser():
    def __init__(self):

        self.possible_responses = {
            'error': self.parse_error,
            'info': self.parse_info,
            'message': self.parse_message,
            'history': self.parse_history
	    # More key:values pairs are needed	
        }

    def parse(self, payload):
        payload = json.loads(payload)
        if payload['response'] in self.possible_responses:
            return self.possible_responses[payload['response']](payload)
        else:
            return "fail"

    def parse_error(self, payload):
        return payload["content"]

    def parse_info(self, payload):
        if str(payload["content"]).startswith("["): #Only if 'names' request -> format string
            msg = ''
            for el in payload["content"]:
                msg += el + ','
            return "Users: " + msg
        return payload["content"]

    def parse_message(self, payload):
        return payload["content"] #skjer ingenting ? - ingen output

    def parse_history(self, payload):
        if payload["content"] == []:
            return "No chat history"
        else:
            msg = ''
            for el in payload["content"]:
                x = json.loads(el)
                streng = x['sender'] + ': ' + x['content'] + '\n'
                msg += streng
            return "Chat history: \n"+ msg
    # Include more methods for handling the different responses... 
