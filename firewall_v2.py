#!/usr/bin/env python3
"""FIREWALL MANAGER v2.0 — Windows Firewall con Tráfico Sync"""

import sys, os, json, time, socket, threading, subprocess, random
from datetime import datetime
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# ── Matrix / Hacktivist Palette ───────────────────────────────
BG     = "#000000"   # pure black
BG2    = "#030303"   # near-black
BG3    = "#0a0a0a"   # dark panel
ACC    = "#001a00"   # hover / selection bg
BLUE   = "#00e5cc"   # cyan-teal (contrast action)
GREEN  = "#00ff41"   # matrix green (primary)
RED    = "#ff003c"   # alert red
ORANGE = "#ffaa00"   # warning amber
YELLOW = "#aaff00"   # neon lime
PURPLE = "#00ccff"   # info cyan
TEXT   = "#00ff41"   # matrix green text
MUTED  = "#005c12"   # dim green
BORDER = "#003300"   # dark green border

MONO = "'Courier New', 'Consolas', monospace"

BASE_STYLE = f"""
QMainWindow, QWidget  {{ background:{BG}; color:{TEXT}; font-family:{MONO}; font-size:14px; }}
QTabWidget::pane      {{ border:1px solid {BORDER}; background:{BG2}; }}
QTabBar::tab          {{ background:{BG}; color:{MUTED}; border:none; border-right:1px solid {BORDER};
                         padding:12px 20px; font-size:13px; font-family:{MONO}; letter-spacing:1px; }}
QTabBar::tab:selected {{ background:{BG2}; color:{GREEN}; border-bottom:2px solid {GREEN}; }}
QTabBar::tab:hover    {{ background:{ACC}; color:{GREEN}; }}
QTableWidget          {{ background:{BG}; color:{TEXT}; border:1px solid {BORDER};
                         gridline-color:{BORDER}; alternate-background-color:{BG2}; font-size:13px;
                         font-family:{MONO}; }}
QTableWidget::item    {{ padding:5px 6px; }}
QTableWidget::item:selected {{ background:{ACC}; color:{GREEN}; }}
QHeaderView::section  {{ background:{BG3}; color:{GREEN}; border:none; border-bottom:1px solid {BORDER};
                         border-right:1px solid {BORDER}; padding:9px 8px; font-weight:bold;
                         font-size:12px; font-family:{MONO}; letter-spacing:2px; }}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background:{BG3}; color:{GREEN}; border:1px solid {BORDER}; border-radius:0px;
    padding:8px 10px; font-size:14px; font-family:{MONO}; min-height:20px; }}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{ border-color:{GREEN}; }}
QComboBox QAbstractItemView {{ background:{BG3}; color:{GREEN}; border:1px solid {BORDER}; selection-background-color:{ACC}; }}
QPushButton {{ background:{BG3}; color:{GREEN}; border:1px solid {GREEN}; border-radius:0px;
               padding:9px 18px; font-size:13px; font-weight:bold; font-family:{MONO}; min-height:20px; }}
QPushButton:hover   {{ background:{ACC}; color:{GREEN}; border-color:{GREEN}; }}
QPushButton:pressed {{ background:{GREEN}; color:{BG}; }}
QPushButton:disabled {{ background:{BG}; color:{BORDER}; border-color:{BORDER}; }}
QScrollBar:vertical   {{ background:{BG}; width:8px; border:none; border-left:1px solid {BORDER}; }}
QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:0px; min-height:20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0px; }}
QScrollBar:horizontal {{ background:{BG}; height:8px; border:none; border-top:1px solid {BORDER}; }}
QScrollBar::handle:horizontal {{ background:{BORDER}; border-radius:0px; min-width:20px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width:0px; }}
QTextEdit, QPlainTextEdit {{
    background:{BG}; color:{GREEN}; border:1px solid {BORDER}; border-radius:0px;
    font-family:{MONO}; font-size:13px; selection-background-color:{ACC}; }}
QGroupBox {{ border:1px solid {BORDER}; border-radius:0px; margin-top:18px; background:{BG2}; }}
QGroupBox::title {{ color:{GREEN}; subcontrol-origin:margin; left:10px; padding:0 8px;
                    font-size:12px; font-weight:bold; font-family:{MONO}; letter-spacing:2px; }}
QProgressBar {{ background:{BG3}; border:1px solid {BORDER}; border-radius:0px; height:10px;
                color:transparent; text-align:center; }}
QProgressBar::chunk {{ background:{GREEN}; border-radius:0px; }}
QSplitter::handle {{ background:{BORDER}; }}
QListWidget {{ background:{BG}; color:{GREEN}; border:1px solid {BORDER}; border-radius:0px;
               font-family:{MONO}; font-size:13px; }}
QListWidget::item {{ padding:4px 8px; }}
QListWidget::item:selected {{ background:{ACC}; color:{GREEN}; }}
QMenuBar {{ background:{BG}; color:{GREEN}; border-bottom:1px solid {BORDER}; font-family:{MONO}; }}
QMenuBar::item:selected {{ background:{ACC}; }}
QMenu {{ background:{BG}; color:{GREEN}; border:1px solid {BORDER}; font-family:{MONO}; }}
QMenu::item:selected {{ background:{ACC}; }}
QStatusBar {{ background:{BG}; color:{MUTED}; border-top:1px solid {BORDER}; font-family:{MONO}; }}
QDialog {{ background:{BG2}; color:{TEXT}; }}
QMessageBox {{ background:{BG2}; color:{TEXT}; }}
QCheckBox {{ color:{GREEN}; font-family:{MONO}; }}
QCheckBox::indicator {{ width:14px; height:14px; border:1px solid {GREEN}; background:{BG}; }}
QCheckBox::indicator:checked {{ background:{GREEN}; }}
QLabel {{ color:{GREEN}; }}
"""

def _btn(text, color=GREEN, min_w=100):
    is_red = color in (RED, "#ef233c")
    is_dim = color in (MUTED, "#64748b", "#005c12")
    border = color if not is_dim else BORDER
    hover_bg = ACC if not is_red else "#2a0008"
    b = QPushButton(text)
    b.setStyleSheet(
        f"QPushButton{{background:{BG3};color:{color};border:1px solid {border};"
        f"border-radius:0px;padding:9px 18px;font-weight:bold;font-size:13px;"
        f"font-family:{MONO};min-width:{min_w}px;}}"
        f"QPushButton:hover{{background:{hover_bg};color:{color};border-color:{color};}}"
        f"QPushButton:pressed{{background:{color};color:{BG};}}"
        f"QPushButton:disabled{{background:{BG};color:{BORDER};border-color:{BORDER};}}"
    )
    return b

def _card(title=""):
    prefix = "// " if title else ""
    g = QGroupBox(f"{prefix}{title.upper()}")
    return g

def _fmt_bps(bps):
    if bps < 1024:      return f"{bps:.0f} B/s"
    if bps < 1024**2:   return f"{bps/1024:.1f} KB/s"
    if bps < 1024**3:   return f"{bps/1024**2:.1f} MB/s"
    return f"{bps/1024**3:.2f} GB/s"

def _fmt_bytes(b):
    if b < 1024:    return f"{b} B"
    if b < 1024**2: return f"{b/1024:.1f} KB"
    if b < 1024**3: return f"{b/1024**2:.1f} MB"
    return f"{b/1024**3:.2f} GB"

# ── Matrix Rain Widget ────────────────────────────────────────
_MX_CHARS = (
    "アイウエオカキクケコサシスセソタチツテトナニヌネノ"
    "ハヒフヘホマミムメモヤユヨラリルレロワヲン"
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "!@#$%^&*<>[]{}|/\\;:=+-"
)

