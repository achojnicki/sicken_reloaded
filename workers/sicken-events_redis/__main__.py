from sicken.config import Config
from sicken.log import Log
from sicken.paths import Paths
from adistools.adisconfig import adisconfig

from redis import Redis
from yaml import safe_load, dump
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path
from pprint import pprint
from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient
from platform import system
from time import sleep

class EventsException(Exception):
	pass

class EventsFileNotFound(Exception):
	pass

class EventNotFound(EventsException):
	pass

class EventParentNotFound(EventsException):
	pass



class Events:
	project_name="sicken-events_redis"
	def __init__(self):
		self._active=True
		self._project_events={}
		self._events=[]
		self._destinations=[]

		self._config=Config(self)

		self._log=Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)

		self._log.info('Initialising sicken-events_redis worker')
		self._paths=Paths()

		self._redis_config=adisconfig(
			self._paths("REDIS_CONFIG_FILE")
			)

		self._redis=Redis(
			host=self._redis_config.redis.host,
			port=self._redis_config.redis.port,
			db=self._redis_config.redis.db,
			password=self._redis_config.redis.password
			)
		self._pubsub=self._redis.pubsub()

		self._mongo_cli=MongoClient(
			self._config.mongo.host,
			self._config.mongo.port,
		)

		self._mongo_db=self._mongo_cli[self._config.mongo.db]
		self._metrics=self._mongo_db['events_metrics']

		self._events_file=Path(self._paths("EVENTS_FILE_PATH"))

		if self._events_file.is_file():
			self._log.debug('Events file detected. Opening...')
			self._load_events()

		self._log.success('Worker sicken-events initialised successfully')

	def _add_metric(self, event_uuid, event_source, event_name, event_destination, event_data, event_timestamp):
		document={
			"event_uuid": event_uuid,
			"event_source": event_source,
			"event_name": event_name,
			"event_destination": event_destination,
			"event_data": event_data
			}

		self._metrics.insert_one(document)

	def _translate_mapping(self, destination_index, event_data, event_uuid, event_name, event_destination):
		mapping=self._destinations[destination_index]['event_mapping']
		data={}
		for item in event_data:
			if item in mapping:
				data[mapping[item]]=event_data[item]

		data['event_uuid']=event_uuid
		data['event_name']=event_name
		data['event_destination']=event_destination

		return data


	def _load_events(self):
		try:
			with open(self._events_file,'r') as events_file:
				events_data=safe_load(events_file)
				
				for project_name in events_data:
					events=[]
					for event_name in events_data[project_name]:

						destinations=[]
						for destination in events_data[project_name][event_name]:
							destination={
								"event_source": project_name,
								"event_name": event_name,
								"event_destination": destination,
								"event_mapping": events_data[project_name][event_name][destination]
							}
							self._destinations.append(destination)
							destinations.append(self._destinations.index(destination))

						event={
							"event_name":event_name,
							"destinations": destinations
						}
						self._events.append(event)
						events.append(self._events.index(event))

					project_event={
						"project_name": project_name,
						"events": events
					}

					self._project_events[project_name]=project_event
		except:
			self._log.exception("exception occured in the events during parsing events definitions file.", as_fatal=True)



	def _event_request(self, data):
		try:
			message=json_loads(data.decode('utf-8'))

			if not message['event_source'] in self._project_events:
				self._log.error(f'Got the event {message["event_name"]} from the {message["event_source"]}, but the source not found in the definitions')
				raise EventParentNotFound
			
			found=False
			for event_index in self._project_events[message['event_source']]['events']:
				
				for destination_index in self._events[event_index]['destinations']:
					destination=self._destinations[destination_index]
					if message['event_name']==destination['event_name']:
						found=True
						event_uuid=str(uuid4())
						time=datetime.now()

						if message['event_name'] != 'logs' and message['event_name']!='gui_logs':
							self._log.info(f'Received event {event_uuid} {message["event_name"]} from the worker {message["event_source"]} to the queue {destination["event_destination"]}.')

						self._add_metric(
							event_uuid=event_uuid,
							event_name=message['event_name'],
							event_destination=destination['event_destination'],
							event_timestamp=time.timestamp(),
							event_data=message['event_data'],
							event_source=message['event_source']
						)

						self._redis.publish(
							destination['event_destination'],
							json_dumps(
								self._translate_mapping(
									destination_index=destination_index,
									event_data=message['event_data'],
									event_uuid=event_uuid,
									event_name=message['event_name'],
									event_destination=destination['event_destination']
									)
								)
							)
			
			if not found:
				self._log.error(f'Got the {message["event_name"]} event from the {message["event_source"]}, but the event not found in definitions')
				raise EventNotFound
		except:
			raise
			self._log.exception("Error occured in events during processing an event", as_fatal=True)


	def loop(self):
		self._pubsub.subscribe('sicken-events')

		while self._active:
			data=self._pubsub.get_message()

			if data and data['type']=='message':
				self._event_request(data['data'])

			sleep(0.001)

	def start(self):
		self.loop()

	def stop(self):
		self._active=False

if __name__=="__main__":
	events=Events()
	events.start()