from .exceptions import EventsFileNotFound, EventNotFound
from sicken.paths import Paths
from adistools.adisconfig import adisconfig

from redis import Redis
from yaml import safe_load, dump
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path
from pprint import pprint
from datetime import datetime
from platform import system
from threading import Thread
from time import sleep


class AttrDict(dict):
	def __init__(self, *args, **kwargs):
		super(AttrDict, self).__init__(*args, **kwargs)
		self.__dict__ = self     

class events:
	def __init__(self, root):
		self._events=[]

		self._root=root
		self._config=root._config
		self._log=None

		if hasattr(root,'_log'):
			self._log=root._log
			self._log.info('Initialising events module')

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


		self._events_file=Path(self._paths("EVENTS_FILE_PATH"))
		if self._events_file.is_file():
			if self._log:
				self._log.debug('Found an events definition file. Opening and loading...')
			self._load_events()
		else:
			raise EventsFileNotFound


		if self._log:
			self._log.success('Events module initialised successfully')




	def _load_events(self):
		with open(self._events_file,'r') as events_file:
			events_data=safe_load(events_file)
			
			if not self._root.project_name in events_data:
				return

			for event_name in events_data[self._root.project_name]:
				self._events.append(event_name)


	def event(self, event_name, event_data):
		if not event_name in self._events:
			raise EventNotFound

		msg={
			"event_name": event_name,
			"event_source": self._root.project_name,
			"event_data": event_data,
			"event_timestamp": datetime.now().timestamp()
		}

		if self._log:
			self._log.info(f'Emitting event name:{event_name} source:{self._root.project_name}')

		self._redis.publish('sicken-events', json_dumps(msg))

		if self._log:
			self._log.success(f'Event {event_name} emitted successfully')


class events_listener:
	def __init__(self, root):
		self._active=True
		self._events={}

		self._registered_events=[]

		self._root=root
		self._config=root._config
		self._log=None

		if hasattr(root,'_log'):
			self._log=root._log
			self._log.info('Initialising events module')

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


		self._events_file=Path(self._paths("EVENTS_FILE_PATH"))
		if self._events_file.is_file():
			if self._log:
				self._log.debug('Found an events definition file. Opening and loading...')
			self._load_events()
		else:
			raise EventsFileNotFound


		if self._log:
			self._log.success('Events_listener module initialised successfully')


	def _load_events(self):
		with open(self._events_file,'r') as events_file:
			events_data=safe_load(events_file)
			
			if not self._root.project_name in events_data:
				return


			for event_name in events_data[self._root.project_name]:


				data=[]
				for x in events_data[self._root.project_name][event_name]:
					data.append(x)
				self._events[event_name]=data



	def register_event(self, event_destination, callback, start_in_thread=False):
		self._registered_events.append({
			"event_destination": event_destination,
			"callback": callback,
			"start_in_thread": start_in_thread
			})

		self._pubsub.subscribe(event_destination)


	def loop(self):
		while self._active:
			try:
				data=self._pubsub.get_message()
				if data and data['type']=='message':
					message=json_loads(data['data'])

					for sicken_event in self._registered_events:
						if sicken_event['event_destination'] == message['event_destination']:

							if sicken_event['start_in_thread']:
								t=Thread(target=sicken_event['callback'], args=[message])
								t.daemon=True
								t.start()

							else:
								sicken_event['callback'](message)
			except:
				raise
				if self._log:
					self._log.exception('Exception occured in events_listener loop')


			sleep(0.001)