class MatrixRainWidget(QWidget):
    def __init__(self, parent=None, h=160):
        super().__init__(parent)
        self.setMinimumHeight(h); self.setMaximumHeight(h)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._cols = []
        self._ready = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(45)

    def _init(self):
        cw = 15
        n = max(1, self.width() // cw)
        self._cols = [{
            "x":     i * cw,
            "y":     random.randint(-self.height(), 0),
            "speed": random.uniform(0.8, 2.8),
            "len":   random.randint(6, 22),
            "chars": [random.choice(_MX_CHARS) for _ in range(25)],
            "mut":   0,
        } for i in range(n)]
        self._ready = True

    def _tick(self):
        if not self._ready or self.width() < 2: return
        for c in self._cols:
            c["mut"] += 1
            if c["mut"] % 4 == 0:
                idx = random.randint(0, len(c["chars"]) - 1)
                c["chars"][idx] = random.choice(_MX_CHARS)
            c["y"] += c["speed"]
            if c["y"] > self.height() + c["len"] * 16:
                c["y"] = random.randint(-80, -10)
                c["speed"] = random.uniform(0.8, 2.8)
                c["len"]   = random.randint(6, 22)
        self.update()

    def resizeEvent(self, e):
        self._ready = False
        super().resizeEvent(e)

    def paintEvent(self, e):
        if not self._ready:
            self._init()
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(BG))
        fnt = QFont("Courier New", 11)
        p.setFont(fnt)
        ch = p.fontMetrics().height()

        for col in self._cols:
            for i in range(col["len"]):
                cy = int(col["y"]) - (col["len"] - i - 1) * ch
                if cy < 0 or cy > self.height(): continue
                char = col["chars"][i % len(col["chars"])]
                t = i / col["len"]
                if i == col["len"] - 1:
                    r, g, b, a = 220, 255, 220, 255   # head: near-white
                elif t > 0.65:
                    g_v = int(180 + 75 * (t - 0.65) / 0.35)
                    r, g, b, a = 0, min(255, g_v), int(g_v * 0.25), 230
                else:
                    g_v = int(60 + 120 * t / 0.65)
                    r, g, b, a = 0, g_v, int(g_v * 0.15), int(80 + 120 * t)
                p.setPen(QColor(r, g, b, a))
                p.drawText(col["x"], cy, char)
        p.end()


# ── Traffic Graph ─────────────────────────────────────────────
class TrafficGraph(QWidget):
    def __init__(self, title="Tráfico", color_a=GREEN, color_b=BLUE, pts=60):
        super().__init__()
        self.title = title
        self.ca = QColor(color_a); self.cb = QColor(color_b)
        self.pts = pts
        self.da  = deque([0]*pts, maxlen=pts)
        self.db  = deque([0]*pts, maxlen=pts)
        self.peak = 1
        self.label_a = "Subida"; self.label_b = "Bajada"
        self.setMinimumHeight(170)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def push(self, a, b):
        self.da.append(a); self.db.append(b)
        self.peak = max(1, max(self.da), max(self.db))
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        PL, PR, PT, PB = 68, 12, 26, 26
        p.fillRect(0, 0, W, H, QColor(BG))
        gw = W - PL - PR; gh = H - PT - PB

        # Horizontal grid lines (dim green dashes)
        pen_grid = QPen(QColor(BORDER), 1, Qt.DotLine)
        p.setPen(pen_grid)
        for i in range(1, 5):
            y = PT + gh * i // 4
            p.drawLine(PL, y, W - PR, y)

        def fill_series(data, color):
            n = len(data)
            if n < 2: return
            pts_t = [QPointF(PL + gw * i // (self.pts-1), PT + gh - gh * v / self.peak) for i, v in enumerate(data)]
            pts_b = [QPointF(pt.x(), PT + gh) for pt in pts_t]
            poly = QPolygonF(pts_t + list(reversed(pts_b)))
            fc = QColor(color); fc.setAlpha(28)
            p.setBrush(QBrush(fc)); p.setPen(Qt.NoPen); p.drawPolygon(poly)
            p.setPen(QPen(QColor(color), 1.5)); p.setBrush(Qt.NoBrush)
            for i in range(len(pts_t) - 1):
                p.drawLine(pts_t[i], pts_t[i+1])

        fill_series(self.da, self.ca)
        fill_series(self.db, self.cb)

        # Axes
        p.setPen(QPen(QColor(BORDER), 1)); p.setBrush(Qt.NoBrush)
        p.drawLine(PL, PT, PL, H - PB)
        p.drawLine(PL, H - PB, W - PR, H - PB)

        # Y-axis labels
        p.setPen(QColor(MUTED)); p.setFont(QFont("Courier New", 8))
        for i in range(5):
            val = self.peak * (4-i) / 4
            y   = PT + gh * i // 4
            p.drawText(0, y-7, PL-4, 14, Qt.AlignRight|Qt.AlignVCenter, _fmt_bps(val))

        # Title
        p.setFont(QFont("Courier New", 10, QFont.Bold)); p.setPen(QColor(GREEN))
        p.drawText(PL, 2, gw, PT-2, Qt.AlignCenter, f"// {self.title.upper()} //")

        # Legend
        lx = W - 170
        p.setPen(QPen(self.ca, 2)); p.drawLine(lx, H-13, lx+16, H-13)
        p.setPen(QColor(self.ca)); p.setFont(QFont("Courier New", 8))
        p.drawText(lx+20, H-21, 60, 14, Qt.AlignLeft, self.label_a)
        lx2 = lx + 80
        p.setPen(QPen(self.cb, 2)); p.drawLine(lx2, H-13, lx2+16, H-13)
        p.setPen(QColor(self.cb)); p.setFont(QFont("Courier New", 8))
        p.drawText(lx2+20, H-21, 60, 14, Qt.AlignLeft, self.label_b)


# ── Workers ───────────────────────────────────────────────────
class TrafficWorker(QObject):
    data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._running = False
        self._last_net = None
        self._last_t   = time.time()
        self._last_proc = {}

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self): self._running = False

    def _loop(self):
        while self._running:
            try: self.data_ready.emit(self._collect())
            except: pass
            time.sleep(1.0)

    def _collect(self):
        now = time.time(); dt = max(0.001, now - self._last_t); self._last_t = now
        out = {"up":0, "down":0, "connections":0, "ifaces":{}, "procs":[]}
        if not HAS_PSUTIL: return out

        net = psutil.net_io_counters()
        if self._last_net:
            out["up"]   = max(0, (net.bytes_sent - self._last_net.bytes_sent) / dt)
            out["down"] = max(0, (net.bytes_recv - self._last_net.bytes_recv) / dt)
        self._last_net = net

        for name, st in psutil.net_io_counters(pernic=True).items():
            out["ifaces"][name] = (_fmt_bytes(st.bytes_sent), _fmt_bytes(st.bytes_recv))

        try:
            out["connections"] = len([c for c in psutil.net_connections() if c.status == "ESTABLISHED"])
        except: pass

        try:
            procs = []
            for proc in psutil.process_iter(["pid","name","connections"]):
                try:
                    info = proc.info
                    conns = len([c for c in (info.get("connections") or []) if getattr(c,"status","")=="ESTABLISHED"])
                    if conns > 0:
                        procs.append({"pid": info["pid"], "name": info["name"] or "?", "connections": conns,
                                      "up": 0, "down": 0})
                except (psutil.NoSuchProcess, psutil.AccessDenied): pass
            procs.sort(key=lambda x: x["connections"], reverse=True)
            out["procs"] = procs[:25]
        except: pass

        return out


class PortScanWorker(QObject):
    port_open = pyqtSignal(int, str)
    finished  = pyqtSignal(int)

    SERVICES = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",
                135:"RPC",139:"NetBIOS",143:"IMAP",443:"HTTPS",445:"SMB",
                1433:"MSSQL",3306:"MySQL",3389:"RDP",5432:"Postgres",
                8080:"HTTP-Alt",8443:"HTTPS-Alt",27017:"MongoDB"}

    def __init__(self): super().__init__(); self._stop = False

    def scan(self, host, p1, p2, timeout):
        self._stop = False
        threading.Thread(target=self._run, args=(host,p1,p2,timeout), daemon=True).start()

    def abort(self): self._stop = True

    def _run(self, host, p1, p2, timeout):
        open_n = 0; sem = threading.Semaphore(150)
        results = []
        lock = threading.Lock()

        def check(port):
            nonlocal open_n
            if self._stop: return
            with sem:
                try:
                    s = socket.socket(); s.settimeout(timeout)
                    if s.connect_ex((host, port)) == 0:
                        with lock:
                            open_n += 1
                            results.append((port, self.SERVICES.get(port,"")))
                    s.close()
                except: pass

        ts = [threading.Thread(target=check, args=(p,), daemon=True) for p in range(p1, p2+1)]
        for t in ts: t.start()
        for t in ts: t.join()

        for port, svc in sorted(results):
            self.port_open.emit(port, svc)
        self.finished.emit(open_n)


