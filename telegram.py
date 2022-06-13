import requests
from config import telegram_requests_endpoint, telegram_target_chat_id
import math

class Telegram:

	def __init__(self):
		self.url = f'{telegram_requests_endpoint}'
		self.active = True

	def httpGet(self, endpoint):
		if self.active == False:
			return
		r = requests.get(f'{self.url}/{endpoint}')
		if r.status_code == 200:
			print(r.text)

	def httpPost(self, endpoint, data):
		if self.active == False:
			return
		r = requests.post(f'{self.url}/{endpoint}', data=data)
		if r.status_code == 200:
			print(r.text)

	def activate(self):
		self.active = True

	def deactivate(self):
		self.active = False

	def tprint(self, toutput):
		if self.active == False:
			print(toutput)

	def getMe(self):
		self.httpGet('getMe')

	def getUpdates(self):		
		self.httpGet('getUpdates')

	def sendSimpleMessage(self, message):
		data = {
			'chat_id': f'{telegram_target_chat_id}',
			'text': message,
			'parse_mode': 'HTML',
			'disable_notification': True
		}
		self.httpPost('sendMessage', data)		

	def sendMessage(self, api_result):
		api_result_len = len(api_result)
		if api_result_len < 4906:
			api_result_len = 4096
		parts_float = len(api_result) / 4096
		parts_ceil = math.ceil(parts_float)

		for p in range(0, parts_ceil):
			data = {
				'chat_id': f'{telegram_target_chat_id}',
				'text': api_result[p*4096:(p*4096)+4096],
				'parse_mode': 'HTML'
			}

			self.httpPost('sendMessage', data)
