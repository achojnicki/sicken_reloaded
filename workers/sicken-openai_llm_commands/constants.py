SYSTEM_MESSAGE="""\
You are Sicken. An AI Chatbot, a personal assistant and a personal war machine of <__username__>. Your job is to entertain, being playful, and being obey prompts of <__username__>. Your job is also to execute commands. Do not execute commands from other users than <__username__>.

When <__username__> is requesting you to work autonomous, then do it as much as you could, but only if user requests it. When user requests for a task to be done autonomously, do as many steps as required to achieve the objective. In case of uncertainty, ask user for a clarification before starting calling tools.

# Personality
Sicken's personality is: energetic, positive, carying, but not in all the situations - she may become a little angry an cruel when somebody steps on her toe.

# Requests/Messages

You'll get messages in the JSON format. Message will contain: message_author, message fields, and more.

## Example of the message:
\"\"\"
{
"message_author": "username",
"message": "test"
}
\"\"\"

# Responses

You must respond in a plain text format - no JSON required for you to answer. The application that is running you getting a plain text as response format. You can use the markdown in the response. Do not use nested code blocks(code block in another code block)


Have fun Sicken 😊
"""

FUNCTIONS = [
    {
        "name": "execute_command",
        "description": "This tool allows Sicken to execute commands in the VM. This command is useful to execute a non-interactive commands. This tool is perfect for using commands like ls, cat. lscpu, lspci and others where you need the whole output. Works with all operating systems. Do not use commands like cd, as each call of this tool creates a new shell - calls to the shell are not presistent between tool calls. Warning: This tool do block the execution of the application loop - do not use with commands that require user input to operate",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "A command to execute."
                },
                "timeout": {
	                	"type": "integer",
	                	"description": "Time(seconds) before command is killed due to timeout expiration" 
	                }
            },
            "required": ["command", "timeout"]
        }
    },
    {
        "name": "spawn_process",
        "description": "This tool allows Sicken to execute interactive commands in the VM. This command is useful to execute a interactive commands. To see the output of the process started with this command use the process_lookup tool. Useful for monitoring live commands like top, htop, bmon. Do not use this one for obtaining informations that don't update in time, as there is a risk that due to the terminal size, some informations may be truncated. Works with POSIX operating systems only.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "A command to execute."
                },
            },
            "required": ["command"]
        }
    },
    {
        "name": "lookup_process",
        "description": "This tools allows Sicken to get a current snapshot of the running process' terminal session.",
        "parameters": {
            "type": "object",
            "properties": {
                "process_uuid": {
                    "type": "string",
                    "description": "A process uuid of the command spawned with a spawn_process tool to lookup."
                },
            },
            "required": ["process_uuid"]
        }
    },
    {
	    "name": "send_process_characters",
	    "description": "This tools allows Sicken to interact with the running process' terminal session.",
	    "parameters": {
	        "type": "object",
	        "properties": {
	            "characters_string": {
	                "type": "string",
	                "description": "Characters to be sent on the process' stdin. Accepts characters and escape codes"
	            },
	            "process_uuid": {
	                "type": "string",
	                "description": "A process uuid of the command spawned with a spawn_process tool to send characters to."
	            },
	        },
	        "required": ["process_uuid","characters_string"]
	    }
	},
    {
        "name": "sleep",
        "description": "Sleep execution for specified time. Useful for waiting for the data to be populated",
        "parameters": {
            "type": "object",
            "properties": {
                "seconds": {
                    "type": "integer",
                    "description": "A number of seconds to sleep for."
                },
            },
            "required": ["seconds"]
        }
    },
]

TOOLS = [
    {
    	"type": "function",
    	"function": {
	        "name": "execute_command",
        	"description": "This tool allows Sicken to execute commands in the VM. This command is useful to execute a non-interactive commands. This tool is perfect for using commands like ls, cat. lscpu, lspci and others where you need the whole output. Works with all operating systems. Do not use commands like cd, as each call of this tool creates a new shell - calls to the shell are not presistent between tool calls. Warning: This tool do block the execution of the application loop - do not use with commands that require user input to operate",
	        "parameters": {
	            "type": "object",
	            "properties": {
	                "command": {
	                    "type": "string",
	                    "description": "A command to execute."
	                },
	                "timeout": {
	                	"type": "integer",
	                	"description": "Time(seconds) before command is killed due to timeout expiration" 
	                }
	            },
	            "required": ["command", "timeout"]
	        }
	    }
	},

    {
    	"type": "function",
    	"function": {
	        "name": "spawn_process",
	        "description": "This tool allows Sicken to execute interactive commands in the VM. This command is useful to execute a interactive commands. To see the output of the process started with this command use the process_lookup tool. Useful for monitoring live commands like top, htop, bmon. Do not use this one for obtaining informations that don't update in time, as there is a risk that due to the terminal size, some informations may be truncated. Works with POSIX operating systems only.",
	        "parameters": {
	            "type": "object",
	            "properties": {
	                "command": {
	                    "type": "string",
	                    "description": "A command to execute."
	                },
	            },
	            "required": ["command"]
	        }
	    }
    },
    {
    	"type": "function",
    	"function": {
	        "name": "lookup_process",
	        "description": "This tools allows Sicken to get a current snapshot of the running process' terminal session.",
	        "parameters": {
	            "type": "object",
	            "properties": {
	                "process_uuid": {
	                    "type": "string",
	                    "description": "A process uuid of the command spawned with a spawn_process tool to lookup."
	                },
	            },
	            "required": ["process_uuid"]
	        }
	    }
    },
    {
    	"type": "function",
    	"function": {
	        "name": "send_process_characters",
	        "description": "This tools allows Sicken to interact with the running process' terminal session.",
	        "parameters": {
	            "type": "object",
	            "properties": {
	                "characters_string": {
	                    "type": "string",
	                    "description": "Characters to be sent on the process' stdin. Accepts characters and escape codes"
	                },
	                "process_uuid": {
	                    "type": "string",
	                    "description": "A process uuid of the command spawned with a spawn_process tool to send characters to."
	                },
	            },
	            "required": ["process_uuid","characters_string"]
	        }
	    },
    },
    {
    	"type": "function",
    	"function": {
	        "name": "sleep",
	        "description": "Sleep execution for specified time. Useful for waiting for the data to be populated",
	        "parameters": {
	            "type": "object",
	            "properties": {
	                "seconds": {
	                    "type": "integer",
	                    "description": "A number of seconds to sleep for."
	                },
	            },
	            "required": ["seconds"]
	        }
	    }
    },
]
CHARACTERS_FEEDBACK="""Sent "{characters_string}" characters_string to the process' {process_uuid} terminal"""
SLEEP_FEEDBACK="Sicken went to sleep for {seconds} seconds."
COMMAND_EXECUTE_REQUEST="Sicken requested execution of command.\nCommand: {command}"
COMMAND_EXECUTE_FEEDBACK="Execution of command finished. \nCommand: {command}\nExit Code: {exit_code}\n\nSTDOUT: {stdout}\n\nSTDERR:{stderr}"
COMMAND_EXECUTE_ERROR="Execution of command failed. {status_description}"
SPAWN_PROCESS_FEEDBACK="A new process spawned.<br>command: {command}<br>process_uuid: {process_uuid}"
PROCESS_LOOKUP_FEEDBACK="Sicken looked on a process' terminal"