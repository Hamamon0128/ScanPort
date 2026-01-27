import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import time

stop_event = threading.Event()
start_time = 0
checked_ports = 0
total_ports = 0

def start_scan():
    global start_time, checked_ports, total_ports

    stop_event.clear()
    checked_ports = 0

    target = target_entry.get()
    start_port = int(start_entry.get())
    end_port = int(end_entry.get())

    total_ports = end_port - start_port + 1
    start_time = time.time()

    status_var.set("スキャン中…")
    progress_var.set(f"0 / {total_ports}")
    time_var.set("経過時間: 0.0 秒")

    scan_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    result_box.delete("1.0", tk.END)

    print(f"{target} の {start_port}〜{end_port} 番ポートをスキャンします。")

    threading.Thread(target=scan_ports, daemon=True).start()
    update_timer()

def scan_ports():
    global checked_ports

    target = target_entry.get()
    start_port = int(start_entry.get())
    end_port = int(end_entry.get())

    for port in range(start_port, end_port + 1):
        if stop_event.is_set():
            print("スキャン中断")
            root.after(0, scan_stopped)
            return

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            if sock.connect_ex((target, port)) == 0:
                print(f"OPEN : {port}")
                append_text(f"OPEN : {port}\n")
            sock.close()
        except:
            pass

        checked_ports += 1
        root.after(0, update_progress)

    print("スキャン完了")
    root.after(0, scan_finished)

def stop_scan():
    stop_event.set()

def scan_finished():
    status_var.set("スキャン完了")
    scan_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    append_text("スキャン完了\n")

def scan_stopped():
    status_var.set("スキャン中断")
    scan_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    append_text("スキャン中断\n")

def update_progress():
    progress_var.set(f"{checked_ports} / {total_ports}")

def update_timer():
    if status_var.get() == "スキャン中…":
        elapsed = time.time() - start_time
        time_var.set(f"経過時間: {elapsed:.1f} 秒")
        root.after(200, update_timer)

def append_text(text):
    result_box.insert(tk.END, text)

# GUI
root = tk.Tk()
root.title("Simple Port Scanner")

tk.Label(root, text="ターゲット IP / ドメイン").pack()
target_entry = tk.Entry(root, width=40)
target_entry.pack()

frame = tk.Frame(root)
frame.pack()

tk.Label(frame, text="開始ポート").grid(row=0, column=0)
start_entry = tk.Entry(frame, width=10)
start_entry.insert(0, "1")
start_entry.grid(row=0, column=1)

tk.Label(frame, text="終了ポート").grid(row=0, column=2)
end_entry = tk.Entry(frame, width=10)
end_entry.insert(0, "1024")
end_entry.grid(row=0, column=3)

scan_button = tk.Button(root, text="スキャン開始", command=start_scan)
scan_button.pack(pady=5)

stop_button = tk.Button(root, text="スキャン中断", command=stop_scan, state=tk.DISABLED)
stop_button.pack()

status_var = tk.StringVar(value="待機中")
tk.Label(root, textvariable=status_var).pack()

progress_var = tk.StringVar(value="0 / 0")
tk.Label(root, textvariable=progress_var).pack()

time_var = tk.StringVar(value="経過時間: 0.0 秒")
tk.Label(root, textvariable=time_var).pack()

result_box = scrolledtext.ScrolledText(root, width=60, height=20)
result_box.pack()

root.mainloop()
