
import os
import psutil

def kill_other_instances():
    
    this_pid = os.getpid()
    this_script = os.path.abspath(__file__)

    for proc in psutil.process_iter(["pid", "cmdline"]):
        pid = proc.info["pid"]
        cmdline = proc.info["cmdline"] or []

        # přeskočit sám sebe
        if pid == this_pid:
            continue

        # hledáme jiný proces, který spouští stejný skript
        if len(cmdline) >= 2 and os.path.abspath(cmdline[-1]) == this_script:
            if kill_others:
                try:
                    proc.kill()
                    print(f"[KILL] Old instance PID {pid} killed")
                except psutil.NoSuchProcess:
                    pass
            else:
                print(f"[INFO] Another instance is already running (PID {pid}), exiting.")
                raise SystemExit(0)

