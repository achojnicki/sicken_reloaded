from sicken.config import Config
from sicken.log import Log
from sicken.events import events

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from yaml import safe_load
from uuid import uuid4
from time import time
from pathlib import Path
from requests.auth import HTTPBasicAuth

import tweepy
import requests
import base64
import os



SCOPES=["tweet.read", "users.read", "tweet.write", "media.write", "offline.access"]

class Post_Uploader_X:
	project_name="sicken-x_worker"

	def __init__(self):
		self._config=Config(self)

		self._log=Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)


		self._rabbitmq_conn = BlockingConnection(
			ConnectionParameters(
				host=self._config.rabbitmq.host,
				port=self._config.rabbitmq.port,
				credentials=PlainCredentials(
					self._config.rabbitmq.user,
					self._config.rabbitmq.password
				)
			)
		)

		self._rabbitmq_channel = self._rabbitmq_conn.channel()
		self._rabbitmq_channel.basic_consume(
			queue='sicken-publish_x_post_requests',
			auto_ack=True,
			on_message_callback=self._post_publish_request
		)

		self._events=events(self)

		self.authenticate()


		
	def authenticate(self):		
		self._refreshed = self.refresh_access_token(
			refresh_token=self._config.post_uploader_x.refresh_token,
			client_id=self._config.post_uploader_x.oauth2_client_id,
			client_secret=self._config.post_uploader_x.oauth2_secret)
		
		self._config.post_uploader_x.refresh_token=self._refreshed['refresh_token']
		self._config.save()

		self._client=tweepy.Client(self._refreshed['access_token'])

	def refresh_access_token(self, refresh_token, client_id, client_secret):
		url = "https://api.twitter.com/2/oauth2/token"
		
		data = {
			"refresh_token": refresh_token,
			"grant_type": "refresh_token",
			"client_id": client_id,
		}
		
		# For confidential clients (most bots use this)
		auth = HTTPBasicAuth(client_id, client_secret)
		
		response = requests.post(
			url,
			data=data,
			auth=auth,
			headers={"Content-Type": "application/x-www-form-urlencoded"}
		)
		return response.json()  # {'access_token': ..., 'refresh_token': ..., 'expires_in': ...}
	
	def upload_media_v2(self, access_token: str, file_path: str) -> str | None:
		url = "https://api.x.com/2/media/upload"

		files = { "media": ("example-file", open(file_path,'rb')) }
		payload = {
		    "media_category": "tweet_image",
		    "media_type": "image/jpeg",
		    }
		headers = {"Authorization": f"Bearer {access_token}"}

		response = requests.post(url, data=payload, files=files, headers=headers)
		response=response.json()

		if 'data' in response:
			return response['data']['id'] 


	# def publish_post(self, access_token, post_text, media_ids):
	# 	url = "https://api.x.com/2/tweets"

	# 	payload = {
	# 		"media": {
	# 		    "media_ids": media_ids,
	# 		},
	# 		"text": post_text
	# 	}
	# 	headers = {
	# 		"Authorization": f"Bearer {access_token}",
	# 		"Content-Type": "application/json"
	# 	}

	# 	response = requests.post(url, json=payload, headers=headers)

	# 	return response.ok

	def publish_post(self, access_token, post_text):
		url = "https://api.x.com/2/tweets"

		payload = {
			"text": post_text
		}
		headers = {
			"Authorization": f"Bearer {access_token}",
			"Content-Type": "application/json"
		}

		response = requests.post(url, json=payload, headers=headers)
		self._log.debug(response.text)
		
	def _post_publish_request(self, channel, method, properties, body):
		try:			
			message=loads(body.decode('utf8'))
			post_content=message['post_content']


			response = self.publish_post(
				access_token=self._refreshed['access_token'],
				post_text=post_content,
			)


		except:
			self._log.exception('Exception occured')

	def start(self):
		self._rabbitmq_channel.start_consuming()


	def stop(self):
		self._rabbitmq_channel.stop_consuming()


if __name__=="__main__":
	post_uploader_x=Post_Uploader_X()
	post_uploader_x.start()
