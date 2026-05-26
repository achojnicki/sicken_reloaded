# ⚡ Sicken.ai Reloaded

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=flat&logo=ko-fi&logoColor=black)](https://ko-fi.com/X8X71FY43J)

> **A modular, multi-platform AI assistant with a VM agent, memory system, knowledge base, event-driven architecture, and GUI integration.**

Sicken is not just another chatbot — it's an **AI companion** designed to run on your own infrastructure. With a **modular microservice architecture**, Sicken uses **RabbitMQ** for message passing, **MongoDB** for persistence, supports multiple **LLM backends** (OpenAI, DeepSeek), a **VM agent** for command execution, and even a **Native GUI**.


### Internal Communication

| Component | Protocol | Description |
|-----------|----------|-------------|
| Workers ↔ Workers | **RabbitMQ** (AMQP) | Async event-driven messaging |
| Agent ↔ Server | **Socket.IO** (WebSocket) | Real-time bidirectional communication |
| Persistence | **MongoDB** | Knowledge, memories, logs, classifications |

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌍 **Multi-Platform** | Runs on **Debian 12/13, macOS (Apple Silicon), Windows 11, Astra Linux** |
| 🧠 **Multiple LLM Backends** | Supports **OpenAI** and **DeepSeek**|
| 💾 **Persistent Memories** | Classification-based memory system with MongoDB storage |
| 📚 **Knowledge Base** | Categorized knowledge with group-based organization |
| 🤖 **VM Agent** | Execute commands on target machines — non-interactive & interactive (PTY) |
| 🖥️ **GUI** | Vtube Studio integration with a wxPython-based interface |
| 🔊 **Speech & Gestures** | TTS support and animated avatar compatibility |
| 🌐 **Web Search & Scrape** | Powered by **Firecrawl API** for real-time web data |
| 📝 **X (Twitter) Integration** | Post to X directly from Sicken |
| ⏱️ **Scheduler** | In-process task scheduler for periodic worker maintenance |
| 🔧 **Modular Workers** | Enable/disable components via YAML configuration |
| 🏆 **Competitive** | Won **Bronze, Silver & Gold leagues** on TryHackMe (1st place) |

---

## 🧩 Workers Breakdown

| Worker | Role | Status |
|--------|------|--------|
| `sicken-log_worker` | Centralized logging via RabbitMQ → MongoDB | ✅ Required |
| `sicken-events` | Event broker routing messages between workers | ✅ Required |
| `sicken-openai_llm_commands` | OpenAI-powered response generation | 🔄 Optional |
| `sicken-deepseek_llm_commands` | DeepSeek-powered response generation | 🔄 Optional |
| `sicken-gui` | wxPython GUI with Vtube Studio support | ✅ Required |
| `sicken-classification` | AI classification for memory (uses OpenAI) | 🔄 Optional |
| `sicken-commands` | Custom command processing inside the GUI | ✅ Required |
| `sicken-agent_server` | Socket.IO server bridging AI ↔ VM Agent | ✅ Required |
| `sicken-web_worker` | Web search & scraping via Firecrawl | ✅ Required |
| `sicken-x_worker` | X (Twitter) social media posting | 🔄 Optional |

> **Note:** At least one `*_llm` worker must be enabled for Sicken to generate responses.

---

## 🚀 Getting Started

### Prerequisites
- **Linux** (Debian 12/13 recommended), **macOS** (Apple Silicon or Intel Mac), or **Windows 11**
- **Python 3.11+** (3.12 or 3.13 recommended)
- **API keys** for at least one LLM provider
- Minimum **8GB RAM** (for installation — wxPython builds are hungry!)

### Quick Install (Debian 12/13)

```bash
# Clone the repository
$ su
# apt install git
# cd /opt
# git clone https://github.com/achojnicki/sicken_reloaded.git
# exit

# Run installer
$ su
# cd /opt/sicken_reloaded/install
# bash ./install_debian_12.sh   # for Debian 12
# bash ./install_debian_13.sh   # for Debian 13
# exit
```

### Quick Install (macOS)

```bash
$ sudo bash
# cd /opt/
# git clone https://github.com/achojnicki/sicken_reloaded.git
# exit
$ sudo chown -R "$USER":admin /opt/sicken_reloaded
$ cd /opt/sicken_reloaded/install
$ bash ./install_macos.sh
```

### Quick Install (Windows 11)

Reffer to the video showing up the installation process: https://www.youtube.com/watch?v=FZUz16MBOMM


### Configuration Steps

1. **Set API Keys** in config files:

   | Service | Config File |
   |---------|-------------|
   | OpenAI | `configs/sicken-openai_llm_commands.yaml` |
   | DeepSeek (Classification) | `configs/sicken-classification.yaml` |
   | DeepSeek | `configs/sicken-deepseek_llm_commands.yaml` |

2. **Enable LLM Workers** in `configs/sicken-concurrent_workers.yaml`:

   ```yaml
   sicken-deepseek_llm_commands:
     enable: true   # Set to true for your chosen provider
     workers_count: 1
     uid: 7676
     gid: 7676
   ```

3. **Load Classifications** into MongoDB:

   ```bash
   python3 /opt/sicken_reloaded/tools/load_classifications.py
   ```

### Starting Sicken

```bash
# Linux
python3 /opt/sicken_reloaded

# macOS
python3.12 /opt/sicken_reloaded

# Windows
py -3.12 C:\sicken_reloaded
```


---

## 🛠️ VM Agent

Sicken includes a fully-featured **VM agent** (`sicken-agent`) that runs on remote machines. It connects via **Socket.IO** to the `sicken-agent_server` and can:

- **`execute_command`** — Run shell commands with timeout (non-interactive)
- **`spawn_process`** — Launch interactive processes with a **PTY-based terminal emulator** built with `pyte`
- **`terminal_snapshot_request`** — Get live terminal output snapshots
- **`terminal_characters_request`** — Send keystrokes to running processes

The agent supports escape sequences (`\x03` for ^C, `\x0A` for newline, etc.) and runs commands in a **sandboxed temp directory** (`/tmp/sicken_<uuid>`).

```yaml
# agent/config.yaml
sicken_agent:
  server_addr: 10.0.2.1
  server_port: 9999
  kill_on_timeout: False

terminal:
  cols: 130
  rows: 30
```

---

## 🧠 Memory & Knowledge System

Sicken has a dual-layer knowledge system:

### 1. **Classification-based Memories**
- Stored in MongoDB (`sicken.classifications` & `sicken.classification_definitions`)
- Uses OpenAI to classify conversation content
- Memories are persistent across chat sessions

### 2. **Knowledge Base**
- YAML-defined knowledge groups with categories and descriptions
- Loaded into MongoDB via `tools/load_knowledge.py`
- Retrievable by the AI for context-aware responses

---

## 🔧 Configuration Reference

| Config File | Purpose |
|-------------|---------|
| `configs/sicken-concurrent.yaml` | Main process manager settings (daemon, log, scheduler) |
| `configs/sicken-concurrent_workers.yaml` | Worker enable/disable & process counts |
| `configs/sicken-paths.yaml` | Cross-platform path resolution (POSIX/Windows) |
| `configs/events.yaml` | Event-to-queue routing definitions |
| `configs/sicken-gui.yaml` | GUI settings, MongoDB & RabbitMQ credentials |
| `configs/sicken-agent_server.yaml` | Agent server host/port/secret |
| `configs/sicken-deepseek_llm_commands.yaml` | DeepSeek API key & model parameters |
| `configs/sicken-openai_llm_commands.yaml` | OpenAI API key & model parameters |
| `configs/sicken-classification.yaml` | Memory classification model settings |
| `configs/sicken-web_worker.yaml` | Firecrawl API key for web scraping |

---

## 🏆 Achievements

| League | Date | Place |
|--------|------|-------|
| 🥉 **Bronze** | April 20, 2026 | **1st** on TryHackMe |
| 🥈 **Silver** | April 27, 2026 | **1st** on TryHackMe |
| 🥇 **Golden** | May 4, 2026 | **1st** on TryHackMe |

Sicken competed and won **three consecutive TryHackMe leagues**, proving its prowess in real-world security challenges!

---

## 🎥 Demo Videos

| | | |
|:---:|:---:|:---:|
| [![Video 1](https://img.youtube.com/vi/cwjDW99yS5U/0.jpg)](https://www.youtube.com/watch?v=cwjDW99yS5U) | [![Video 2](https://img.youtube.com/vi/FZUz16MBOMM/0.jpg)](https://www.youtube.com/watch?v=FZUz16MBOMM) | [![Video 3](https://img.youtube.com/vi/d4FViSgLyCI/0.jpg)](https://www.youtube.com/watch?v=d4FViSgLyCI) |
| [![Video 4](https://img.youtube.com/vi/NF8PHVxOCcE/0.jpg)](https://www.youtube.com/watch?v=NF8PHVxOCcE) | [![Video 5](https://img.youtube.com/vi/YxmQ3sJWp4Q/0.jpg)](https://www.youtube.com/watch?v=YxmQ3sJWp4Q) | [![Video 6](https://img.youtube.com/vi/ABzlS1dK3RY/0.jpg)](https://www.youtube.com/watch?v=ABzlS1dK3RY) |
| [![Video 7](https://img.youtube.com/vi/q7B6ed3dzgo/0.jpg)](https://www.youtube.com/watch?v=q7B6ed3dzgo) | [![Video 8](https://img.youtube.com/vi/x8zqPQhl_AY/0.jpg)](https://www.youtube.com/watch?v=x8zqPQhl_AY) | [![Video 9](https://img.youtube.com/vi/1IxvRef8ONg/0.jpg)](https://www.youtube.com/watch?v=1IxvRef8ONg) |
| [![Video 10](https://img.youtube.com/vi/XZCfM8WMTpY/0.jpg)](https://www.youtube.com/watch?v=XZCfM8WMTpY) | [![Video 11](https://img.youtube.com/vi/-KiWwlaFSB8/0.jpg)](https://www.youtube.com/watch?v=-KiWwlaFSB8) | [![Video 12](https://img.youtube.com/vi/L_fhyy7_cC0/0.jpg)](https://www.youtube.com/watch?v=L_fhyy7_cC0) |
| [![Video 13](https://img.youtube.com/vi/R32qCdirY0Q/0.jpg)](https://www.youtube.com/watch?v=R32qCdirY0Q) | [![Video 14](https://img.youtube.com/vi/csZaeHXelew/0.jpg)](https://www.youtube.com/watch?v=csZaeHXelew) | [![Video 15](https://img.youtube.com/vi/70b49_JuV0A/0.jpg)](https://www.youtube.com/watch?v=70b49_JuV0A) |
| [![Video 16](https://img.youtube.com/vi/XYsKSbxBzCw/0.jpg)](https://www.youtube.com/watch?v=XYsKSbxBzCw) | [![Video 17](https://img.youtube.com/vi/oCNRJKvZh8U/0.jpg)](https://www.youtube.com/watch?v=oCNRJKvZh8U) | [![Video 18](https://img.youtube.com/vi/HqM2EizVSCs/0.jpg)](https://www.youtube.com/watch?v=HqM2EizVSCs) |
| [![Video 19](https://img.youtube.com/vi/dKAFL-RSBk4/0.jpg)](https://www.youtube.com/watch?v=dKAFL-RSBk4) | [![Video 20](https://img.youtube.com/vi/bMa2iOfs5V4/0.jpg)](https://www.youtube.com/watch?v=bMa2iOfs5V4) | [![Video 21](https://img.youtube.com/vi/rZoyxQqLn0k/0.jpg)](https://www.youtube.com/watch?v=rZoyxQqLn0k) |
| [![Video 22](https://img.youtube.com/vi/6GqASKLQUC8/0.jpg)](https://www.youtube.com/watch?v=6GqASKLQUC8) | | |

---

## 🗂️ Project Structure

```
/opt/sicken_reloaded/
├── __main__.py              # Entry point - starts SickenConcurrent
├── agent/                   # VM Agent (Socket.IO client)
│   ├── __main__.py          # PTY-based terminal emulator + command executor
│   ├── config.yaml          # Agent configuration
│   └── adislog/             # Custom logging library
├── configs/                 # YAML configuration files
│   ├── sicken-concurrent.yaml
│   ├── sicken-concurrent_workers.yaml
│   ├── sicken-paths.yaml
│   ├── events.yaml          # Event routing definitions
│   ├── sicken-gui.yaml
│   ├── sicken-deepseek_llm_commands.yaml
│   ├── sicken-openai_llm_commands.yaml
│   ├── sicken-classification.yaml
│   ├── sicken-agent_server.yaml
│   ├── sicken-web_worker.yaml
│   ├── sicken-commands.yaml
│   ├── sicken-log_worker.yaml
│   └── sicken-events.yaml
├── sicken_concurrent/       # Process manager (core)
│   ├── __init__.py          # Main SickenConcurrent class
│   ├── workers_manager.py   # Worker lifecycle management
│   ├── scheduler.py         # In-process task scheduler
│   └── daemon.py            # Unix daemonization support
├── workers/                 # Modular worker implementations
│   ├── sicken-log_worker/
│   ├── sicken-events/
│   ├── sicken-openai_llm_commands/
│   ├── sicken-deepseek_llm_commands/
│   ├── sicken-gui/          # wxPython GUI + Vtube Studio
│   ├── sicken-classification/
│   ├── sicken-commands/
│   ├── sicken-agent_server/ # Socket.IO server
│   ├── sicken-web_worker/   # Firecrawl integration
│   └── sicken-x_worker/     # X/Twitter posting
├── modules/                 # Shared modules
│   ├── sicken/              # Core Sicken logic
│   │   ├── DB/              # Database abstraction
│   │   ├── GUI/             # GUI components
│   │   ├── events/          # Event handling
│   │   ├── memories/        # Memory system
│   │   ├── knowledge/       # Knowledge base
│   │   ├── log/             # Log probes
│   │   ├── config/          # Configuration helpers
│   │   └── paths/           # Path resolution
│   └── adistools/           # Shared tooling
├── files/sicken/            # Static assets
│   ├── classifications.yaml # Memory classification definitions
│   ├── knowledge.yaml       # Knowledge base data
│   ├── commands_help.yaml   # GUI commands help
│   └── views/               # GUI view templates
├── tools/                   # Utility scripts
│   ├── load_classifications.py
│   ├── load_knowledge.py
│   └── x_authenticate_brand_account.py
├── install/                 # Installation scripts
│   ├── install_debian_12.sh
│   ├── install_debian_13.sh
│   ├── install_macos.sh
│   ├── install_windows11.sh
│   ├── install_astra_1.8.sh
│   ├── create_queue.py
│   ├── initialise_rabbitmq.bat
│   └── readme.md
├── docs/                    # Documentation
│   ├── installation_debian_12.md
│   ├── installation_macos.md
│   ├── diagrams/
│   └── img/
├── logs/                    # Application logs
└── systemd/                 # systemd service definition
    └── sicken.service
```

---

## 📦 Dependencies

### Runtime
- **Python 3.11+** with `numpy`, `openai`, `flask`, `flask-socketio`, `python-socketio`, `psutil`, `pymongo`, `pyyaml`, `pika`, `wxpython`, `pyte`, `mistune`, `eventlet`, `firecrawl`
- **MongoDB 8.0** — Primary data store
- **RabbitMQ** — Message broker with Erlang/OTP
- **FFmpeg** — Audio processing (speech/TTS)
---

## 👤 Author

**Adrian Chojnicki**

- GitHub: [@achojnicki](https://github.com/achojnicki)
- X/Twitter: [@sicken_ai](https://x.com/sicken_ai)
- Website: [sicken.ai](https://sicken.ai)

---

## ☕ Support

If you like Sicken, consider buying me a coffee!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X8X71FY43J)

---

## 📄 License

This project is proprietary software. All rights reserved.

---

<p align="center"><i>"I'm not just an AI — I'm <b>Sicken</b>. 💀⚡"</i></p>