class SyncWorker(QObject):
    peer_found  = pyqtSignal(str, str)
    sync_done   = pyqtSignal(str, bool)
    log_msg     = pyqtSignal(str)

    PORT  = 54321
    MAGIC = b"FWM2SYNC\x00"

    def __init__(self): super().__init__(); self._running = False

    def start_server(self, rules_fn):
        self._running = True; self._rules_fn = rules_fn
        threading.Thread(target=self._serve, daemon=True).start()

    def stop_server(self): self._running = False

    def _serve(self):
        try:
            srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("0.0.0.0", self.PORT)); srv.listen(5); srv.settimeout(1.0)
            self.log_msg.emit(f"Servidor Sync activo — puerto {self.PORT}")
            while self._running:
                try:
                    conn, addr = srv.accept()
                    threading.Thread(target=self._handle, args=(conn,addr), daemon=True).start()
                except socket.timeout: pass
            srv.close()
        except Exception as e: self.log_msg.emit(f"Error servidor: {e}")

    def _handle(self, conn, addr):
        try:
            if conn.recv(len(self.MAGIC)) == self.MAGIC:
                payload = json.dumps(self._rules_fn()).encode()
                conn.sendall(len(payload).to_bytes(4,"big") + payload)
                self.log_msg.emit(f"Reglas enviadas a {addr[0]}")
        except Exception as e: self.log_msg.emit(f"Error con {addr[0]}: {e}")
        finally: conn.close()

    def scan_peers(self, subnet):
        threading.Thread(target=self._scan_peers, args=(subnet,), daemon=True).start()

    def _scan_peers(self, subnet):
        base = ".".join(subnet.split(".")[:3]); found = 0
        self.log_msg.emit(f"Escaneando {base}.1-254 ...")
        for i in range(1, 255):
            ip = f"{base}.{i}"
            try:
                s = socket.socket(); s.settimeout(0.25)
                if s.connect_ex((ip, self.PORT)) == 0:
                    try: host = socket.gethostbyaddr(ip)[0]
                    except: host = ip
                    self.peer_found.emit(ip, host); found += 1
                s.close()
            except: pass
        self.log_msg.emit(f"Scan completado — {found} peer(s) con Firewall Manager")

    def pull_rules(self, ip):
        threading.Thread(target=self._pull, args=(ip,), daemon=True).start()

    def _pull(self, ip):
        try:
            s = socket.socket(); s.settimeout(6); s.connect((ip, self.PORT))
            s.sendall(self.MAGIC)
            size = int.from_bytes(s.recv(4), "big")
            data = b""
            while len(data) < size:
                chunk = s.recv(4096)
                if not chunk: break
                data += chunk
            s.close()
            rules = json.loads(data.decode())
            self.sync_done.emit(f"Recibidas {len(rules)} reglas de {ip}", True)
        except Exception as e:
            self.sync_done.emit(f"Error con {ip}: {e}", False)


