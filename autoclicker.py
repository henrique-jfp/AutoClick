import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import threading
import time
import random
import json
import os
import sys
import ctypes
from pynput import keyboard, mouse
from PIL import Image, ImageTk

# Optional pystray for system tray integration
try:
    import pystray
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

# Sound support on Windows
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


def check_is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def relaunch_as_admin():
    try:
        if not check_is_admin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]), None, 1
            )
            sys.exit(0)
    except Exception as e:
        messagebox.showerror("Erro de Privilégio", f"Não foi possível reiniciar como Administrador: {e}")


# Enable Windows High-Precision Timer (1ms resolution)
def set_windows_high_precision_timer(enable=True):
    try:
        winmm = ctypes.windll.winmm
        if enable:
            winmm.timeBeginPeriod(1)
        else:
            winmm.timeEndPeriod(1)
    except Exception:
        pass

# --- UI CONSTANTS & UTILITIES ---
COLOR_BG_MAIN = "#0F1117"
COLOR_BG_CARD = "#171A23"
COLOR_BG_INPUT = "#1E212C"
COLOR_BORDER = "#2A2E3A"
COLOR_PRIMARY = "#5B8CFF"
COLOR_PRIMARY_HOVER = "#4A78E6"
COLOR_SUCCESS = "#3ECF8E"
COLOR_SUCCESS_HOVER = "#33B87D"
COLOR_ERROR = "#FF5C5C"
COLOR_ERROR_HOVER = "#E64A4A"
COLOR_WARNING = "#FFB84D"
COLOR_TEXT_MAIN = "#F5F6FA"
COLOR_TEXT_SEC = "#9BA1B0"
COLOR_TEXT_DISABLED = "#5A5F6E"

FONT_MAIN = "Inter"
FONT_MONO = "JetBrains Mono"

def bind_hover(widget, normal_bg, hover_bg, normal_fg=None, hover_fg=None):
    def on_enter(e):
        if widget["state"] != "disabled":
            widget.config(bg=hover_bg)
            if hover_fg: widget.config(fg=hover_fg)
    def on_leave(e):
        if widget["state"] != "disabled":
            widget.config(bg=normal_bg)
            if normal_fg: widget.config(fg=normal_fg)
    widget.bind("<Enter>", on_enter, add="+")
    widget.bind("<Leave>", on_leave, add="+")

class ToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        if not self.text: return
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert") or (0,0,0,0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        tw.attributes("-topmost", True)
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         bg=COLOR_BG_INPUT, fg=COLOR_TEXT_MAIN, relief=tk.SOLID, borderwidth=1,
                         font=(FONT_MAIN, 9, "normal"), padx=4, pady=2)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_kbd_chip(parent, text):
    f = tk.Frame(parent, bg=COLOR_BORDER, padx=1, pady=1)
    inner = tk.Frame(f, bg=COLOR_BG_INPUT)
    inner.pack(fill="both", expand=True)
    lbl = tk.Label(inner, text=text, font=(FONT_MONO, 10, "bold"), bg=COLOR_BG_INPUT, fg=COLOR_TEXT_MAIN, padx=4, pady=1)
    lbl.pack()
    return f, lbl

