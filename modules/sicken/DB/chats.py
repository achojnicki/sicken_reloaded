from sicken.exceptions import ChatNotFoundException
from pymongo import ASCENDING

class Chats:
	def get_chats(self):
		chats={}

		cursor=self._chats_collection.find({})

		for chat in cursor:
			del chat['_id']
			chats[chat['chat_uuid']]=chat

		return chats


	def create_chat(self, chat_uuid, chat_created):
		document={
			"chat_uuid": str(chat_uuid),
			"chat_created": chat_created
		}
			
		self._chats_collection.insert_one(document)

	def get_chat(self, chat_uuid):
		query={'chat_uuid': chat_uuid}
		return self._chats_collection.find_one(query)

	def get_chat_messages(self, chat_uuid, del_id=True):
		if not self.get_chat(chat_uuid):
			raise ChatNotFoundException

		messages=[]

		query={'chat_uuid': chat_uuid}
		cursor=self._chat_messages_collection.find(query, sort=[('_id', ASCENDING)])

		for message in cursor:
			if del_id:
				del message['_id']

			messages.append(message)

		return messages

	def remove_chat_message(self, _id):
		query={"_id": _id}
		self._chat_messages_collection.delete_one(query)


	def add_chat_message(self, chat_uuid, message_author, message_source, speech=None, gesture=None, func_name=None, call_id=None, tool_calls=None, reasoning_content=None, msg=None):
		if not self.get_chat(chat_uuid):
			raise ChatNotFoundException

		message={
			"chat_uuid": str(chat_uuid),
			"message_author": message_author,
			"message_source": message_source,
		}

		if speech:
			message['speech']=speech

		if gesture:
			message['gesture']=gesture

		if msg:
			message['message']=msg

		if func_name:
			message['func_name']=func_name

		if call_id:
			message['call_id']=call_id

		if tool_calls:
			message['tool_calls']=tool_calls

		if reasoning_content:
			message['reasoning_content']=reasoning_content


		self._chat_messages_collection.insert_one(message)