# ── Firewall helpers ──────────────────────────────────────────
class FwRulesLoader(QObject):
    ready = pyqtSignal(list)
    def load(self):
        threading.Thread(target=self._run, daemon=True).start()
    def _run(self):
        try:
            r = subprocess.run(
                ["netsh","advfirewall","firewall","show","rule","name=all","verbose"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
            self.ready.emit(_parse_rules(r.stdout))
        except Exception as e:
            self.ready.emit([])

def _parse_rules(txt):
    rules = []; cur = {}
    for line in txt.splitlines():
        line = line.strip()
        if not line:
            if cur.get("name"): rules.append(cur); cur = {}
            continue
        if ":" in line:
            k, _, v = line.partition(":"); k = k.strip().lower(); v = v.strip()
            if   "rule name"  in k: cur["name"]      = v
            elif "enabled"    in k: cur["enabled"]   = v
            elif "direction"  in k: cur["direction"] = v
            elif "action"     in k: cur["action"]    = v
            elif "protocol"   in k: cur["protocol"]  = v
            elif "localport"  in k: cur["port"]      = v
            elif "remoteip"   in k: cur["remote"]    = v
            elif "program"    in k: cur["program"]   = v
    if cur.get("name"): rules.append(cur)
    return rules

def _add_rule(name, direction, action, protocol, port):
    cmd = ["netsh","advfirewall","firewall","add","rule",
           f"name={name}", f"dir={direction}", f"action={action}",
           f"protocol={protocol}", "enable=yes"]
    if port and port.lower() not in ("any","cualquiera",""): cmd.append(f"localport={port}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e: return False, str(e)

def _del_rule(name):
    try:
        r = subprocess.run(
            ["netsh","advfirewall","firewall","delete","rule",f"name={name}"],
            capture_output=True, text=True, timeout=12)
        return r.returncode == 0, r.stdout.strip()
    except Exception as e: return False, str(e)

def _my_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8",80))
        ip = s.getsockname()[0]; s.close(); return ip
    except: return "N/D"

def _gateway():
    try:
        r = subprocess.run(["ipconfig"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        for line in r.stdout.splitlines():
            if "enlace predeterminado" in line.lower() or "default gateway" in line.lower():
                gw = line.split(":")[-1].strip()
                if gw: return gw
    except: pass
    return "N/D"


# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════

# ── Dashboard ────────────────────────────────────────────────
class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,10); layout.setSpacing(0)

        # Matrix rain header
        self.rain = MatrixRainWidget(h=130)
        layout.addWidget(self.rain)

        inner = QVBoxLayout(); inner.setContentsMargins(14,10,14,0); inner.setSpacing(10)

        # Stat cards row
        row = QHBoxLayout(); row.setSpacing(8)
        self.s_up   = self._stat("[↑] SUBIDA",         "0 B/s",  GREEN)
        self.s_down = self._stat("[↓] BAJADA",          "0 B/s",  BLUE)
        self.s_conn = self._stat("[⚡] CONEXIONES",      "0",      ORANGE)
        self.s_proc = self._stat("[⚙] PROCESOS ACTIVOS","0",       PURPLE)
        for w in [self.s_up, self.s_down, self.s_conn, self.s_proc]: row.addWidget(w)
        inner.addLayout(row)

        # Main graph
        self.graph = TrafficGraph("Tráfico de Red en Tiempo Real", GREEN, BLUE)
        inner.addWidget(self.graph, 2)

        # Bottom split
        bot = QHBoxLayout(); bot.setSpacing(8)

        iface_g = _card("Interfaces de Red")
        il = QVBoxLayout(iface_g)
        self.iface_tbl = self._table(["Interfaz","Enviado","Recibido"])
        self.iface_tbl.setMaximumHeight(130)
        il.addWidget(self.iface_tbl)
        bot.addWidget(iface_g, 1)

        proc_g = _card("Top Procesos con Conexiones")
        pl = QVBoxLayout(proc_g)
        self.proc_tbl = self._table(["Proceso","PID","Conexiones"])
        self.proc_tbl.setMaximumHeight(130)
        pl.addWidget(self.proc_tbl)
        bot.addWidget(proc_g, 1)

        inner.addLayout(bot)
        layout.addLayout(inner)

    def _stat(self, title, value, color):
        w = QWidget()
        w.setStyleSheet(
            f"background:{BG}; border:1px solid {color}; border-left:3px solid {color};")
        vl = QVBoxLayout(w); vl.setContentsMargins(12,8,12,8); vl.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet(f"color:{MUTED}; font-size:10px; font-family:{MONO}; "
                        f"border:none; background:transparent; letter-spacing:1px;")
        v = QLabel(value)
        v.setStyleSheet(f"color:{color}; font-size:20px; font-weight:bold; "
                        f"font-family:{MONO}; border:none; background:transparent;")
        vl.addWidget(t); vl.addWidget(v); w._v = v; return w

    def _table(self, headers):
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.verticalHeader().hide()
        t.setEditTriggers(QAbstractItemView.NoEditTriggers)
        t.setAlternatingRowColors(True)
        return t

    def update(self, d):
        self.s_up._v.setText(_fmt_bps(d["up"]))
        self.s_down._v.setText(_fmt_bps(d["down"]))
        self.s_conn._v.setText(str(d["connections"]))
        self.s_proc._v.setText(str(len(d["procs"])))
        self.graph.push(d["up"], d["down"])

        ifaces = list(d["ifaces"].items())
        self.iface_tbl.setRowCount(len(ifaces))
        for i, (name, (sent, recv)) in enumerate(ifaces):
            for j, v in enumerate([name, sent, recv]):
                self.iface_tbl.setItem(i, j, QTableWidgetItem(v))

        procs = d["procs"][:8]
        self.proc_tbl.setRowCount(len(procs))
        for i, proc in enumerate(procs):
            for j, v in enumerate([proc["name"], str(proc["pid"]), str(proc["connections"])]):
                item = QTableWidgetItem(v)
                if j == 2: item.setForeground(QBrush(QColor(ORANGE)))
                self.proc_tbl.setItem(i, j, item)


# ── Traffic Real Time ────────────────────────────────────────
class TrafficTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(14,14,14,14); layout.setSpacing(10)

        graphs = QHBoxLayout()
        self.g_total = TrafficGraph("Total Red", GREEN, BLUE)
        self.g_conns = TrafficGraph("Conexiones Activas", ORANGE, PURPLE)
        self.g_conns.label_a = "Establecidas"; self.g_conns.label_b = "Procesos"
        graphs.addWidget(self.g_total); graphs.addWidget(self.g_conns)
        layout.addLayout(graphs)

        proc_card = _card("Procesos con Actividad de Red")
        pl = QVBoxLayout(proc_card)
        sf = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Filtrar por nombre...")
        self.search.textChanged.connect(self._filter)
        sf.addWidget(self.search)
        pl.addLayout(sf)

        self.tbl = QTableWidget(0, 4)
        self.tbl.setHorizontalHeaderLabels(["Proceso","PID","Conexiones Activas","Estado"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.verticalHeader().hide()
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        pl.addWidget(self.tbl)
        layout.addWidget(proc_card, 1)
        self._procs = []

    def update(self, d):
        self.g_total.push(d["up"], d["down"])
        self.g_conns.push(d["connections"], len(d["procs"]) * 10)
        self._procs = d["procs"]
        self._filter(self.search.text())

    def _filter(self, text):
        procs = [p for p in self._procs if text.lower() in p["name"].lower()] if text else self._procs
        self.tbl.setRowCount(len(procs))
        for i, proc in enumerate(procs):
            conns = proc["connections"]
            color = RED if conns > 20 else ORANGE if conns > 5 else GREEN
            items = [proc["name"], str(proc["pid"]), str(conns),
                     "Alta actividad" if conns > 20 else "Media" if conns > 5 else "Normal"]
            for j, v in enumerate(items):
                item = QTableWidgetItem(v)
                if j in (2, 3): item.setForeground(QBrush(QColor(color)))
                self.tbl.setItem(i, j, item)


# ── Alerts ───────────────────────────────────────────────────
class AlertsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.rules   = []
        self.history = []
        self._last_alert = {}

        layout = QVBoxLayout(self); layout.setContentsMargins(14,14,14,14); layout.setSpacing(10)

        # Alert bar
        self.alert_bar = QLabel("  Sin alertas activas")
        self.alert_bar.setStyleSheet(f"background:{BG3}; color:{GREEN}; border-radius:6px; padding:10px; font-size:13px; font-weight:bold;")
        layout.addWidget(self.alert_bar)

        main = QHBoxLayout()

        # Left: rule editor
        left = _card("Nueva Regla de Alerta")
        ll = QVBoxLayout(left)
        form = QFormLayout()
        self.a_name  = QLineEdit(); self.a_name.setPlaceholderText("Nombre alerta")
        self.a_thr   = QSpinBox();  self.a_thr.setRange(1,100000); self.a_thr.setValue(10)
        self.a_unit  = QComboBox(); self.a_unit.addItems(["KB/s","MB/s"])
        self.a_dir   = QComboBox(); self.a_dir.addItems(["Bajada","Subida","Ambas"])
        self.a_notif = QCheckBox("Mostrar popup"); self.a_notif.setChecked(True)
        form.addRow("Nombre:",    self.a_name)
        form.addRow("Umbral:",    self.a_thr)
        form.addRow("Unidad:",    self.a_unit)
        form.addRow("Dirección:", self.a_dir)
        form.addRow("",           self.a_notif)
        ll.addLayout(form)
        add_btn = _btn("+ Añadir Alerta", GREEN)
        add_btn.clicked.connect(self._add_rule)
        ll.addWidget(add_btn)

        self.rules_tbl = QTableWidget(0, 4)
        self.rules_tbl.setHorizontalHeaderLabels(["Nombre","Umbral","Dirección","✓"])
        self.rules_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rules_tbl.verticalHeader().hide()
        self.rules_tbl.setMaximumHeight(200)
        del_btn = _btn("✕ Eliminar seleccionada", RED)
        del_btn.clicked.connect(self._del_rule)
        ll.addWidget(self.rules_tbl)
        ll.addWidget(del_btn)
        main.addWidget(left, 1)

        # Right: history
        right = _card("Historial de Alertas")
        rl = QVBoxLayout(right)
        self.hist_tbl = QTableWidget(0, 3)
        self.hist_tbl.setHorizontalHeaderLabels(["Hora","Alerta","Detalle"])
        self.hist_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hist_tbl.verticalHeader().hide()
        self.hist_tbl.setAlternatingRowColors(True)
        rl.addWidget(self.hist_tbl)
        clr = _btn("Limpiar historial", MUTED)
        clr.clicked.connect(lambda: (self.history.clear(), self._refresh_hist()))
        rl.addWidget(clr)
        main.addWidget(right, 1)

        layout.addLayout(main)

    def _add_rule(self):
        name = self.a_name.text().strip() or f"Alerta {len(self.rules)+1}"
        dm = {"Bajada":"down","Subida":"up","Ambas":"both"}
        self.rules.append({"name":name, "threshold":self.a_thr.value(),
                            "unit":self.a_unit.currentText(),
                            "direction":dm[self.a_dir.currentText()],
                            "popup":self.a_notif.isChecked(), "enabled":True})
        self._refresh_rules()

    def _del_rule(self):
        row = self.rules_tbl.currentRow()
        if 0 <= row < len(self.rules):
            self.rules.pop(row); self._refresh_rules()

    def _refresh_rules(self):
        self.rules_tbl.setRowCount(len(self.rules))
        for i, r in enumerate(self.rules):
            self.rules_tbl.setItem(i,0,QTableWidgetItem(r["name"]))
            self.rules_tbl.setItem(i,1,QTableWidgetItem(f"{r['threshold']} {r['unit']}"))
            self.rules_tbl.setItem(i,2,QTableWidgetItem(r["direction"]))
            chk = QTableWidgetItem("✓")
            chk.setForeground(QBrush(QColor(GREEN))); self.rules_tbl.setItem(i,3,chk)

    def _refresh_hist(self):
        h = list(reversed(self.history[-60:]))
        self.hist_tbl.setRowCount(len(h))
        for i, ev in enumerate(h):
            self.hist_tbl.setItem(i,0,QTableWidgetItem(ev["time"]))
            self.hist_tbl.setItem(i,1,QTableWidgetItem(ev["rule"]))
            item = QTableWidgetItem(ev["msg"])
            item.setForeground(QBrush(QColor(ORANGE)))
            self.hist_tbl.setItem(i,2,item)

    def check_traffic(self, up, down):
        now = time.time()
        for rule in self.rules:
            if not rule.get("enabled"): continue
            mult = 1024 if rule["unit"] == "KB/s" else 1024**2
            thr  = rule["threshold"] * mult
            hit  = (rule["direction"] in ("up","both") and up > thr) or \
                   (rule["direction"] in ("down","both") and down > thr)
            if hit:
                last = self._last_alert.get(rule["name"], 0)
                if now - last < 10: continue
                self._last_alert[rule["name"]] = now
                val = max(up, down)
                msg = f"Tráfico {rule['direction']}: {_fmt_bps(val)} > {rule['threshold']} {rule['unit']}"
                self.history.append({"time": datetime.now().strftime("%H:%M:%S"), "rule": rule["name"], "msg": msg})
                self.alert_bar.setText(f"  ⚠ ALERTA: {rule['name']} — {msg}")
                self.alert_bar.setStyleSheet(f"background:{RED}22; color:{RED}; border:1px solid {RED}; border-radius:6px; padding:10px; font-size:13px; font-weight:bold;")
                if rule.get("popup"):
                    QTimer.singleShot(100, lambda t=rule["name"], m=msg: QMessageBox.warning(self, f"Alerta: {t}", m))
                QTimer.singleShot(8000, self._clear_bar)
                self._refresh_hist()

    def _clear_bar(self):
        self.alert_bar.setText("  Sin alertas activas")
        self.alert_bar.setStyleSheet(f"background:{BG3}; color:{GREEN}; border-radius:6px; padding:10px; font-size:13px; font-weight:bold;")


# ── Default Rules ─────────────────────────────────────────────
DEFAULT_RULES = [
    ("Bloquear Telnet Entrada",      "in",  "block", "TCP", "23"),
    ("Bloquear FTP Entrada",         "in",  "block", "TCP", "21"),
    ("Bloquear RDP desde Internet",  "in",  "block", "TCP", "3389"),
    ("Bloquear NetBIOS Entrada",     "in",  "block", "TCP", "139"),
    ("Bloquear SMB Entrada",         "in",  "block", "TCP", "445"),
    ("Bloquear RPC Entrada",         "in",  "block", "TCP", "135"),
    ("Bloquear Telnet Salida",       "out", "block", "TCP", "23"),
    ("Bloquear SMTP Salida",         "out", "block", "TCP", "25"),
    ("Permitir HTTP Salida",         "out", "allow", "TCP", "80"),
    ("Permitir HTTPS Salida",        "out", "allow", "TCP", "443"),
    ("Permitir DNS Salida",          "out", "allow", "UDP", "53"),
    ("Permitir SSH Entrada",         "in",  "allow", "TCP", "22"),
    ("Bloquear WinRM Entrada",       "in",  "block", "TCP", "5985"),
    ("Bloquear mDNS Entrada",        "in",  "block", "UDP", "5353"),
    ("Bloquear UPnP Entrada",        "in",  "block", "TCP", "1900"),
    ("Bloquear VNC Entrada",         "in",  "block", "TCP", "5900"),
]


class DefaultRulesDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reglas de Seguridad por Defecto")
        self.setMinimumSize(740, 540)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        layout = QVBoxLayout(self)

        info = QLabel("Selecciona las reglas que deseas aplicar al Firewall de Windows.\n"
                       "Las reglas BLOCK aumentan la seguridad bloqueando puertos peligrosos. "
                       "Las reglas ALLOW garantizan conectividad básica.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{MUTED}; font-size:13px; padding:8px;")
        layout.addWidget(info)

        # Category buttons
        cat_row = QHBoxLayout()
        sel_all  = _btn("✔ Seleccionar Todo",   GREEN)
        sel_blk  = _btn("🛑 Solo BLOCK",         RED)
        sel_alw  = _btn("✅ Solo ALLOW",          BLUE)
        desel    = _btn("☐ Deseleccionar Todo",  MUTED)
        for b in [sel_all, sel_blk, sel_alw, desel]: cat_row.addWidget(b)
        layout.addLayout(cat_row)

        self.tbl = QTableWidget(len(DEFAULT_RULES), 5)
        self.tbl.setHorizontalHeaderLabels(["✓","Nombre","Dirección","Acción","Puerto"])
        hdr = self.tbl.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        for i in range(2,5): hdr.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.tbl.verticalHeader().hide()
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self._checks = []
        for i, (name, direc, action, proto, port) in enumerate(DEFAULT_RULES):
            chk = QCheckBox()
            chk.setChecked(True)
            self._checks.append(chk)
            cell = QWidget(); cl = QHBoxLayout(cell); cl.setContentsMargins(6,2,6,2); cl.addWidget(chk)
            self.tbl.setCellWidget(i, 0, cell)
            self.tbl.setItem(i, 1, QTableWidgetItem(name))
            dir_item = QTableWidgetItem("Entrada" if direc=="in" else "Salida")
            dir_item.setForeground(QBrush(QColor(ORANGE if direc=="out" else BLUE)))
            self.tbl.setItem(i, 2, dir_item)
            act_item = QTableWidgetItem(action.upper())
            act_item.setForeground(QBrush(QColor(RED if action=="block" else GREEN)))
            self.tbl.setItem(i, 3, act_item)
            self.tbl.setItem(i, 4, QTableWidgetItem(f"{proto} {port}"))
        layout.addWidget(self.tbl, 1)

        sel_all.clicked.connect(lambda: [c.setChecked(True)  for c in self._checks])
        desel.clicked.connect(lambda:   [c.setChecked(False) for c in self._checks])
        sel_blk.clicked.connect(lambda: [c.setChecked(DEFAULT_RULES[i][2]=="block") for i,c in enumerate(self._checks)])
        sel_alw.clicked.connect(lambda: [c.setChecked(DEFAULT_RULES[i][2]=="allow") for i,c in enumerate(self._checks)])

        self.progress = QProgressBar(); self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(100)
        self.log.setVisible(False)
        layout.addWidget(self.log)

        btns = QHBoxLayout()
        self.apply_btn = _btn("⚡ Aplicar Seleccionadas", GREEN)
        self.apply_btn.clicked.connect(self._apply)
        cancel = _btn("Cerrar", MUTED); cancel.clicked.connect(self.close)
        btns.addStretch(); btns.addWidget(self.apply_btn); btns.addWidget(cancel)
        layout.addLayout(btns)

    def _apply(self):
        selected = [(DEFAULT_RULES[i], c.isChecked()) for i, c in enumerate(self._checks) if c.isChecked()]
        if not selected:
            QMessageBox.information(self, "Sin selección", "Selecciona al menos una regla.")
            return
        self.apply_btn.setEnabled(False)
        self.progress.setVisible(True); self.progress.setMaximum(len(selected)); self.progress.setValue(0)
        self.log.setVisible(True)
        ok_count = err_count = 0
        for idx, ((name, direc, action, proto, port), _) in enumerate(selected):
            ok, msg = _add_rule(name, direc, action, proto, port)
            if ok:
                ok_count += 1
                self.log.appendHtml(f'<span style="color:{GREEN}">✓ {name}</span>')
            else:
                err_count += 1
                self.log.appendHtml(f'<span style="color:{RED}">✗ {name}: {msg}</span>')
            self.progress.setValue(idx+1)
            QApplication.processEvents()
        self.apply_btn.setEnabled(True)
        self.log.appendHtml(f'<br><b style="color:{GREEN}">Aplicadas: {ok_count} ✓ &nbsp; Errores: {err_count} ✗</b>')


# ── Firewall Rules ────────────────────────────────────────────
class RulesTab(QWidget):
    def __init__(self):
        super().__init__()
        self._rules  = []
        self._loader = FwRulesLoader()
        self._loader.ready.connect(self._on_loaded)
        layout = QVBoxLayout(self); layout.setContentsMargins(14,14,14,14); layout.setSpacing(8)

        tb = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Buscar regla...")
        self.search.textChanged.connect(self._filter)
        tb.addWidget(self.search, 1)
        reload  = _btn("↻ Recargar",      BLUE);   reload.clicked.connect(self._load)
        add     = _btn("+ Añadir",         GREEN);  add.clicked.connect(self._add_dlg)
        defbtn  = _btn("📋 Por Defecto",   PURPLE); defbtn.clicked.connect(self._default_dlg)
        delete  = _btn("✕ Eliminar",       RED);    delete.clicked.connect(self._delete)
        export  = _btn("⬇ Exportar",       ORANGE); export.clicked.connect(self._export)
        for b in [reload, add, defbtn, delete, export]: tb.addWidget(b)
        layout.addLayout(tb)

        self.tbl = QTableWidget(0, 7)
        self.tbl.setHorizontalHeaderLabels(["Nombre","Dirección","Acción","Protocolo","Puerto","IP Remota","Activa"])
        hdr = self.tbl.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1,7): hdr.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        self.tbl.verticalHeader().hide()
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setAlternatingRowColors(True)
        layout.addWidget(self.tbl)

        self.status = QLabel("Cargando reglas...")
        self.status.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        layout.addWidget(self.status)
        self._load()

    def _load(self):
        self.status.setText("Cargando reglas del sistema...")
        self._loader.load()

    def _on_loaded(self, rules):
        self._rules = rules
        self._filter(self.search.text())
        self.status.setText(f"{len(rules)} reglas de firewall cargadas  •  {datetime.now().strftime('%H:%M:%S')}")

    def _filter(self, text):
        shown = [r for r in self._rules if text.lower() in r.get("name","").lower()] if text else self._rules
        self.tbl.setRowCount(len(shown))
        for i, r in enumerate(shown):
            enabled = r.get("enabled","").lower() in ("yes","sí","si","habilitado")
            vals = [r.get("name",""), r.get("direction",""), r.get("action",""),
                    r.get("protocol",""), r.get("port","Any"), r.get("remote","Any")]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                act = r.get("action","").lower()
                if act == "block": item.setForeground(QBrush(QColor(RED)))
                elif act == "allow": item.setForeground(QBrush(QColor(GREEN)))
                self.tbl.setItem(i, j, item)
            chk = QTableWidgetItem("✓" if enabled else "✗")
            chk.setForeground(QBrush(QColor(GREEN if enabled else MUTED)))
            self.tbl.setItem(i, 6, chk)

    def _default_dlg(self):
        dlg = DefaultRulesDlg(self)
        dlg.exec_()
        self._load()

    def _add_dlg(self):
        dlg = AddRuleDlg(self)
        if dlg.exec_() == QDialog.Accepted:
            name, direction, action, protocol, port = dlg.values()
            ok, msg = _add_rule(name, direction, action, protocol, port)
            QMessageBox.information(self, "Resultado", "✓ Regla añadida" if ok else f"Error:\n{msg}")
            if ok: self._load()

    def _delete(self):
        row = self.tbl.currentRow()
        if row < 0: return
        name = self.tbl.item(row, 0).text()
        if QMessageBox.question(self,"Confirmar", f"¿Eliminar '{name}'?") == QMessageBox.Yes:
            ok, msg = _del_rule(name)
            QMessageBox.information(self,"Resultado","✓ Eliminada" if ok else f"Error:\n{msg}")
            if ok: self._load()

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(self,"Exportar","","Script BAT (*.bat);;JSON (*.json)")
        if not path: return
        if path.endswith(".json"):
            with open(path,"w") as f: json.dump(self._rules, f, indent=2)
        else:
            lines = ["@echo off","echo Importando reglas de firewall..."]
            for r in self._rules:
                cmd = f'netsh advfirewall firewall add rule name="{r.get("name","")}" dir={r.get("direction","in")} action={r.get("action","allow")} protocol={r.get("protocol","TCP")} enable=yes'
                if r.get("port","Any") not in ("Any",""): cmd += f' localport={r["port"]}'
                lines.append(cmd)
            with open(path,"w") as f: f.write("\n".join(lines))
        QMessageBox.information(self,"Exportado",f"Guardado en:\n{path}")

    def get_rules(self): return self._rules


class AddRuleDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Regla de Firewall"); self.setFixedSize(400,260)
        layout = QFormLayout(self)
        self.name  = QLineEdit(); self.name.setPlaceholderText("Mi Regla")
        self.dir   = QComboBox(); self.dir.addItems(["in","out"])
        self.act   = QComboBox(); self.act.addItems(["allow","block"])
        self.proto = QComboBox(); self.proto.addItems(["TCP","UDP","Any"])
        self.port  = QLineEdit(); self.port.setPlaceholderText("80 o 8000-9000 o Any")
        layout.addRow("Nombre:",     self.name)
        layout.addRow("Dirección:",  self.dir)
        layout.addRow("Acción:",     self.act)
        layout.addRow("Protocolo:",  self.proto)
        layout.addRow("Puerto:",     self.port)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        layout.addRow(btns)
    def values(self):
        return (self.name.text() or "Nueva Regla", self.dir.currentText(),
                self.act.currentText(), self.proto.currentText(), self.port.text() or "Any")


# ── Port Scanner ─────────────────────────────────────────────
class PortScanTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = PortScanWorker()
        self.worker.port_open.connect(self._on_open)
        self.worker.finished.connect(self._on_done)
        self._count = 0; self._total = 0

        layout = QVBoxLayout(self); layout.setContentsMargins(14,14,14,14); layout.setSpacing(10)

        ctrl = QHBoxLayout()
        self.host  = QLineEdit("127.0.0.1"); self.host.setPlaceholderText("IP o hostname")
        self.p1    = QSpinBox(); self.p1.setRange(1,65535); self.p1.setValue(1)
        self.p2    = QSpinBox(); self.p2.setRange(1,65535); self.p2.setValue(1024)
        self.tmo   = QDoubleSpinBox(); self.tmo.setRange(0.1,5.0); self.tmo.setValue(0.4)
        self.go    = _btn("▶ Escanear", GREEN, 120); self.go.clicked.connect(self._start)
        self.stop  = _btn("⏹ Detener",  RED,   100); self.stop.setEnabled(False); self.stop.clicked.connect(self._abort)
        ctrl.addWidget(QLabel("Host:")); ctrl.addWidget(self.host,2)
        ctrl.addWidget(QLabel("Puertos:")); ctrl.addWidget(self.p1)
        ctrl.addWidget(QLabel("–")); ctrl.addWidget(self.p2)
        ctrl.addWidget(QLabel("Timeout:")); ctrl.addWidget(self.tmo)
        ctrl.addWidget(self.go); ctrl.addWidget(self.stop)
        layout.addLayout(ctrl)

        self.progress = QProgressBar(); layout.addWidget(self.progress)

        split = QSplitter(Qt.Horizontal)

        open_g = _card("Puertos Abiertos")
        ol = QVBoxLayout(open_g)
        self.open_tbl = QTableWidget(0, 3)
        self.open_tbl.setHorizontalHeaderLabels(["Puerto","Estado","Servicio"])
        self.open_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.open_tbl.verticalHeader().hide()
        ol.addWidget(self.open_tbl)
        split.addWidget(open_g)

        hist_g = _card("Historial de Escaneos")
        hl = QVBoxLayout(hist_g)
        self.hist = QListWidget()
        hl.addWidget(self.hist)
        clr = _btn("Limpiar", MUTED); clr.clicked.connect(self.hist.clear)
        hl.addWidget(clr)
        split.addWidget(hist_g)

        layout.addWidget(split, 1)

        self.status_lbl = QLabel("Listo")
        self.status_lbl.setStyleSheet(f"color:{MUTED};")
        layout.addWidget(self.status_lbl)

    def _start(self):
        host = self.host.text().strip()
        if not host: return
        self.open_tbl.setRowCount(0); self._count = 0
        p1, p2 = self.p1.value(), self.p2.value()
        self._total = p2 - p1 + 1
        self.progress.setRange(0, self._total); self.progress.setValue(0)
        self.go.setEnabled(False); self.stop.setEnabled(True)
        self.status_lbl.setText(f"Escaneando {host} — puertos {p1}–{p2}...")
        self.worker.scan(host, p1, p2, self.tmo.value())

    def _abort(self):
        self.worker.abort(); self.go.setEnabled(True); self.stop.setEnabled(False)
        self.status_lbl.setText("Escaneo cancelado")

    def _on_open(self, port, svc):
        self._count += 1; self.progress.setValue(self.progress.value() + 1)
        row = self.open_tbl.rowCount(); self.open_tbl.insertRow(row)
        p_item = QTableWidgetItem(str(port)); p_item.setForeground(QBrush(QColor(GREEN)))
        self.open_tbl.setItem(row,0,p_item)
        self.open_tbl.setItem(row,1,QTableWidgetItem("ABIERTO"))
        self.open_tbl.setItem(row,2,QTableWidgetItem(svc))

    def _on_done(self, count):
        self.go.setEnabled(True); self.stop.setEnabled(False)
        self.progress.setValue(self._total)
        host = self.host.text(); ts = datetime.now().strftime("%H:%M:%S")
        self.status_lbl.setText(f"Completado — {count} puerto(s) abierto(s) de {self._total} escaneados")
        self.hist.insertItem(0, f"[{ts}] {host} puertos {self.p1.value()}–{self.p2.value()} → {count} abiertos")


# ── Sync Tab ─────────────────────────────────────────────────
class SyncTab(QWidget):
    def __init__(self, worker, rules_fn):
        super().__init__()
        self.worker = worker; self.rules_fn = rules_fn

        layout = QVBoxLayout(self); layout.setContentsMargins(14,14,14,14); layout.setSpacing(10)

        srv_g = _card("Servidor de Sincronización")
        sl = QHBoxLayout(srv_g)
        self.srv_lbl = QLabel("⚫ Inactivo")
        self.srv_lbl.setStyleSheet(f"color:{RED}; font-weight:bold;")
        self.srv_start = _btn("▶ Iniciar Servidor", GREEN, 160)
        self.srv_stop  = _btn("⏹ Detener", RED, 110); self.srv_stop.setEnabled(False)
        self.srv_start.clicked.connect(self._start_srv)
        self.srv_stop.clicked.connect(self._stop_srv)
        sl.addWidget(self.srv_lbl,1)
        sl.addWidget(QLabel(f"Puerto: {worker.PORT}"))
        sl.addWidget(self.srv_start); sl.addWidget(self.srv_stop)
        layout.addWidget(srv_g)

        main = QHBoxLayout()

        # Peer discovery
        peer_g = _card("Dispositivos en Red")
        pl = QVBoxLayout(peer_g)
        drow = QHBoxLayout()
        self.subnet = QLineEdit(); self.subnet.setPlaceholderText("192.168.1.0")
        ip = _my_ip(); parts = ip.split(".")
        if len(parts)==4: self.subnet.setText(".".join(parts[:3])+".0")
        scan_btn = _btn("🔍 Buscar Peers", BLUE, 150)
        scan_btn.clicked.connect(self._scan)
        drow.addWidget(self.subnet,1); drow.addWidget(scan_btn)
        pl.addLayout(drow)

        self.peer_tbl = QTableWidget(0, 3)
        self.peer_tbl.setHorizontalHeaderLabels(["IP","Hostname","Acción"])
        self.peer_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.peer_tbl.verticalHeader().hide()
        pl.addWidget(self.peer_tbl)
        main.addWidget(peer_g, 1)

        # Log
        log_g = _card("Log de Sincronización")
        ll = QVBoxLayout(log_g)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True)
        ll.addWidget(self.log)
        clr = _btn("Limpiar", MUTED); clr.clicked.connect(self.log.clear)
        ll.addWidget(clr)
        main.addWidget(log_g, 1)

        layout.addLayout(main, 1)

        worker.peer_found.connect(self._on_peer)
        worker.sync_done.connect(self._on_sync)
        worker.log_msg.connect(self._log)

    def _start_srv(self):
        self.worker.start_server(self.rules_fn)
        self.srv_lbl.setText("🟢 Servidor activo")
        self.srv_lbl.setStyleSheet(f"color:{GREEN}; font-weight:bold;")
        self.srv_start.setEnabled(False); self.srv_stop.setEnabled(True)

    def _stop_srv(self):
        self.worker.stop_server()
        self.srv_lbl.setText("⚫ Inactivo")
        self.srv_lbl.setStyleSheet(f"color:{RED}; font-weight:bold;")
        self.srv_start.setEnabled(True); self.srv_stop.setEnabled(False)

    def _scan(self):
        self.peer_tbl.setRowCount(0)
        self.worker.scan_peers(self.subnet.text().strip())

    def _on_peer(self, ip, host):
        row = self.peer_tbl.rowCount(); self.peer_tbl.insertRow(row)
        self.peer_tbl.setItem(row,0,QTableWidgetItem(ip))
        self.peer_tbl.setItem(row,1,QTableWidgetItem(host))
        btn2 = QPushButton("⬇ Importar Reglas")
        btn2.setStyleSheet(f"background:{ACC}; color:{TEXT}; border-radius:4px; padding:3px;")
        btn2.clicked.connect(lambda _, i=ip: self.worker.pull_rules(i))
        self.peer_tbl.setCellWidget(row,2,btn2)

    def _on_sync(self, msg, ok):
        self._log(("✓ " if ok else "✗ ") + msg)
        if ok: QMessageBox.information(self,"Sync",msg)

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.appendPlainText(f"[{ts}] {msg}")


# ── Net Info Tab ─────────────────────────────────────────────
class NetInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(14,14,14,14); layout.setSpacing(10)

        row = QHBoxLayout()
        self.c_ip   = self._card("Mi IP (WiFi/LAN)", _my_ip(),             BLUE)
        self.c_gw   = self._card("Gateway (Router)", _gateway(),           GREEN)
        self.c_host = self._card("Hostname",          socket.gethostname(), PURPLE)
        self.c_psut = self._card("psutil",            "✓ Instalado" if HAS_PSUTIL else "✗ No disponible",
                                 GREEN if HAS_PSUTIL else RED)
        for c in [self.c_ip, self.c_gw, self.c_host, self.c_psut]: row.addWidget(c)
        layout.addLayout(row)

        ref = _btn("↻ Actualizar", BLUE); ref.clicked.connect(self._refresh)
        layout.addWidget(ref)

        iface_g = _card("Interfaces de Red")
        il = QVBoxLayout(iface_g)
        self.iface_tbl = QTableWidget(0, 5)
        self.iface_tbl.setHorizontalHeaderLabels(["Interfaz","IP","Máscara","Enviado","Recibido"])
        self.iface_tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.iface_tbl.verticalHeader().hide()
        self.iface_tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        il.addWidget(self.iface_tbl)
        layout.addWidget(iface_g)

        raw_g = _card("ipconfig /all")
        rl = QVBoxLayout(raw_g)
        self.raw = QPlainTextEdit(); self.raw.setReadOnly(True)
        rl.addWidget(self.raw)
        layout.addWidget(raw_g, 1)

        self._refresh()

    def _card(self, title, value, color):
        w = QWidget()
        w.setStyleSheet(f"background:{BG3}; border:1px solid {BORDER}; border-radius:8px;")
        vl = QVBoxLayout(w); vl.setContentsMargins(14,10,14,10)
        t = QLabel(title); t.setStyleSheet(f"color:{MUTED}; font-size:11px; border:none; background:transparent;")
        v = QLabel(value); v.setStyleSheet(f"color:{color}; font-size:16px; font-weight:bold; border:none; background:transparent;")
        v.setWordWrap(True); vl.addWidget(t); vl.addWidget(v); w._v = v; return w

    def _refresh(self):
        self.c_ip._v.setText(_my_ip()); self.c_gw._v.setText(_gateway())
        self._load_ifaces(); self._load_raw()

    def _load_ifaces(self):
        self.iface_tbl.setRowCount(0)
        if not HAS_PSUTIL: return
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_io_counters(pernic=True)
            for iface, addr_list in addrs.items():
                ip = mask = "N/D"
                for a in addr_list:
                    if a.family == socket.AF_INET:
                        ip = a.address; mask = a.netmask or "N/D"
                st = stats.get(iface)
                row = self.iface_tbl.rowCount(); self.iface_tbl.insertRow(row)
                for j, v in enumerate([iface, ip, mask,
                                        _fmt_bytes(st.bytes_sent) if st else "N/D",
                                        _fmt_bytes(st.bytes_recv) if st else "N/D"]):
                    self.iface_tbl.setItem(row,j,QTableWidgetItem(v))
        except: pass

    def _load_raw(self):
        try:
            r = subprocess.run(["ipconfig","/all"], capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.raw.setPlainText(r.stdout)
        except Exception as e:
            self.raw.setPlainText(f"Error: {e}")


# ── TCP Traces Live ──────────────────────────────────────────
STATE_COLORS = {
    "ESTABLISHED": GREEN,  "LISTEN":    BLUE,    "TIME_WAIT": YELLOW,
    "CLOSE_WAIT":  ORANGE, "SYN_SENT":  PURPLE,  "SYN_RECV":  PURPLE,
    "FIN_WAIT1":   MUTED,  "FIN_WAIT2": MUTED,   "CLOSING":   RED,
    "CLOSE":       RED,    "NONE":      MUTED,
}


class TcpTracesWorker(QObject):
    data_ready = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._running = False

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self): self._running = False

    def _loop(self):
        while self._running:
            try:
                pid_map = {}
                if HAS_PSUTIL:
                    for proc in psutil.process_iter(["pid","name"]):
                        try: pid_map[proc.info["pid"]] = proc.info["name"] or "?"
                        except: pass
                result = []
                for conn in psutil.net_connections(kind="inet"):
                    laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
                    raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
                    pid   = conn.pid or 0
                    fam   = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
                    result.append({
                        "pid":    pid,
                        "name":   pid_map.get(pid, "Sistema"),
                        "laddr":  laddr,
                        "raddr":  raddr,
                        "status": conn.status or "NONE",
                        "family": fam,
                    })
                self.data_ready.emit(result)
            except: pass
            time.sleep(1.0)


class TcpTracesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = TcpTracesWorker()
        self.worker.data_ready.connect(self._on_data)
        self._paused = False
        self._prev_est = set()
        self._all_conns = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14,14,14,14); layout.setSpacing(10)

        # Controls row
        ctrl = QHBoxLayout()
        lbl_s = QLabel("Estado:")
        lbl_s.setStyleSheet("font-size:14px;")
        self.filter_state = QComboBox()
        self.filter_state.addItems(["Todos","ESTABLISHED","LISTEN","TIME_WAIT","CLOSE_WAIT","SYN_SENT"])
        self.filter_state.currentTextChanged.connect(lambda _: self._apply_filter())
        self.filter_proc = QLineEdit(); self.filter_proc.setPlaceholderText("Filtrar proceso...")
        self.filter_proc.textChanged.connect(lambda _: self._apply_filter())
        self.filter_ip = QLineEdit(); self.filter_ip.setPlaceholderText("Filtrar IP remota...")
        self.filter_ip.textChanged.connect(lambda _: self._apply_filter())
        self.pause_btn = _btn("⏸ Pausar", ORANGE)
        self.pause_btn.clicked.connect(self._toggle_pause)
        clr_log = _btn("Limpiar Log", MUTED)
        clr_log.clicked.connect(lambda: self.log.clear())
        ctrl.addWidget(lbl_s); ctrl.addWidget(self.filter_state)
        ctrl.addWidget(self.filter_proc, 1); ctrl.addWidget(self.filter_ip, 1)
        ctrl.addWidget(self.pause_btn); ctrl.addWidget(clr_log)
        layout.addLayout(ctrl)

        # Stats bar
        sr = QHBoxLayout()
        self.lbl_total = self._stat("Total: 0",        TEXT)
        self.lbl_est   = self._stat("ESTABLISHED: 0",  GREEN)
        self.lbl_lst   = self._stat("LISTEN: 0",       BLUE)
        self.lbl_tw    = self._stat("TIME_WAIT: 0",    YELLOW)
        self.lbl_cw    = self._stat("CLOSE_WAIT: 0",   ORANGE)
        for l in [self.lbl_total, self.lbl_est, self.lbl_lst, self.lbl_tw, self.lbl_cw]:
            sr.addWidget(l)
        sr.addStretch()
        layout.addLayout(sr)

        # Splitter: table + event log
        split = QSplitter(Qt.Vertical)

        conn_g = _card("Conexiones TCP/UDP en Vivo (auto-refresh 1s)")
        cl = QVBoxLayout(conn_g)
        self.tbl = QTableWidget(0, 6)
        self.tbl.setHorizontalHeaderLabels(["Proceso","PID","Dir. Local","Dir. Remota","Estado","Tipo"])
        hdr = self.tbl.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tbl.verticalHeader().hide()
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        cl.addWidget(self.tbl)
        split.addWidget(conn_g)

        log_g = _card("Eventos: Nuevas / Cerradas conexiones ESTABLISHED")
        ll = QVBoxLayout(log_g)
        self.log = QPlainTextEdit(); self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(800)
        ll.addWidget(self.log)
        split.addWidget(log_g)

        split.setSizes([450, 200])
        layout.addWidget(split, 1)

        if HAS_PSUTIL:
            self.worker.start()
        else:
            self.log.appendPlainText("psutil no instalado — ejecuta: py -m pip install psutil")

    def _stat(self, text, color):
        l = QLabel(text)
        l.setStyleSheet(f"color:{color}; font-size:14px; font-weight:bold; "
                        f"background:{BG3}; border-radius:6px; padding:5px 12px;")
        return l

    def _toggle_pause(self):
        self._paused = not self._paused
        self.pause_btn.setText("▶ Reanudar" if self._paused else "⏸ Pausar")
        col = GREEN if self._paused else ORANGE
        self.pause_btn.setStyleSheet(
            f"QPushButton{{background:{col};border:none;border-radius:6px;padding:10px 20px;"
            f"font-size:14px;font-weight:bold;}}")

    def _on_data(self, conns):
        if self._paused: return
        self._all_conns = conns

        curr_est = {(c["laddr"], c["raddr"]) for c in conns if c["status"] == "ESTABLISHED"}
        new_c    = curr_est - self._prev_est
        closed_c = self._prev_est - curr_est

        ts = datetime.now().strftime("%H:%M:%S")
        for (la, ra) in new_c:
            name = next((c["name"] for c in conns if c["laddr"]==la), "?")
            self.log.appendHtml(
                f'<span style="color:{GREEN}">[{ts}] ▶ NUEVA &nbsp;&nbsp;&nbsp;'
                f'<b>{name[:22]:22s}</b> &nbsp; {la} → {ra}</span>')
        for (la, ra) in closed_c:
            self.log.appendHtml(
                f'<span style="color:{RED}">[{ts}] ✕ CERRADA &nbsp;&nbsp;&nbsp;'
                f'{la} → {ra}</span>')

        self._prev_est = curr_est

        est  = sum(1 for c in conns if c["status"]=="ESTABLISHED")
        lst  = sum(1 for c in conns if c["status"]=="LISTEN")
        tw   = sum(1 for c in conns if c["status"]=="TIME_WAIT")
        cw   = sum(1 for c in conns if c["status"]=="CLOSE_WAIT")
        self.lbl_total.setText(f"Total: {len(conns)}")
        self.lbl_est.setText(f"ESTABLISHED: {est}")
        self.lbl_lst.setText(f"LISTEN: {lst}")
        self.lbl_tw.setText(f"TIME_WAIT: {tw}")
        self.lbl_cw.setText(f"CLOSE_WAIT: {cw}")

        self._apply_filter()

    def _apply_filter(self):
        sf = self.filter_state.currentText()
        pf = self.filter_proc.text().lower()
        rf = self.filter_ip.text().lower()
        shown = [c for c in self._all_conns
                 if (sf == "Todos" or c["status"] == sf)
                 and (not pf or pf in c["name"].lower())
                 and (not rf or rf in c["raddr"].lower())]
        self.tbl.setRowCount(len(shown))
        for i, c in enumerate(shown):
            col = STATE_COLORS.get(c["status"], MUTED)
            vals = [c["name"], str(c["pid"]) if c["pid"] else "-",
                    c["laddr"], c["raddr"], c["status"], c["family"]]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                if j == 4:
                    item.setForeground(QBrush(QColor(col)))
                elif j == 3 and c["raddr"] != "-" and c["status"] == "ESTABLISHED":
                    item.setForeground(QBrush(QColor(ORANGE)))
                self.tbl.setItem(i, j, item)


# ══════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("[ FIREWALL_SYS v2.0 ] // MATRIX MODE // TRAFFIC SYNC ACTIVE")
        self.setMinimumSize(1180, 760)
        self.setStyleSheet(BASE_STYLE)
        self._build()
        self._start_monitor()
        self.resize(1400, 900)
        self.show()
        if not self._is_admin():
            self.statusBar().showMessage(
                ">> WARNING: no root privileges — rule management may fail | run as Administrator for full control",8000)

    def _is_admin(self):
        try:
            import ctypes; return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except: return False

    def _build(self):
        # Status bar
        sb = self.statusBar()
        _sf = f"font-family:'Courier New',monospace; font-size:12px; font-weight:bold; padding:0 10px; border-left:1px solid {BORDER};"
        self._sb_up   = QLabel("TX: 0 B/s");   self._sb_up.setStyleSheet(_sf + f"color:{GREEN};")
        self._sb_down = QLabel("RX: 0 B/s");   self._sb_down.setStyleSheet(_sf + f"color:{BLUE};")
        self._sb_conn = QLabel("CONN: 0");      self._sb_conn.setStyleSheet(_sf + f"color:{ORANGE};")
        self._sb_sys  = QLabel(">> SYS_OK");    self._sb_sys.setStyleSheet(_sf + f"color:{MUTED};")
        sb.addPermanentWidget(self._sb_sys)
        sb.addPermanentWidget(self._sb_up)
        sb.addPermanentWidget(self._sb_down)
        sb.addPermanentWidget(self._sb_conn)

        # Menu
        mb = self.menuBar()
        fm = mb.addMenu("Archivo")
        fm.addAction("Exportar Reglas", lambda: self.rules_tab._export())
        fm.addSeparator(); fm.addAction("Salir", self.close)
        vm = mb.addMenu("Ver")
        vm.addAction("Recargar Reglas", lambda: self.rules_tab._load())
        vm.addAction("Actualizar Red",  lambda: self.net_tab._refresh())
        mb.addMenu("Ayuda").addAction("Acerca de", self._about)

        # Tabs (side)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border:none; border-left:1px solid {BORDER}; background:{BG}; }}
            QTabBar {{ background:{BG}; border-right:1px solid {BORDER}; }}
            QTabBar::tab {{ background:{BG}; color:{MUTED}; border:none; border-bottom:1px solid {BORDER};
                            padding:14px 4px; font-size:11px; font-family:'Courier New',monospace;
                            min-height:80px; width:86px; letter-spacing:1px; }}
            QTabBar::tab:selected {{ background:{BG2}; color:{GREEN}; border-left:3px solid {GREEN};
                                     font-weight:bold; }}
            QTabBar::tab:hover {{ background:{ACC}; color:{GREEN}; }}
        """)

        self.syncer    = SyncWorker()
        self.dash_tab  = DashboardTab()
        self.traf_tab  = TrafficTab()
        self.alrt_tab  = AlertsTab()
        self.rules_tab = RulesTab()
        self.sync_tab  = SyncTab(self.syncer, self.rules_tab.get_rules)
        self.scan_tab  = PortScanTab()
        self.tcp_tab   = TcpTracesTab()
        self.net_tab   = NetInfoTab()

        tabs_data = [
            (self.dash_tab,  "//\nDASH"),
            (self.traf_tab,  "//\nTRAFIC"),
            (self.alrt_tab,  "//\nALERTS"),
            (self.rules_tab, "//\nRULES"),
            (self.sync_tab,  "//\nSYNC"),
            (self.scan_tab,  "//\nSCAN"),
            (self.tcp_tab,   "//\nTCP"),
            (self.net_tab,   "//\nNET"),
        ]
        for widget, label in tabs_data:
            self.tabs.addTab(widget, label)

        self.setCentralWidget(self.tabs)

    def _start_monitor(self):
        if not HAS_PSUTIL:
            self.statusBar().showMessage("psutil no instalado — instala con: py -m pip install psutil", 6000)
            return
        self.monitor = TrafficWorker()
        self.monitor.data_ready.connect(self._on_traffic)
        self.monitor.start()

    def _on_traffic(self, d):
        self.dash_tab.update(d)
        self.traf_tab.update(d)
        self.alrt_tab.check_traffic(d["up"], d["down"])
        self._sb_up.setText(f"TX: {_fmt_bps(d['up'])}")
        self._sb_down.setText(f"RX: {_fmt_bps(d['down'])}")
        self._sb_conn.setText(f"CONN: {d['connections']}")

    def _about(self):
        QMessageBox.about(self, "Firewall Manager v2.0",
            "<b>Firewall Manager v2.0</b><br>Tráfico Sync para Windows<br><br>"
            "• 📊 Dashboard — tráfico en tiempo real<br>"
            "• 📡 Tráfico — monitoreo por proceso<br>"
            "• 🔔 Alertas — umbrales de ancho de banda<br>"
            "• 🛡 Reglas — gestión del Firewall Windows<br>"
            "• 🔄 Sync — sincronización de reglas en red<br>"
            "• 🔍 Escáner — escáner de puertos TCP<br>"
            "• 🌐 Red Info — interfaces y configuración")

    def closeEvent(self, ev):
        if hasattr(self, "monitor"): self.monitor.stop()
        self.syncer.stop_server()
        ev.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Firewall Manager v2.0")
    w = MainWindow()
    sys.exit(app.exec_())
