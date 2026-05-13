from ..constants import MSG_FORMAT, LOG_LEVELS

from json import dumps
from pika import BlockingConnection, ConnectionParameters, PlainCredentials, exceptions


class rabbitmq_emiter:
	_rabbitmq_connection=None
	_rabbitmq_channel=None

	_rabbitmq_host=None
	_rabbitmq_port=None
	_rabbitmq_user=None
	_rabbitmq_passwd=None

	def __init__(self,
				 rabbitmq_host,
				 rabbitmq_port,
				 rabbitmq_queue,
				 rabbitmq_user,
				 rabbitmq_passwd,
				 **kwargs
				 ):
		 
		self._rabbitmq_host=rabbitmq_host
		self._rabbitmq_port=rabbitmq_port
		self._rabbitmq_user=rabbitmq_user
		self._rabbitmq_passwd=rabbitmq_passwd
		self._rabbitmq_queue=rabbitmq_queue
		self._open_rabbitmq_connection()

	
	def _open_rabbitmq_connection(self):
		self._rabbitmq_connection=BlockingConnection(
			ConnectionParameters(
				host=self._rabbitmq_host,
				port=self._rabbitmq_port,
				credentials=PlainCredentials(
					self._rabbitmq_user,
					self._rabbitmq_passwd
					)
				))
		
		self._rabbitmq_channel=self._rabbitmq_connection.channel()

	def _close_rabbitmq_connection(self):
		if self._rabbitmq_channel.is_open:
			self._rabbitmq_channel.close()
		if self._rabbitmq_connection.is_open:
			self._rabbitmq_connection.close()

	def _emit_message(self, message):
		message=dumps(message)

		self._rabbitmq_channel.basic_publish(
				exchange="",
				routing_key=self._rabbitmq_queue,
				body=message
			)
			
	def emit(self,msg):
		attempts=0

		while attempts<3:
			if self._rabbitmq_channel.is_closed or self._rabbitmq_connection.is_closed:
				self._open_rabbitmq_connection()
			try:		
				self._emit_message(msg)
				return
				
			except exceptions.StreamLostError:
				self._close_rabbitmq_connection()
				
			attempts+=1
	
		
