## 🧠 Sicken-Agent - Architecture Block Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          /opt/sicken_reloaded/agent                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         __main__.py                                  │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │                     sicken_agent Class                          │ │   │
│  │  │                                                                 │ │   │
│  │  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐    │ │   │
│  │  │  │   Config    │  │    Logger    │  │   SocketIO Client    │    │ │   │
│  │  │  │ (adisconfig)│  │  (adislog)   │  │  (python-socketio)   │    │ │   │
│  │  │  └──────┬──────┘  └──────┬───────┘  └──────────┬───────────┘    │ │   │
│  │  │         │                │                     │                │ │   │
│  │  │         ▼                ▼                     ▼                │ │   │
│  │  │  ┌─────────────────────────────────────────────────────────┐    │ │   │
│  │  │  │              Session State                              │    │ │   │
│  │  │  │  ┌─ _active: bool                                       │    │ │   │
│  │  │  │  └─ _processes: dict[process_uuid → ProcessEntry]       │    │ │   │
│  │  │  │     └─ Protected by _processes_lock (threading.Lock)    │    │ │   │
│  │  │  │  ┌─ _session_uuid: str                                  │    │ │   │
│  │  │  │  └─ Temp dir: /tmp/sicken_{uuid}                        │    │ │   │
│  │  │  └─────────────────────────────────────────────────────────┘    │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │              Event Handlers (SocketIO callbacks)                │ │   │
│  │  │                                                                 │ │   │
│  │  │  ┌─────────────────────┐                                        │ │   │
│  │  │  │ command_request     │──→ _execute_command(data)              │ │   │
│  │  │  │                     │    ├─ Popen(cmd, shell=True)           │ │   │
│  │  │  │                     │    ├─ communicate(timeout)             │ │   │
│  │  │  │                     │    ├─ On timeout: kill child procs     │ │   │
│  │  │  │                     │    └─ Emit: command_response           │ │   │
│  │  │  └─────────────────────┘                                        │ │   │
│  │  │  ┌─────────────────────┐                                        │ │   │
│  │  │  │ spawn_process_      │──→ spawn_process(data)                 │ │   │
│  │  │  │ request             │    └─ _spawn_process(uuid, cmd)        │ │   │
│  │  │  │                     │       ├─ pty.openpty() → master/slave  │ │   │
│  │  │  │                     │       ├─ Popen with PTY as stdio       │ │   │
│  │  │  │                     │       ├─ pyte.Screen + pyte.Stream     │ │   │
│  │  │  │                     │       └─ Store in _processes dict      │ │   │
│  │  │  └─────────────────────┘                                        │ │   │
│  │  │  ┌─────────────────────┐                                        │ │   │
│  │  │  │ terminal_snapshot_  │──→ process_terminal_snapshot_request() │ │   │
│  │  │  │ request             │    ├─ _screen_snapshot(uuid)           │ │   │
│  │  │  │                     │    └─ Emit: terminal_snapshot_response │ │   │
│  │  │  └─────────────────────┘                                        │ │   │
│  │  │  ┌─────────────────────┐                                        │ │   │
│  │  │  │ terminal_characters │──→ terminal_characters(data)           │ │   │
│  │  │  │ _request            │    └─ _send_string(uuid, str)          │ │   │
│  │  │  │                     │       ├─ Replace escape sequences      │ │   │
│  │  │  │                     │       └─ write(pty_master_fd, bytes)   │ │   │
│  │  │  └─────────────────────┘                                        │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │               Background Threads                                │ │   │
│  │  │                                                                 │ │   │
│  │  │  ┌──────────────────────────────────────────────────────────┐   │ │   │
│  │  │  │  Terminal Updater Thread (daemon)                        │   │ │   │
│  │  │  │  while True:                                             │   │ │   │
│  │  │  │    for each process:                                     │   │ │   │
│  │  │  │      select([pty_fd]) → if readable:                     │   │ │   │
│  │  │  │        data = read(pty_fd, 4096)                         │   │ │   │
│  │  │  │        stream.feed(data) → updates pyte.Screen           │   │ │   │
│  │  │  │      if process exited → mark status="Exited"            │   │ │   │
│  │  │  │    sleep(0.01)                                           │   │ │   │
│  │  │  └──────────────────────────────────────────────────────────┘   │ │   │
│  │  │                                                                 │ │   │
│  │  │  ┌──────────────────────────────────────────────────────────┐   │ │   │
│  │  │  │  Ping Thread (daemon)                                    │   │ │   │
│  │  │  │  while _active:                                          │   │ │   │
│  │  │  │    emit('agent_ping')                                    │   │ │   │
│  │  │  │    if fails → kill(getpid(), SIGTERM)                    │   │ │   │
│  │  │  │    sleep(1)                                              │   │ │   │
│  │  │  └──────────────────────────────────────────────────────────┘   │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │                    Lifecycle (start())                          │ │   │
│  │  │  1. terminal_updater_thread()  → starts terminal updater        │ │   │
│  │  │  2. connect()                 → WebSocket to server             │ │   │
│  │  │  3. ping()                    → starts ping thread              │ │   │
│  │  │  4. socketio.wait()           → blocks, handles events          │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────┐   ┌──────────────────────────────────────┐    │
│  │     adisconfig Module    │   │        adislog Module                │    │
│  │  ┌────────────────────┐  │   │  ┌────────────────────────────────┐  │    │
│  │  │ AttrDict (dict)    │  │   │  │ adislog_methods:               │  │    │
│  │  │  - dot access cfg  │  │   │  │  .debug(), .info(), .warning() │  │    │
│  │  │  - YAML loading    │  │   │  │  .error(), .fatal(), .success()│  │    │
│  │  └────────────────────┘  │   │  │  .exception()                  │  │    │
│  │  Loads: config.yaml      │   │  │                                │  │    │
│  │  ┌─ sicken_agent:        │   │  │  inspect.py → caller info      │  │    │
│  │  │  server_addr: 10.0.2.1│   │  │  process.py → PID, PPID, CWD   │  │    │
│  │  │  server_port: 9999    │   │  │  traceback.py → exc details    │  │    │
│  │  │  kill_on_timeout: F   │   │  │  constants.py → levels/colors  │  │    │
│  │  └─ terminal:            │   │  │                                │  │    │
│  │     cols: 130, rows: 30  │   │  │  Backends:                     │  │    │
│  │                          │   │  │  └─ terminal_colorful.py       │  │    │
│  └──────────────────────────┘   │  │     (used by agent)            │  │    │
│                                 │  └────────────────────────────────┘  │    │
│                                 └──────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                       External Dependencies                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐            │   │
│  │  │ socketio │  │  pyte    │  │ psutil    │  │   pty     │            │   │
│  │  │ (client) │  │(term emu)│  │(procs mgt)│  │(native OS)│            │   │
│  │  └──────────┘  └──────────┘  └───────────┘  └───────────┘            │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Summary

