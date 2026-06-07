import customtkinter as ctk
import requests, uuid, subprocess, os, webbrowser

# ══ CẤU HÌNH ══════════════════════════════
SERVER = "https://your-server.com"
GETKEY_LINK = "https://linkvertise.com/your-link"
APP_PATH = r"C:\Users\WIN PRO\Desktop\VPNlag.exe"
KEY_FILE = os.path.join(os.getenv("APPDATA"), "vpnlag_key.txt")
# ══════════════════════════════════════════

def get_hwid():
    return str(uuid.getnode())

def save_key(key):
    with open(KEY_FILE, "w") as f:
        f.write(key)

def load_key():
    try:
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    except:
        return ""

def verify_key(key):
    try:
        r = requests.get(f"{SERVER}/verify",
                        params={"key": key, "hwid": get_hwid()},
                        timeout=5)
        return r.json()
    except:
        return {"valid": False, "reason": "Không kết nối được server"}

def launch_app():
    subprocess.Popen(APP_PATH)
    root.destroy()

def on_verify():
    key = entry.get().strip()
    if not key:
        label_status.configure(text="⚠️ Nhập key trước!", text_color="orange")
        return
    label_status.configure(text="⏳ Đang kiểm tra...", text_color="gray")
    root.update()
    result = verify_key(key)
    if result["valid"]:
        save_key(key)
        label_status.configure(text="✅ Hợp lệ! Đang mở app...", text_color="green")
        root.after(1000, launch_app)
    else:
        label_status.configure(text=f"❌ {result.get('reason')}", text_color="red")

def on_getkey():
    webbrowser.open(GETKEY_LINK)

# ══ KIỂM TRA KEY ĐÃ LƯU ══════════════════
saved = load_key()
if saved:
    result = verify_key(saved)
    if result["valid"]:
        subprocess.Popen(APP_PATH)
        exit()

# ══ GIAO DIỆN ════════════════════════════
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("VPNlag - Xác minh")
root.geometry("420x240")
root.resizable(False, False)

ctk.CTkLabel(root, text="🔐 VPNlag Launcher",
             font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(25,5))

ctk.CTkLabel(root, text="Nhập key để sử dụng phần mềm",
             font=ctk.CTkFont(size=12), text_color="gray").pack()

entry = ctk.CTkEntry(root, width=300, height=38,
                     placeholder_text="Dán key vào đây...",
                     font=ctk.CTkFont(size=13, family="Consolas"))
entry.pack(pady=12)
entry.insert(0, saved)

ctk.CTkButton(root, text="Xác minh", width=300,
              height=36, command=on_verify).pack()

label_status = ctk.CTkLabel(root, text="", font=ctk.CTkFont(size=11))
label_status.pack(pady=5)

ctk.CTkButton(root, text="🔑 Get Key", width=100, height=28,
              fg_color="transparent", border_width=1,
              font=ctk.CTkFont(size=11),
              command=on_getkey).place(x=300, y=200)

root.mainloop()