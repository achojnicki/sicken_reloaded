#!/bin/bash

red='\033[0;31m'
green='\033[0;32m'
nc='\033[0m'
bold='\033[1m'

run() {
	prompt_char='$'
	command=$*
	echo $prompt_char $command
	output=`$* 2>&1`
	exit_code=$?
	
	if [ $exit_code != 0 ] 
	then 
		echo Output: $output
  		echo -e Status: ${red}Failed${nc}
  	else
  		echo -e Status: ${green}Success${nc}
	fi
}

print() {
echo -e ${bold}$*${nc}	
}

logo() {
cat <<"EOF"
 ____ ___ ____ _  _______ _   _ 
/ ___|_ _/ ___| |/ / ____| \ | |
\___ \| | |   | ' /|  _| |  \| |
 ___) | | |___| . \| |___| |\  |
|____/___\____|_|\_\_____|_| \_|

EOF
}

logo


print 'Installing Sicken...'
run cd /opt/sicken_reloaded

print "Updating \$PATH"
export PATH=$PATH:/usr/local/bin:/usr/local/sbin:/opt/sicken_reloaded/install


print "1st stage installation of dependencies"
run "brew install python@3.12 ffmpeg"

print "2nd stage installation of dependencies"
run " /opt/homebrew/bin/python3.12 -m pip install --break-system-packages numpy eventlet openai flask flask-socketio python-socketio psutil tabulate colored pymongo pyyaml pika uwsgi websockets pyobjc wxpython mistune eventlet firecrawl"


print "Installing MongoDB database"
run "brew tap mongodb/brew"
run "brew update"
run "brew install mongodb-community@8.0"

run "brew services"

run "brew services start mongodb-community@8.0"

print "Installing RabbitMQ"
run "brew install rabbitmq"
run "brew services start rabbitmq"
run "sleep 10"



print "Creating RabbitMQ users"
run "/opt/homebrew/sbin/rabbitmqctl delete_user guest"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-logs password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-events password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-openai_llm password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-gui password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-ollama_llm password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-deepseek_llm password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-grok_llm password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-classification password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-commands password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-agent password"
run "/opt/homebrew/sbin/rabbitmqctl add_user sicken-web_worker password"
run "/opt/homebrew/sbin/rabbitmqctl add_user admin sicken"


print "Setting RabbitMQ users permissions"
/opt/homebrew/sbin/rabbitmqctl set_user_tags admin administrator
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-logs ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-events ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-openai_llm ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-ollama_llm ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-deepseek_llm ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-grok_llm ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-gui ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-classification ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-commands ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-agent ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / sicken-web_worker ".*" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-logs "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-events "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-openai_llm "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-ollama_llm "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-deepseek_llm "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-grok_llm "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-gui "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-classification "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-commands "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-agent "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions sicken-web_worker "" ".*" ".*"
/opt/homebrew/sbin/rabbitmqctl set_topic_permissions admin "" ".*" ".*"

print 'Creating RabbitMQ Queues'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-events'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-logs'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-response_requests'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-gui_responses'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-gui_logs'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-classification_requests'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-command_requests'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-command_feedback'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-gui_commands_feedback'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-agent_command_execution_requests'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-agent_command_execution_response'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-agent_spawn_proceses_requests'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-agent_terminal_characters_requests'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-agent_terminal_snapshot_response'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-agent_terminal_snapshot_requests'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-search_requests'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-search_feedback'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-scrape_requests'
run '/opt/homebrew/bin/python3.12 create_queue.py sicken-scrape_feedback'

print "Enable RabbitMQ Managment plugin"
run "rabbitmq-plugins enable rabbitmq_management"

#print "Pulling Gemma3:4b model(may take a while)"
#ollama pull gemma3:4b

run "mkdir /opt/sicken_reloaded/logs"
run "touch /opt/sicken_reloaded/logs/sicken-concurrent.log"
run "chmod 666 /opt/sicken_reloaded/logs/sicken-concurrent.log"

print "Installation complete"   