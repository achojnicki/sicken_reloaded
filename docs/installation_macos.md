# Installing Sicken on MacOS

## Introduction

To install Sicken Reloaded on a MacOS machine you'll need:

* Intel Mac(Tested on Sonoma and Sequoia)
* Homebrew installed

## Installation

1. **Download and install Homebrew on your Mac:** [https://brew.sh/](https://brew.sh/)
2. **Clone Sicken's Git Repository to the /opt/sicken_reloaded directory**.

	```
 	sudo bash
	cd /opt/
	git clone https://github.com/achojnicki/sicken_reloaded.git
 	exit
 	sudo chown -R "$USER":admin /opt/sicken_reloaded
	```
3. **Run installation script**
	```
	cd /opt/sicken_reloaded/install
	bash ./install_macos.sh
	```
4. **Populate an OpenAI API key in the config files.**  

	Files to modify to populate API Keys:

	* OpenAI
		- `/opt/sicken_reloaded/configs/sicken-openai_llm_commands.yaml`
		- `/opt/sicken_reloaded/configs/sicken-classification.yaml`
	* DeepSeek
		- `/opt/sicken_reloaded/configs/sicken-deepseek_llm_commands.yaml`

	The modification requires changing the `api_key` property of the `openai` tree to your API key obtained from [https://platform.openai.com](https://platform.openai.com)

5. **Installation is complete. To start Sicken run in the terminal:**
	```
	python3.12 /opt/sicken_reloaded
	```