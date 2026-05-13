from html import escape
from pathlib import Path
from pprint import pformat, pprint
import wx
import wx.html2
import wx.stc
import mistune


class Historic_Chats_Page(wx.Panel):
    def __init__(self, root, parent, frame):
        self._root=root
        self._frame=frame
        wx.Panel.__init__(self, parent)

        self._chats={}
        self._chats_indexes=[]
        

        self._view_path=Path(self._root._paths('VIEWS_DIR')).joinpath('gui').joinpath('chat.view')

        self.chat_template=open(self._view_path,'r').read()
        self.sizer=wx.BoxSizer(wx.VERTICAL)        

        self.html=wx.html2.WebView.New(self)
        self.html.SetPage(self.chat_template,"")
        self.html.EnableContextMenu(self._root._config.chat.allow_context_menu)
        self.html.EnableAccessToDevTools(self._root._config.chat.allow_inspect)

        self.choice=wx.Choice(self, choices=[])

        self.sizer.Add(self.choice, 0, wx.EXPAND)
        self.sizer.Add(self.html, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.SetBackgroundColour((32,34,39))
    
        

        self._markdown=mistune.create_markdown(plugins=['table','url','task_lists','def_list','mark','superscript','subscript','strikethrough'])
        
        self.Bind(wx.EVT_CHOICE, self._on_select, self.choice)

        self._propagate_chats()
        wx.CallLater(1000, self._on_select,)
        self.Show(True)


    def _propagate_chats(self, event=None):
        self._chats=self._root._db.get_chats()
        self._chats_indexes=list(self._chats.keys())

        
        for chat in self._chats:
            self.choice.Insert(
                self._chats[chat]['chat_uuid'],
                pos=self._chats_indexes.index(chat)
                )

        self.Layout()
        self.Update()


    def _on_select(self, event=None):
        chat_uuid=self._chats[self._chats_indexes[self.choice.GetSelection()]]['chat_uuid']
        chat=self._root._db.get_chat_messages(chat_uuid=chat_uuid)

        s='clean_chat();'
        self.html.RunScript(s)

        print(chat)
        for message in chat:
            if message['message_author']=='Sicken.ai':

                if 'reasoning_content' in message and message['reasoning_content']:
                    self.add_sickens_message(message=message['reasoning_content'], callafter=False)

                self.add_sickens_message(message=message['speech'], callafter=False)

            elif message['message_author']=='function':
                self.add_system_message(pformat(message['message']), esc=True, callafter=False)

            elif message['message_author']=='tool_calls':
                if 'reasoning_content' in message and message['reasoning_content']:
                    self.add_sickens_message(message=message['reasoning_content'], callafter=False)

                self.add_system_message(pformat(message['tool_calls']), esc=True, callafter=False)

            else:
                self.add_user_message(message['message'])

    def parse_command(self, cmd):
        cmd=cmd.replace('/','')

        cmd=cmd.split(' ')
        command=cmd[0]
        del cmd[0]
        args=cmd

        return [command, args]

            
    def add_user_message(self, message):
        message=message.replace('\\',"&#92;")
        message=message.replace('\n','\\n') 
        message=message.replace('\r','\\r') 
        message=escape(message)
        self.html.RunScript('add_user_message("{0}");'.format(message))

    def add_sickens_message(self, message, callafter=True):
        #message=message.replace('\r','')
        #message=message.replace('\t','')

        #message=self._markdown_escaper.escape(message)
        
        message=self._markdown(message)
        message=message.replace('\\',"&#92;")
        message=message.replace('\n','\\n') 
        message=message.replace('\r','\\r') 
        message=message.replace('"',"'")


        s='add_sickens_message("{0}");'.format(message)
        print(s)
        if callafter:
            wx.CallAfter(self.html.RunScript, s)
        else:
            self.html.RunScript(s)

    def add_system_message(self, message, esc=True, callafter=True):
        message=message.replace('\r','')
        message=message.replace('\t','')
        
        if esc:
            message=escape(message)
            message=message.replace('\\',"&#92;")

        message=message.replace('\n','<br>')

        s='add_system_message("{0}");'.format(message)
        print(s)
        if callafter:
            wx.CallAfter(self.html.RunScript, s)
        else:
            self.html.RunScript(s)



