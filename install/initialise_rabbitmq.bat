@echo off

cd c:\sicken\install

echo "Updating \$PATH"
set PATH=%PATH%;C:\Program Files\RabbitMQ Server\rabbitmq_server-4.1.0\sbin

echo "Creating RabbitMQ users"
call rabbitmqctl.bat delete_user guest
call rabbitmqctl.bat add_user sicken-logs password
call rabbitmqctl.bat add_user sicken-events password
call rabbitmqctl.bat add_user sicken-openai_llm password
call rabbitmqctl.bat add_user sicken-gui password
call rabbitmqctl.bat add_user sicken-ollama_llm password
call rabbitmqctl.bat add_user sicken-deepseek_llm password
call rabbitmqctl.bat add_user sicken-grok_llm password
call rabbitmqctl.bat add_user sicken-classification password
call rabbitmqctl.bat add_user sicken-commands password
call rabbitmqctl.bat add_user admin sicken



echo "Setting RabbitMQ users permissions"
call rabbitmqctl.bat set_user_tags admin administrator
call rabbitmqctl.bat set_permissions -p / sicken-logs ".*" ".*" ".*"
call rabbitmqctl.bat set_permissions -p / sicken-events ".*" ".*" ".*"
call rabbitmqctl.bat set_permissions -p / sicken-openai_llm ".*" ".*" ".*"
call rabbitmqctl.bat set_permissions -p / sicken-ollama_llm ".*" ".*" ".*"
call rabbitmqctl.bat set_permissions -p / sicken-deepseek_llm ".*" ".*" ".*"
call rabbitmqctl.bat set_permissions -p / sicken-grok_llm ".*" ".*" ".*"
call rabbitmqctl.bat set_permissions -p / sicken-gui ".*" ".*" ".*"
call rabbitmqctl.bat set_permissions -p / sicken-classification ".*" ".*" ".*"
call rabbitmqctl.bat set_permissions -p / sicken-commands ".*" ".*" ".*"
call rabbitmqctl.bat set_permissions -p / admin ".*" ".*" ".*"

call rabbitmqctl.bat set_topic_permissions sicken-logs "" ".*" ".*"
call rabbitmqctl.bat set_topic_permissions sicken-events "" ".*" ".*"
call rabbitmqctl.bat set_topic_permissions sicken-openai_llm "" ".*" ".*"
call rabbitmqctl.bat set_topic_permissions sicken-ollama_llm "" ".*" ".*"
call rabbitmqctl.bat set_topic_permissions sicken-deepseek_llm "" ".*" ".*"
call rabbitmqctl.bat set_topic_permissions sicken-grok_llm "" ".*" ".*"
call rabbitmqctl.bat set_topic_permissions sicken-gui "" ".*" ".*"
call rabbitmqctl.bat set_topic_permissions sicken-classification "" ".*" ".*"
call rabbitmqctl.bat set_topic_permissions sicken-commands "" ".*" ".*"
call rabbitmqctl.bat set_topic_permissions admin "" ".*" ".*"

echo 'Creating RabbitMQ Queues'
py ./create_queue.py sicken-events
py ./create_queue.py sicken-logs
py ./create_queue.py sicken-response_requests
py ./create_queue.py sicken-gui_responses
py ./create_queue.py sicken-gui_logs
py ./create_queue.py sicken-classification_requests
py ./create_queue.py sicken-command_requests
py ./create_queue.py sicken-command_feedback
py ./create_queue.py sicken-gui_commands_feedback
py ./create_queue.py sicken-agent_command_execution_requests
py ./create_queue.py sicken-agent_command_execution_response
py ./create_queue.py sicken-agent_spawn_proceses_requests
py ./create_queue.py sicken-agent_terminal_characters_requests
py ./create_queue.py sicken-agent_terminal_snapshot_response

echo 'Enable RabbitMQ Managment plugin'
call rabbitmq-plugins.bat enable rabbitmq_management


pause
