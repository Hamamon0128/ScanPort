import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog
from queue import Queue
import time
import csv
import json

# =====================
# 設定
# =====================
MAX_THREADS = 50
TIMEOUT = 0.3

# =====================
# グローバル状態
# =====================
queue = Queue()
stop_event = threading.Event()
scan_done = False
scan_done_lock = threading.Lock()

open_ports = []
checked_ports = 0
total_ports = 0
start_time = 0

# =====================
# ネットワーク自動検出
# =====================
def detect_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

# =====================
# スキャン開始
# =====================
def start_scan():
    global checked_ports, total_ports, start_time, open_ports, scan_done

    scan_done = False
    stop_event.clear()
    open_ports = []
    checked_ports = 0

    target = target_entry.get()
    start_port = int(start_entry.get())
    end_port = int(end_entry.get())

    total_ports = end_port - start_port + 1
    start_time = time.time()

    result_box.delete("1.0", tk.END)

    status_var.set("スキャン中…")
    progress_var.set(f"0 / {total_ports}")
    time_var.set("経過時間: 0.0 秒")

    scan_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    print(f"{target} の {start_port}〜{end_port} 番ポートをスキャンします。")

    while not queue.empty():
        queue.get()

    for port in range(start_port, end_port + 1):
        queue.put((target, port))

    for _ in range(MAX_THREADS):
        threading.Thread(target=worker, daemon=True).start()

    update_timer()

# =====================
# ワーカー
# =====================
def worker():
    global checked_ports, scan_done

    while True:
        if stop_event.is_set():
            return

        try:
            target, port = queue.get_nowait()
        except:
            break

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            if sock.connect_ex((target, port)) == 0:
                open_ports.append(port)
                print(f"OPEN : {port}")
                root.after(0, append_text, f"OPEN : {port}\n")
            sock.close()
        except:
            pass

        checked_ports += 1
        root.after(0, update_progress)
        queue.task_done()

    # 完了判定（必ず1回）
    with scan_done_lock:
        if not scan_done and checked_ports == total_ports:
            scan_done = True
            root.after(0, scan_finished)

# =====================
# 中断
# =====================
def stop_scan():
    stop_event.set()
    status_var.set("スキャン中断")
    scan_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    append_text("スキャン中断\n")
    print("スキャン中断")

# =====================
# 完了処理
# =====================
def scan_finished():
    status_var.set("スキャン完了")
    scan_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    append_text("スキャン完了\n")
    print("スキャン完了")

# =====================
# UI更新
# =====================
def update_progress():
    progress_var.set(f"{checked_ports} / {total_ports}")

def update_timer():
    if status_var.get() == "スキャン中…":
        elapsed = time.time() - start_time
        time_var.set(f"経過時間: {elapsed:.1f} 秒")
        root.after(200, update_timer)

def append_text(text):
    result_box.insert(tk.END, text)

# =====================
# 保存
# =====================
def save_csv():
    path = filedialog.asksaveasfilename(defaultextension=".csv")
    if not path:
        return
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["open_port"])
        for p in sorted(open_ports):
            writer.writerow([p])

def save_json():
    path = filedialog.asksaveasfilename(defaultextension=".json")
    if not path:
        return
    with open(path, "w") as f:
        json.dump(
            {
                "target": target_entry.get(),
                "open_ports": sorted(open_ports)
            },
            f,
            indent=2
        )

# =====================
# GUI
# =====================
root = tk.Tk()
root.title("Advanced Port Scanner")

local_ip = detect_local_ip()

tk.Label(root, text=f"ローカルIP: {local_ip}").pack()
tk.Label(root, text="ターゲット IP / ドメイン").pack()

target_entry = tk.Entry(root, width=40)
target_entry.insert(0, local_ip)
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
progress_var = tk.StringVar(value="0 / 0")
time_var = tk.StringVar(value="経過時間: 0.0 秒")

tk.Label(root, textvariable=status_var).pack()
tk.Label(root, textvariable=progress_var).pack()
tk.Label(root, textvariable=time_var).pack()

save_frame = tk.Frame(root)
save_frame.pack(pady=5)

tk.Button(save_frame, text="CSV保存", command=save_csv).pack(side=tk.LEFT, padx=5)
tk.Button(save_frame, text="JSON保存", command=save_json).pack(side=tk.LEFT, padx=5)

result_box = scrolledtext.ScrolledText(root, width=60, height=20)
result_box.pack()

root.mainloop()
