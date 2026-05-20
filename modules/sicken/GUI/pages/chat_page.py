from html import escape
from pathlib import Path
from pprint import pformat, pprint
import wx
import wx.html2
import wx.stc
import mistune


class Chat_Page(wx.Panel):
    def __init__(self, root, parent, frame):
        self._root=root
        self._parent=parent
        self._frame=frame
        wx.Panel.__init__(self, parent)


        self._view_path=Path(self._root._paths('VIEWS_DIR')).joinpath('gui').joinpath('chat.view')

        self.chat_template=open(self._view_path,'r').read()
        self.sizer=wx.BoxSizer(wx.VERTICAL)        

        self.html=wx.html2.WebView.New(self)
        self.html.SetPage(self.chat_template,"")
        self.html.EnableContextMenu(self._root._config.chat.allow_context_menu)
        self.html.EnableAccessToDevTools(self._root._config.chat.allow_inspect)

        self.textctrl=wx.TextCtrl(self,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.TE_PROCESS_ENTER
            )

        self._cleanup_button=wx.Button(self, label="remove last\ntool calls")
        self._autoscroll_checkbox=wx.CheckBox(self, label='Autoscroll')
        self._autoscroll_checkbox.SetValue(True)


        self._bottom_bar_sizer=wx.BoxSizer(wx.HORIZONTAL)
        self._bottom_bar_sizer.Add(self._autoscroll_checkbox, 0, wx.EXPAND)
        self._bottom_bar_sizer.AddStretchSpacer(1)
        self._bottom_bar_sizer.Add(self._cleanup_button, 0, wx.EXPAND)


        self.sizer.Add(self.html, 1, wx.EXPAND)
        self.sizer.Add(self._bottom_bar_sizer, 0, wx.EXPAND)
        self.sizer.Add(self.textctrl, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.SetBackgroundColour((32,34,39))
    
        self.Bind(wx.EVT_TEXT_ENTER, self.enter_event, self.textctrl)
        self.Bind(wx.EVT_CHECKBOX, self._on_autoscroll_toggle, self._autoscroll_checkbox)
        self.Bind(wx.EVT_BUTTON, self._on_remove_tool_calls, self._cleanup_button)
        

        self._markdown=mistune.create_markdown(plugins=['table','url','task_lists','def_list','mark','superscript','subscript','strikethrough'])
        self.Show(True)



    def _on_remove_tool_calls(self, event=None):
        chat_uuid=self._root._chat_uuid
        chat=self._root._db.get_chat_messages(chat_uuid=chat_uuid, del_id=False)

        if chat[-1]['message_author'] =='tool_calls':
            self._root._db.remove_chat_message(_id=chat[-1]['_id'])

        self.resume(chat_uuid=chat_uuid)



    def _on_autoscroll_toggle(self, event=None):
        state=str(self._autoscroll_checkbox.GetValue()).lower()
        self.html.RunScript(f"autoscroll={state};""")

    def parse_command(self, cmd):
        cmd=cmd.replace('/','')

        cmd=cmd.split(' ')
        command=cmd[0]
        del cmd[0]
        args=cmd

        return [command, args]

    def resume(self, chat_uuid):
        chat=self._root._db.get_chat_messages(chat_uuid=chat_uuid)

        s='clean_chat();'
        self.html.RunScript(s)

        self._root._chat_uuid=chat_uuid

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

        self._parent.SetSelection(0)

    def enter_event(self, event):
        msg=self.textctrl.GetValue()
        if msg!='':
            if not self._root._chat_uuid:
                self._root._set_chat_uuid()

            self.textctrl.SetValue("")
            self.add_user_message(msg)

            if msg[0]!='/':
                self._root._events.event(
                        event_name="message_entered",
                        event_data={
                            "chat_uuid": self._root._chat_uuid,
                            "message_author": self._root._config.user.username,
                            "message_source": "sicken-gui",
                            "message": msg 
                            }
                        )
            else:
                cmd, args=self.parse_command(msg)
                self._root._events.event(
                        event_name="command_entered",
                        event_data={
                            "chat_uuid": self._root._chat_uuid,
                            "message_author": self._root._config.user.username,
                            "message_source": "sicken-gui",
                            "cmd": cmd,
                            "args": args
                          }
                        )
            
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




