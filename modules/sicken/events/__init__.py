from .exceptions import EventsFileNotFound, EventNotFound
from sicken.paths import Paths

from pika import BlockingConnection, ConnectionParameters, PlainCredentials, exceptions
from yaml import safe_load, dump
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path
from pprint import pprint
from datetime import datetime
from platform import system


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

		self._events_file=Path(self._paths("EVENTS_FILE_PATH"))
		if self._events_file.is_file():
			if self._log:
				self._log.debug('Found an events definition file. Opening and loading...')
			self._load_events()
		else:
			raise EventsFileNotFound

		self._open_rabbitmq_connection()

		if self._log:
			self._log.success('Events module initialised successfully')


	def _open_rabbitmq_connection(self):
		self._rabbitmq_connection=BlockingConnection(
			ConnectionParameters(
				host=self._config.rabbitmq.host,
				port=self._config.rabbitmq.port,
				credentials=PlainCredentials(
					self._config.rabbitmq.user,
					self._config.rabbitmq.password
					)
				))
		
		self._rabbitmq_channel=self._rabbitmq_connection.channel()

	def _close_rabbitmq_connection(self):
		if self._rabbitmq_channel.is_open:
			self._rabbitmq_channel.close()

		if self._rabbitmq_connection.is_open:
			self._rabbitmq_connection.close()


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
		attempt=0

		while attempt<3:
			if self._rabbitmq_channel.is_closed or self._rabbitmq_connection.is_closed:
				self._open_rabbitmq_connection()

			if self._log:
				self._log.info(f'Emitting event name:{event_name} source:{self._root.project_name}')
			try:
				self._rabbitmq_channel.basic_publish(
					exchange="",
					routing_key="sicken-events",
					body=json_dumps(msg)
					)
				if self._log:
					self._log.success(f'Event {event_name} emitted successfully')
				return
			
			except exceptions.StreamLostError:
				self._log.warning('Failed to emit event. retrying')
				self._close_rabbitmq_connection()

			attempt+=1
		self._log.fatal('Reached max attempts of event delively')


