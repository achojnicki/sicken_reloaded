
from sicken.config import Config

from sicken.log import Log
from sicken.events import events
from sicken.DB import DB
from sicken.paths import Paths

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from yaml import safe_load
from uuid import uuid4
from time import time

from firecrawl import Firecrawl
from firecrawl.v2.utils.error_handler import BadRequestError

class Web_worker:
	project_name="sicken-web_worker"

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

		self._search_requests_channel = self._rabbitmq_conn.channel()
		self._search_requests_channel.basic_consume(
			queue='sicken-search_requests',
			auto_ack=True,
			on_message_callback=self._search_request
		)

		self._scrape_requests_channel = self._rabbitmq_conn.channel()
		self._scrape_requests_channel.basic_consume(
			queue='sicken-scrape_requests',
			auto_ack=True,
			on_message_callback=self._scrape_request
		)

		self._db=DB(self)
		self._events=events(self)
		self._paths=Paths()


		self._firecrawl=Firecrawl(api_key=self._config.firecrawl.api_key)

			
	def _search_request(self, channel, method, properties, body):
		try:		
			message=loads(body.decode('utf8'))
			
			results=self._firecrawl.search(
				query=message['search_query'], 
				limit=message['search_results_limit']
				)

			data=[]
			for result in results.web:
				data.append(dict(result))

			self._events.event(
				event_name='search_feedback',
				event_data={
					"search_uuid": message['search_uuid'],
					"search_query": message['search_query'],
					"search_results_limit": message['search_results_limit'],
					"search_results": data
				})

		except:
			self._log.exception('Exception occured')
			raise


	def _scrape_request(self, channel, method, properties, body):
		try:		
			message=loads(body.decode('utf8'))
			
			result=self._firecrawl.scrape(
				url=message['scrape_url'],
				formats=['markdown']
				)

			self._events.event(
				event_name='scrape_feedback',
				event_data={
					"scrape_status": "Success",
					"scrape_uuid": message['scrape_uuid'],
					"scrape_url": message['scrape_url'],
					"scrape_result": result.markdown
				})
			self._log.success(f'Webpage {message["scrape_url"]} scraped successfully.')

		except BadRequestError as e:
			self._events.event(
				event_name='scrape_feedback',
				event_data={
					"scrape_status": "Failed",
					"scrape_uuid": message['scrape_uuid'],
					"scrape_url": message['scrape_url'],
					"scrape_result": None	
				})

			self._log.error(f'Scrapping webpage {message["scrape_url"]} failed. Error message: {str(e.args[0])}')
			
		except:
			self._log.exception('Exception occured')
			raise

	def start(self):
		self._scrape_requests_channel.start_consuming()
		

	def stop(self):
		self._scrape_requests_channel.stop_consuming()


if __name__=="__main__":
	web_worker=Web_worker()
	web_worker.start()