def truncate_text(widget, max_width, original_text, font_measurer=None):
    if not original_text: return
    # Basic proportional approximation if exact measurement is heavy
    char_width_approx = 7 
    max_chars = max(3, max_width // char_width_approx)
    if len(original_text) > max_chars:
        widget.config(text=original_text[:max_chars-3] + "...")
        if not hasattr(widget, '_tooltip'):
            widget._tooltip = ToolTip(widget, original_text)
        else:
            widget._tooltip.text = original_text
    else:
        widget.config(text=original_text)
        if hasattr(widget, '_tooltip'):
            widget._tooltip.text = ""

class PulseIndicator(tk.Canvas):
    def __init__(self, parent, size=12, color_on=COLOR_SUCCESS, color_off=COLOR_TEXT_DISABLED, **kwargs):
        super().__init__(parent, width=size, height=size, bg=kwargs.pop('bg', COLOR_BG_CARD), highlightthickness=0, **kwargs)
        self.size = size
        self.color_on = color_on
        self.color_off = color_off
        self.is_active = False
        self.pulse_state = 0
        self.oval = self.create_oval(2, 2, size-2, size-2, fill=self.color_off, outline="")
        
    def set_state(self, active):
        self.is_active = active
        if active:
            self.pulse()
        else:
            self.itemconfig(self.oval, fill=self.color_off)
            self.coords(self.oval, 2, 2, self.size-2, self.size-2)

    def pulse(self):
        if not self.is_active: return
        self.pulse_state = (self.pulse_state + 1) % 20
        # breathing effect
        offset = abs(10 - self.pulse_state) / 10.0 * 2
        self.coords(self.oval, 2+offset, 2+offset, self.size-2-offset, self.size-2-offset)
        self.itemconfig(self.oval, fill=self.color_on)
        self.after(50, self.pulse)




class ModularMacroDialog(tk.Toplevel):
    """Dynamic Modular Step-by-Step Macro Builder & Editor Dialog (Full Featured)"""
    def __init__(self, parent, game_name, preset_data=None, on_save_callback=None):
        super().__init__(parent)
        self.title("🧙‍♂️ Criador Modular Avançado de Macros por Blocos")
        self.minsize(620, 700)
        self.resizable(True, True)
        
        # Center window and adapt to screen height
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        w, h = 640, 840
        if screen_h < 900:
            h = screen_h - 80
        
        x = int((screen_w / 2) - (w / 2))
        y = int((screen_h / 2) - (h / 2))
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.configure(bg=COLOR_BG_MAIN)
        self.transient(parent)
        self.grab_set()

        self.on_save_callback = on_save_callback
        self.game_name = game_name
        self.editing_preset = preset_data is not None

        # Color Palette
        self.bg_color = COLOR_BG_MAIN
        self.card_bg = COLOR_BG_CARD
        self.card_border = COLOR_BORDER
        self.accent_color = COLOR_PRIMARY
        self.text_color = COLOR_TEXT_MAIN
        self.text_subtle = COLOR_TEXT_SEC
        self.success_color = COLOR_SUCCESS
        self.danger_color = COLOR_ERROR
        self.warning_color = COLOR_WARNING

        # Preset Name, Start Hotkey & Emergency Hotkey Variables
        init_name = preset_data.get("name", "Novo Preset Modular") if preset_data else "Novo Preset Modular"
        init_hotkey = preset_data.get("hotkey_name", "F12") if preset_data else "F12"
        init_emergency = preset_data.get("emergency_hotkey_name", "ESC") if preset_data else "ESC"

        self.var_name = tk.StringVar(value=init_name)
        self.var_hotkey_name = tk.StringVar(value=init_hotkey)
        self.var_emergency_hotkey = tk.StringVar(value=init_emergency)

        # Convert/Extract Modular Steps List
        self.steps = self._extract_or_convert_steps(preset_data)

        self._create_widgets()
        self._render_steps()
        self._update_live_preview()

    def _extract_or_convert_steps(self, preset_data):
        if not preset_data:
            # Default new macro template (Genshin Stamina Loop style)
            return [
                {"type": "press_hold", "enabled": True, "key": "w"},
                {"type": "tap_loop", "enabled": True, "key": "shift", "count": 7, "interval_sec": 1.0, "use_range": False, "interval_min": 0.8, "interval_max": 1.2},
                {"type": "release", "enabled": True, "key": "w"},
                {"type": "pause", "enabled": True, "duration_sec": 0.45, "use_range": False, "duration_min": 0.3, "duration_max": 0.6},
                {"type": "hold_duration", "enabled": True, "key": "w", "duration_sec": 6.0, "use_range": False, "duration_min": 5.0, "duration_max": 7.0}
            ]

        # 1. Existing modular steps
        if "modular_steps" in preset_data and isinstance(preset_data["modular_steps"], list) and preset_data["modular_steps"]:
            steps_copy = json.loads(json.dumps(preset_data["modular_steps"]))
            for s in steps_copy:
                if "enabled" not in s:
                    s["enabled"] = True
            return steps_copy

        # 2. Legacy step_macro or dash5x_cooldown
        if "step_macro_config" in preset_data:
            cfg = preset_data["step_macro_config"]
            return [
                {"type": "press_hold", "enabled": True, "key": cfg.get("hold_key", "w")},
                {"type": "tap_loop", "enabled": True, "key": cfg.get("tap_key", "shift"), "count": int(cfg.get("tap_count", 7)), "interval_sec": float(cfg.get("tap_interval_sec", 1.0))},
                {"type": "release", "enabled": True, "key": cfg.get("hold_key", "w")},
                {"type": "pause", "enabled": True, "duration_sec": float(cfg.get("pause_sec", 0.45))},
                {"type": "hold_duration", "enabled": True, "key": cfg.get("cooldown_hold_key", "w"), "duration_sec": float(cfg.get("cooldown_walk_sec", 6.0))}
            ]

        target_type = preset_data.get("target_type", "")
        if target_type in ["dash5x_cooldown", "step_macro"]:
            return [
                {"type": "press_hold", "enabled": True, "key": "w"},
                {"type": "tap_loop", "enabled": True, "key": "shift", "count": 7, "interval_sec": 1.0},
                {"type": "release", "enabled": True, "key": "w"},
                {"type": "pause", "enabled": True, "duration_sec": 0.45},
                {"type": "hold_duration", "enabled": True, "key": "w", "duration_sec": 6.0}
            ]

        # 3. Legacy sequence combo
        if target_type == "sequence":
            raw_seq = preset_data.get("target_sequence_raw", ["shift+space"])
            interval_ms = preset_data.get("interval_ms", 820)
            return [
                {"type": "sequence_combo", "enabled": True, "sequence_raw": raw_seq, "interval_ms": interval_ms}
            ]

        # 4. Default fallback step template
        return [
            {"type": "press_hold", "enabled": True, "key": "w"},
            {"type": "tap_loop", "enabled": True, "key": "shift", "count": 7, "interval_sec": 1.0},
            {"type": "release", "enabled": True, "key": "w"},
            {"type": "pause", "enabled": True, "duration_sec": 0.45},
            {"type": "hold_duration", "enabled": True, "key": "w", "duration_sec": 6.0}
        ]

    def _create_widgets(self):
        # Header Banner with JSON Import/Export Buttons
        f_head = tk.Frame(self, bg=self.bg_color)
        f_head.pack(fill="x", padx=15, pady=8)

        f_title = tk.Frame(f_head, bg=self.bg_color)
        f_title.pack(side="left")

        title_text = "✏️ Editar Preset por Blocos" if self.editing_preset else "🧙‍♂️ Criar Macro Modular por Blocos"
        tk.Label(f_title, text=title_text, font=(FONT_MAIN, 12, "bold"), bg=self.bg_color, fg=self.accent_color).pack(anchor="w")
        tk.Label(f_title, text=f"Perfil do Jogo: {self.game_name}", font=(FONT_MAIN, 8), bg=self.bg_color, fg=self.warning_color).pack(anchor="w")

        # JSON Import/Export Controls Top-Right
        f_json = tk.Frame(f_head, bg=self.bg_color)
        f_json.pack(side="right")

        btn_imp = tk.Button(
            f_json, text="📥 Importar JSON", font=(FONT_MAIN, 8, "bold"), bg=COLOR_BORDER, fg=self.accent_color, bd=0, padx=6, pady=3, cursor="hand2", command=self._import_preset_json
        )
        btn_imp.pack(side="left", padx=2)

        btn_exp = tk.Button(
            f_json, text="📤 Exportar JSON", font=(FONT_MAIN, 8, "bold"), bg=COLOR_BORDER, fg=self.warning_color, bd=0, padx=6, pady=3, cursor="hand2", command=self._export_preset_json
        )
        btn_exp.pack(side="left", padx=2)

        # Name & Hotkey Setup Card
        f_meta_card = tk.Frame(self, bg=self.card_bg, padx=10, pady=6)
        f_meta_card.pack(fill="x", padx=15, pady=3)

        r1 = tk.Frame(f_meta_card, bg=self.card_bg)
        r1.pack(fill="x", pady=2)

        tk.Label(r1, text="Nome do Preset:", font=(FONT_MAIN, 9, "bold"), bg=self.card_bg, fg=self.text_color).pack(side="left")
        e_name = tk.Entry(r1, textvariable=self.var_name, font=(FONT_MAIN, 9, "bold"), bg=COLOR_BG_MAIN, fg=self.warning_color, bd=1, insertbackground="white")
        e_name.pack(side="left", fill="x", expand=True, padx=(8, 0))
        e_name.bind("<KeyRelease>", lambda e: self._update_live_preview())

        r2 = tk.Frame(f_meta_card, bg=self.card_bg)
        r2.pack(fill="x", pady=4)

        tk.Label(r2, text="⌨️ Atalho Início:", font=(FONT_MAIN, 8, "bold"), bg=self.card_bg, fg=self.accent_color).pack(side="left")
        e_hk = tk.Entry(r2, textvariable=self.var_hotkey_name, width=6, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=self.warning_color, bd=1)
        e_hk.pack(side="left", padx=4)

        tk.Label(r2, text="🚨 Parada de Emergência:", font=(FONT_MAIN, 8, "bold"), bg=self.card_bg, fg=self.danger_color).pack(side="left", padx=(10, 2))
        e_em = tk.Entry(r2, textvariable=self.var_emergency_hotkey, width=6, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=self.danger_color, bd=1)
        e_em.pack(side="left", padx=4)

        # Add Step Control Bar (Expanded with Mouse & Group Actions)
        f_add_bar = tk.Frame(self, bg=self.card_bg, padx=10, pady=8)
        f_add_bar.pack(fill="x", padx=15, pady=3)

        tk.Label(f_add_bar, text="➕ Adicionar Etapa ao Fluxo:", font=(FONT_MAIN, 9, "bold"), bg=self.card_bg, fg=self.accent_color).pack(anchor="w", pady=(0, 4))

        # Row 1: Keyboard & Delay Actions
        f_add_row1 = tk.Frame(f_add_bar, bg=self.card_bg)
        f_add_row1.pack(fill="x", pady=1)

        add_buttons_row1 = [
            ("✊ Segurar", "press_hold"),
            ("🔄 Repetir", "tap_loop"),
            ("👐 Soltar", "release"),
            ("⏱️ Pausa", "pause"),
            ("🚶 Caminhar", "hold_duration"),
            ("🔤 Combo", "sequence_combo")
        ]

        for label, stype in add_buttons_row1:
            btn = tk.Button(f_add_row1, text=label, font=(FONT_MAIN, 8, "bold"), bg=COLOR_BORDER, fg=self.text_color, activebackground=COLOR_BORDER, bd=0, padx=5, pady=2, cursor="hand2", command=lambda t=stype: self.add_step(t))
            btn.pack(side="left", padx=1)

        # Row 2: Mouse Actions & Grouping
        f_add_row2 = tk.Frame(f_add_bar, bg=self.card_bg)
        f_add_row2.pack(fill="x", pady=(3, 1))

        add_buttons_row2 = [
            ("🖱️ Clique", "mouse_click"),
            ("📍 Mover", "mouse_move"),
            ("🖐️ Arrastar", "mouse_drag"),
            ("📜 Rolar", "mouse_scroll"),
            ("📦 Agrupar", "group_block")
        ]

        for label, stype in add_buttons_row2:
            btn = tk.Button(f_add_row2, text=label, font=(FONT_MAIN, 8, "bold"), bg=COLOR_BORDER, fg=self.warning_color, activebackground=COLOR_BG_INPUT, bd=0, padx=6, pady=2, cursor="hand2", command=lambda t=stype: self.add_step(t))
            btn.pack(side="left", padx=2)

        # Scrollable Steps Container Canvas & Frame
        f_steps_outer = tk.Frame(self, bg=self.card_bg, padx=6, pady=6)
        f_steps_outer.pack(fill="both", expand=True, padx=15, pady=4)

        self.canvas = tk.Canvas(f_steps_outer, bg=self.card_bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(f_steps_outer, orient="vertical", command=self.canvas.yview)
        
        self.f_steps_inner = tk.Frame(self.canvas, bg=self.card_bg)

        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.f_steps_inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window_id, width=e.width))
        self.f_steps_inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Live Summary Frame
        self.f_summary = tk.Frame(self, bg=COLOR_BG_MAIN, padx=10, pady=8, bd=1, relief="solid")
        self.f_summary.pack(fill="x", padx=15, pady=(4, 6))

        tk.Label(self.f_summary, text="💡 Resumo Visual da Sequência Dinâmica:", font=(FONT_MAIN, 8, "bold"), bg=COLOR_BG_MAIN, fg=self.accent_color).pack(anchor="w")
        self.lbl_flow_summary = tk.Label(self.f_summary, text="", font=(FONT_MAIN, 8), bg=COLOR_BG_MAIN, fg=self.text_color, wraplength=550, justify="left")
        self.lbl_flow_summary.pack(anchor="w", pady=(2, 0))

        # Action Buttons Row
        f_actions = tk.Frame(self, bg=self.bg_color)
        f_actions.pack(fill="x", padx=15, pady=(4, 10))

        btn_save = tk.Button(
            f_actions,
            text="✔️ Salvar Preset Modular",
            font=(FONT_MAIN, 10, "bold"),
            bg=self.success_color,
            fg=COLOR_BG_MAIN,
            activebackground=COLOR_SUCCESS,
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._save_preset
        )
        btn_save.pack(side="right")

        btn_cancel = tk.Button(
            f_actions,
            text="Cancelar",
            font=(FONT_MAIN, 9),
            bg=COLOR_BORDER,
            fg=self.text_color,
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.destroy
        )
        btn_cancel.pack(side="right", padx=8)

    def add_step(self, step_type):
        defaults = {
            "press_hold": {"type": "press_hold", "enabled": True, "key": "w"},
            "tap_loop": {"type": "tap_loop", "enabled": True, "key": "shift", "count": 5, "interval_sec": 0.5, "use_range": False, "interval_min": 0.3, "interval_max": 0.7},
            "release": {"type": "release", "enabled": True, "key": "w"},
            "pause": {"type": "pause", "enabled": True, "duration_sec": 0.45, "use_range": False, "duration_min": 0.3, "duration_max": 0.6},
            "hold_duration": {"type": "hold_duration", "enabled": True, "key": "w", "duration_sec": 4.0, "use_range": False, "duration_min": 3.0, "duration_max": 5.0},
            "sequence_combo": {"type": "sequence_combo", "enabled": True, "sequence_raw": ["shift+space"], "interval_ms": 500},
            "mouse_click": {"type": "mouse_click", "enabled": True, "button": "left", "use_coords": False, "x": 0, "y": 0},
            "mouse_move": {"type": "mouse_move", "enabled": True, "x": 500, "y": 500},
            "mouse_drag": {"type": "mouse_drag", "enabled": True, "x1": 100, "y1": 100, "x2": 500, "y2": 500, "duration_sec": 1.0},
            "mouse_scroll": {"type": "mouse_scroll", "enabled": True, "direction": "down", "clicks": 5},
            "group_block": {"type": "group_block", "enabled": True, "name": "Bloco de Ações", "collapsed": False, "steps": []}
        }
        if step_type in defaults:
            self.steps.append(json.loads(json.dumps(defaults[step_type])))
            self._render_steps()
            self._update_live_preview()
            self.canvas.yview_moveto(1.0)

    def remove_step(self, index):
        if 0 <= index < len(self.steps):
            del self.steps[index]
            self._render_steps()
            self._update_live_preview()

    def move_step(self, index, direction):
        target_idx = index + direction
        if 0 <= target_idx < len(self.steps):
            self.steps[index], self.steps[target_idx] = self.steps[target_idx], self.steps[index]
            self._render_steps()
            self._update_live_preview()

    def duplicate_step(self, index):
        if 0 <= index < len(self.steps):
            cloned = json.loads(json.dumps(self.steps[index]))
            self.steps.insert(index + 1, cloned)
            self._render_steps()
            self._update_live_preview()

    def toggle_step_enabled(self, index):
        if 0 <= index < len(self.steps):
            self.steps[index]["enabled"] = not self.steps[index].get("enabled", True)
            self._render_steps()
            self._update_live_preview()

    def _render_steps(self):
        for widget in self.f_steps_inner.winfo_children():
            widget.destroy()

        if not self.steps:
            tk.Label(self.f_steps_inner, text="Nenhuma etapa adicionada. Clique em um dos botões acima para adicionar etapas ao fluxo!", font=(FONT_MAIN, 8, "italic"), bg=self.card_bg, fg=self.text_subtle).pack(pady=20)
        else:
            for idx, step in enumerate(self.steps):
                s_type = step.get("type", "press_hold")
                is_enabled = step.get("enabled", True)

                card_bg = COLOR_BG_INPUT if is_enabled else COLOR_BG_MAIN
                text_fg = self.text_color if is_enabled else COLOR_TEXT_DISABLED

                card = tk.Frame(self.f_steps_inner, bg=card_bg, padx=8, pady=6, bd=1, relief="solid")
                card.pack(fill="x", expand=True, pady=3, padx=2)

                # Left controls: Enabled Toggle & Number Badge
                f_left = tk.Frame(card, bg=card_bg)
                f_left.pack(side="left", padx=(0, 6))

                chk_icon = "👁️" if is_enabled else "🙈"
                btn_toggle = tk.Button(
                    f_left, text=chk_icon, font=(FONT_MAIN, 8), bg=card_bg, fg=self.accent_color if is_enabled else self.text_subtle, bd=0, padx=2, cursor="hand2", command=lambda i=idx: self.toggle_step_enabled(i)
                )
                btn_toggle.pack(side="left", padx=(0, 4))

                lbl_idx = tk.Label(f_left, text=f"{idx+1}", font=(FONT_MAIN, 8, "bold"), bg=self.accent_color if is_enabled else COLOR_BORDER, fg=COLOR_BG_MAIN, padx=6, pady=1)
                lbl_idx.pack(side="left")

                # Middle controls frame for step parameters
                f_ctrls = tk.Frame(card, bg=card_bg)
                f_ctrls.pack(side="left", fill="x", expand=True)

                if s_type == "press_hold":
                    tk.Label(f_ctrls, text="✊ Segurar Tecla:", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.warning_color if is_enabled else text_fg).pack(side="left")
                    v_key = tk.StringVar(value=step.get("key", "w"))
                    e_key = tk.Entry(f_ctrls, textvariable=v_key, width=6, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_key.pack(side="left", padx=4)
                    e_key.bind("<KeyRelease>", lambda e, s=step, v=v_key: self._on_step_field_change(s, "key", v.get()))
                    btn_cap = tk.Button(f_ctrls, text="🎯", font=(FONT_MAIN, 7), bg=COLOR_BG_INPUT, fg=self.accent_color, bd=0, padx=3, pady=1, cursor="hand2")
                    btn_cap.config(command=lambda s=step, b=btn_cap: self._capture_key_for_step(s, "key", b))
                    btn_cap.pack(side="left", padx=1)

                elif s_type == "tap_loop":
                    tk.Label(f_ctrls, text="🔄 Repetir Tecla:", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.success_color if is_enabled else text_fg).pack(side="left")
                    v_key = tk.StringVar(value=step.get("key", "shift"))
                    e_key = tk.Entry(f_ctrls, textvariable=v_key, width=5, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_key.pack(side="left", padx=2)
                    e_key.bind("<KeyRelease>", lambda e, s=step, v=v_key: self._on_step_field_change(s, "key", v.get()))
                    btn_cap = tk.Button(f_ctrls, text="🎯", font=(FONT_MAIN, 7), bg=COLOR_BG_INPUT, fg=self.accent_color, bd=0, padx=3, pady=1, cursor="hand2")
                    btn_cap.config(command=lambda s=step, b=btn_cap: self._capture_key_for_step(s, "key", b))
                    btn_cap.pack(side="left", padx=1)

                    tk.Label(f_ctrls, text="Toques:", font=(FONT_MAIN, 8), bg=card_bg, fg=text_fg).pack(side="left", padx=(4, 1))
                    v_cnt = tk.IntVar(value=step.get("count", 5))
                    e_cnt = tk.Entry(f_ctrls, textvariable=v_cnt, width=3, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=self.warning_color if is_enabled else text_fg, bd=1)
                    e_cnt.pack(side="left")
                    e_cnt.bind("<KeyRelease>", lambda e, s=step, v=v_cnt: self._on_step_field_change(s, "count", v.get()))

                    tk.Label(f_ctrls, text="Intervalo (s):", font=(FONT_MAIN, 8), bg=card_bg, fg=text_fg).pack(side="left", padx=(4, 1))
                    v_int = tk.DoubleVar(value=step.get("interval_sec", 1.0))
                    e_int = tk.Entry(f_ctrls, textvariable=v_int, width=4, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_int.pack(side="left")
                    e_int.bind("<KeyRelease>", lambda e, s=step, v=v_int: self._on_step_field_change(s, "interval_sec", v.get()))

                    # Min-Max Range Toggle
                    v_rng = tk.BooleanVar(value=step.get("use_range", False))
                    chk_rng = tk.Checkbutton(f_ctrls, text="🎲 Faixa Min-Max", variable=v_rng, bg=card_bg, fg=self.text_subtle, selectcolor=COLOR_BG_MAIN, command=lambda s=step, v=v_rng: self._on_step_field_change(s, "use_range", v.get()))
                    chk_rng.pack(side="left", padx=(4, 0))

                elif s_type == "release":
                    tk.Label(f_ctrls, text="👐 Soltar Tecla:", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.danger_color if is_enabled else text_fg).pack(side="left")
                    v_key = tk.StringVar(value=step.get("key", "w"))
                    e_key = tk.Entry(f_ctrls, textvariable=v_key, width=6, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_key.pack(side="left", padx=4)
                    e_key.bind("<KeyRelease>", lambda e, s=step, v=v_key: self._on_step_field_change(s, "key", v.get()))
                    btn_cap = tk.Button(f_ctrls, text="🎯", font=(FONT_MAIN, 7), bg=COLOR_BG_INPUT, fg=self.accent_color, bd=0, padx=3, pady=1, cursor="hand2")
                    btn_cap.config(command=lambda s=step, b=btn_cap: self._capture_key_for_step(s, "key", b))
                    btn_cap.pack(side="left", padx=1)

                elif s_type == "pause":
                    tk.Label(f_ctrls, text="⏱️ Pausa (s):", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.warning_color if is_enabled else text_fg).pack(side="left")
                    v_dur = tk.DoubleVar(value=step.get("duration_sec", 0.45))
                    e_dur = tk.Entry(f_ctrls, textvariable=v_dur, width=5, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_dur.pack(side="left", padx=4)
                    e_dur.bind("<KeyRelease>", lambda e, s=step, v=v_dur: self._on_step_field_change(s, "duration_sec", v.get()))

                elif s_type == "hold_duration":
                    tk.Label(f_ctrls, text="🚶 Caminhar Tecla:", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.accent_color if is_enabled else text_fg).pack(side="left")
                    v_key = tk.StringVar(value=step.get("key", "w"))
                    e_key = tk.Entry(f_ctrls, textvariable=v_key, width=5, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_key.pack(side="left", padx=2)
                    e_key.bind("<KeyRelease>", lambda e, s=step, v=v_key: self._on_step_field_change(s, "key", v.get()))
                    btn_cap = tk.Button(f_ctrls, text="🎯", font=(FONT_MAIN, 7), bg=COLOR_BG_INPUT, fg=self.accent_color, bd=0, padx=3, pady=1, cursor="hand2")
                    btn_cap.config(command=lambda s=step, b=btn_cap: self._capture_key_for_step(s, "key", b))
                    btn_cap.pack(side="left", padx=1)

                    tk.Label(f_ctrls, text="Duração (s):", font=(FONT_MAIN, 8), bg=card_bg, fg=text_fg).pack(side="left", padx=(4, 1))
                    v_dur = tk.DoubleVar(value=step.get("duration_sec", 4.0))
                    e_dur = tk.Entry(f_ctrls, textvariable=v_dur, width=4, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=self.warning_color if is_enabled else text_fg, bd=1)
                    e_dur.pack(side="left")
                    e_dur.bind("<KeyRelease>", lambda e, s=step, v=v_dur: self._on_step_field_change(s, "duration_sec", v.get()))

                elif s_type == "sequence_combo":
                    tk.Label(f_ctrls, text="🔤 Combo:", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.warning_color if is_enabled else text_fg).pack(side="left")
                    raw_seq = step.get("sequence_raw", ["shift+space"])
                    v_seq = tk.StringVar(value=", ".join(raw_seq) if isinstance(raw_seq, list) else str(raw_seq))
                    e_seq = tk.Entry(f_ctrls, textvariable=v_seq, width=12, font=(FONT_MAIN, 8, "bold"), justify="center", bg=COLOR_BG_MAIN, fg=self.warning_color if is_enabled else text_fg, bd=1)
                    e_seq.pack(side="left", padx=4)
                    e_seq.bind("<KeyRelease>", lambda e, s=step, v=v_seq: self._on_step_field_change(s, "sequence_raw", [t.strip() for t in v.get().replace(",", " ").split() if t.strip()]))

                elif s_type == "mouse_click":
                    tk.Label(f_ctrls, text="🖱️ Clique Mouse:", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.accent_color if is_enabled else text_fg).pack(side="left")
                    v_btn = tk.StringVar(value=step.get("button", "left"))
                    om = tk.OptionMenu(f_ctrls, v_btn, "left", "right", "middle", command=lambda val, s=step: self._on_step_field_change(s, "button", val))
                    om.config(font=(FONT_MAIN, 7, "bold"), bg=COLOR_BG_MAIN, fg=text_fg, bd=0, highlightthickness=0)
                    om.pack(side="left", padx=2)

                    v_use_pos = tk.BooleanVar(value=step.get("use_coords", False))
                    chk_pos = tk.Checkbutton(f_ctrls, text="X,Y", variable=v_use_pos, bg=card_bg, fg=self.text_subtle, selectcolor=COLOR_BG_MAIN, command=lambda s=step, v=v_use_pos: self._on_step_field_change(s, "use_coords", v.get()))
                    chk_pos.pack(side="left", padx=2)

                    v_x = tk.IntVar(value=step.get("x", 0))
                    e_x = tk.Entry(f_ctrls, textvariable=v_x, width=4, font=(FONT_MAIN, 8), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_x.pack(side="left", padx=1)
                    e_x.bind("<KeyRelease>", lambda e, s=step, v=v_x: self._on_step_field_change(s, "x", v.get()))

                    v_y = tk.IntVar(value=step.get("y", 0))
                    e_y = tk.Entry(f_ctrls, textvariable=v_y, width=4, font=(FONT_MAIN, 8), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_y.pack(side="left", padx=1)
                    e_y.bind("<KeyRelease>", lambda e, s=step, v=v_y: self._on_step_field_change(s, "y", v.get()))
                    btn_cap_pos = tk.Button(f_ctrls, text="📍", font=(FONT_MAIN, 7), bg=COLOR_BG_INPUT, fg=self.accent_color, bd=0, padx=3, pady=1, cursor="hand2")
                    btn_cap_pos.config(command=lambda s=step, b=btn_cap_pos: self._capture_pos_for_step(s, {"x": "x", "y": "y"}, b))
                    btn_cap_pos.pack(side="left", padx=1)

                elif s_type == "mouse_move":
                    tk.Label(f_ctrls, text="📍 Mover Mouse X,Y:", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.warning_color if is_enabled else text_fg).pack(side="left")
                    v_x = tk.IntVar(value=step.get("x", 500))
                    e_x = tk.Entry(f_ctrls, textvariable=v_x, width=4, font=(FONT_MAIN, 8), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_x.pack(side="left", padx=2)
                    e_x.bind("<KeyRelease>", lambda e, s=step, v=v_x: self._on_step_field_change(s, "x", v.get()))

                    v_y = tk.IntVar(value=step.get("y", 500))
                    e_y = tk.Entry(f_ctrls, textvariable=v_y, width=4, font=(FONT_MAIN, 8), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_y.pack(side="left", padx=2)
                    e_y.bind("<KeyRelease>", lambda e, s=step, v=v_y: self._on_step_field_change(s, "y", v.get()))
                    btn_cap_pos = tk.Button(f_ctrls, text="📍", font=(FONT_MAIN, 7), bg=COLOR_BG_INPUT, fg=self.accent_color, bd=0, padx=3, pady=1, cursor="hand2")
                    btn_cap_pos.config(command=lambda s=step, b=btn_cap_pos: self._capture_pos_for_step(s, {"x": "x", "y": "y"}, b))
                    btn_cap_pos.pack(side="left", padx=1)

                elif s_type == "mouse_drag":
                    tk.Label(f_ctrls, text="🖐️ Arrastar (X1,Y1) -> (X2,Y2):", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.success_color if is_enabled else text_fg).pack(side="left")
                    v_x1 = tk.IntVar(value=step.get("x1", 100))
                    e_x1 = tk.Entry(f_ctrls, textvariable=v_x1, width=4, font=(FONT_MAIN, 8), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_x1.pack(side="left", padx=1)
                    e_x1.bind("<KeyRelease>", lambda e, s=step, v=v_x1: self._on_step_field_change(s, "x1", v.get()))

                    v_y1 = tk.IntVar(value=step.get("y1", 100))
                    e_y1 = tk.Entry(f_ctrls, textvariable=v_y1, width=4, font=(FONT_MAIN, 8), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_y1.pack(side="left", padx=1)
                    e_y1.bind("<KeyRelease>", lambda e, s=step, v=v_y1: self._on_step_field_change(s, "y1", v.get()))

                    v_x2 = tk.IntVar(value=step.get("x2", 500))
                    e_x2 = tk.Entry(f_ctrls, textvariable=v_x2, width=4, font=(FONT_MAIN, 8), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_x2.pack(side="left", padx=1)
                    e_x2.bind("<KeyRelease>", lambda e, s=step, v=v_x2: self._on_step_field_change(s, "x2", v.get()))

                    v_y2 = tk.IntVar(value=step.get("y2", 500))
                    e_y2 = tk.Entry(f_ctrls, textvariable=v_y2, width=4, font=(FONT_MAIN, 8), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_y2.pack(side="left", padx=1)
                    e_y2.bind("<KeyRelease>", lambda e, s=step, v=v_y2: self._on_step_field_change(s, "y2", v.get()))
                    btn_cap_drag = tk.Button(f_ctrls, text="📍", font=(FONT_MAIN, 7), bg=COLOR_BG_INPUT, fg=self.accent_color, bd=0, padx=3, pady=1, cursor="hand2")
                    btn_cap_drag.config(command=lambda s=step, b=btn_cap_drag: self._capture_pos_for_step(s, {"x1": "x1", "y1": "y1", "x2": "x2", "y2": "y2"}, b))
                    btn_cap_drag.pack(side="left", padx=1)

                elif s_type == "mouse_scroll":
                    tk.Label(f_ctrls, text="📜 Rolar Mouse:", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.accent_color if is_enabled else text_fg).pack(side="left")
                    v_dir = tk.StringVar(value=step.get("direction", "down"))
                    om_dir = tk.OptionMenu(f_ctrls, v_dir, "down", "up", command=lambda val, s=step: self._on_step_field_change(s, "direction", val))
                    om_dir.config(font=(FONT_MAIN, 7, "bold"), bg=COLOR_BG_MAIN, fg=text_fg, bd=0, highlightthickness=0)
                    om_dir.pack(side="left", padx=2)

                    tk.Label(f_ctrls, text="Cliques:", font=(FONT_MAIN, 8), bg=card_bg, fg=text_fg).pack(side="left", padx=(4, 1))
                    v_clk = tk.IntVar(value=step.get("clicks", 5))
                    e_clk = tk.Entry(f_ctrls, textvariable=v_clk, width=4, font=(FONT_MAIN, 8), justify="center", bg=COLOR_BG_MAIN, fg=text_fg, bd=1)
                    e_clk.pack(side="left")
                    e_clk.bind("<KeyRelease>", lambda e, s=step, v=v_clk: self._on_step_field_change(s, "clicks", v.get()))

                elif s_type == "group_block":
                    tk.Label(f_ctrls, text="📦 Agrupador:", font=(FONT_MAIN, 8, "bold"), bg=card_bg, fg=self.warning_color if is_enabled else text_fg).pack(side="left")
                    v_gname = tk.StringVar(value=step.get("name", "Bloco de Ações"))
                    e_gname = tk.Entry(f_ctrls, textvariable=v_gname, width=16, font=(FONT_MAIN, 8, "bold"), bg=COLOR_BG_MAIN, fg=self.warning_color if is_enabled else text_fg, bd=1)
                    e_gname.pack(side="left", padx=4)
                    e_gname.bind("<KeyRelease>", lambda e, s=step, v=v_gname: self._on_step_field_change(s, "name", v.get()))

                # Right Controls Frame: Move Up, Move Down, Duplicate, Delete
                f_right = tk.Frame(card, bg=card_bg)
                f_right.pack(side="right")

                btn_up = tk.Button(f_right, text="🔼", font=(FONT_MAIN, 7), bg=COLOR_BORDER, fg=self.text_color, bd=0, padx=3, pady=1, cursor="hand2", command=lambda i=idx: self.move_step(i, -1))
                btn_up.pack(side="left", padx=1)

                btn_down = tk.Button(f_right, text="🔽", font=(FONT_MAIN, 7), bg=COLOR_BORDER, fg=self.text_color, bd=0, padx=3, pady=1, cursor="hand2", command=lambda i=idx: self.move_step(i, 1))
                btn_down.pack(side="left", padx=1)

                btn_dup = tk.Button(f_right, text="📋", font=(FONT_MAIN, 7), bg=COLOR_BORDER, fg=self.accent_color, bd=0, padx=3, pady=1, cursor="hand2", command=lambda i=idx: self.duplicate_step(i))
                btn_dup.pack(side="left", padx=1)

                btn_del = tk.Button(f_right, text="❌", font=(FONT_MAIN, 7, "bold"), bg=COLOR_BORDER, fg=self.danger_color, bd=0, padx=3, pady=1, cursor="hand2", command=lambda i=idx: self.remove_step(i))
                btn_del.pack(side="left", padx=1)

        # Force Tkinter geometry update for Canvas Scrollregion calculation
        self.f_steps_inner.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_step_field_change(self, step_obj, field_name, value):
        try:
            step_obj[field_name] = value
        except Exception:
            pass
        self._update_live_preview()

    def _capture_key_for_step(self, step, field_name, btn_widget):
        """Listen for next key press and assign it to the step's field."""
        original_text = btn_widget.cget("text")
        btn_widget.config(text="⌛ Pressione...", bg=self.accent_color, fg=COLOR_BG_MAIN, state="disabled")

        def on_key(event):
            key_name = event.keysym.lower()
            # Map common keysyms to simpler names
            key_map = {
                "space": "space", "return": "enter", "escape": "esc",
                "shift_l": "shift", "shift_r": "shift",
                "control_l": "ctrl", "control_r": "ctrl",
                "alt_l": "alt", "alt_r": "alt",
                "tab": "tab", "backspace": "backspace",
                "caps_lock": "caps_lock", "delete": "delete",
            }
            # F-keys
            for i in range(1, 25):
                key_map[f"f{i}"] = f"f{i}"

            resolved = key_map.get(key_name, key_name)

            step[field_name] = resolved
            btn_widget.config(text=original_text, bg=COLOR_BG_INPUT, fg=self.accent_color, state="normal")
            self.unbind_all("<Key>")
            self._render_steps()
            self._update_live_preview()

        self.bind_all("<Key>", on_key)

    def _capture_pos_for_step(self, step, fields, btn_widget):
        """Countdown 3s then capture current mouse position into the step's fields.
        fields is a dict like {"x": "x", "y": "y"} or {"x1": "x1", "y1": "y1", "x2": "x2", "y2": "y2"}
        For drag (4 fields), captures origin first, then destination after another 3s.
        """
        original_text = btn_widget.cget("text")
        btn_widget.config(state="disabled")
        
        field_keys = list(fields.keys())
        is_drag = len(field_keys) == 4  # x1,y1,x2,y2

        from pynput import mouse as pmouse
        mc = pmouse.Controller()

        def countdown(secs, phase=1):
            if secs > 0:
                if is_drag and phase == 1:
                    btn_widget.config(text=f"Origem em {secs}s...")
                elif is_drag and phase == 2:
                    btn_widget.config(text=f"Destino em {secs}s...")
                else:
                    btn_widget.config(text=f"Capturando em {secs}s...")
                self.after(1000, lambda: countdown(secs - 1, phase))
            else:
                pos = mc.position
                if is_drag and phase == 1:
                    step[field_keys[0]] = pos[0]  # x1
                    step[field_keys[1]] = pos[1]  # y1
                    # Now capture destination
                    countdown(3, phase=2)
                elif is_drag and phase == 2:
                    step[field_keys[2]] = pos[0]  # x2
                    step[field_keys[3]] = pos[1]  # y2
                    btn_widget.config(text=original_text, state="normal")
                    self._render_steps()
                    self._update_live_preview()
                else:
                    # Simple x,y capture
                    step[field_keys[0]] = pos[0]
                    step[field_keys[1]] = pos[1]
                    btn_widget.config(text=original_text, state="normal")
                    self._render_steps()
                    self._update_live_preview()

        countdown(3, phase=1)


    def _update_live_preview(self):
        active_steps = [s for s in self.steps if s.get("enabled", True)]
        if not active_steps:
            self.lbl_flow_summary.config(text="Nenhuma etapa ativa no momento.")
            return

        flow_parts = []
        for step in active_steps:
            stype = step.get("type", "")
            if stype == "press_hold":
                flow_parts.append(f"Segura [{str(step.get('key', 'w')).upper()}]")
            elif stype == "tap_loop":
                k = str(step.get('key', 'shift')).upper()
                cnt = step.get('count', 5)
                interval = step.get('interval_sec', 1.0)
                flow_parts.append(f"Toca [{k}] {cnt}x ({interval}s)")
            elif stype == "release":
                flow_parts.append(f"Solta [{str(step.get('key', 'w')).upper()}]")
            elif stype == "pause":
                flow_parts.append(f"Pausa ({step.get('duration_sec', 0.45)}s)")
            elif stype == "hold_duration":
                k = str(step.get('key', 'w')).upper()
                dur = step.get('duration_sec', 4.0)
                flow_parts.append(f"Caminha [{k}] {dur}s")
            elif stype == "sequence_combo":
                seq = step.get('sequence_raw', ["shift+space"])
                seq_str = ", ".join(seq).upper() if isinstance(seq, list) else str(seq).upper()
                flow_parts.append(f"Combo [{seq_str}]")
            elif stype == "mouse_click":
                btn = step.get("button", "left").upper()
                flow_parts.append(f"Clique Mouse [{btn}]")
            elif stype == "mouse_move":
                flow_parts.append(f"Mover Mouse ({step.get('x',0)}, {step.get('y',0)})")
            elif stype == "mouse_drag":
                flow_parts.append(f"Arrastar ({step.get('x1',0)},{step.get('y1',0)})->({step.get('x2',0)},{step.get('y2',0)})")
            elif stype == "mouse_scroll":
                flow_parts.append(f"Rolar Mouse {step.get('direction','down').upper()} ({step.get('clicks',5)}x)")
            elif stype == "group_block":
                flow_parts.append(f"📦 [{step.get('name','Bloco')}]")

        full_summary = " -> ".join(flow_parts) + " -> [Loop Continuous]"
        self.lbl_flow_summary.config(text=full_summary)

    def _export_preset_json(self):
        name = self.var_name.get().strip() or "preset_macro"
        file_path = filedialog.asksaveasfilename(
            title="Exportar Preset em JSON",
            initialfile=f"{name.replace(' ', '_')}.json",
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
            parent=self
        )
        if not file_path:
            return

        preset_data = {
            "name": name,
            "target_type": "modular_macro",
            "target_name": f"Macro ({len(self.steps)} Etapas)",
            "hotkey_name": self.var_hotkey_name.get().strip().upper() or "F12",
            "emergency_hotkey_name": self.var_emergency_hotkey.get().strip().upper() or "ESC",
            "modular_steps": json.loads(json.dumps(self.steps)),
            "mode": "spam",
            "interval_ms": 50
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Sucesso", f"Preset exportado com sucesso para:\n{file_path}", parent=self)
        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Não foi possível exportar o arquivo: {e}", parent=self)

    def _import_preset_json(self):
        file_path = filedialog.askopenfilename(
            title="Importar Preset em JSON",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
            parent=self
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or ("modular_steps" not in data and "step_macro_config" not in data and "target_type" not in data):
                raise ValueError("Estrutura JSON inválida para um Preset do Auto Clicker Pro.")

            self.var_name.set(data.get("name", "Preset Importado"))
            self.var_hotkey_name.set(data.get("hotkey_name", "F12"))
            self.var_emergency_hotkey.set(data.get("emergency_hotkey_name", "ESC"))
            self.steps = self._extract_or_convert_steps(data)
            self._render_steps()
            self._update_live_preview()
            messagebox.showinfo("Sucesso", "Preset importado e carregado com sucesso!", parent=self)
        except Exception as e:
            messagebox.showerror("Erro de Importação", f"Não foi possível carregar o preset: {e}", parent=self)

    def _save_preset(self):
        name = self.var_name.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Digite um nome para o preset!", parent=self)
            return

        if not self.steps:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma etapa à sua macro!", parent=self)
            return

        preset_data = {
            "name": name,
            "target_type": "modular_macro",
            "target_name": f"Macro ({len(self.steps)} Etapas)",
            "hotkey_name": self.var_hotkey_name.get().strip().upper() or "F12",
            "emergency_hotkey_name": self.var_emergency_hotkey.get().strip().upper() or "ESC",
            "modular_steps": json.loads(json.dumps(self.steps)),
            "mode": "spam",
            "interval_ms": 50
        }

        if self.on_save_callback:
            self.on_save_callback(preset_data)
        self.destroy()


class AutoClickerApp:
    CONFIG_FILE = "config.json"

    # Default presets dictionary grouped by Game Category
    DEFAULT_GAMES = {
        "🎮 Genshin Impact": [
            {
                "name": "🏃 Run Dash 7x + Walk 6s (Stamina Loop)",
                "target_type": "modular_macro",
                "target_name": "Macro Dash 7x + Walk 6s",
                "hotkey_name": "F12",
                "emergency_hotkey_name": "ESC",
                "modular_steps": [
                    {"type": "press_hold", "enabled": True, "key": "w"},
                    {"type": "tap_loop", "enabled": True, "key": "shift", "count": 7, "interval_sec": 1.0},
                    {"type": "release", "enabled": True, "key": "w"},
                    {"type": "pause", "enabled": True, "duration_sec": 0.45},
                    {"type": "hold_duration", "enabled": True, "key": "w", "duration_sec": 6.0}
                ],
                "mode": "spam",
                "interval_ms": 50
            },
            {
                "name": "⚔️ Diálogo / Coletar (F)",
                "target_type": "keyboard",
                "target_name": "'F'",
                "hotkey_name": "F12",
                "emergency_hotkey_name": "ESC",
                "mode": "spam",
                "interval_ms": 45,
                "use_jitter": True,
                "jitter_ms": 8
            },
            {
                "name": "🏹 Ataque Rápido",
                "target_type": "mouse",
                "target_name": "Clique Esquerdo",
                "target_mouse_action": "left",
                "hotkey_name": "F12",
                "emergency_hotkey_name": "ESC",
                "mode": "spam",
                "interval_ms": 50,
                "use_jitter": True,
                "jitter_ms": 5
            },
            {
                "name": "🏃 Sprint Jump / BHop",
                "target_type": "sequence",
                "target_name": "Seq: Shift+Espaço",
                "target_sequence_raw": ["shift+space"],
                "hotkey_name": "F12",
                "emergency_hotkey_name": "ESC",
                "mode": "spam",
                "interval_ms": 820,
                "use_jitter": True,
                "jitter_ms": 10
            },
            {
                "name": "💫 Segurar Habilidade (E)",
                "target_type": "keyboard",
                "target_name": "'E'",
                "hotkey_name": "F12",
                "emergency_hotkey_name": "ESC",
                "mode": "hold"
            }
        ],
        "⛏️ Minecraft": [
            {
                "name": "⚔️ Fast CPS (50ms)",
                "target_type": "mouse",
                "target_name": "Clique Esquerdo",
                "target_mouse_action": "left",
                "hotkey_name": "F12",
                "emergency_hotkey_name": "ESC",
                "mode": "spam",
                "interval_ms": 50,
                "use_jitter": True,
                "jitter_ms": 10
            },
            {
                "name": "🛡️ Auto Shield",
                "target_type": "mouse",
                "target_name": "Clique Direito",
                "target_mouse_action": "right",
                "hotkey_name": "F12",
                "emergency_hotkey_name": "ESC",
                "mode": "spam",
                "interval_ms": 100
            }
        ],
        "🧱 Roblox": [
            {
                "name": "🚀 Auto-Farm (Espaço)",
                "target_type": "keyboard",
                "target_name": "Espaço",
                "hotkey_name": "F12",
                "emergency_hotkey_name": "ESC",
                "mode": "spam",
                "interval_ms": 80
            },
            {
                "name": "🖱️ Clicker Rápido",
                "target_type": "mouse",
                "target_name": "Clique Esquerdo",
                "target_mouse_action": "left",
                "hotkey_name": "F12",
                "emergency_hotkey_name": "ESC",
                "mode": "spam",
                "interval_ms": 40
            }
        ]
    }

    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Auto Clicker Pro & Key Presser")
        
        self.root.minsize(520, 750)
        self.root.resizable(True, True)
        
        # Center main window and adapt to screen height
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        w, h = 580, 920
        if screen_h < 1000:
            h = screen_h - 100
            
        x = int((screen_w / 2) - (w / 2))
        y = int((screen_h / 2) - (h / 2))
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        set_windows_high_precision_timer(True)
        self.is_admin = check_is_admin()
        
        # Usage tracking for donation popup
        self.total_run_time_sec = 0
        self.last_donation_popup = 0

        # Dark theme premium palette applied
        self.bg_color = COLOR_BG_MAIN
        self.card_bg = COLOR_BG_CARD
        self.card_border = COLOR_BORDER
        self.accent_color = COLOR_PRIMARY
        self.text_color = COLOR_TEXT_MAIN
        self.text_subtle = COLOR_TEXT_SEC
        self.success_color = COLOR_SUCCESS
        self.danger_color = COLOR_ERROR
        self.warning_color = COLOR_WARNING
        
        self.root.configure(bg=self.bg_color)

        # Set Window Icon if exists
        self.icon_image = None
        if os.path.exists("app_icon.png"):
            try:
                self.icon_image = ImageTk.PhotoImage(file="app_icon.png")
                self.root.iconphoto(False, self.icon_image)
            except Exception:
                pass
        elif os.path.exists("app_icon.ico"):
            try:
                self.root.iconbitmap("app_icon.ico")
            except Exception:
                pass

        # --- State Variables ---
        self.is_running = False
        self.is_capturing_target = False
        self.is_capturing_hotkey = False
        self.is_capturing_emergency = False
        self.is_capturing_pos = False

        # Target Key / Mouse / Sequence / Modular Macro Action
        self.target_type = "keyboard"
        self.target_key = keyboard.Key.space
        self.target_mouse_action = "left"
        self.target_sequence_raw = []
        self.target_sequence_parsed = []
        self.target_name = "Espaço"
        
        # Modular Steps List
        self.modular_steps = [
            {"type": "press_hold", "enabled": True, "key": "w"},
            {"type": "tap_loop", "enabled": True, "key": "shift", "count": 7, "interval_sec": 1.0},
            {"type": "release", "enabled": True, "key": "w"},
            {"type": "pause", "enabled": True, "duration_sec": 0.45},
            {"type": "hold_duration", "enabled": True, "key": "w", "duration_sec": 6.0}
        ]

        # Global Hotkey (Default F12) & Emergency Stop Hotkey (Default ESC)
        self.hotkey_code = keyboard.Key.f12
        self.hotkey_name = "F12"
        self.emergency_hotkey_code = keyboard.Key.esc
        self.emergency_hotkey_name = "ESC"

        # Modes & Settings Variables
        self.mode = tk.StringVar(value="spam")  # "spam" or "hold"
        self.interval_ms = tk.IntVar(value=50)
        self.use_jitter = tk.BooleanVar(value=False)
        self.jitter_ms = tk.IntVar(value=5)

        # Position Settings
        self.position_mode = tk.StringVar(value="current")  # "current" or "fixed"
        self.fixed_x = tk.IntVar(value=0)
        self.fixed_y = tk.IntVar(value=0)

        # Stop Limits
        self.use_stop_clicks = tk.BooleanVar(value=False)
        self.stop_clicks_limit = tk.IntVar(value=100)
        self.use_stop_timer = tk.BooleanVar(value=False)
        self.stop_timer_sec = tk.IntVar(value=60)

        # UI & System Options
        self.always_on_top = tk.BooleanVar(value=False)
        self.sound_enabled = tk.BooleanVar(value=True)
        self.minimize_to_tray = tk.BooleanVar(value=False)

        # Games & Profiles State
        self.game_profiles = json.loads(json.dumps(self.DEFAULT_GAMES))
        self.active_game = "🎮 Genshin Impact"
        self.active_preset_name = ""

        # Floating Mini Overlay Window
        self.mini_bar_window = None
        self.mini_bar_inner_frame = None
        self.mini_bar_btn_frame = None
        self.mini_bar_status_btn = None
        self._drag_x = 0
        self._drag_y = 0

        # Live Statistics & Real-time Execution Log
        self.total_clicks = 0
        self.start_time = 0
        self.cps_history = []

        # Threading
        self.click_thread = None
        self.stop_event = threading.Event()

        # Controllers
        self.kb_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()

        # Tray Icon Thread
        self.tray_icon = None

        # Load persisted config if exists
        self._load_config()

        # Setup GUI Components
        self._setup_styles()
        self._create_widgets()

        # Apply initial window state
        self._toggle_always_on_top()

        # Start Global Listeners
        self._start_global_listeners()

        # Periodic UI update for CPS and stats
        self._update_stats_loop()

        # Window Close Protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_bg, relief="flat")
        style.configure("TLabel", background=self.card_bg, foreground=self.text_color, font=(FONT_MAIN, 9))
        style.configure("Title.TLabel", background=self.bg_color, foreground=self.accent_color, font=(FONT_MAIN, 15, "bold"))
        style.configure("TRadiobutton", background=self.card_bg, foreground=self.text_color, font=(FONT_MAIN, 9))
        style.configure("TCheckbutton", background=self.card_bg, foreground=self.text_color, font=(FONT_MAIN, 9))

    def log_message(self, msg):
        timestamp = time.strftime("[%H:%M:%S]")
        formatted_line = f"{timestamp} {msg}\n"
        
        def _append():
            if hasattr(self, 'txt_log') and self.txt_log.winfo_exists():
                self.txt_log.config(state="normal")
                self.txt_log.insert(tk.END, formatted_line)
                self.txt_log.see(tk.END)
                self.txt_log.config(state="disabled")

        self.root.after(0, _append)

    def _create_widgets(self):
        # Top Header
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title_lbl = tk.Label(header_frame, text="⚡ Auto Clicker Pro", font=(FONT_MAIN, 20, "bold"), bg=self.bg_color, fg=self.accent_color)
        title_lbl.pack(side="left")

        # Mini Bar Overlay Toggle Button
        btn_mini_mode = tk.Button(
            header_frame, text="🖥️ Flutuante", font=(FONT_MAIN, 10, "bold"),
            bg=COLOR_BG_INPUT, fg=self.accent_color, bd=0, padx=8, pady=4, cursor="hand2", command=self.open_mini_bar
        )
        bind_hover(btn_mini_mode, COLOR_BG_INPUT, COLOR_BORDER)
        btn_mini_mode.pack(side="left", padx=10)

        if self.is_admin:
            admin_btn = tk.Label(header_frame, text="🛡️ ADMIN", font=(FONT_MAIN, 10, "bold"), bg=COLOR_BG_INPUT, fg=self.success_color, padx=6, pady=4)
            admin_btn.pack(side="right")
        else:
            admin_btn = tk.Button(
                header_frame, text="⚠️ ADMIN", font=(FONT_MAIN, 10, "bold"), 
                bg=self.warning_color, fg=COLOR_BG_MAIN, bd=0, padx=6, pady=4, cursor="hand2", command=relaunch_as_admin
            )
            bind_hover(admin_btn, self.warning_color, "#FFC973")
            admin_btn.pack(side="right")

        # Status Card (Redesigned)
        self.status_frame = tk.Frame(self.root, bg=self.card_bg, highlightbackground=COLOR_BORDER, highlightthickness=1, cursor="hand2")
        self.status_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.status_frame.bind("<Button-1>", lambda e: self.prepare_capture_hotkey())
        
        status_inner = tk.Frame(self.status_frame, bg=self.card_bg, padx=12, pady=12)
        status_inner.pack(fill="x")
        status_inner.bind("<Button-1>", lambda e: self.prepare_capture_hotkey())

        # Pulse indicator & Text
        status_top = tk.Frame(status_inner, bg=self.card_bg)
        status_top.pack(fill="x", pady=(0, 6))
        status_top.bind("<Button-1>", lambda e: self.prepare_capture_hotkey())

        self.pulse_ind = PulseIndicator(status_top, size=14)
        self.pulse_ind.pack(side="left", pady=2)
        self.pulse_ind.bind("<Button-1>", lambda e: self.prepare_capture_hotkey())

        self.status_label = tk.Label(
            status_top, text=f"PARADO (Atalho: {self.hotkey_name})", 
            font=(FONT_MAIN, 13, "bold"), bg=self.card_bg, fg=COLOR_TEXT_SEC, cursor="hand2"
        )
        self.status_label.pack(side="left", padx=8)
        self.status_label.bind("<Button-1>", lambda e: self.prepare_capture_hotkey())

        # Stats Badges
        stats_bot = tk.Frame(status_inner, bg=self.card_bg)
        stats_bot.pack(fill="x")
        stats_bot.bind("<Button-1>", lambda e: self.prepare_capture_hotkey())

        def make_badge(parent, text):
            f = tk.Frame(parent, bg=COLOR_BG_INPUT, padx=6, pady=2, highlightbackground=COLOR_BORDER, highlightthickness=1)
            l = tk.Label(f, text=text, font=(FONT_MONO, 12, "bold"), bg=COLOR_BG_INPUT, fg=self.accent_color)
            f.pack(side="left", padx=(0, 6))
            f.bind("<Button-1>", lambda e: self.prepare_capture_hotkey())
            l.bind("<Button-1>", lambda e: self.prepare_capture_hotkey())
            return l

        self.lbl_clicks = make_badge(stats_bot, "Cliques: 0")
        self.lbl_cps = make_badge(stats_bot, "CPS: 0.0")
        self.lbl_time = make_badge(stats_bot, "Tempo: 00:00")

        # Bottom Action Bar (Fixed)
        self.bottom_frame = tk.Frame(self.root, bg=self.bg_color, pady=15, padx=20)
        self.bottom_frame.pack(side="bottom", fill="x")

        # Big Main Start/Stop Action Button
        self.btn_toggle = tk.Button(
            self.bottom_frame, text=f"▶ INICIAR ({self.hotkey_name})", 
            font=(FONT_MAIN, 15, "bold"), bg=self.success_color, fg=COLOR_BG_MAIN,
            activebackground=COLOR_SUCCESS_HOVER, cursor="hand2", pady=12, bd=0
        )
        bind_hover(self.btn_toggle, self.success_color, COLOR_SUCCESS_HOVER)
        self.btn_toggle.pack(fill="x")

        # Main Container (Remaining space)
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=20, pady=0)

        # Helper to create styled section cards
        def create_section_card(parent, number, title):
            card = tk.Frame(parent, bg=self.card_bg, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=12, pady=12)
            card.pack(fill="x", pady=5)
            header = tk.Frame(card, bg=self.card_bg)
            header.pack(fill="x", pady=(0, 8))
            
            # Badge number
            badge = tk.Frame(header, bg=COLOR_BG_INPUT, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=6, pady=2)
            badge.pack(side="left", padx=(0, 8))
            tk.Label(badge, text=number, font=(FONT_MONO, 11, "bold"), bg=COLOR_BG_INPUT, fg=self.accent_color).pack()
            
            tk.Label(header, text=title, font=(FONT_MAIN, 15, "bold"), bg=self.card_bg, fg=self.text_color).pack(side="left")
            return card

        # --- SECTION 0: GAMES & PRESETS ---
        card_games = tk.Frame(main_container, bg=self.card_bg, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=12, pady=12)
        card_games.pack(fill="x", pady=5)
        
        lbl_sec0 = tk.Label(card_games, text="🎮 Perfis & Presets Rápidos", font=(FONT_MAIN, 15, "bold"), bg=self.card_bg, fg=self.text_color)
        lbl_sec0.pack(anchor="w", pady=(0, 8))

        self.f_game_tabs = tk.Frame(card_games, bg=self.card_bg)
        self.f_game_tabs.pack(fill="x", pady=2)

        self.f_quick_buttons = tk.Frame(card_games, bg=self.card_bg)
        self.f_quick_buttons.pack(fill="x", pady=(6, 4))

        self.f_preset_actions = tk.Frame(card_games, bg=self.card_bg)
        self.f_preset_actions.pack(fill="x", pady=(4, 0))

        self._render_game_tabs()
        self._render_quick_preset_buttons()

        # --- SECTION 1: TARGET KEY ---
        card1 = create_section_card(main_container, "1", "Alvo & Atalhos")

        f_target = tk.Frame(card1, bg=self.card_bg)
        f_target.pack(fill="x", pady=4)

        # target display
        f_tgt_disp = tk.Frame(f_target, bg=COLOR_BG_INPUT, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=8, pady=6)
        f_tgt_disp.pack(side="left", fill="x", expand=True)
        tk.Label(f_tgt_disp, text="Alvo:", font=(FONT_MAIN, 13, "bold"), bg=COLOR_BG_INPUT, fg=COLOR_TEXT_SEC).pack(side="left")
        self.key_display_lbl = tk.Label(f_tgt_disp, text=self.target_name, font=(FONT_MAIN, 13, "bold"), bg=COLOR_BG_INPUT, fg=self.warning_color)
        self.key_display_lbl.pack(side="left", padx=5)

        self.btn_capture = tk.Button(
            f_target, text="🎯 Capturar Alvo", font=(FONT_MAIN, 12, "bold"),
            bg=COLOR_BG_INPUT, fg=self.accent_color, activebackground=COLOR_BORDER, command=self.prepare_capture_target, cursor="hand2", padx=10, pady=5, bd=0
        )
        bind_hover(self.btn_capture, COLOR_BG_INPUT, COLOR_BORDER)
        self.btn_capture.pack(side="left", padx=6)

        # Actions Row
        actions_row = tk.Frame(card1, bg=self.card_bg)
        actions_row.pack(fill="x", pady=(8, 0))

        self.btn_hotkey = tk.Button(
            actions_row, text=f"⌨️ Atalho: [{self.hotkey_name}]", font=(FONT_MAIN, 11, "bold"),
            bg=COLOR_BG_INPUT, fg=self.text_color, activebackground=COLOR_BORDER, command=self.prepare_capture_hotkey, cursor="hand2", padx=8, pady=4, bd=0
        )
        bind_hover(self.btn_hotkey, COLOR_BG_INPUT, COLOR_BORDER)
        self.btn_hotkey.pack(side="left", padx=(0, 5))

        self.btn_emergency_hotkey = tk.Button(
            actions_row, text=f"🚨 Emergência: [{self.emergency_hotkey_name}]", font=(FONT_MAIN, 11, "bold"),
            bg=COLOR_BG_INPUT, fg=self.danger_color, activebackground=COLOR_BORDER, command=self.prepare_capture_emergency_hotkey, cursor="hand2", padx=8, pady=4, bd=0
        )
        bind_hover(self.btn_emergency_hotkey, COLOR_BG_INPUT, COLOR_BORDER)
        self.btn_emergency_hotkey.pack(side="left")

        # Quick targets
        basic_presets_frame = tk.Frame(card1, bg=self.card_bg)
        basic_presets_frame.pack(fill="x", pady=(10, 0))
        tk.Label(basic_presets_frame, text="Ações rápidas:", font=(FONT_MAIN, 12, "bold"), bg=self.card_bg, fg=COLOR_TEXT_SEC).pack(side="left", padx=(0, 6))
        
        preset_items = [
            ("Mouse Esq", "mouse", mouse.Button.left, "left", "Clique Esquerdo"),
            ("Mouse Dir", "mouse", mouse.Button.right, "right", "Clique Direito"),
            ("Duplo Esq", "mouse", mouse.Button.left, "double", "Clique Duplo"),
            ("Espaço", "keyboard", keyboard.Key.space, "left", "Espaço")
        ]
        for p_name, p_type, p_key, p_action, p_label in preset_items:
            btn = tk.Button(
                basic_presets_frame, text=p_name, font=(FONT_MAIN, 11), bg=COLOR_BG_INPUT, fg=self.text_color, bd=0, padx=6, pady=3,
                command=lambda t=p_type, k=p_key, a=p_action, l=p_label: self.set_target(t, k, a, l)
            )
            bind_hover(btn, COLOR_BG_INPUT, COLOR_BORDER)
            btn.pack(side="left", padx=3)

        # --- SECTION 2: MODE & FREQUENCY ---
        card2 = create_section_card(main_container, "2", "Modo & Velocidade")
        
        f_modes = tk.Frame(card2, bg=self.card_bg)
        f_modes.pack(fill="x", pady=2)
        ttk.Radiobutton(f_modes, text="🔄 Repetição (Spam)", value="spam", variable=self.mode, command=self._on_mode_change).pack(side="left", padx=(0, 20))
        ttk.Radiobutton(f_modes, text="✊ Segurar (Hold)", value="hold", variable=self.mode, command=self._on_mode_change).pack(side="left")

        self.f_interval = tk.Frame(card2, bg=self.card_bg)
        self.f_interval.pack(fill="x", pady=(10, 0))
        tk.Label(self.f_interval, text="Intervalo (ms):", font=(FONT_MAIN, 12, "bold"), bg=self.card_bg, fg=self.text_color).pack(side="left")
        self.entry_interval = tk.Entry(self.f_interval, width=6, font=(FONT_MONO, 12), justify="center", bg=COLOR_BG_INPUT, fg=self.text_color, bd=1, relief=tk.SOLID, insertbackground="white")
        self.entry_interval.insert(0, str(self.interval_ms.get()))
        self.entry_interval.pack(side="left", padx=6)

        ttk.Checkbutton(self.f_interval, text="🎲 Humano (Jitter ±ms):", variable=self.use_jitter).pack(side="left", padx=(15, 6))
        self.entry_jitter = tk.Entry(self.f_interval, width=4, font=(FONT_MONO, 12), justify="center", bg=COLOR_BG_INPUT, fg=self.text_color, bd=1, relief=tk.SOLID, insertbackground="white")
        self.entry_jitter.insert(0, str(self.jitter_ms.get()))
        self.entry_jitter.pack(side="left")

        # --- SECTION 3: MOUSE POSITION ---
        card3 = create_section_card(main_container, "3", "Posição do Clique")
        
        f_pos_radios = tk.Frame(card3, bg=self.card_bg)
        f_pos_radios.pack(fill="x")
        ttk.Radiobutton(f_pos_radios, text="📍 Posição Atual do Cursor", value="current", variable=self.position_mode).pack(side="left", padx=(0, 20))
        ttk.Radiobutton(f_pos_radios, text="🎯 Posição Fixa (X, Y)", value="fixed", variable=self.position_mode).pack(side="left")

        f_pos_inputs = tk.Frame(card3, bg=self.card_bg)
        f_pos_inputs.pack(fill="x", pady=(10, 0))
        tk.Label(f_pos_inputs, text="X:", font=(FONT_MAIN, 12, "bold"), bg=self.card_bg, fg=self.text_color).pack(side="left")
        self.entry_x = tk.Entry(f_pos_inputs, width=5, font=(FONT_MONO, 12), justify="center", bg=COLOR_BG_INPUT, fg=self.text_color, bd=1, relief=tk.SOLID, insertbackground="white")
        self.entry_x.insert(0, str(self.fixed_x.get()))
        self.entry_x.pack(side="left", padx=(4, 12))

        tk.Label(f_pos_inputs, text="Y:", font=(FONT_MAIN, 12, "bold"), bg=self.card_bg, fg=self.text_color).pack(side="left")
        self.entry_y = tk.Entry(f_pos_inputs, width=5, font=(FONT_MONO, 12), justify="center", bg=COLOR_BG_INPUT, fg=self.text_color, bd=1, relief=tk.SOLID, insertbackground="white")
        self.entry_y.insert(0, str(self.fixed_y.get()))
        self.entry_y.pack(side="left", padx=(4, 15))

        self.btn_cap_pos = tk.Button(
            f_pos_inputs, text="📍 Capturar (3s)", font=(FONT_MAIN, 11, "bold"),
            bg=COLOR_BG_INPUT, fg=self.accent_color, activebackground=COLOR_BORDER, command=self.prepare_capture_position, cursor="hand2", padx=8, pady=3, bd=0
        )
        bind_hover(self.btn_cap_pos, COLOR_BG_INPUT, COLOR_BORDER)
        self.btn_cap_pos.pack(side="left")
        
        # --- SECTION 4: REAL-TIME EXECUTION LOG ACCORDION ---
        card_log = tk.Frame(main_container, bg=self.card_bg, highlightbackground=COLOR_BORDER, highlightthickness=1, padx=12, pady=12)
        card_log.pack(fill="x", pady=5)
        
        lbl_log = tk.Label(card_log, text="📜 Log de Execução em Tempo Real", font=(FONT_MAIN, 12, "bold"), bg=self.card_bg, fg=COLOR_TEXT_SEC)
        lbl_log.pack(anchor="w")

        f_log_text = tk.Frame(card_log, bg=self.card_bg)
        f_log_text.pack(fill="x", pady=(8, 0))

        self.txt_log = tk.Text(f_log_text, height=4, font=(FONT_MONO, 11), bg=COLOR_BG_INPUT, fg=self.success_color, bd=1, highlightbackground=COLOR_BORDER, highlightthickness=1, state="disabled")
        self.txt_log.pack(fill="x", expand=True)
        self.log_message("Sistema pronto. Pressione o atalho para iniciar.")

    def set_hotkey_by_name(self, hk_name):
        self.hotkey_name = str(hk_name).upper()
        if self.hotkey_name.startswith("F") and self.hotkey_name[1:].isdigit():
            f_num = int(self.hotkey_name[1:])
            if hasattr(keyboard.Key, f"f{f_num}"):
                self.hotkey_code = getattr(keyboard.Key, f"f{f_num}")
        else:
            try:
                self.hotkey_code = keyboard.KeyCode.from_char(self.hotkey_name.lower())
            except Exception:
                pass

        self._update_hotkey_ui()

    def set_emergency_hotkey_by_name(self, hk_name):
        self.emergency_hotkey_name = str(hk_name).upper()
        if self.emergency_hotkey_name == "ESC":
            self.emergency_hotkey_code = keyboard.Key.esc
        elif self.emergency_hotkey_name.startswith("F") and self.emergency_hotkey_name[1:].isdigit():
            f_num = int(self.emergency_hotkey_name[1:])
            if hasattr(keyboard.Key, f"f{f_num}"):
                self.emergency_hotkey_code = getattr(keyboard.Key, f"f{f_num}")
        else:
            try:
                self.emergency_hotkey_code = keyboard.KeyCode.from_char(self.emergency_hotkey_name.lower())
            except Exception:
                pass

        self._update_hotkey_ui()

    # --- FLOATING MINI OVERLAY TOOLBAR (DYNAMIC RESIZING & GAME SELECTOR) ---
    def open_mini_bar(self):
        if self.mini_bar_window and self.mini_bar_window.winfo_exists():
            self.mini_bar_window.lift()
            return

        self.root.withdraw()

        self.mini_bar_window = tk.Toplevel(self.root)
        self.mini_bar_window.overrideredirect(True)
        self.mini_bar_window.attributes('-topmost', True)
        self.mini_bar_window.configure(bg=COLOR_BORDER) # outer border

        self.mini_bar_inner_frame = tk.Frame(self.mini_bar_window, bg=self.card_bg, padx=4, pady=4)
        self.mini_bar_inner_frame.pack(fill="both", expand=True, padx=1, pady=1)

        # Drag handle (Grip)
        handle_lbl = tk.Label(self.mini_bar_inner_frame, text="⠿", font=(FONT_MAIN, 14, "bold"), bg=self.card_bg, fg=COLOR_TEXT_DISABLED, cursor="fleur")
        handle_lbl.pack(side="left", padx=(4, 6))
        handle_lbl.bind("<Button-1>", self._start_drag_mini_bar)
        handle_lbl.bind("<B1-Motion>", self._on_drag_mini_bar)
        self.mini_bar_inner_frame.bind("<Button-1>", self._start_drag_mini_bar)
        self.mini_bar_inner_frame.bind("<B1-Motion>", self._on_drag_mini_bar)

        # Game Selector OptionMenu inside Floating Bar
        game_names = list(self.game_profiles.keys())
        self.mini_game_var = tk.StringVar(value=self.active_game)
        
        game_menu = tk.OptionMenu(
            self.mini_bar_inner_frame,
            self.mini_game_var,
            *game_names,
            command=self._on_mini_game_switch
        )
        game_menu.config(
            font=(FONT_MAIN, 11, "bold"), bg=self.card_bg, fg=self.warning_color,
            activebackground=COLOR_BG_INPUT, activeforeground=self.warning_color,
            bd=0, highlightthickness=0, indicatoron=0, padx=6, pady=4
        )
        game_menu["menu"].config(bg=COLOR_BG_INPUT, fg=self.text_color, activebackground=self.accent_color, activeforeground=COLOR_BG_MAIN)
        game_menu.pack(side="left", padx=4)

        # Presets Buttons Frame on Mini Bar
        self.mini_bar_btn_frame = tk.Frame(self.mini_bar_inner_frame, bg=self.card_bg)
        self.mini_bar_btn_frame.pack(side="left", fill="x", expand=True, padx=6)

        # Start/Stop Button on Mini Bar
        btn_bg = self.success_color if not self.is_running else self.danger_color
        btn_text = f"▶ ({self.hotkey_name})" if not self.is_running else f"⏹ ({self.hotkey_name})"
        self.mini_bar_status_btn = tk.Button(
            self.mini_bar_inner_frame, text=btn_text, font=(FONT_MAIN, 11, "bold"),
            bg=btn_bg, fg=COLOR_BG_MAIN, bd=0, padx=12, pady=4, cursor="hand2", command=self.toggle_autoclicker
        )
        self.mini_bar_status_btn.pack(side="left", padx=6)

        # Restore Full Window Button (Config)
        btn_restore = tk.Button(
            self.mini_bar_inner_frame, text="⚙", font=(FONT_MAIN, 13, "bold"),
            bg=COLOR_BG_INPUT, fg=self.text_color, bd=0, padx=8, pady=4, cursor="hand2", command=self.close_mini_bar
        )
        bind_hover(btn_restore, COLOR_BG_INPUT, COLOR_BORDER)
        btn_restore.pack(side="left", padx=(2, 4))

        # Render Presets and Adjust Size Dynamically
        self._render_mini_bar_presets()

    def _on_mini_game_switch(self, game_name):
        self.switch_game(game_name)

    def _start_drag_mini_bar(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag_mini_bar(self, event):
        if self.mini_bar_window:
            x = self.mini_bar_window.winfo_x() + (event.x - self._drag_x)
            y = self.mini_bar_window.winfo_y() + (event.y - self._drag_y)
            self.mini_bar_window.geometry(f"+{x}+{y}")

    def _render_mini_bar_presets(self):
        if not self.mini_bar_btn_frame or not self.mini_bar_btn_frame.winfo_exists():
            return

        for widget in self.mini_bar_btn_frame.winfo_children():
            widget.destroy()

        presets = self.game_profiles.get(self.active_game, [])
        for preset in presets:
            p_name = preset.get("name", "Preset")
            is_active = (p_name == self.active_preset_name)
            btn_bg = COLOR_PRIMARY if is_active else COLOR_BG_INPUT
            btn_fg = COLOR_BG_MAIN if is_active else self.text_color

            btn = tk.Button(
                self.mini_bar_btn_frame, text=p_name, font=(FONT_MAIN, 11, "bold" if is_active else "normal"),
                bg=btn_bg, fg=btn_fg, bd=0, padx=8, pady=4, cursor="hand2", command=lambda p=preset: self.apply_preset(p)
            )
            if not is_active:
                bind_hover(btn, COLOR_BG_INPUT, COLOR_BORDER)
            btn.pack(side="left", padx=2)
            
            # Truncate text if too long
            truncate_text(btn, 120, p_name)

        # Dynamic Window Geometry Calculation
        if self.mini_bar_window and self.mini_bar_window.winfo_exists():
            self.mini_bar_window.update_idletasks()
            req_w = self.mini_bar_inner_frame.winfo_reqwidth() + 10
            req_h = max(45, self.mini_bar_inner_frame.winfo_reqheight() + 2)
            
            curr_x = self.mini_bar_window.winfo_x()
            curr_y = self.mini_bar_window.winfo_y()
            if curr_x <= 0 or curr_y <= 0:
                curr_x = 200
                curr_y = 100
            
            self.mini_bar_window.geometry(f"{req_w}x{req_h}+{curr_x}+{curr_y}")

    def close_mini_bar(self):
        if self.mini_bar_window and self.mini_bar_window.winfo_exists():
            self.mini_bar_window.destroy()
            self.mini_bar_window = None
        self.root.deiconify()

    # --- GAMES & QUICK PRESET BUTTONS DYNAMIC RENDERING ---
    def _render_game_tabs(self):
        for widget in self.f_game_tabs.winfo_children():
            widget.destroy()

        for game_name in self.game_profiles.keys():
            is_active = (game_name == self.active_game)
            btn_bg = COLOR_BORDER if is_active else COLOR_BG_INPUT
            btn_fg = self.accent_color if is_active else self.text_color
            
            btn = tk.Button(
                self.f_game_tabs, text=game_name, font=(FONT_MAIN, 11, "bold" if is_active else "normal"),
                bg=btn_bg, fg=btn_fg, bd=0, padx=12, pady=5, cursor="hand2", command=lambda g=game_name: self.switch_game(g)
            )
            if not is_active: bind_hover(btn, COLOR_BG_INPUT, COLOR_BORDER)
            btn.pack(side="left", padx=3)

        btn_add_game = tk.Button(
            self.f_game_tabs, text="➕ Novo", font=(FONT_MAIN, 11, "bold"),
            bg=self.success_color, fg=COLOR_BG_MAIN, bd=0, padx=8, pady=5, cursor="hand2", command=self.create_new_game
        )
        bind_hover(btn_add_game, self.success_color, COLOR_SUCCESS_HOVER)
        btn_add_game.pack(side="left", padx=(8, 3))

        if len(self.game_profiles) > 1:
            btn_del_game = tk.Button(
                self.f_game_tabs, text="❌", font=(FONT_MAIN, 11, "bold"),
                bg=self.danger_color, fg=COLOR_BG_MAIN, bd=0, padx=6, pady=5, cursor="hand2", command=self.delete_current_game
            )
            bind_hover(btn_del_game, self.danger_color, COLOR_ERROR_HOVER)
            btn_del_game.pack(side="left", padx=3)

    def _render_quick_preset_buttons(self):
        for widget in self.f_quick_buttons.winfo_children():
            widget.destroy()
        for widget in self.f_preset_actions.winfo_children():
            widget.destroy()

        presets = self.game_profiles.get(self.active_game, [])

        if not presets:
            tk.Label(self.f_quick_buttons, text="Nenhum preset neste jogo.", font=(FONT_MAIN, 11, "italic"), bg=self.card_bg, fg=self.text_subtle).pack(side="left")
        else:
            for preset in presets:
                p_name = preset.get("name", "Preset")
                is_active = (p_name == self.active_preset_name)
                btn_bg = self.accent_color if is_active else COLOR_BG_INPUT
                btn_fg = COLOR_BG_MAIN if is_active else self.text_color

                pill_frame = tk.Frame(self.f_quick_buttons, bg=btn_bg, bd=0, highlightbackground=COLOR_BORDER, highlightthickness=1 if not is_active else 0)
                pill_frame.pack(side="left", padx=3, pady=3)

                btn = tk.Button(
                    pill_frame, text=p_name, font=(FONT_MAIN, 11, "bold" if is_active else "normal"),
                    bg=btn_bg, fg=btn_fg, activebackground=COLOR_PRIMARY_HOVER, bd=0, padx=8, pady=4, cursor="hand2", command=lambda p=preset: self.apply_preset(p)
                )
                btn.pack(side="left")
                truncate_text(btn, 130, p_name)

                # Inline Edit
                btn_edit = tk.Button(
                    pill_frame, text="✏", font=(FONT_MAIN, 10), bg=btn_bg, fg=COLOR_BG_MAIN if is_active else self.accent_color,
                    activebackground=COLOR_PRIMARY_HOVER, bd=0, padx=4, pady=4, cursor="hand2", command=lambda p=preset: self.edit_preset(p)
                )
                btn_edit.pack(side="left")

                # Inline Delete
                btn_del = tk.Button(
                    pill_frame, text="🗑", font=(FONT_MAIN, 10), bg=btn_bg, fg=COLOR_BG_MAIN if is_active else self.danger_color,
                    activebackground=COLOR_PRIMARY_HOVER, bd=0, padx=4, pady=4, cursor="hand2", command=lambda p=preset: self.delete_preset(p)
                )
                btn_del.pack(side="left")

        # Action Control Buttons Row
        btn_add_builder = tk.Button(
            self.f_preset_actions, text="🧙‍♂️ Criar Novo Preset", font=(FONT_MAIN, 11, "bold"),
            bg=COLOR_BORDER, fg=self.accent_color, activebackground=COLOR_BG_INPUT, bd=0, padx=12, pady=5, cursor="hand2", command=self.open_custom_macro_builder
        )
        bind_hover(btn_add_builder, COLOR_BORDER, COLOR_BG_INPUT)
        btn_add_builder.pack(side="left", padx=(0, 4))

        if self.active_preset_name:
            active_p = next((p for p in presets if p.get("name") == self.active_preset_name), None)
            if active_p:
                btn_edit_act = tk.Button(
                    self.f_preset_actions, text="✏️ Editar", font=(FONT_MAIN, 11, "bold"),
                    bg=COLOR_BG_INPUT, fg=self.warning_color, bd=0, padx=10, pady=5, cursor="hand2", command=lambda: self.edit_preset(active_p)
                )
                bind_hover(btn_edit_act, COLOR_BG_INPUT, COLOR_BORDER)
                btn_edit_act.pack(side="left", padx=3)

                btn_del_act = tk.Button(
                    self.f_preset_actions, text="🗑️ Excluir", font=(FONT_MAIN, 11, "bold"),
                    bg=COLOR_BG_INPUT, fg=self.danger_color, bd=0, padx=10, pady=5, cursor="hand2", command=lambda: self.delete_preset(active_p)
                )
                bind_hover(btn_del_act, COLOR_BG_INPUT, COLOR_BORDER)
                btn_del_act.pack(side="left", padx=3)

        self._render_mini_bar_presets()

    def switch_game(self, game_name):
        if game_name in self.game_profiles:
            self.active_game = game_name
            self.active_preset_name = ""
            self._render_game_tabs()
            self._render_quick_preset_buttons()
            self._render_mini_bar_presets()
            self._save_config()

    def create_new_game(self):
        name = simpledialog.askstring("Novo Jogo", "Digite o nome do novo jogo/categoria (ex: Roblox, Valorant, GTA V):", parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        if not name.startswith("🎮") and not name.startswith("⛏️") and not name.startswith("🧱") and not name.startswith("🚀"):
            name = f"🎮 {name}"

        if name not in self.game_profiles:
            self.game_profiles[name] = []
            self.active_game = name
            self.active_preset_name = ""
            self._render_game_tabs()
            self._render_quick_preset_buttons()
            self._render_mini_bar_presets()
            self._save_config()

    def delete_current_game(self):
        if len(self.game_profiles) <= 1:
            messagebox.showwarning("Aviso", "Você precisa ter pelo menos um jogo/categoria registrado!")
            return

        if messagebox.askyesno("Excluir Jogo", f"Tem certeza que deseja excluir a categoria '{self.active_game}' e todos os seus presets?"):
            del self.game_profiles[self.active_game]
            self.active_game = list(self.game_profiles.keys())[0]
            self.active_preset_name = ""
            self._render_game_tabs()
            self._render_quick_preset_buttons()
            self._render_mini_bar_presets()
            self._save_config()

    def open_custom_macro_builder(self):
        ModularMacroDialog(self.root, self.active_game, preset_data=None, on_save_callback=self._on_custom_macro_saved)

    def edit_preset(self, preset_data):
        ModularMacroDialog(self.root, self.active_game, preset_data=preset_data, on_save_callback=self._on_custom_macro_saved)

    def delete_preset(self, preset_data):
        p_name = preset_data.get("name", "Preset")
        if messagebox.askyesno("Excluir Preset", f"Tem certeza que deseja excluir o preset '{p_name}' do jogo '{self.active_game}'?"):
            presets = self.game_profiles.get(self.active_game, [])
            self.game_profiles[self.active_game] = [p for p in presets if p.get("name") != p_name]
            
            if self.active_preset_name == p_name:
                self.active_preset_name = ""
            
            self._render_quick_preset_buttons()
            self._render_mini_bar_presets()
            self._save_config()

    def _on_custom_macro_saved(self, preset_data):
        presets = self.game_profiles[self.active_game]
        p_name = preset_data.get("name")
        existing_idx = next((i for i, p in enumerate(presets) if p.get("name") == p_name), -1)
        if existing_idx >= 0:
            presets[existing_idx] = preset_data
        else:
            presets.append(preset_data)

        self.apply_preset(preset_data)
        self._render_quick_preset_buttons()
        self._render_mini_bar_presets()
        self._save_config()

    def apply_preset(self, data):
        self.active_preset_name = data.get("name", "")

        self.target_type = data.get("target_type", "keyboard")
        self.target_name = data.get("target_name", "Espaço")
        self.target_mouse_action = data.get("target_mouse_action", "left")

        if "hotkey_name" in data and data["hotkey_name"]:
            self.set_hotkey_by_name(data["hotkey_name"])
        if "emergency_hotkey_name" in data and data["emergency_hotkey_name"]:
            self.set_emergency_hotkey_by_name(data["emergency_hotkey_name"])

        if "modular_steps" in data:
            self.modular_steps = data["modular_steps"]
            self.target_name = f"Macro ({len(self.modular_steps)} Etapas)"
        elif self.target_type == "sequence":
            self.target_sequence_raw = data.get("target_sequence_raw", ["shift+space"])
            self.target_sequence_parsed = self._parse_sequence_list(self.target_sequence_raw)
            disp_seq = ", ".join(self.target_sequence_raw).upper()
            self.target_name = f"Seq: {disp_seq}"
        elif self.target_type == "mouse":
            if self.target_mouse_action == "right":
                self.target_key = mouse.Button.right
            elif self.target_mouse_action == "middle":
                self.target_key = mouse.Button.middle
            else:
                self.target_key = mouse.Button.left
        elif self.target_type == "keyboard":
            if len(self.target_name) == 3 and self.target_name.startswith("'") and self.target_name.endswith("'"):
                self.target_key = keyboard.KeyCode.from_char(self.target_name[1].lower())
            else:
                self.target_key = keyboard.Key.space

        self.key_display_lbl.config(text=f"Alvo: [ {self.target_name} ]", fg=self.warning_color)

        self.mode.set(data.get("mode", "spam"))
        self.interval_ms.set(data.get("interval_ms", 50))
        self.entry_interval.delete(0, tk.END)
        self.entry_interval.insert(0, str(self.interval_ms.get()))

        self.use_jitter.set(data.get("use_jitter", False))
        self.jitter_ms.set(data.get("jitter_ms", 5))
        self.entry_jitter.delete(0, tk.END)
        self.entry_jitter.insert(0, str(self.jitter_ms.get()))

        self.position_mode.set(data.get("position_mode", "current"))
        self.fixed_x.set(data.get("fixed_x", 0))
        self.fixed_y.set(data.get("fixed_y", 0))
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, str(self.fixed_x.get()))
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(self.fixed_y.get()))

        self._on_mode_change()
        self._render_quick_preset_buttons()
        self._render_mini_bar_presets()
        self._play_sound(1200, 80)
        self.log_message(f"Preset carregado: '{self.active_preset_name}' ({self.target_name})")
        self._save_config()

    def _toggle_always_on_top(self):
        self.root.attributes('-topmost', self.always_on_top.get())

    def _on_mode_change(self):
        if self.mode.get() == "spam":
            self.entry_interval.config(state="normal")
            self.entry_jitter.config(state="normal")
        else:
            self.entry_interval.config(state="disabled")
            self.entry_jitter.config(state="disabled")

    def set_target(self, target_type, key_or_btn, mouse_action="left", name=""):
        self.target_type = target_type
        if isinstance(key_or_btn, str) and len(key_or_btn) == 1:
            try:
                self.target_key = keyboard.KeyCode.from_char(key_or_btn.lower())
            except Exception:
                self.target_key = key_or_btn
        else:
            self.target_key = key_or_btn

        self.target_mouse_action = mouse_action
        self.target_name = name
        self.key_display_lbl.config(text=f"Alvo: [ {self.target_name} ]", fg=self.warning_color)
        self.log_message(f"Alvo alterado para: {self.target_name}")
        self._save_config()

    def prepare_capture_target(self):
        if self.is_running:
            messagebox.showwarning("Aviso", "Pare o Auto Clicker antes de alterar o alvo!")
            return
        
        self.is_capturing_target = True
        self.is_capturing_hotkey = False
        self.is_capturing_emergency = False
        self.key_display_lbl.config(text="⌛ PRESSIONE QUALQUER TECLA OU CLIQUE...", fg=self.accent_color)
        self.btn_capture.config(state="disabled", bg=COLOR_BORDER)

    def prepare_capture_hotkey(self):
        if self.is_running:
            messagebox.showwarning("Aviso", "Pare o Auto Clicker antes de alterar o atalho!")
            return
        
        self.is_capturing_hotkey = True
        self.is_capturing_target = False
        self.is_capturing_emergency = False
        self.btn_hotkey.config(text="⌛ PRESSIONE TECLA...", bg=self.accent_color, fg=COLOR_BG_MAIN)

    def prepare_capture_emergency_hotkey(self):
        if self.is_running:
            messagebox.showwarning("Aviso", "Pare o Auto Clicker antes de alterar o atalho de emergência!")
            return

        self.is_capturing_emergency = True
        self.is_capturing_target = False
        self.is_capturing_hotkey = False
        self.btn_emergency_hotkey.config(text="⌛ TECLA EMERGÊNCIA...", bg=self.warning_color, fg=COLOR_BG_MAIN)

    def prepare_capture_position(self):
        if self.is_capturing_pos:
            return
        
        self.is_capturing_pos = True
        self.btn_cap_pos.config(state="disabled")
        
        def countdown(secs):
            if secs > 0:
                self.btn_cap_pos.config(text=f"Posicione em {secs}s...")
                self.root.after(1000, lambda: countdown(secs - 1))
            else:
                pos = self.mouse_controller.position
                self.entry_x.delete(0, tk.END)
                self.entry_x.insert(0, str(pos[0]))
                self.entry_y.delete(0, tk.END)
                self.entry_y.insert(0, str(pos[1]))
                self.fixed_x.set(pos[0])
                self.fixed_y.set(pos[1])
                self.position_mode.set("fixed")
                self.btn_cap_pos.config(text="📍 Capturar Posição (3s)", state="normal")
                self.is_capturing_pos = False
                self.log_message(f"Posição fixa capturada: ({pos[0]}, {pos[1]})")
                self._play_sound(1200, 80)
                self._save_config()

        countdown(3)

    def _start_global_listeners(self):
        # Keyboard Listener
        self.kb_listener = keyboard.Listener(on_press=self._on_key_press)
        self.kb_listener.daemon = True
        self.kb_listener.start()

        # Mouse Listener for capture
        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()

    def _on_key_press(self, key):
        # 1. Capture target key mode
        if self.is_capturing_target:
            self.is_capturing_target = False
            
            if isinstance(key, keyboard.Key):
                name = key.name.upper() if hasattr(key, 'name') else str(key)
                name_map = {
                    "SPACE": "Espaço", "ENTER": "Enter", "BACKSPACE": "Backspace",
                    "TAB": "Tab", "SHIFT": "Shift", "CTRL": "Ctrl", "ALT": "Alt", "ESC": "Esc"
                }
                name = name_map.get(name, name)
            elif hasattr(key, 'char') and key.char:
                name = f"'{key.char.upper()}'"
            else:
                name = str(key)

            self.root.after(0, self.set_target, "keyboard", key, "left", name)
            self.root.after(0, lambda: self.btn_capture.config(state="normal", bg=self.accent_color))
            return

        # 2. Capture hotkey mode
        if self.is_capturing_hotkey:
            self.is_capturing_hotkey = False
            self.hotkey_code = key
            if isinstance(key, keyboard.Key):
                self.hotkey_name = key.name.upper() if hasattr(key, 'name') else str(key)
            elif hasattr(key, 'char') and key.char:
                self.hotkey_name = key.char.upper()
            else:
                self.hotkey_name = str(key)

            self.root.after(0, self._update_hotkey_ui)
            return

        # 3. Capture emergency hotkey mode
        if self.is_capturing_emergency:
            self.is_capturing_emergency = False
            self.emergency_hotkey_code = key
            if isinstance(key, keyboard.Key):
                self.emergency_hotkey_name = key.name.upper() if hasattr(key, 'name') else str(key)
            elif hasattr(key, 'char') and key.char:
                self.emergency_hotkey_name = key.char.upper()
            else:
                self.emergency_hotkey_name = str(key)

            self.root.after(0, self._update_hotkey_ui)
            return

        # 4. Check for Emergency Stop Hotkey Trigger
        if key == self.emergency_hotkey_code:
            if self.is_running:
                self.log_message(f"🚨 PARADA DE EMERGÊNCIA DISPARADA ({self.emergency_hotkey_name})!")
                self.root.after(0, self.stop_autoclicker)
            return

        # 5. Check for Main Global Start Hotkey
        if key == self.hotkey_code:
            self.root.after(0, self.toggle_autoclicker)

    def _on_mouse_click(self, x, y, button, pressed):
        if not pressed:
            return
        
        if self.is_capturing_target:
            try:
                wx = self.root.winfo_rootx()
                wy = self.root.winfo_rooty()
                ww = self.root.winfo_width()
                wh = self.root.winfo_height()
                if wx <= x <= wx + ww and wy <= y <= wy + wh:
                    return
            except Exception:
                pass

            self.is_capturing_target = False
            b_name = "Clique Esquerdo"
            a_type = "left"

            if button == mouse.Button.right:
                b_name = "Clique Direito"
                a_type = "right"
            elif button == mouse.Button.middle:
                b_name = "Clique Meio"
                a_type = "middle"

            self.root.after(0, self.set_target, "mouse", button, a_type, b_name)
            self.root.after(0, lambda: self.btn_capture.config(state="normal", bg=self.accent_color))

    def _update_hotkey_ui(self):
        self.btn_hotkey.config(text=f"⌨️ Atalho: [{self.hotkey_name}]", bg=COLOR_BORDER, fg=self.text_color)
        self.btn_emergency_hotkey.config(text=f"🚨 Parada: [{self.emergency_hotkey_name}]", bg=COLOR_ERROR, fg=COLOR_BG_MAIN)
        self.btn_toggle.config(text=f"▶ INICIAR ({self.hotkey_name})")
        if not self.is_running:
            self.status_label.config(text=f"⏹ PARADO  (Pressione {self.hotkey_name} para Ligar | {self.emergency_hotkey_name} Emergência)")
        else:
            self.status_label.config(text=f"▶ ATIVO  (Pressione {self.hotkey_name} para Parar | {self.emergency_hotkey_name} Emergência)")
        
        if self.mini_bar_status_btn and self.mini_bar_status_btn.winfo_exists():
            btn_bg = self.success_color if not self.is_running else self.danger_color
            btn_text = f"▶ ({self.hotkey_name})" if not self.is_running else f"⏹ ({self.hotkey_name})"
            self.mini_bar_status_btn.config(text=btn_text, bg=btn_bg)

        self._save_config()

    def toggle_autoclicker(self):
        if self.is_capturing_target or self.is_capturing_hotkey or self.is_capturing_emergency or self.is_capturing_pos:
            return

        if self.is_running:
            self.stop_autoclicker()
        else:
            self.start_autoclicker()

    def _validate_inputs(self):
        try:
            if self.mode.get() == "spam":
                ms = int(self.entry_interval.get())
                if ms < 1:
                    raise ValueError
                self.interval_ms.set(ms)

                jit = int(self.entry_jitter.get())
                if jit < 0:
                    raise ValueError
                self.jitter_ms.set(jit)

            if self.position_mode.get() == "fixed":
                self.fixed_x.set(int(self.entry_x.get()))
                self.fixed_y.set(int(self.entry_y.get()))

            return True
        except ValueError:
            messagebox.showerror("Erro de Configuração", "Por favor, verifique se os números digitados nos campos são inteiros válidos e maiores que zero.")
            return False

    def start_autoclicker(self):
        if self.is_running:
            return

        if not self._validate_inputs():
            return

        self._save_config()

        self.is_running = True
        self.stop_event.clear()
        
        self.btn_toggle.config(text=f"⏹ PARAR ({self.hotkey_name})", bg=self.danger_color)
        bind_hover(self.btn_toggle, self.danger_color, COLOR_ERROR_HOVER)

        self.status_label.config(text=f"RODANDO (Atalho: {self.hotkey_name})", fg=self.success_color)
        self.status_frame.config(highlightbackground=self.success_color)
        self.pulse_ind.set_state(True)
        self.btn_capture.config(state="disabled")
        self.btn_hotkey.config(state="disabled")
        self.btn_emergency_hotkey.config(state="disabled")

        if self.mini_bar_status_btn and self.mini_bar_status_btn.winfo_exists():
            self.mini_bar_status_btn.config(text=f"⏹ ({self.hotkey_name})", bg=self.danger_color)
        
        self.total_clicks = 0
        self.start_time = time.time()
        self.cps_history.clear()
        
        self.log_message(f"▶ EXECUÇÃO INICIADA (Atalho {self.hotkey_name})")
        self._play_sound(1000, 100)

        # Start Click Thread
        self.click_thread = threading.Thread(target=self._run_autoclick_loop, daemon=True)
        self.click_thread.start()

    def stop_autoclicker(self):
        if not self.is_running: return
        self.is_running = False
        self.stop_event.set()

        if self.mode.get() == "hold":
            self._release_target_key()
        
        self.btn_toggle.config(text=f"▶ INICIAR ({self.hotkey_name})", bg=self.success_color)
        bind_hover(self.btn_toggle, self.success_color, COLOR_SUCCESS_HOVER)

        self.status_label.config(text=f"PARADO (Atalho: {self.hotkey_name})", fg=COLOR_TEXT_SEC)
        self.status_frame.config(highlightbackground=COLOR_BORDER)
        self.pulse_ind.set_state(False)
        self.btn_capture.config(state="normal")
        self.btn_hotkey.config(state="normal")
        self.btn_emergency_hotkey.config(state="normal")

        if self.mini_bar_status_btn and self.mini_bar_status_btn.winfo_exists():
            self.mini_bar_status_btn.config(text=f"▶ ({self.hotkey_name})", bg=self.success_color)

        # Update total run time
        if hasattr(self, 'start_time'):
            elapsed = int(time.time() - self.start_time)
            self.total_run_time_sec += elapsed
            self._save_config()
            
            # Show donation popup if used for more than 1 hour total
            if self.total_run_time_sec > 3600:
                self.show_donation_popup()

        self._play_sound(600, 100)

    def _play_sound(self, freq, duration):
        if self.sound_enabled.get() and WINSOUND_AVAILABLE:
            try:
                threading.Thread(target=lambda: winsound.Beep(freq, duration), daemon=True).start()
            except Exception:
                pass

    def show_donation_popup(self):
        # Don't show if already showed recently (within 24 hours)
        now = time.time()
        if now - self.last_donation_popup < 86400:
            return

        self.last_donation_popup = now
        self._save_config()

        popup = tk.Toplevel(self.root)
        popup.title("☕ Apoie o Projeto")
        popup.geometry("450x300")
        popup.configure(bg=COLOR_BG_MAIN)
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        # Center popup
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 225
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 150
        popup.geometry(f"+{x}+{y}")

        tk.Label(popup, text="⚡ O Auto Clicker já trabalhou bastante pra você!", font=(FONT_MAIN, 11, "bold"), bg=COLOR_BG_MAIN, fg=self.accent_color).pack(pady=(20, 5))
        
        msg = "Este programa é 100% gratuito e não tem anúncios.\nSe ele te ajudou a farmar ou poupou o seu tempo,\nconsidere pagar um café ☕ pro desenvolvedor!"
        tk.Label(popup, text=msg, font=(FONT_MAIN, 9), bg=COLOR_BG_MAIN, fg=self.text_color, justify="center").pack(pady=10)

        # Pix Key Box
        pix_frame = tk.Frame(popup, bg=COLOR_BG_CARD, bd=1, relief="solid")
        pix_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(pix_frame, text="Chave PIX (Cole no seu Banco):", font=(FONT_MAIN, 8, "bold"), bg=COLOR_BG_CARD, fg=self.text_subtle).pack(pady=(10, 0))
        
        pix_key = "seu-pix-aqui@gmail.com" # PLACEHOLDER
        e_pix = tk.Entry(pix_frame, font=(FONT_MONO, 10, "bold"), bg=COLOR_BG_INPUT, fg=self.success_color, justify="center", bd=0)
        e_pix.insert(0, pix_key)
        e_pix.config(state="readonly")
        e_pix.pack(pady=10, padx=10, fill="x")

        def copy_pix():
            self.root.clipboard_clear()
            self.root.clipboard_append(pix_key)
            btn_copy.config(text="Copiado! ✔️", bg=self.success_color, fg=COLOR_BG_MAIN)
            popup.after(2000, lambda: btn_copy.config(text="Copiar Chave PIX", bg=COLOR_BG_INPUT, fg=self.accent_color))

        btn_copy = tk.Button(pix_frame, text="Copiar Chave PIX", font=(FONT_MAIN, 9, "bold"), bg=COLOR_BG_INPUT, fg=self.accent_color, bd=0, padx=10, pady=5, cursor="hand2", command=copy_pix)
        btn_copy.pack(pady=(0, 10))

        # Star Github button
        def open_github():
            import webbrowser
            webbrowser.open("https://github.com/henrique-jfp/AutoClick")
            popup.destroy()

        btn_star = tk.Button(popup, text="⭐ Não tem PIX? Deixe uma Estrela no Github!", font=(FONT_MAIN, 9, "bold"), bg=COLOR_BG_MAIN, fg=self.accent_color, bd=0, cursor="hand2", command=open_github)
        btn_star.pack(pady=(10, 5))

        # Close button
        btn_close = tk.Button(popup, text="Já apoiei / Fechar", font=(FONT_MAIN, 8), bg=COLOR_BG_MAIN, fg=self.text_subtle, bd=0, cursor="hand2", command=popup.destroy)
        btn_close.pack(side="bottom", pady=15)

    def _parse_single_key(self, token):
        token_upper = str(token).upper()
        name_map = {
            "ESPAÇO": keyboard.Key.space, "ESPAC": keyboard.Key.space, "SPACE": keyboard.Key.space,
            "ENTER": keyboard.Key.enter, "BACKSPACE": keyboard.Key.backspace, "TAB": keyboard.Key.tab,
            "SHIFT": keyboard.Key.shift, "CTRL": keyboard.Key.ctrl, "ALT": keyboard.Key.alt, "ESC": keyboard.Key.esc
        }
        if token_upper in name_map:
            return name_map[token_upper]
        elif len(str(token)) == 1:
            try:
                return keyboard.KeyCode.from_char(str(token).lower())
            except Exception:
                return token
        return token

    def _parse_sequence_list(self, raw_tokens):
        parsed = []
        for token in raw_tokens:
            if "+" in token:
                sub_parts = [p.strip() for p in token.split("+") if p.strip()]
                parsed.append([self._parse_single_key(p) for p in sub_parts])
            else:
                parsed.append(self._parse_single_key(token))
        return parsed

    def _press_target_action(self):
        try:
            if self.position_mode.get() == "fixed":
                self.mouse_controller.position = (self.fixed_x.get(), self.fixed_y.get())

            if self.target_type == "keyboard":
                self.kb_controller.press(self.target_key)
            elif self.target_type == "mouse":
                act = self.target_mouse_action
                btn = self.target_key if isinstance(self.target_key, mouse.Button) else mouse.Button.left
                if act == "left" or act == "right" or act == "middle":
                    self.mouse_controller.click(btn, 1)
                elif act == "double":
                    self.mouse_controller.click(btn, 2)
        except Exception as e:
            print(f"Erro ao disparar ação: {e}")

    def _release_target_key(self):
        try:
            if self.target_type == "keyboard":
                self.kb_controller.release(self.target_key)
            elif self.target_type == "mouse" and isinstance(self.target_key, mouse.Button):
                self.mouse_controller.release(self.target_key)
        except Exception as e:
            print(f"Erro ao soltar tecla: {e}")

    # --- ADVANCED DYNAMIC MODULAR MULTI-STEP MACRO ENGINE ---
    def _run_modular_macro_loop(self):
        held_keys = set()

        try:
            while not self.stop_event.is_set():
                for idx, step in enumerate(self.modular_steps):
                    if self.stop_event.is_set():
                        break

                    # Skip disabled steps
                    if not step.get("enabled", True):
                        continue

                    stype = step.get("type", "")

                    if stype == "press_hold":
                        k = self._parse_single_key(step.get("key", "w"))
                        self.log_message(f"Etapa {idx+1}: Segurar Tecla [{str(step.get('key','w')).upper()}]")
                        self.kb_controller.press(k)
                        held_keys.add(k)
                        time.sleep(0.025)

                    elif stype == "tap_loop":
                        k = self._parse_single_key(step.get("key", "shift"))
                        count = int(step.get("count", 1))
                        base_int = float(step.get("interval_sec", 0.5))

                        self.log_message(f"Etapa {idx+1}: Tocar [{str(step.get('key','shift')).upper()}] {count}x")
                        for _ in range(count):
                            if self.stop_event.is_set():
                                break
                            t_start = time.time()
                            self.kb_controller.press(k)
                            time.sleep(0.035)
                            self.kb_controller.release(k)

                            self.total_clicks += 1
                            self.cps_history.append(t_start)

                            # Handle Range if enabled
                            target_interval = base_int
                            if step.get("use_range", False):
                                min_i = float(step.get("interval_min", 0.3))
                                max_i = float(step.get("interval_max", 0.7))
                                target_interval = random.uniform(min_i, max_i)

                            target_delay = max(0.01, target_interval - 0.035)
                            t_loop = time.time()
                            while (time.time() - t_loop) < target_delay and not self.stop_event.is_set():
                                time.sleep(0.005)

                    elif stype == "release":
                        k = self._parse_single_key(step.get("key", "w"))
                        self.log_message(f"Etapa {idx+1}: Soltar Tecla [{str(step.get('key','w')).upper()}]")
                        self.kb_controller.release(k)
                        if k in held_keys:
                            held_keys.remove(k)
                        time.sleep(0.015)

                    elif stype == "pause":
                        base_pause = float(step.get("duration_sec", 0.45))
                        if step.get("use_range", False):
                            min_p = float(step.get("duration_min", 0.3))
                            max_p = float(step.get("duration_max", 0.6))
                            base_pause = random.uniform(min_p, max_p)

                        self.log_message(f"Etapa {idx+1}: Pausa de {base_pause:.2f}s")
                        t_pause = time.time()
                        while (time.time() - t_pause) < base_pause and not self.stop_event.is_set():
                            time.sleep(0.005)

                    elif stype == "hold_duration":
                        k = self._parse_single_key(step.get("key", "w"))
                        dur_sec = float(step.get("duration_sec", 4.0))

                        self.log_message(f"Etapa {idx+1}: Caminhar com [{str(step.get('key','w')).upper()}] por {dur_sec:.1f}s")
                        self.kb_controller.press(k)
                        held_keys.add(k)
                        t_walk = time.time()
                        while (time.time() - t_walk) < dur_sec and not self.stop_event.is_set():
                            time.sleep(0.005)
                        self.kb_controller.release(k)
                        if k in held_keys:
                            held_keys.remove(k)

                    elif stype == "sequence_combo":
                        raw_seq = step.get("sequence_raw", ["shift+space"])
                        interval_ms = int(step.get("interval_ms", 500))
                        parsed_items = self._parse_sequence_list(raw_seq)

                        self.log_message(f"Etapa {idx+1}: Combo [{', '.join(raw_seq).upper()}]")
                        for item in parsed_items:
                            if self.stop_event.is_set():
                                break
                            try:
                                if isinstance(item, list):
                                    for sub_k in item:
                                        self.kb_controller.press(sub_k)
                                        time.sleep(0.025)
                                    time.sleep(0.035)
                                    for sub_k in reversed(item):
                                        self.kb_controller.release(sub_k)
                                        time.sleep(0.015)
                                else:
                                    self.kb_controller.press(item)
                                    time.sleep(0.020)
                                    self.kb_controller.release(item)
                                    time.sleep(0.015)
                            except Exception:
                                pass

                            t_sub = time.time()
                            while (time.time() - t_sub) < (interval_ms / 1000.0) and not self.stop_event.is_set():
                                time.sleep(0.005)

                    elif stype == "mouse_click":
                        btn_str = step.get("button", "left")
                        btn = mouse.Button.right if btn_str == "right" else (mouse.Button.middle if btn_str == "middle" else mouse.Button.left)
                        if step.get("use_coords", False):
                            x, y = int(step.get("x", 0)), int(step.get("y", 0))
                            self.mouse_controller.position = (x, y)
                            self.log_message(f"Etapa {idx+1}: Clique Mouse [{btn_str.upper()}] em ({x}, {y})")
                        else:
                            self.log_message(f"Etapa {idx+1}: Clique Mouse [{btn_str.upper()}] na posição atual")

                        self.mouse_controller.click(btn, 1)
                        self.total_clicks += 1
                        time.sleep(0.03)

                    elif stype == "mouse_move":
                        x, y = int(step.get("x", 500)), int(step.get("y", 500))
                        self.log_message(f"Etapa {idx+1}: Mover Mouse para ({x}, {y})")
                        self.mouse_controller.position = (x, y)
                        time.sleep(0.02)

                    elif stype == "mouse_drag":
                        x1, y1 = int(step.get("x1", 100)), int(step.get("y1", 100))
                        x2, y2 = int(step.get("x2", 500)), int(step.get("y2", 500))
                        dur = float(step.get("duration_sec", 1.0))

                        self.log_message(f"Etapa {idx+1}: Arrastar de ({x1},{y1}) até ({x2},{y2}) em {dur}s")
                        self.mouse_controller.position = (x1, y1)
                        time.sleep(0.02)
                        self.mouse_controller.press(mouse.Button.left)

                        # Smooth interpolation
                        steps_count = max(10, int(dur * 30))
                        for s_i in range(steps_count + 1):
                            if self.stop_event.is_set():
                                break
                            curr_x = int(x1 + (x2 - x1) * (s_i / steps_count))
                            curr_y = int(y1 + (y2 - y1) * (s_i / steps_count))
                            self.mouse_controller.position = (curr_x, curr_y)
                            time.sleep(dur / steps_count)

                        self.mouse_controller.release(mouse.Button.left)

                    elif stype == "mouse_scroll":
                        direc = step.get("direction", "down")
                        clks = int(step.get("clicks", 5))
                        amount = -clks if direc == "down" else clks
                        self.log_message(f"Etapa {idx+1}: Rolar Mouse [{direc.upper()}] ({clks} cliques)")
                        self.mouse_controller.scroll(0, amount)
                        time.sleep(0.04)

                    elif stype == "group_block":
                        self.log_message(f"Etapa {idx+1}: Executando Bloco [{step.get('name','Bloco')}]")

        finally:
            for k in list(held_keys):
                try:
                    self.kb_controller.release(k)
                except Exception:
                    pass

    def _run_autoclick_loop(self):
        if self.target_type in ["modular_macro", "dash5x_cooldown", "step_macro"]:
            self._run_modular_macro_loop()
            return

        current_mode = self.mode.get()
        base_delay = self.interval_ms.get() / 1000.0

        if current_mode == "spam":
            while not self.stop_event.is_set():
                t_start = time.time()
                self._press_target_action()
                if self.target_type == "keyboard":
                    time.sleep(0.015)
                    self._release_target_key()

                self.total_clicks += 1
                self.cps_history.append(t_start)

                delay_sec = base_delay
                if self.use_jitter.get() and self.jitter_ms.get() > 0:
                    jit = random.uniform(-self.jitter_ms.get(), self.jitter_ms.get()) / 1000.0
                    delay_sec = max(0.001, base_delay + jit)

                elapsed = 0
                while elapsed < delay_sec and not self.stop_event.is_set():
                    time.sleep(min(0.002, delay_sec - elapsed))
                    elapsed += 0.002

        elif current_mode == "hold":
            while not self.stop_event.is_set():
                if self.position_mode.get() == "fixed":
                    self.mouse_controller.position = (self.fixed_x.get(), self.fixed_y.get())

                self._press_target_action()
                self.total_clicks += 1
                time.sleep(0.03)

            self._release_target_key()

    def _update_stats_loop(self):
        if self.is_running:
            now = time.time()
            elapsed_sec = int(now - self.start_time)
            mins = elapsed_sec // 60
            secs = elapsed_sec % 60
            time_str = f"{mins:02d}:{secs:02d}"

            self.cps_history = [t for t in self.cps_history if now - t <= 1.0]
            cps = len(self.cps_history)

            self.lbl_clicks.config(text=f"Cliques: {self.total_clicks:,}")
            self.lbl_cps.config(text=f"CPS: {cps:.1f}")
            self.lbl_time.config(text=f"Tempo: {time_str}")
        else:
            self.lbl_clicks.config(text="Cliques: 0")
            self.lbl_cps.config(text="CPS: 0.0")
            self.lbl_time.config(text="Tempo: 00:00")

        self.root.after(200, self._update_stats_loop)

    def _save_config(self):
        data = {
            "target_type": self.target_type,
            "target_name": self.target_name,
            "target_mouse_action": self.target_mouse_action,
            "target_sequence_raw": self.target_sequence_raw,
            "modular_steps": self.modular_steps,
            "hotkey_name": self.hotkey_name,
            "emergency_hotkey_name": self.emergency_hotkey_name,
            "mode": self.mode.get(),
            "interval_ms": self.interval_ms.get(),
            "use_jitter": self.use_jitter.get(),
            "jitter_ms": self.jitter_ms.get(),
            "position_mode": self.position_mode.get(),
            "fixed_x": self.fixed_x.get(),
            "fixed_y": self.fixed_y.get(),
            "total_run_time_sec": self.total_run_time_sec,
            "last_donation_popup": self.last_donation_popup,
            "always_on_top": self.always_on_top.get(),
            "sound_enabled": self.sound_enabled.get(),
            "minimize_to_tray": self.minimize_to_tray.get(),
            "active_game": self.active_game,
            "active_preset_name": self.active_preset_name,
            "game_profiles": self.game_profiles
        }
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _load_config(self):
        if not os.path.exists(self.CONFIG_FILE):
            return

        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "game_profiles" in data and isinstance(data["game_profiles"], dict) and data["game_profiles"]:
                self.game_profiles = data["game_profiles"]

                if "🎮 Genshin Impact" in self.game_profiles:
                    presets = self.game_profiles["🎮 Genshin Impact"]
                    existing_idx = next((i for i, p in enumerate(presets) if "Run Dash" in p.get("name", "")), -1)
                    stamina_preset = self.DEFAULT_GAMES["🎮 Genshin Impact"][0]
                    if existing_idx >= 0:
                        presets[existing_idx] = stamina_preset
                    else:
                        presets.insert(0, stamina_preset)

            self.active_game = data.get("active_game", list(self.game_profiles.keys())[0] if self.game_profiles else "🎮 Genshin Impact")
            self.active_preset_name = data.get("active_preset_name", "")

            self.target_type = data.get("target_type", "keyboard")
            self.target_name = data.get("target_name", "Espaço")
            self.target_mouse_action = data.get("target_mouse_action", "left")

            if "modular_steps" in data:
                self.modular_steps = data["modular_steps"]

            if self.target_type in ["modular_macro", "dash5x_cooldown", "step_macro"]:
                self.target_name = f"Macro ({len(self.modular_steps)} Etapas)"
            elif self.target_type == "sequence":
                self.target_sequence_raw = data.get("target_sequence_raw", ["shift+space"])
                self.target_sequence_parsed = self._parse_sequence_list(self.target_sequence_raw)

            self.hotkey_name = data.get("hotkey_name", "F12")
            if self.hotkey_name.startswith("F") and self.hotkey_name[1:].isdigit():
                f_num = int(self.hotkey_name[1:])
                if hasattr(keyboard.Key, f"f{f_num}"):
                    self.hotkey_code = getattr(keyboard.Key, f"f{f_num}")

            self.emergency_hotkey_name = data.get("emergency_hotkey_name", "ESC")
            if self.emergency_hotkey_name == "ESC":
                self.emergency_hotkey_code = keyboard.Key.esc
            elif self.emergency_hotkey_name.startswith("F") and self.emergency_hotkey_name[1:].isdigit():
                f_num = int(self.emergency_hotkey_name[1:])
                if hasattr(keyboard.Key, f"f{f_num}"):
                    self.emergency_hotkey_code = getattr(keyboard.Key, f"f{f_num}")

            self.mode.set(data.get("mode", "spam"))
            self.interval_ms.set(data.get("interval_ms", 50))
            self.use_jitter.set(data.get("use_jitter", False))
            self.jitter_ms.set(data.get("jitter_ms", 5))

            self.position_mode.set(data.get("position_mode", "current"))
            self.fixed_x.set(data.get("fixed_x", 0))
            self.fixed_y.set(data.get("fixed_y", 0))

            self.always_on_top.set(data.get("always_on_top", False))
            self.sound_enabled.set(data.get("sound_enabled", True))
            self.minimize_to_tray.set(data.get("minimize_to_tray", False))
            self.total_run_time_sec = data.get("total_run_time_sec", 0)
            self.last_donation_popup = data.get("last_donation_popup", 0)
        except Exception:
            pass

    def on_close(self):
        self._save_config()
        if self.is_running:
            self.stop_autoclicker()

        set_windows_high_precision_timer(False)

        if PYSTRAY_AVAILABLE and self.minimize_to_tray.get():
            self.root.withdraw()
            self._create_system_tray()
        else:
            self.root.destroy()
            sys.exit(0)

    def _create_system_tray(self):
        if self.tray_icon:
            return

        icon_img = Image.open("app_icon.png") if os.path.exists("app_icon.png") else Image.new("RGB", (64, 64), (137, 180, 250))
        
        menu = pystray.Menu(
            pystray.MenuItem("Exibir Auto Clicker", self._show_from_tray, default=True),
            pystray.MenuItem(f"Ligar/Desligar ({self.hotkey_name})", lambda: self.root.after(0, self.toggle_autoclicker)),
            pystray.MenuItem("Sair Completamente", self._quit_from_tray)
        )
        
        self.tray_icon = pystray.Icon("AutoClicker", icon_img, "Auto Clicker Pro", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _show_from_tray(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.root.after(0, self.root.deiconify)

    def _quit_from_tray(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)
        sys.exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
