from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, uuid, datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB = "keys.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS keys (
        key TEXT PRIMARY KEY, hwid TEXT,
        expires TEXT, created TEXT, note TEXT)""")
    con.commit()
    con.close()

init_db()

def db():
    return sqlite3.connect(DB)

@app.get("/verify")
def verify(key: str, hwid: str):
    con = db()
    row = con.execute("SELECT * FROM keys WHERE key=?", (key,)).fetchone()
    con.close()
    if not row:
        return {"valid": False, "reason": "Key không tồn tại"}
    _, db_hwid, expires, _, _ = row
    if datetime.date.today().isoformat() > expires:
        return {"valid": False, "reason": "Key đã hết hạn"}
    if db_hwid is None:
        con = db()
        con.execute("UPDATE keys SET hwid=? WHERE key=?", (hwid, key))
        con.commit()
        con.close()
    elif db_hwid != hwid:
        return {"valid": False, "reason": "Key đang dùng trên máy khác"}
    return {"valid": True, "expires": expires}

@app.get("/admin/create")
def create_key(days: int = 30, note: str = "", pw: str = ""):
    if pw != "MATKHAU123":
        return {"error": "Sai mật khẩu"}
    key = "-".join([uuid.uuid4().hex[:5].upper() for _ in range(3)])
    expires = (datetime.date.today() + datetime.timedelta(days=days)).isoformat()
    con = db()
    con.execute("INSERT INTO keys VALUES (?,?,?,?,?)",
                (key, None, expires, datetime.date.today().isoformat(), note))
    con.commit()
    con.close()
    return {"key": key, "expires": expires}

@app.get("/admin/list")
def list_keys(pw: str = ""):
    if pw != "MATKHAU123":
        return {"error": "Sai mật khẩu"}
    con = db()
    rows = con.execute("SELECT * FROM keys").fetchall()
    con.close()
    return [{"key": r[0], "hwid": r[1], "expires": r[2], "note": r[4]} for r in rows]

@app.delete("/admin/delete")
def delete_key(key: str, pw: str = ""):
    if pw != "MATKHAU123":
        return {"error": "Sai mật khẩu"}
    con = db()
    con.execute("DELETE FROM keys WHERE key=?", (key,))
    con.commit()
    con.close()
    return {"deleted": True}
