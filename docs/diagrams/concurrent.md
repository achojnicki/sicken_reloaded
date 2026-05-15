## 🧠 Sicken Concurrent - Architecture Block Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         /opt/sicken_reloaded/__main__.py                            │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  from modules.sicken.paths import Paths                                     │    │
│  │  from sicken_concurrent import SickenConcurrent                             │    │
│  │                                                                             │    │
│  │  paths = Paths()                    ◄── loads sicken-paths.yaml             │    │
│  │  sc = SickenConcurrent(paths)       ◄── passes path resolver                │    │
│  │  sc.start()                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                         │                                           │
└─────────────────────────────────────────┼───────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                     sicken_concurrent / SickenConcurrent Class                      │
│                                                                                     │
│  ┌──────────────────────────────────┐   ┌──────────────────────────────────────┐    │
│  │         CONFIG LOADING           │   │          LOGGING SETUP               │    │
│  │                                  │   │                                      │    │
│  │  ┌────────────────────────────┐  │   │  adislog(                            │    │
│  │  │ adisconfig(main_config)    │  │   │    project_name="sickens-concurrent" │    │
│  │  │  → sicken-concurrent.yaml  │  │   │    backends=[                        │    │
│  │  │    general:                │  │   │      terminal_colorful / table       │    │
│  │  │      daemonize: bool       │  │   │      file_plain                      │    │
│  │  │      start_workers: bool   │  │   │    ]                                 │    │
│  │  │    log: {debug, print_log} │  │   │    debug=config.log.debug            │    │
│  │  │    daemon: {pid_file}      │  │   │  )                                   │    │
│  │  │    scheduler: {interval}   │  │   └──────────────────────────────────────┘    │
│  │  └────────────────────────────┘  │                                               │
│  │  ┌────────────────────────────┐  │                                               │
│  │  │ adisconfig(workers_config) │  │                                               │
│  │  │  → sicken-concurrent_      │  │                                               │
│  │  │    workers.yaml            │  │                                               │
│  │  │    Lists all workers with: │  │                                               │
│  │  │    enable, workers_count,  │  │                                               │
│  │  │    uid, gid                │  │                                               │
│  │  └────────────────────────────┘  │                                               │
│  └──────────────────────────────────┘                                               │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                      COMPONENT INITIALIZATION                                │   │
│  │                                                                              │   │
│  │  ┌─────────────────────┐    ┌─────────────────────┐    ┌───────────────┐     │   │
│  │  │                     │    │                     │    │               │     │   │
│  │  │  ┌───────────────┐  │    │  ┌───────────────┐  │    │  Only if      │     │   │
│  │  │  │  Scheduler    │  │    │  │ Workers_man-  │  │    │  daemonize:   │     │   │
│  │  │  │  (scheduler)  │  │    │  │ ager          │  │    │  True         │     │   │
│  │  │  │               │  │    │  │ (workers_     │  │    │               │     │   │
│  │  │  │  Task loop    │◄─┼────┼──┤ manager.py)   │  │    │  ┌─────────┐  │     │   │
│  │  │  │  every 0.1s   │  │    │  │               │  │    │  │ Daemon  │  │     │   │
│  │  │  └───────────────┘  │    │  │  Manages      │  │    │  │(daemon) │  │     │   │
│  │  └─────────────────────┘    │  │  subprocesses │  │    │  │         │  │     │   │
│  │                             │  └───────────────┘  │    │  │ Double  │  │     │   │
│  │                             └─────────────────────┘    │  │ fork    │  │     │   │
│  │                                                        │  └─────────┘  │     │   │
│  │                                                        └───────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │      │
│  ┌──────────────────────────────────────────────────────────────────────────┐│      │
│  │               SIGNAL HANDLING (SIGTERM / SIGINT)                         ││      │
│  │  _signal_handler(sig, frame) → stop() → scheduler.stop()                 ││      │
│  │                                        → workers_manager.stop()          ││      │
│  │                                        → daemon.stop() (remove pidfile)  ││      │
│  └──────────────────────────────────────────────────────────────────────────┘│      │
└──────────────────────────────────────────────────────────────────────────────┼──────┘
                                                                               │
                                                                               ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                            Scheduler (scheduler.py)                                  │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐     │
