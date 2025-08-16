#!/usr/bin/env python3
"""
run.py - safe Python launcher for Skynet Lite web app

Behaviors:
- checks for an existing listener on TCP/5000 and verifies its commandline
- attempts graceful shutdown (SIGTERM) then SIGKILL if needed
- prefers .venv/bin/python when present, falls back to system python3
- starts web/app.py in background, writes logs to logs/skynet_web.log and pid to /tmp/skynet_web.pid
"""

import os
import sys
import subprocess
import time
import signal


def find_listener_pid(port=5000):
    """Return PID listening on TCP port or None."""
    try:
        out = subprocess.check_output(['lsof', '-nP', f'-iTCP:{port}', '-sTCP:LISTEN', '-t'], stderr=subprocess.DEVNULL, text=True)
        pid = out.strip().splitlines()[0]
        return int(pid)
    except Exception:
        return None


def cmdline_contains(pid, needle):
    try:
        with open(f'/proc/{pid}/cmdline', 'rb') as f:
            data = f.read().replace(b'\x00', b' ').decode(errors='ignore')
            return needle in data
    except Exception:
        return False


def kill_pid(pid, timeout=5):
    try:
        os.kill(pid, signal.SIGTERM)
    except Exception:
        return False
    # wait for exit
    for _ in range(timeout):
        if not os.path.exists(f'/proc/{pid}'):
            return True
        time.sleep(1)
    try:
        os.kill(pid, signal.SIGKILL)
    except Exception:
        return False
    return not os.path.exists(f'/proc/{pid}')


def start_server(python_exe, log_path, pidfile):
    with open(log_path, 'ab') as logf:
        # Start in background
        proc = subprocess.Popen([python_exe, 'web/app.py'], stdout=logf, stderr=subprocess.STDOUT)
        with open(pidfile, 'w') as f:
            f.write(str(proc.pid))
        return proc.pid


def ensure_logs_dir():
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return os.path.join(logs_dir, 'skynet_web.log')


def main():
    print('run.py: safe launcher')

    # 1) check existing listener
    pid = find_listener_pid(5000)
    if pid:
        print(f'Found listener PID: {pid}')
        # only kill if it looks like our app (contains web/app.py or skynet-lite)
        if cmdline_contains(pid, 'web/app.py') or cmdline_contains(pid, 'skynet-lite') or cmdline_contains(pid, '.venv'):
            print(f'Killing PID {pid} (graceful then force)')
            ok = kill_pid(pid)
            if not ok:
                print(f'Failed to kill PID {pid} — aborting')
                sys.exit(1)
        else:
            print('PID commandline does not match web app; refusing to kill. Aborting.')
            sys.exit(1)
    else:
        print('No existing listener on port 5000')

    # 2) pick python executable
    python_exe = 'python3'
    venv_python = os.path.join(os.getcwd(), '.venv', 'bin', 'python')
    if os.path.isfile(venv_python) and os.access(venv_python, os.X_OK):
        python_exe = venv_python
        print('Using project venv python:', python_exe)
    else:
        print('Using system python3')

    # 3) start server
    # ensure logs dir
    log_path = ensure_logs_dir()
    pidfile = '/tmp/skynet_web.pid'
    print('Starting server — logs ->', log_path)
    newpid = start_server(python_exe, log_path, pidfile)
    print('Started server pid=', newpid)
    print('Tail of logs:')
    time.sleep(1)
    try:
        subprocess.check_call(['tail', '-n', '40', log_path])
    except Exception:
        pass


if __name__ == '__main__':
    main()
