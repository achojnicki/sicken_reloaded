from sicken.config import Config

from sicken.log import Log
from sicken.events import events
from sicken.DB import DB
from sicken.memories import Memories
from sicken.knowledge import Knowledge
from sicken.exceptions import ChatNotFoundException

from constants import SYSTEM_MESSAGE, FUNCTIONS, TOOLS,COMMAND_EXECUTE_REQUEST, COMMAND_EXECUTE_ERROR, COMMAND_EXECUTE_FEEDBACK, SPAWN_PROCESS_FEEDBACK, PROCESS_LOOKUP_FEEDBACK, SLEEP_FEEDBACK, CHARACTERS_FEEDBACK

from openai import OpenAI
from pika import BlockingConnection, PlainCredentials, ConnectionParameters
from json import loads, dumps
from pathlib import Path
from uuid import uuid4
from time import time, sleep
from threading import Thread, Lock

from IPython import embed



class DeepSeek_LLM_Commands:
	project_name="sicken-deepseek_llm_commands"

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
				heartbeat=0,
				host=self._config.rabbitmq.host,
				port=self._config.rabbitmq.port,
				credentials=PlainCredentials(
					self._config.rabbitmq.user,
					self._config.rabbitmq.password
				)
			)
		)

		self._threaded_rabbitmq_conn = BlockingConnection(
			ConnectionParameters(
				heartbeat=0,
				host=self._config.rabbitmq.host,
				port=self._config.rabbitmq.port,
				credentials=PlainCredentials(
					self._config.rabbitmq.user,
					self._config.rabbitmq.password
				)
			)
		)

		self._response_requests_channel = self._rabbitmq_conn.channel()
		self._response_requests_channel.basic_consume(
			queue='sicken-response_requests',
			auto_ack=True,
			on_message_callback=self._response_request
		)
		

		self._agent_command_execution_response_channel = self._threaded_rabbitmq_conn.channel()
		self._agent_command_execution_response_channel.basic_consume(
			queue='sicken-agent_command_execution_response',
			auto_ack=True,
			on_message_callback=self._command_handler
		)

		self._agent_terminal_snapshot_response_channel = self._threaded_rabbitmq_conn.channel()
		self._agent_terminal_snapshot_response_channel.basic_consume(
			queue='sicken-agent_terminal_snapshot_response',
			auto_ack=True,
			on_message_callback=self._snapshot_handler
		)


		self._db=DB(self)
		self._events=events(self)

		self._deepseek=OpenAI(
			api_key=self._config.deepseek.api_key, 
			base_url="https://api.deepseek.com"
			)

		self._memories=Memories(self)
		self._knowledge=Knowledge(self)

		self._commands={}
		self._commands_lock=Lock()

		self._processes={}
		self._processes_lock=Lock()


	def _command_handler(self, channel, method, properties, body):
		message=loads(body)
		command_uuid=message['command_uuid']

		with self._commands_lock:
			if command_uuid in self._commands:
				self._commands[command_uuid]['executed']=True
				self._commands[command_uuid]['exit_code']=message['exit_code']
				self._commands[command_uuid]['stdout']=message['stdout']
				self._commands[command_uuid]['stderr']=message['stderr']
				self._commands[command_uuid]['status']=message['status']
				self._commands[command_uuid]['status_description']=message['status_description']


	def _snapshot_handler(self, channel, method, properties, body):
		message=loads(body)
		process_uuid=message['process_uuid']

		with self._processes_lock:
			if process_uuid in self._processes:
				self._processes[process_uuid]['received']=True
				self._processes[process_uuid]['terminal_snapshot']=message['terminal_snapshot']
				
	def _build_prompt(self,chat_uuid, msg=None):
		try:
			prompt=[]
			prompt.append(
				{"role": "system", "content": SYSTEM_MESSAGE.replace("<__username__>", self._config.user.admin_username)}
				)

			previous_messages=self._db.get_chat_messages(
				chat_uuid=chat_uuid
				)


			for message in previous_messages:
				del message['chat_uuid']
				if message['message_author'] == 'Sicken.ai':
					prompt.append(
						{"role": "assistant", "content": message['speech']}
						)

				elif message['message_author'] == 'function':
					m={
						"role": "tool" if self._config.deepseek.use_tools_calls else "function",
						"name": message['func_name'],
						"content": dumps(message['message'])
					}
					if self._config.deepseek.use_tools_calls:
						m['type']='function_tool_output'
						m['tool_call_id']=message['call_id']
					prompt.append(m)

				elif message['message_author']=='tool_calls':
					prompt.append(
						{"role": "assistant", "content": None, "tool_calls": message['tool_calls']}
						)

				else:
					prompt.append(
						{"role": "user", "content": dumps(message)}
						)
			if msg:
				msg['memories']=dumps(self._memories._get_user_memories(
					profile_user_name=msg['message_author'],
					profile_platform=msg['message_source']))
				
				msg['knowledge']=dumps(self._knowledge._get_knowledge())

				self._db.add_chat_message(
					chat_uuid=msg['chat_uuid'],
					message_author=msg['message_author'],
					message_source=msg['message_source'],
					msg=msg['message']
					)

				prompt.append({"role": "user", "content": dumps(msg)})

			return prompt
		except:
			self._log.exception('Exception ocured in the build_prompt')
			raise


	def _get_model_response(self, prompt):
		try:
			self._log.info('Calling an DeepSeek LLM for response')

			args={
				"model":self._config.sicken.model,
				"seed":self._config.sicken.seed,
				"top_p":self._config.sicken.top_p,
				"top_logprobs":self._config.sicken.top_logprobs,
				"messages": prompt,
			}
			if self._config.deepseek.use_tools_calls:
				args['tools']=TOOLS
			else:
				args['functions']=FUNCTIONS
				args['function_call']="auto"

			completion=self._deepseek.chat.completions.create(**args)
			self._log.success('Received response')
		   
			resp=completion.choices[0].message
			return resp
		except:
			self._log.exception('Exception occured')
			raise


	def _execute_command(self, command, timeout): 
		command_uuid=str(uuid4())
		with self._commands_lock:
			self._commands[command_uuid]={
				"command_uuid": command_uuid,
				"executed": False,
				"command": command,
				"exit_code": None,
				"stdout": None,
				"stderr": None,
				"status": None,
				"status_description": None,
				"timeout": timeout
			}

		self._events.event(
			event_name="execute_command",
			event_data={
				"command_uuid": command_uuid,
				"command": command,
				"timeout": timeout
				}
			)

		while True:
			if self._commands[command_uuid]['executed']:
				break

			sleep(0.1)

		return self._commands[command_uuid]

	def _spawn_process(self, command):
		process_uuid=str(uuid4())

		with self._processes_lock:
			self._processes[process_uuid]={
				"process_uuid": process_uuid,
				"command": command,
				"received": False,
				"terminal_snapshot": None
			}

		self._events.event(
			event_name="spawn_process",
			event_data={
				"process_uuid": process_uuid,
				"command": command
				}
			)
		return {"process_uuid": process_uuid}

	def _send_characters(self, characters_string, process_uuid):

		if process_uuid in self._processes:
			self._events.event(
				event_name="send_characters",
				event_data={
					"process_uuid": process_uuid,
					"characters_string": characters_string
					}
				)

	def _lookup_process(self, process_uuid): 
		with self._processes_lock:
			self._processes[process_uuid]["received"]=False
			self._processes[process_uuid]["terminal_snapshot"]=None 


		self._events.event(
			event_name="lookup_process",
			event_data={
				"process_uuid": process_uuid,
				}
			)

		while True:
			if self._processes[process_uuid]['received']:
				process=self._processes[process_uuid].copy()
				break
			print('waiting')

			sleep(0.1)

		with self._processes_lock:
			self._processes[process_uuid]["received"]=False
			self._processes[process_uuid]["terminal_snapshot"]=None 
		return process

	def _exec_function(self, func_name, func_args):
		if func_name=="execute_command":
			self._events.event(
				event_name="command_feedback",
				event_data={
					"message": COMMAND_EXECUTE_REQUEST.format(command=func_args['command']),
					"escape": True
					}
				)
			result=self._execute_command(
				command=func_args['command'],
				timeout=func_args['timeout']
				)


			if result['status'] == 'Success':
				self._events.event(
					event_name="command_feedback",
					event_data={
						"message": COMMAND_EXECUTE_FEEDBACK.format(**result),
						"escape": True
						}
					)
			else:
				self._events.event(
					event_name="command_feedback",
					event_data={
						"message": COMMAND_EXECUTE_ERROR.format(status_description=result['status_description']),
						"escape": True
						}
					)

		elif func_name=="spawn_process":
			result=self._spawn_process(
				command=func_args['command']
				)

			self._events.event(
				event_name="command_feedback",
				event_data={
					"message": SPAWN_PROCESS_FEEDBACK.format(command=func_args['command'], **result),
					"escape": True
					}
				)

		elif func_name=="lookup_process":
			result=self._lookup_process(
				process_uuid=func_args['process_uuid']
				)

			self._events.event(
				event_name="command_feedback",
				event_data={
					"message": PROCESS_LOOKUP_FEEDBACK,
					"escape": True
					}
				)

		elif func_name=="sleep":
			result=SLEEP_FEEDBACK.format(seconds=func_args['seconds'])
			self._events.event(
				event_name="command_feedback",
				event_data={
					"message": SLEEP_FEEDBACK.format(seconds=func_args['seconds']),
					"escape": True
					}
				)

			sleep(func_args['seconds'])


		elif func_name=="send_process_characters":
			self._send_characters(
				process_uuid=func_args['process_uuid'],
				characters_string=func_args['characters_string']
				)

			result=CHARACTERS_FEEDBACK.format(characters_string=func_args['characters_string'], process_uuid=func_args['process_uuid'])
			
			self._events.event(
				event_name="command_feedback",
				event_data={
					"message": CHARACTERS_FEEDBACK.format(characters_string=func_args['characters_string'], process_uuid=func_args['process_uuid']),
					"escape": True
					}
				)

		
		return result

	def _response_request(self, channel, method, properties, body):
		try:		
			message=loads(body.decode('utf8'))
			self._log.info('Received response request')
			

			if message:
				self._log.debug(message)
				response_uuid=str(uuid4())
				prompt=self._build_prompt(chat_uuid=message['chat_uuid'],msg=message)
				while True:
					self._log.info(prompt)
					response=self._get_model_response(
						prompt=prompt
						)
					self._log.info(response.content)

					#embed()

					if not response.function_call and not response.tool_calls:
						response=response.content

						self._db.add_chat_message(
							chat_uuid=message['chat_uuid'],
							message_author='Sicken.ai',
							message_source='DeepSeek',
							speech=response,
							)
						break

					elif response.function_call:
						func_name = response.function_call.name
						func_args = loads(response.function_call.arguments)

						result=self._exec_function(func_name, func_args)

						self._db.add_chat_message(
								chat_uuid=message['chat_uuid'],
								message_author='function',
								message_source=None,
								msg=result,
								func_name=func_name,
								)
						prompt=self._build_prompt(chat_uuid=message['chat_uuid'])

					elif response.tool_calls:
						self._db.add_chat_message(
								chat_uuid=message['chat_uuid'],
								message_author='tool_calls',
								message_source=None,
								tool_calls=response.dict()['tool_calls']
								)

						for tool_call in response.tool_calls:
							func_name=tool_call.function.name
							func_args=loads(tool_call.function.arguments)
							result=self._exec_function(func_name, func_args)

							self._db.add_chat_message(
								chat_uuid=message['chat_uuid'],
								message_author='function',
								message_source=None,
								msg=result,
								func_name=func_name,
								call_id=tool_call.id
								)
						prompt=self._build_prompt(chat_uuid=message['chat_uuid'])


				self._events.event(
					event_name="request_responded",
					event_data={
						"response_uuid": response_uuid,
						"chat_uuid": message['chat_uuid'],
						"message_author":message['message_author'],
						"message": message['message'],
						"speech": response,
						}
					)
				self._log.success('Response request responded successfully')
		except:
			self._log.exception('Exception occured')
			raise


	def start(self):
		t=Thread(target=self._agent_terminal_snapshot_response_channel.start_consuming, args=[])
		t.daemon=True
		t.start()

		self._response_requests_channel.start_consuming()
		


	def stop(self):
		self._response_requests_channel.stop_consuming()


if __name__=="__main__":
	DeepSeek_LLM_Commands=DeepSeek_LLM_Commands()
	DeepSeek_LLM_Commands.start()