│  │  _tasks = [                                                                 │     │
│  │    ['workers_manager', callback, interval_ms=100, last_exec=0]              │     │
│  │  ]                                                                          │     │
│  │                                                                             │     │
│  │  _loop():                                                                   │     │
│  │    while _active:                                                           │     │
│  │      for each task:                                                         │     │
│  │        if no interval:  → execute every loop iteration                      │     │
│  │        if interval:     → if time()*1000 - last >= interval → execute       │     │
│  │      sleep(config.scheduler.interval)  # default 0.1s                       │     │
│  └─────────────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                          Workers_manager (workers_manager.py)                            │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐     │
│  │                         WORKER REGISTRATION                                     │     │
│  │  load_workers():                                                                │     │
│  │    for each worker in config:                                                   │     │
│  │      read worker_dir/manifest.yaml (name, exec, script)                         │     │
│  │      _declare_worker(name, exec, script, uid, gid, workers_count, ...)          │     │
│  └─────────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐     │
│  │                       WORKER PROCESS LIFECYCLE                                  │     │
│  │                                                                                 │     │
│  │  _start_worker(name):                                                           │     │
│  │    uuid = str(uuid4())                                                          │     │
│  │    env = {PYTHONPATH, PYTHONUNBUFFERED, PYTHONIOENCODING}                       │     │
│  │    Popen([executable or python3, script.py],                                    │     │
│  │          preexec_fn=demote(uid, gid) if daemonized,                             │     │
│  │          stdout=PIPE, stderr=PIPE)                                              │     │
│  │    set_blocking(stdout, False)   ← non-blocking pipes                           │     │
│  │    set_blocking(stderr, False)                                                  │     │
│  │    store → _active_workers[]                                                    │     │
│  │                                                                                 │     │
│  │  _start_workers(name):  ← auto-respawn                                          │     │
│  │    while active_count < desired_count:                                          │     │
│  │      _start_worker(name)                                                        │     │
│  │                                                                                 │     │
│  └─────────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐     │
│  │                   STREAM READING (called by scheduler task)                     │     │
│  │                                                                                 │     │
│  │  task():   ← called every 100ms by scheduler                                    │     │
│  │    for each active worker:                                                      │     │
│  │      _read_process_stream(worker, 'stdout')  ← select() + read()                │     │
│  │      _read_process_stream(worker, 'stderr')  ← buffered → _log.info/error       │     │
│  │    _clear_zombies()                                                             │     │
│  │    for each worker type: _start_workers(name)  ← respawn if needed              │     │
│  │                                                                                 │     │
│  │  stop():                                                                        │     │
│  │    kill(pid, 15) for all workers                                                │     │
│  │    wait until all polled                                                        │     │
│  │    drain remaining stdout/stderr                                                │     │
│  └─────────────────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────────────────┘
                                        │                                                 
                                        ▼
                    ┌───────────────────────────────────────────────────┐
                    │            WORKER SUBPROCESSES                    │
                    │                                                   │
                    │  ┌──────────────────────────────┐                 │
                    │  │ sicken-deepseek_llm_commands │  ◄── LLM        │
                    │  │   → __main__.py              │                 │
                    │  └──────────────────────────────┘                 │
                    │  ┌──────────────────────────────┐                 │
                    │  │ sicken-gui                   │  ◄── GUI        │
                    │  │   → __main__.py              │                 │
                    │  └──────────────────────────────┘                 │
                    │  ┌──────────────────────────────┐                 │
                    │  │ sicken-agent_server          │  ◄── Server     │
                    │  │   → __main__.py              │                 │
                    │  └──────────────────────────────┘                 │
                    │  ┌──────────────────────────────┐                 │
                    │  │ sicken-web_worker            │  ◄── Web        │
                    │  │   → __main__.py              │                 │
                    │  └──────────────────────────────┘                 │
                    │  ┌──────────────────────────────┐                 │
                    │  │ sicken-commands              │  ◄── Commands   │
                    │  │   → __main__.py              │                 │
                    │  └──────────────────────────────┘                 │
                    │  ┌──────────────────────────────┐                 │
                    │  │ sicken-events                │  ◄── Events     │
                    │  │   → __main__.py              │                 │
                    │  └──────────────────────────────┘                 │
                    │  ┌──────────────────────────────┐                 │
                    │  │ sicken-log_worker            │  ◄── Logger     │
                    │  │   → __main__.py              │                 │
                    │  └──────────────────────────────┘                 │
                    │  ┌──────────────────────────────┐                 │
                    │  │ sicken-classification        │  ◄── Memory     │
                    │  │   → __main__.py              │                 │
                    │  └──────────────────────────────┘                 │
                    │  ┌──────────────────────────────┐                 │
                    │  │ sicken-openai_llm_commands   │  ◄── LLM Alt    │
                    │  │   → __main__.py              │                 │
                    │  └──────────────────────────────┘                 │
                    └───────────────────────────────────────────────────┘

```

---

## 🧩 Key Architecture Insights

| Component | Role |
|-----------|------|
| **SickenConcurrent** 🧠 | Mothership — orchestrates everything, owns lifecycle |
| **Scheduler** ⏱️ | Tick-based loop (100ms), runs the workers_manager task |
| **Workers_manager** 👷 | Spawns/respawns worker processes, reads their stdout/stderr, cleans zombies |
| **Daemon** 👻 | Double-fork daemonization + PID file to prevent multiple instances |
| **adisconfig** ⚙️ | Dot-accessible config loader from YAML |
| **adislog** 📝 | Multi-backend logger (colorful terminal + file) |
| **Paths** 📂 | Resolves cross-platform paths from `sicken-paths.yaml` |

### 🔁 The Main Loop Flow

```
Scheduler tick (0.1s)
    │
    ├── _read_process_stream (stdout)  → buffered → _log.info / _log.error
    ├── _read_process_stream (stderr)
    ├── _clear_zombies()               → remove dead workers from _active_workers
    └── _start_workers(name)           → auto-respawn if count < desired
```

### ⚡ Worker Isolation Design

Each worker is a **separate OS process** with:
- `PYTHONPATH` pointing to its own dir + shared `modules/`
- Non-blocking pipes for async stdout/stderr reading
- Optional `setuid/setgid` privilege drop when daemonized
- Auto-respawn on crash (the scheduler keeps topping up the count)

