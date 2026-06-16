from sicken.config import Config
from sicken.log import Log
from sicken.GUI.GUI import Sicken_GUI
from sicken.events_redis import events, events_listener
from sicken.DB import DB
from sicken.paths import Paths

from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from uuid import uuid4
from time import time
from threading import Thread
from json import loads

import wx


class Sicken:
	project_name="sicken-gui"
	def __init__(self):
		self._active=True
		self._config=Config(self)
		self._log=Log(
			parent=self,
			rabbitmq_host=self._config.rabbitmq.host,
			rabbitmq_port=self._config.rabbitmq.port,
			rabbitmq_user=self._config.rabbitmq.user,
			rabbitmq_passwd=self._config.rabbitmq.password,
			debug=self._config.log.debug,
			)

		self._log.info('Initialising sicken-gui')
		
		self._app=wx.App()

		self._events=events(self)
		self._events_listener=events_listener(self)

		self._db=DB(self)
		self._paths=Paths()

		self._sicken_gui=Sicken_GUI(self)
		self._chat_uuid=None


		self._events_listener.register_event("sicken-gui_responses", self._gui_response)
		self._events_listener.register_event("sicken-gui_logs", self._logs)
		self._events_listener.register_event("sicken-gui_commands_feedback", self._command_feedback)
		self._events_listener.register_event("sicken-agent_connected_feedback", self._agent_connected_feedback)

		self._exception_warning_showed=False
		self._log.success('Worker sicken-gui initialised successfully')


	def _set_chat_uuid(self):
		self._chat_uuid=str(uuid4())
		self._db.create_chat(
            chat_uuid=self._chat_uuid,
            chat_created=time()
            )

	def _gui_response(self, message):
		if message and message['speech']:
			self._sicken_gui._chat_page.add_sickens_message(message['speech'])

	def _command_feedback(self, message):
		if message and message['message']:
			self._sicken_gui._chat_page.add_system_message(message['message'], esc=message['escape'])

	def _agent_connected_feedback(self, message):
		if message:
			self._sicken_gui._chat_page.add_system_message(message['status_description'], esc=True)


	def _logs(self, message):
		if message:
			wx.CallAfter(
				self._sicken_gui._logs_page._add_item,
				message)
			if message['exception_data'] and not self._exception_warning_showed:
				self._exception_warning_showed=True
				wx.CallAfter(wx.MessageBox, "Exception occured.", "Error", wx.OK|wx.ICON_ERROR)

	def start(self):
		self._sicken_gui.Show()

		t=Thread(target=self._events_listener.loop, args=[])
		t.daemon=True
		t.start()

		self._app.MainLoop()

if __name__=="__main__":
	app=Sicken()
	app.start()