```
   Server (10.0.2.1:9999)
         │
         │ WebSocket (SocketIO)
         │
         ▼
┌────────────────────┐
│  sicken_agent      │
│                    │
│  ◄── command_request ──► Popen(cmd) ──► command_response
│  ◄── spawn_process_request ──► PTY + pyte ──► stored in _processes
│  ◄── terminal_snapshot_request ──► reads pyte.Screen.display ──► snapshot_response
│  ◄── terminal_characters_request ──► write(pty_fd, characters)
│  ──► agent_ping (every 1s, heartbeat)
│  ──► agent_connect (on connection)
│                    │
│  Background:       │
│  ──► Terminal Updater Thread (select() loop, feeds pyte)
│  ──► Ping Thread (heartbeat)
└────────────────────┘
```

---

## 🧩 Key Design Highlights

| Component | Purpose |
|-----------|---------|
| **Popen (non-interactive)** | Runs one-shot commands with timeout, captures stdout/stderr |
| **PTY + pyte (interactive)** | Spawns persistent shell processes with virtual terminal emulation |
| **SocketIO Events** | 4 event handlers for command execution, process spawning, terminal reading/writing |
| **Config (YAML)** | Server address, terminal dimensions, timeout kill behavior |
| **Threading** | 2 daemon threads: terminal updater & ping, with Lock for process dict safety |
| **Session Isolation** | Each agent run gets a UUID-based temp directory at `/tmp/sicken_{uuid}` |
