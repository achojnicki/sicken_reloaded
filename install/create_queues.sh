rabbitmqctl delete_user guest
rabbitmqctl add_user sicken-logs password
rabbitmqctl add_user sicken-events password
rabbitmqctl add_user sicken-openai_llm password
rabbitmqctl add_user sicken-speech_generator password
rabbitmqctl add_user sicken-text_input password
rabbitmqctl add_user sicken-microphone_input password
rabbitmqctl add_user sicken-vtube_plugin password
rabbitmqctl add_user sicken-twitch_chat password
rabbitmqctl add_user sicken-gui password
rabbitmqctl add_user sicken-ollama_llm password
rabbitmqctl add_user sicken-deepseek_llm password
rabbitmqctl add_user sicken-grok_llm password
rabbitmqctl add_user sicken-classification password
rabbitmqctl add_user sicken-chat_viewer password
rabbitmqctl add_user sicken-bottom_bar password
rabbitmqctl add_user sicken-tiktok_chat password
rabbitmqctl add_user sicken-commands password


rabbitmqctl add_user admin sicken


rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / sicken-logs ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-events ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-openai_llm ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-speech_generator ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-text_input ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-microphone_input ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-vtube_plugin ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-ollama_llm ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-deepseek_llm ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-grok_llm ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-twitch_chat ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-gui ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-classification ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-chat_viewer ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-bottom_bar ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-tiktok_chat ".*" ".*" ".*
rabbitmqctl set_permissions -p / sicken-commands ".*" ".*" ".*
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*

rabbitmqctl set_topic_permissions sicken-logs "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-events "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-openai_llm "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-speech_generator "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-text_input "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-microphone_input "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-vtube_plugin "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-ollama_llm "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-deepseek_llm "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-grok_llm "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-twitch_chat "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-gui "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-classification "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-chat_viewer "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-bottom_bar "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-tiktok_chat "" ".*" ".*
rabbitmqctl set_topic_permissions sicken-commands "" ".*" ".*
rabbitmqctl set_topic_permissions admin "" ".*" ".*

python3.11 ./create_queue.py sicken-events
python3.11 ./create_queue.py sicken-logs
python3.11 ./create_queue.py sicken-response_requests
python3.11 ./create_queue.py sicken-speech_requests
python3.11 ./create_queue.py sicken-vtube_plugin_speech_generation_finished
python3.11 ./create_queue.py sicken-vtube_plugin_speech_requests
python3.11 ./create_queue.py sicken-standalone_speech_generation_finished
python3.11 ./create_queue.py sicken-standalone_speech_requests
python3.11 ./create_queue.py sicken-model_introduction
python3.11 ./create_queue.py sicken-model_introduction_requests
python3.11 ./create_queue.py sicken-gui_responses
python3.11 ./create_queue.py sicken-twitch_responses
python3.11 ./create_queue.py sicken-gui_logs
python3.11 ./create_queue.py sicken-webchat_requests
python3.11 ./create_queue.py sicken-webchat_responses
python3.11 ./create_queue.py sicken-subtitles
python3.11 ./create_queue.py sicken-classification_requests
python3.11 ./create_queue.py sicken-command_requests
python3.11 ./create_queue.py sicken-command_feedback
python3.11 ./create_queue.py sicken-gui_commands_feedback
