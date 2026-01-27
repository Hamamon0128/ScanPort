import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

def start_scan():
    status_var.set("スキャン中…")
    scan_button.config(state=tk.DISABLED)
    threading.Thread(target=scan_ports, daemon=True).start()

def scan_ports():
    target = target_entry.get()
    start_port = int(start_entry.get())
    end_port = int(end_entry.get())

    print(f"{target} の {start_port}〜{end_port} 番ポートをスキャンします。")

    append_text(
        f"{target} の {start_port}〜{end_port} をスキャン中...\n"
    )

    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            if sock.connect_ex((target, port)) == 0:
                print(f"OPEN : {port}")
                append_text(f"OPEN : {port}\n")
            sock.close()
        except:
            pass

    print("スキャン完了")
    root.after(0, scan_finished)

def scan_finished():
    append_text("スキャン完了\n")
    status_var.set("スキャン完了")
    scan_button.config(state=tk.NORMAL)

def append_text(text):
    root.after(0, result_box.insert, tk.END, text)

# GUI構築
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

status_var = tk.StringVar(value="待機中")
tk.Label(root, textvariable=status_var).pack()

result_box = scrolledtext.ScrolledText(root, width=60, height=20)
result_box.pack()

root.mainloop()
