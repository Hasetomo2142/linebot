import requests

class LineMessenger:
    def __init__(self, access_token):
        self.url = 'https://api.line.me/v2/bot/message/push'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
    
    def send_text(self, user_id, text):
        payload = {
            'to': user_id,
            'messages': [
                {
                    'type': 'text',
                    'text': text
                }
            ]
        }
        response = requests.post(self.url, headers=self.headers, json=payload)
        if response.status_code != 200:
            print('Failed to send message. Error:', response.text)
