#!/usr/bin/env python3
"""
stop.py - graceful stopper for Skynet Lite web app started by run.py/run.sh

Behavior:
- reads pid from /tmp/skynet_web.pid (if present)
- verifies the PID's cmdline looks like our web app
- sends SIGTERM and waits up to N seconds for exit
- falls back to SIGKILL if necessary
- removes pidfile on success
"""

import os
import sys
import time
import signal
import subprocess
import argparse

PIDFILE = '/tmp/skynet_web.pid'


def read_pidfile():
    try:
        with open(PIDFILE, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return None


def proc_exists(pid):
    return os.path.exists(f'/proc/{pid}')


def cmdline_contains(pid, needle):
    try:
        with open(f'/proc/{pid}/cmdline', 'rb') as f:
            data = f.read().replace(b'\x00', b' ').decode(errors='ignore')
            return needle in data
    except Exception:
        return False


def try_terminate(pid, timeout=10):
    try:
        print(f'Sending SIGTERM to {pid}...')
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        print('Process not running')
        return True
    except PermissionError:
        print('Permission denied while trying to signal process')
        return False
    except Exception as e:
        print('Error sending SIGTERM:', e)
        return False

    # wait for process to exit
    for i in range(timeout):
        if not proc_exists(pid):
            print('Process exited')
            return True
        time.sleep(1)
    print('Process still running after SIGTERM timeout')
    return False


def try_kill(pid):
    try:
        print(f'Sending SIGKILL to {pid}...')
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        print('Process not running')
        return True
    except Exception as e:
        print('Error sending SIGKILL:', e)
        return False

    # give a moment
    time.sleep(1)
    if not proc_exists(pid):
        print('Process killed')
        return True
    print('Failed to kill process')
    return False


def tail_logs(lines=40):
    logpath = os.path.join(os.getcwd(), 'logs', 'skynet_web.log')
    if os.path.isfile(logpath):
        try:
            subprocess.check_call(['tail', '-n', str(lines), logpath])
        except Exception:
            pass
    else:
        print('No log file at', logpath)


def main():
    parser = argparse.ArgumentParser(description='Gracefully stop Skynet Lite web server')
    parser.add_argument('--force', '-f', action='store_true', help='Force stop: skip cmdline safety checks')
    parser.add_argument('--pid', type=int, help='Specify PID to stop (overrides pidfile)')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout seconds to wait after SIGTERM')
    args = parser.parse_args()

    pid = None
    if args.pid:
        pid = args.pid
        print('Using PID from --pid:', pid)
    else:
        pid = read_pidfile()

    if not pid:
        print('No pidfile found at', PIDFILE)
        # Try to find a candidate by searching for web/app.py in processes
        try:
            out = subprocess.check_output(['pgrep', '-f', 'web/app.py'], text=True).strip()
            if out:
                pid = int(out.splitlines()[0])
                print('Found candidate PID via pgrep:', pid)
        except Exception:
            pass

    if not pid:
        print('Could not determine server PID; aborting')
        sys.exit(1)

    print('Candidate PID:', pid)
    # Verify it looks like our app unless --force
    if not args.force:
        if not (cmdline_contains(pid, 'web/app.py') or cmdline_contains(pid, '.venv') or cmdline_contains(pid, 'skynet')):
            print('PID command line does not match expected web app; aborting for safety')
            sys.exit(1)
    else:
        print('Force flag set; skipping cmdline verification')

    # Try graceful terminate
    ok = try_terminate(pid, timeout=args.timeout)
    if not ok:
        print('Attempting SIGKILL fallback')
        ok = try_kill(pid)

    if ok:
        # remove pidfile if it exists and owned by us
        try:
            if os.path.isfile(PIDFILE):
                os.remove(PIDFILE)
                print('Removed pidfile', PIDFILE)
        except Exception:
            pass
        print('Shutdown complete')
        tail_logs()
        sys.exit(0)
    else:
        print('Failed to stop server')
        sys.exit(2)


if __name__ == '__main__':
    main()
