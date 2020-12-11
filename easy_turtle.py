
# ©2020 Ryo Fujinami.

import converter
import re
import platform
import sys
import os
import json
import time
import turtle
import webbrowser
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font
from tkinter import ttk
import tkinter as tk
from datetime import datetime
import shutil
import traceback

# TODO: Delete "ask_save_end" key

SIZE = 8
HEIGHT = 72
WIDTH = 480

def GET_CONFIG():
    """設定を取得"""
    global CONFIG
    if os.path.exists(CONFIG_FILE) is True:
        with open(CONFIG_FILE, "r", encoding="UTF-8")as f:
            config = json.load(f)
        CONFIG = {}
        for key, value in DEFAULT_CONFIG.items():
            if key in config:
                CONFIG[key] = config[key]
            else:
                CONFIG[key] = value
    else:
        CONFIG = DEFAULT_CONFIG
    with open(CONFIG_FILE, "w", encoding="UTF-8")as f:
        json.dump(CONFIG, f, indent=4)


SYSTEM = platform.system()
if SYSTEM == "Windows":
    from ctypes import windll

    FONT_TYPE1 = "Courier New"
    FONT_TYPE2 = "Times New Roman"

    os.chdir(os.path.dirname(sys.argv[0]))
    
    ICON_FILE = os.path.abspath("./Files/WinIcon.gif")
    README_FILE = os.path.abspath("./Files/Readme.html")

    try:
        with open("./test", "w")as f:
            f.write("\0")
        os.remove("./test")
        PROGRA = False
    except PermissionError:
        PROGRA = True

    if os.path.exists(os.path.join("C:/Users", os.getlogin(),
                                   "onedrive/ドキュメント")) is True:
        DOCUMENTS = os.path.join("C:/Users", os.getlogin(),
                                 "onedrive/ドキュメント/EasyTurtle")
    else:
        DOCUMENTS = os.path.join("C:/Users", os.getlogin(),
                                 "Documents/EasyTurtle")
    os.makedirs(DOCUMENTS, exist_ok=True)

    samples = os.path.join(DOCUMENTS, "Samples")
    if os.path.exists(samples) is False:
        shutil.copytree('./Samples', samples)

    if PROGRA is False:
        CONFIG_FILE = os.path.abspath("./config.json")
        os.makedirs("./cache", exist_ok=True)
    else:
        CONFIG_FILE = "C:/ProgramData/EasyTurtle/config.json"
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        os.makedirs("C:/ProgramData/EasyTurtle/cache", exist_ok=True)

    DEFAULT_CONFIG = {
        "save_more_info": False,
        "tolerate_danger": False,
        "expand_window": True,
        "delete_cache": True,
        "ask_save_new": True}

    GET_CONFIG()
    if CONFIG["expand_window"] is True:
        WIN_MAG = windll.user32.GetSystemMetrics(0) / 1280
    else:
        WIN_MAG = 1
elif SYSTEM == "Linux":
    import subprocess

    FONT_TYPE1 = "FreeMono"
    FONT_TYPE2 = "FreeSerif"

    os.chdir(os.getcwd())

    ICON_FILE = os.path.abspath("./Files/WinIcon.gif")
    README_FILE = os.path.abspath("./Files/Readme.html")

    PROGRA = False

    DOCUMENTS = os.path.abspath("./")
    CONFIG_FILE = os.path.abspath("./config.json")
    os.makedirs("./cache", exist_ok=True)

    DEFAULT_CONFIG = {
        "save_more_info": False,
        "tolerate_danger": False,
        "expand_window": True,
        "delete_cache": True,
        "ask_save_new": True}
    GET_CONFIG()

    if CONFIG["expand_window"] is True:
        response = subprocess.check_output("xrandr | fgrep '*'", shell=True)
        metrics = response.decode("utf8").split()[0].split("x")
        WIN_MAG = int(metrics[0]) / 1280
    else:
        WIN_MAG = 1
else:
    messagebox.showerror("エラー", f"{SYSTEM}には対応していません。")


def EXPAND(num): return int(round(num * WIN_MAG))


FONT = (FONT_TYPE1, EXPAND(12), "bold")

__version__ = (4, 8, 1)


class EasyTurtle:
    def __init__(self, file=None):
        """初期化"""
        self.index = 0
        self.widgets = []
        self.copied_widgets = []
        self.default_data = []
        self.backed_up = []
        self.warning_ignore = False
        self.program_name = None
        self.basename = "untitled"
        self.setup()
        if file is not None:
            self.opener(file)
        if (SYSTEM == "Linux") and ("FreeMono" not in font.families()):
            messagebox.showwarning("警告", "\
EasyTurtleを安定してご利用いただくために\n\
GNU FreeFontのインストールをおすすめします。")
        self.root.mainloop()

    def __str__(self):
        """文字列を定義"""
        return "EasyTurtleObject"

    def __repr__(self):
        """コンストラクタの文字列定義"""
        data = self.get_data()
        return f"EasyTurtle(self, data={data})"

    def version_info(self, event):
        """設定を編集"""
        self.all_redraw()
        self.win = tk.Toplevel(self.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.icon)
        self.win.wait_visibility()
        self.win.grab_set()
        lab1 = tk.Label(self.win, text="Version",
                        font=(FONT_TYPE2, EXPAND(30)))
        lab1.pack(padx=EXPAND(20), pady=EXPAND(10))
        py_version = '.'.join(platform.python_version_tuple())
        et_version = '.'.join([str(v) for v in __version__])
        os_version = platform.system() + str(platform.release())
        lab2 = tk.Label(self.win, font=FONT,
                        text=f"EasyTurtleバージョン：{et_version}")
        lab2.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        lab3 = tk.Label(self.win, font=FONT,
                        text=f"Pythonバージョン：{py_version}")
        lab3.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        lab4 = tk.Label(self.win, font=FONT,
                        text=f"OSバージョン：{os_version}")
        lab4.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        self.win.resizable(0, 0)
        self.win.mainloop()

    def configure(self, event):
        """設定を編集"""
        self.all_redraw()
        GET_CONFIG()
        self.win = tk.Toplevel(self.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.icon)
        self.win.wait_visibility()
        self.win.grab_set()
        lab1 = tk.Label(self.win, text="Configure",
                        font=(FONT_TYPE2, EXPAND(30)))
        lab1.pack(padx=EXPAND(20), pady=EXPAND(10))
        self.var1 = tk.BooleanVar()
        self.var1.set(CONFIG["save_more_info"])
        text = "より多くの情報を保存する"
        chb1 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var1)
        chb1.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        self.var2 = tk.BooleanVar()
        self.var2.set(CONFIG["delete_cache"])
        text = "ファイルのキャッシュを削除する"
        chb2 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var2)
        chb2.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        self.var3 = tk.BooleanVar()
        self.var3.set(CONFIG["ask_save_new"])
        text = "古いファイルを変更するか確認する"
        chb3 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var3)
        chb3.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        self.var4 = tk.BooleanVar()
        self.var4.set(CONFIG["tolerate_danger"])
        text = "危険なプログラムを許容する"
        chb4 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var4)
        chb4.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        self.var5 = tk.BooleanVar()
        self.var5.set(CONFIG["expand_window"])
        text = "画面の大きさをを調整する"
        chb5 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var5)
        chb5.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        but1 = tk.Button(self.win, text="決定", width=20,
                         font=FONT, command=self.decide)
        but1.pack(padx=EXPAND(10), pady=(0, EXPAND(20)))
        self.win.resizable(0, 0)
        self.win.mainloop()

    def decide(self):
        """設定を決定"""
        global CONFIG
        CONFIG = {
            "save_more_info": self.var1.get(),
            "delete_cache": self.var2.get(),
            "ask_save_new": self.var3.get(),
            "tolerate_danger": self.var4.get(),
            "expand_window": self.var5.get()}
        with open(CONFIG_FILE, "w", encoding="UTF-8")as f:
            json.dump(CONFIG, f, indent=4)
        self.win.destroy()

    def closing(self):
        """終了時の定義"""
        data = [d.get_data(more=False) for d in self.widgets]
        if self.default_data == data:
            self.root.destroy()
            sys.exit()
        else:
            res = messagebox.askyesnocancel("確認", "保存しますか？")
            if res is None:
                return
            elif res is True:
                if self.saver() == 1:
                    return
        self.root.destroy()
        sys.exit()

    def all_redraw(self, back_up=True):
        """全部描き直し"""
        data = self.widgets
        if self.index < 0:
            self.index = 0
        elif (self.index > len(data) - SIZE) and (len(data) >= SIZE):
            self.index = len(data) - SIZE
        for d in data:
            d.redraw()
        self.scroll_set()
        self.check_length()
        if [d.get_data(more=False) for d in self.widgets] == self.default_data:
            self.root.title(f"EasyTurtle - {self.basename}")
        else:
            self.root.title(f"EasyTurtle - *{self.basename}*")
        if back_up is True:
            self.back_up()

    def back_up(self):
        """バックアップ"""
        data = self.get_data()
        if len(self.widgets) < 2:
            return
        elif len(self.backed_up) == 0:
            self.backed_up.append(data)
        elif self.backed_up[-1]["body"] != data["body"]:
            self.backed_up.append(data)

    def undo(self):
        """一回戻る"""
        data = self.get_data()
        if (len(self.backed_up) > 0) and \
           (self.backed_up[-1]["body"] != data["body"]):
            self.set_data(self.backed_up[-1])
            self.backed_up = self.backed_up[:-1]
        elif (len(self.backed_up) > 1) and \
             (self.backed_up[-2]["body"] != data["body"]):
            self.set_data(self.backed_up[-2])
            self.backed_up = self.backed_up[:-2]

    def get_data(self):
        """データを取得"""
        return {"index": self.index,
                "copy": self.copied_widgets,
                "body": [d.get_data() for d in self.widgets]}

    def set_data(self, data):
        """データをセット"""
        self.all_delete()
        self.index = data["index"]
        self.copied_widgets = data["copy"]
        self.data = []
        for d in data["body"]:
            self.make_match_class(d)
        self.index = data["index"]
        self.all_redraw()

    def check_length(self):
        """データの大きさをチェック"""
        if (len(self.widgets) > 999) and \
           (self.warning_ignore is False):
            messagebox.showwarning(
                "警告", "大量のデータを保持すると正常に動作しなくなる可能性があります。")
            self.warning_ignore = True

    def scroll_set(self):
        """スクロールバーの位置をセット"""
        data = self.widgets
        if len(data) <= SIZE:
            first = 0.0
            last = 1.0
        else:
            per = SIZE / len(data)
            first = (1.0 - per) * self.index / (len(data) - 8)
            last = first + per
        self.scr2.set(first, last)

    def listbox_selected(self, event):
        """リストボックス選択時の動作"""
        index = -1
        for i in self.lsb1.curselection():
            index = Texts.index(self.lsb1.get(i))
            break
        if index == -1:
            return
        Widgets[index](parent=self)
        self.all_redraw()

    def scroll1(self, event):
        """スクロール時の動作①"""
        data = self.widgets
        index = self.index - (event.delta // 120)
        max_size = (len(data) - SIZE)
        self.index = (0 if index <= 0 else max_size
                      if (index > max_size) and (len(data) > SIZE)
                      else self.index
                      if len(data) <= SIZE else index)
        self.all_redraw(back_up=False)

    def scroll2(self, *event):
        """スクロール時のデータ②"""
        data = self.widgets
        if event[0] == "scroll":
            index = self.index + int(event[1])
        elif event[0] == "moveto":
            index = int(float(event[1]) * len(data))
        else:
            return
        max_size = (len(data) - SIZE)
        self.index = (0 if index <= 0 else max_size
                      if (index > max_size) and (len(data) > SIZE)
                      else self.index
                      if len(data) <= SIZE else index)
        self.all_redraw(back_up=False)

    def scroll3(self, event):
        """スクロール時の動作③"""
        data = self.widgets
        index = self.index - (1 if event.num == 4 else -1)
        max_size = (len(data) - SIZE)
        self.index = (0 if index <= 0 else max_size
                      if (index > max_size) and (len(data) > SIZE)
                      else self.index
                      if len(data) <= SIZE else index)
        self.all_redraw(back_up=False)

    def kill_runner(self):
        """実行停止の動作"""
        self.killed_runner = True
        self.win.destroy()

    def runner(self):
        """実行"""
        self.all_redraw()
        self.variable_datas = {}
        self.runner_size = (600, 600)
        self.runner_speed = 3
        self.win = tk.Toplevel(self.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.icon)
        self.win.protocol("WM_DELETE_WINDOW", self.kill_runner)
        self.win.wait_visibility(self.win)
        if SYSTEM == "Windows":
            self.win.wm_attributes("-transparentcolor", "snow")
        self.killed_runner = False
        try:
            self.win.grab_set()
        except tk.TclError:
            messagebox.showerror("エラー", "\
すでに実行中のプログラムがないか確認してください。")
            self.win.destroy()
        canvas = tk.Canvas(self.win, width=0, height=0, bg="snow")
        canvas.pack()
        tur = turtle.RawTurtle(canvas)
        tur.shape("turtle")
        self.win.geometry(f"{self.runner_size[0]}x{self.runner_size[1]}")
        canvas.config(width=self.runner_size[0], height=self.runner_size[1])
        tur.penup()
        tur.speed(0)
        tur.goto(self.runner_size[0] // 2, self.runner_size[1] // -2)
        tur.pendown()
        tur.speed(self.runner_speed)
        try:
            for widget in self.widgets:
                if self.killed_runner is False:
                    widget.do(tur)
                else:
                    return
        except tk.TclError:
            self.kill_runner()
            return

    def all_delete(self):
        """全て削除"""
        widgets = [w for w in self.widgets]
        for d in widgets:
            d.delete(back_up=False)
        self.all_redraw()

    def saver(self, file=None):
        """保存動作"""
        self.all_redraw()
        if file is None:
            if self.program_name is not None:
                directory = os.path.dirname(self.program_name)
                name = self.basename
                file = filedialog.asksaveasfilename(
                    parent=self.root, initialdir=directory, initialfile=name,
                    filetypes=[("Jsonファイル", "*.json")])
            else:
                file = filedialog.asksaveasfilename(
                    parent=self.root, initialdir=DOCUMENTS,
                    filetypes=[("Jsonファイル", "*.json")])
        if file == "":
            return 1
        elif file[-5:] != ".json":
            file += ".json"
        body = [d.get_data(more=CONFIG["save_more_info"])
                for d in self.widgets]
        if CONFIG["save_more_info"] is True:
            data = {
                "version": __version__[:2],
                "copy": self.copied_widgets,
                "index": self.index,
                "body": body}
        else:
            data = {"version": __version__[:2], "body": body}
        with open(file, "w")as f:
            json.dump(data, f, indent=2)
        self.default_data = [d.get_data(more=False)
                             for d in self.widgets]
        self.program_name = file
        self.basename = os.path.basename(self.program_name)
        self.all_redraw()

    def opener(self, file=None):
        """開く動作"""
        data = [d.get_data(more=False) for d in self.widgets]
        if self.default_data != data:
            res = messagebox.askyesno("確認", "保存しますか？")
            if res is None:
                return
            elif res is True:
                if self.saver() == 1:
                    return
        now = datetime.now().__str__()
        deletes = ["-", " ", ".", ":"]
        for delete in deletes:
            now = now.replace(delete, "")
        if PROGRA is False:
            cache = os.path.join("./cache", now + ".json")
        else:
            cache = os.path.join(
                "C:/ProgramData/EasyTurtle/cache", now + ".json")
        if file is None:
            if self.program_name is not None:
                directory = os.path.dirname(self.program_name)
                name = self.basename
                file = filedialog.askopenfilename(
                    parent=self.root, initialdir=directory, initialfile=name,
                    filetypes=[("Jsonファイル", "*.json")])
            else:
                file = filedialog.askopenfilename(
                    parent=self.root, initialdir=DOCUMENTS,
                    filetypes=[("Jsonファイル", "*.json")])
        data = converter.converter(
            file, cache, ask=CONFIG["ask_save_new"])
        if data is None:
            return
        if CONFIG["delete_cache"] is True:
            os.remove(cache)
        self.all_delete()
        try:
            backed_cp = self.backed_up[-1] if len(self.backed_up) > 0 \
                else self.get_data()
            self.data = []
            self.warning_ignore = False
            for d in data["body"]:
                self.make_match_class(d)
            self.index = data["index"] if "index" in data else 0
            self.copied_widgets = data["copy"] if "copy" in data else []
            self.all_redraw()
            self.default_data = [d.get_data(more=False)
                                 for d in self.widgets]
            self.program_name = file
            self.basename = os.path.basename(self.program_name)
            self.backed_up = []
            self.all_redraw()
        except:
            self.set_data(backed_cp)
            messagebox.showerror("エラー", "変換エラーが発生しました。")
            traceback.print_exc()
            return

    def make_match_class(self, data, index=-1):
        """ウィジェットを作成"""
        name = data["_name"]
        if name in Names:
            Widgets[Names.index(name)](self, data, index)
        else:
            Undefined(self, {"_name": name, **data}, index)

    def paste(self):
        """ペースト時の動作"""
        for d in self.copied_widgets:
            self.make_match_class(d)
        self.all_redraw()

    def show_browser(self, event):
        """詳しい情報の表示"""
        webbrowser.open_new(README_FILE)

    def initialize(self):
        """データを初期化"""
        res = messagebox.askokcancel(
            "警告", "情報を初期化しますか？", parent=self.root)
        if res is True:
            self.all_delete()
            self.index = 0
            self.widgets = []
            self.copied_widgets = []
            self.default_data = []
            self.backed_up = []
            self.warning_ignore = False
            self.program_name = None
            self.basename = "untitled"
        self.all_redraw()
        self.default_data = [d.get_data(more=False)
                             for d in self.widgets]

    def get_selected(self):
        """選ばれたデータ一覧を取得"""
        selected = []
        for d in self.widgets:
            if d.bln1.get() is True:
                selected.append(d)
        return selected

    def all_select(self):
        """すべて選択"""
        for d in self.widgets:
            d.bln1.set(True)

    def clear_selected(self):
        """選択を解除"""
        for d in self.get_selected():
            d.bln1.set(False)

    def delete_selected(self):
        """選択されたデータを削除"""
        for d in self.get_selected():
            d.delete(back_up=False)
        self.all_redraw()

    def copy_selected(self):
        """選択されたデータをコピー"""
        copy = []
        for d in self.get_selected():
            data = d.get_data()
            data["_check"] = False
            copy.append(data)
        self.copied_widgets = copy

    def destroy(self):
        """ウィンドウを削除"""
        self.root.destroy()

    def setup(self):
        """セットアップ"""
        self.root = tk.Tk()
        self.root.title("EasyTurtle - untitled")
        self.root.geometry(f"{EXPAND(1240)}x{EXPAND(600)}")
        self.root.minsize(EXPAND(1240), EXPAND(600))
        self.root.protocol("WM_DELETE_WINDOW", self.closing)
        self.icon = tk.PhotoImage(file=ICON_FILE)
        self.root.tk.call('wm', 'iconphoto', self.root._w, self.icon)
        frame1 = tk.Frame(self.root)
        frame1.pack()
        frame2 = tk.Frame(frame1)
        frame2.pack(side=tk.LEFT, padx=(10, 0))
        frame2.bind("<MouseWheel>", self.scroll1)
        self.cv1 = tk.Canvas(frame2, width=EXPAND(
            WIDTH), height=EXPAND(HEIGHT*SIZE), bg="#E6E6E6")
        self.cv1.pack(side=tk.LEFT)
        self.cv1.bind("<MouseWheel>", self.scroll1)
        self.cv1.create_rectangle(EXPAND(4), EXPAND(4),
                                  EXPAND(WIDTH), EXPAND(HEIGHT*SIZE),
                                  width=EXPAND(2))
        self.scr2 = ttk.Scrollbar(frame2, orient=tk.VERTICAL,
                                  command=self.scroll2)
        self.scr2.pack(fill='y', side=tk.RIGHT)
        frame3 = tk.Frame(frame1)
        frame3.pack(side=tk.RIGHT, padx=EXPAND(10))
        lab0 = tk.Label(self.cv1, text="EasyTurtle",
                        fg="#D8D8D8", bg="#E6E6E6",
                        font=(FONT_TYPE2, EXPAND(56), "bold", "italic"))
        lab0.place(x=EXPAND(70), y=EXPAND(250))
        frame4 = tk.Frame(frame3)
        frame4.pack(fill="x", side=tk.BOTTOM, pady=0)
        lab1 = tk.Label(frame4, text='©2020 Ryo Fujinami.',
                        font=(FONT_TYPE2, EXPAND(10), "italic"))
        lab1.pack(side=tk.RIGHT, padx=EXPAND(20))
        joined_version = ".".join([str(n) for n in __version__])
        lab2 = tk.Label(frame4, text="v"+joined_version,
                        font=(FONT_TYPE1, EXPAND(12)))
        lab2.pack(side=tk.RIGHT, padx=EXPAND(10))
        lab3 = tk.Label(frame4, text="バージョン情報",
                        width=14, fg="blue", cursor="hand2",
                        font=(FONT_TYPE1, EXPAND(10), "underline"))
        lab3.bind("<Button-1>", self.version_info)
        lab3.pack(side=tk.LEFT, padx=EXPAND(10))
        lab4 = tk.Label(frame4, text="ユーザー設定",
                        width=14, fg="blue", cursor="hand2",
                        font=(FONT_TYPE1, EXPAND(10), "underline"))
        lab4.bind("<Button-1>", self.configure)
        lab4.pack(side=tk.LEFT, padx=EXPAND(10))
        lab5 = tk.Label(frame4, text="ヘルプ情報",
                        width=14, fg="blue", cursor="hand2",
                        font=(FONT_TYPE1, EXPAND(10), "underline"))
        lab5.bind("<Button-1>", self.show_browser)
        lab5.pack(side=tk.LEFT, padx=EXPAND(10))
        frame9 = tk.Frame(frame3)
        frame9.pack(side=tk.BOTTOM, pady=(0, EXPAND(10)))
        but1 = tk.Button(frame9, text="Run Program", bg="#F7DFDF",
                         font=(FONT_TYPE1, EXPAND(18)),
                         width=22, command=self.runner)
        but1.pack(side=tk.LEFT, padx=(0, EXPAND(18)))
        but2 = tk.Button(frame9, text="Initialize", bg="#DFEFF7",
                         font=(FONT_TYPE1, EXPAND(18)),
                         width=22, command=self.initialize)
        but2.pack(side=tk.RIGHT)
        frame8 = tk.Frame(frame3)
        frame8.pack(side=tk.BOTTOM, pady=(0, EXPAND(10)))
        but3 = tk.Button(frame8, text="Save Program",
                         width=22, font=(FONT_TYPE1, EXPAND(18)),
                         bg="#E7F7CF", command=self.saver)
        but3.pack(side=tk.LEFT, padx=(0, EXPAND(18)))
        but4 = tk.Button(frame8, text="Open Program",
                         width=22, font=(FONT_TYPE1, EXPAND(18)),
                         bg="#E7F7CF", command=self.opener)
        but4.pack(side=tk.RIGHT)
        frame4 = tk.Frame(frame3)
        frame4.pack(side=tk.BOTTOM, pady=(0, EXPAND(10)))
        but5 = tk.Button(frame4, text="Copy Selected",
                         width=22, font=(FONT_TYPE1, EXPAND(18)),
                         bg="#DFEFF7", command=self.copy_selected)
        but5.pack(side=tk.LEFT, padx=(0, EXPAND(18)))
        but0 = tk.Button(frame4, text="Paste Widgets",
                         width=22, font=(FONT_TYPE1, EXPAND(18)),
                         bg="#DFEFF7", command=self.paste)
        but0.pack(side=tk.RIGHT)
        frame5 = tk.Frame(frame3)
        frame5.pack(side=tk.BOTTOM, pady=(0, EXPAND(10)))
        but9 = tk.Button(frame5, text="Undo",
                         width=22, font=(FONT_TYPE1, EXPAND(18)),
                         bg="#E7F7CF", command=self.undo)
        but9.pack(side=tk.LEFT, padx=(0, EXPAND(18)))
        but6 = tk.Button(frame5, text="All Select",
                         width=22, font=(FONT_TYPE1, EXPAND(18)),
                         bg="#E7F7CF", command=self.all_select)
        but6.pack(side=tk.RIGHT)
        frame6 = tk.Frame(frame3)
        frame6.pack(side=tk.BOTTOM, pady=(0, EXPAND(10)))
        but7 = tk.Button(frame6, text="Clear Selected",
                         width=22, font=(FONT_TYPE1, EXPAND(18)),
                         bg="#DFEFF7", command=self.clear_selected)
        but7.pack(side=tk.LEFT, padx=(0, EXPAND(18)))
        but8 = tk.Button(frame6, text="Delete Selected",
                         width=22, font=(FONT_TYPE1, EXPAND(18)),
                         bg="#F7DFDF", command=self.delete_selected)
        but8.pack(side=tk.RIGHT)
        frame7 = tk.Frame(frame3)
        frame7.pack(side=tk.TOP, pady=(0, EXPAND(10)))
        var1 = tk.StringVar(self.root, value=Texts)
        height = 8 if SYSTEM == "Windows" else 10
        self.lsb1 = tk.Listbox(frame7, listvariable=var1, height=height,
                               width=37, selectmode='single',
                               bg="#FFEFD7", font=(FONT_TYPE1, EXPAND(22)),
                               selectbackground="#2F4FAF",
                               selectforeground="#FFFFFF")
        self.lsb1.bind('<<ListboxSelect>>', self.listbox_selected)
        self.lsb1.pack(fill='y', side=tk.LEFT)
        scr1 = ttk.Scrollbar(frame7, orient=tk.VERTICAL,
                             command=self.lsb1.yview)
        self.lsb1['yscrollcommand'] = scr1.set
        scr1.pack(fill='y', side=tk.RIGHT)
        self.all_redraw()


class Widget:
    def __init__(self, parent, data=None, index=-1):
        """初期化"""
        self.pressed_x = self.pressed_y = 0
        self.item_id = -1
        self.p = parent

        if self.TYPE == "undefined":
            self.background = "#E7C7F7"
        elif self.TYPE == "default":
            self.background = "#F7F787"
        elif self.TYPE == "variable":
            self.background = "#F7C7A7"
        elif self.TYPE == "normal":
            self.background = "#B7E7F7"
        elif self.TYPE == "comment":
            self.background = "#F7A7A7"
        tops = len(self.p.widgets)
        self.p.index = 0 if tops < SIZE else tops
        if index == -1:
            self.p.widgets.append(self)
        else:
            self.p.widgets.insert(index, self)
        self.set_data(data)
        self.draw()

    def __str__(self):
        """文字列定義"""
        return str(self.get_data())

    def __repr__(self):
        """コンストラクタの文字列定義"""
        data = self.get_data()
        return f"{data['_name']}(self, data={data})"

    def binder(self, widget):
        """ボタンのバインド"""
        widget.bind('<Button-3>', self.show_popup2)
        widget.bind("<B1-Motion>", self.dragged)
        if SYSTEM == "Windows":
            widget.bind("<MouseWheel>", self.p.scroll1)
        elif SYSTEM == "Linux":
            widget.bind("<Button-4>", self.p.scroll3)
            widget.bind("<Button-5>", self.p.scroll3)

    def draw_cv(self):
        """キャンバスを描く"""
        self.cv = tk.Canvas(self.p.cv1, width=EXPAND(WIDTH),
                            height=EXPAND(HEIGHT), bg=self.background)
        self.binder(self.cv)
        self.cv.create_rectangle(EXPAND(42), EXPAND(4),
                                 EXPAND(WIDTH), EXPAND(HEIGHT//2+2),
                                 width=EXPAND(2))
        self.cv.create_rectangle(EXPAND(42), EXPAND(HEIGHT//2+2),
                                 EXPAND(WIDTH), EXPAND(HEIGHT),
                                 width=EXPAND(2))
        self.cv.create_rectangle(EXPAND(4), EXPAND(4),
                                 EXPAND(42), EXPAND(HEIGHT), width=EXPAND(2))
        self.lab4 = tk.Label(self.cv, font=FONT, bg=self.background,
                             text=f"{self.p.widgets.index(self)+1:03}")
        self.binder(self.lab4)
        self.bln1 = tk.BooleanVar()
        self.bln1.set(self.check)
        lab1 = tk.Label(self.cv, text=self.TEXT, font=FONT, bg=self.background)
        self.binder(lab1)
        lab1.place(x=EXPAND(50), y=EXPAND(10))
        self.lab4.place(x=EXPAND(5), y=EXPAND(HEIGHT//4))
        chk1 = tk.Checkbutton(self.cv, variable=self.bln1, cursor="hand2",
                              bg=self.background, font=("", EXPAND(10)))
        chk1.place(x=EXPAND(12), y=EXPAND(HEIGHT//2))
        self.binder(chk1)

    def dragged(self, event):
        """ドラッグ時の動作"""
        index = self.p.widgets.index(self) - self.p.index
        if (index < 0) or (index > SIZE):
            return
        elif (index == 0) and (-0.125 * EXPAND(HEIGHT) > event.y):
            self.up()
        elif -0.5 * EXPAND(HEIGHT) > event.y:
            self.up()
        elif (index == SIZE) and (1.125 * EXPAND(HEIGHT) < event.y):
            self.down()
        elif 1.5 * EXPAND(HEIGHT) < event.y:
            self.down()

    def paste1(self):
        """上へのペースト"""
        index = self.p.widgets.index(self)
        for d in reversed(self.p.copied_widgets):
            self.p.make_match_class(d, index=index)
        self.p.all_redraw()

    def paste2(self):
        """下へのペースト"""
        index = self.p.widgets.index(self)
        for d in reversed(self.p.copied_widgets):
            self.p.make_match_class(d, index=index+1)
        self.p.all_redraw()

    def show_popup2(self, event):
        index = self.p.widgets.index(self)
        menu = tk.Menu(self.p.root, tearoff=False)
        states = ["active" for i in range(7)]
        if index <= 0:
            states[0] = states[2] = "disabled"
        if index >= len(self.p.widgets) - 1:
            states[1] = states[3] = "disabled"
        if len(self.p.copied_widgets) == 0:
            states[6] = "disabled"
        menu.add_command(label=' Top', command=self.top, state=states[0])
        menu.add_command(label=' Bottom', command=self.bottom, state=states[1])
        menu.add_command(label=' Up', command=self.up, state=states[2])
        menu.add_command(label=' Down', command=self.down, state=states[3])
        menu.add_separator()
        menu.add_command(label=' Copy', command=self.copy, state=states[4])
        menu.add_command(label=' Delete', command=self.delete, state=states[5])
        if self.OPTION is True:
            menu.add_separator()
            menu.add_command(label=' Option', command=self.option)
        menu.add_separator()
        menu.add_command(label='⇧Paste⇧', command=self.paste1, state=states[6])
        menu.add_command(label='⇩Paste⇩', command=self.paste2, state=states[6])
        menu.post(event.x_root, event.y_root)

    def delete(self, back_up=True):
        """ウィジェットの削除"""
        self.cv.place_forget()
        self.p.widgets.remove(self)
        self.p.all_redraw(back_up)

    def place_cv(self):
        """キャンバスを置く"""
        index = self.p.widgets.index(self) - self.p.index
        if 0 <= index < SIZE:
            self.cv.place(x=0, y=EXPAND(HEIGHT*index))
            self.lab4.configure(
                text=f"{self.p.widgets.index(self)+1:03}")
        else:
            self.cv.place_forget()

    def redraw(self):
        """ウィジェットを描き直す"""
        self.save_data()
        if hasattr(self, "cv") is False:
            self.draw()
        self.place_cv()

    def copy(self):
        """ウィジェットをコピーする"""
        data = self.get_data()
        data["_check"] = False
        self.p.copied_widgets = [data]

    def top(self):
        """ウィジェットを一番上に移動"""
        self.p.widgets.remove(self)
        self.p.widgets.insert(0, self)
        self.p.index = 0
        self.p.all_redraw()

    def bottom(self):
        """ウィジェットを一番下に移動"""
        self.p.widgets.remove(self)
        self.p.widgets.append(self)
        bottom = len(self.p.widgets)
        self.p.index = bottom if bottom > SIZE else 0
        self.p.all_redraw()

    def up(self):
        """ウィジェットを一個上に移動"""
        index = self.p.widgets.index(self)
        if index == 0:
            return
        upper = self.p.widgets[index - 1]
        self.p.widgets[index - 1] = self
        self.p.widgets[index] = upper
        if index == self.p.index:
            self.p.index -= 1
        self.p.all_redraw()

    def down(self):
        """ウィジェットを一個下に移動"""
        index = self.p.widgets.index(self)
        if index + 1 >= len(self.p.widgets):
            return
        under = self.p.widgets[index + 1]
        self.p.widgets[index + 1] = self
        self.p.widgets[index] = under
        if index == self.p.index + SIZE - 1:
            self.p.index += 1
        self.p.all_redraw()

    def set_check(self, data):
        """チェックが有るか確認する"""
        if data is None:
            self.check = False
        else:
            if "_check" in data:
                self.check = data["_check"]
            else:
                self.check = False

    def get_class_data(self, data, more):
        """クラスのデータを追加する"""
        if more is True:
            data["_check"] = self.bln1.get()
        return {"_name": self.__class__.__name__, **data}

    def copy_entry(self, entry):
        """テキストをコピーする"""
        if entry.selection_present() is True:
            text = entry.selection_get()
        else:
            text = entry.get()
        self.p.root.clipboard_clear()
        self.p.root.clipboard_append(text)

    def paste_entry(self, entry):
        """テキストを表示する"""
        text = self.p.root.clipboard_get()
        entry.insert("insert", text)

    def show_popup1(self, event, entry):
        """ポップアップを表示する"""
        try:
            if self.p.root.clipboard_get() != "":
                paste = "active"
            else:
                paste = "disabled"
        except tk.TclError:
            paste = "disabled"
        menu = tk.Menu(self.cv, tearoff=False)
        menu.add_command(
            label='Copy', command=lambda: self.copy_entry(entry))
        menu.add_command(label='Paste', state=paste,
                         command=lambda: self.paste_entry(entry))
        menu.post(event.x_root, event.y_root)

    def stos(self, string):
        """変数を埋め込み"""
        for var in re.findall(r'\[\w*\]', string):
            name = var[1:-1] if len(var) > 2 else ""
            if name not in self.p.variable_datas:
                messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"は定義されていません。')
                return ""
            elif (self.p.variable_datas[name][1] == "S") or \
                 (self.p.config["tolerate_danger"] is True):
                string = string.replace(
                    var, str(self.p.variable_datas[name][0]))
            else:
                messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"はNumber型です。')
                return ""
        return string

    def var_converter(self, string):
        """変数を埋め込み"""
        for var in re.findall(r'\[\w*\]', string):
            name = var[1:-1] if len(var) > 2 else ""
            if name not in self.p.variable_datas:
                messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"は定義されていません。')
                return 0
            elif (self.p.variable_datas[name][1] == "N") or \
                 (self.p.config["tolerate_danger"] is True):
                string = string.replace(
                    var, str(self.p.variable_datas[name][0]))
            else:
                messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"はString型です。')
                return 0
        return string

    def calculator(self, string):
        """数列の計算"""
        string = self.var_converter(string)
        if string == "":
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
値が入力されていません。')
            return 0
        operators = ["**", "*", "//", "/", "%", "+", "-", "(", ")"]
        formulas = [string]
        for ope in operators:
            new = []
            for form in formulas:
                if form not in operators:
                    for n in form.split(ope):
                        new.append(n)
                        new.append(ope)
                    new = new[:-1]
                else:
                    new.append(form)
                formulas = new
        while "" in formulas:
            formulas.remove("")
        string = ""
        for form in formulas:
            if form in operators:
                string += form
            else:
                string += str(float(form))
        return float(eval(string))

    def stof(self, string):
        """文字列を小数に変換"""
        try:
            return self.calculator(string)
        except:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{string}"を数値に変換できませんでした。')
            traceback.print_exc()
            return 0

    def stoi(self, string):
        """文字列を整数に変換"""
        return int(self.stof(string))


class Title(Widget):
    TEXT = "Title         画面タイトルをｔにする"
    OPTION = False
    TYPE = "default"
    VALUES = {"title": "Turtle"}

    def set_data(self, data):
        if data is None:
            self.title = self.VALUES["title"]
        else:
            if "title" in data:
                self.title = data["title"]
            else:
                self.title = self.VALUES["title"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"title": self.title}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="t = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.title)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.title = self.ent1.get()

    def do(self, tur):
        self.save_data()
        self.p.win.title(self.stos(self.title))


class Geometry(Widget):
    TEXT = "Geometry      画面サイズをｗ×ｈにする"
    OPTION = False
    TYPE = "default"
    VALUES = {"width": "600", "height": "600"}

    def set_data(self, data):
        if data is None:
            self.width = self.VALUES["width"]
            self.height = self.VALUES["height"]
        else:
            if "width" in data:
                self.width = data["width"]
            else:
                self.width = self.VALUES["width"]
            if "height" in data:
                self.height = data["height"]
            else:
                self.height = self.VALUES["height"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({
            "width": self.width,
            "height": self.height}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="w = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.width)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text=", h = ", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.height)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(280), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.width = self.ent1.get()
        self.height = self.ent2.get()

    def do(self, tur):
        self.save_data()
        width = self.stoi(self.width)
        height = self.stoi(self.height)
        self.p.win.geometry(f"{width}x{height}")
        tur.getscreen().getcanvas().config(
            width=width, height=height)
        tur.penup()
        tur.speed(0)
        tur.goto(width // 2, height // -2)
        tur.pendown()
        tur.speed(self.p.runner_speed)
        self.runner_size = (width, height)


class Forward(Widget):
    TEXT = "Forward       前方向にｄ移動する"
    OPTION = False
    TYPE = "normal"
    VALUES = {"distance": "0"}

    def set_data(self, data):
        if data is None:
            self.distance = self.VALUES["distance"]
        else:
            if "distance" in data:
                self.distance = data["distance"]
            else:
                self.distance = self.VALUES["distance"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"distance": self.distance}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="d = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.distance)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.distance = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.forward(self.stoi(self.distance))


class Backward(Widget):
    TEXT = "Backward      後方向にｄ移動する"
    OPTION = False
    TYPE = "normal"
    VALUES = {"distance": "0"}

    def set_data(self, data):
        if data is None:
            self.distance = self.VALUES["distance"]
        else:
            if "distance" in data:
                self.distance = data["distance"]
            else:
                self.distance = self.VALUES["distance"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"distance": self.distance}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="d = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.distance)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.distance = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.backward(self.stoi(self.distance))


class Right(Widget):
    TEXT = "Right         右方向にａ度曲げる"
    OPTION = False
    TYPE = "normal"
    VALUES = {"angle": "0"}

    def set_data(self, data):
        if data is None:
            self.angle = self.VALUES["angle"]
        else:
            if "angle" in data:
                self.angle = data["angle"]
            else:
                self.angle = self.VALUES["angle"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="a = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.angle = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.right(self.stoi(self.angle))


class Left(Widget):
    TEXT = "Left          左方向にａ度曲げる"
    OPTION = False
    TYPE = "normal"
    VALUES = {"angle": "0"}

    def set_data(self, data):
        if data is None:
            self.angle = self.VALUES["angle"]
        else:
            if "angle" in data:
                self.angle = data["angle"]
            else:
                self.angle = self.VALUES["angle"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="a = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.angle = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.left(self.stoi(self.angle))


class GoTo(Widget):
    TEXT = "GoTo          座標ｘ，ｙに移動する"
    OPTION = False
    TYPE = "normal"
    VALUES = {"x": "0", "y": "0"}

    def set_data(self, data):
        if data is None:
            self.x = self.VALUES["x"]
            self.y = self.VALUES["y"]
        else:
            if "x" in data:
                self.x = data["x"]
            else:
                self.x = self.VALUES["x"]
            if "y" in data:
                self.y = data["y"]
            else:
                self.y = self.VALUES["y"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"x": self.x, "y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="x = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text=", y = ", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.y)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(280), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.x = self.ent1.get()
        self.y = self.ent2.get()

    def do(self, tur):
        self.save_data()
        tur.goto(
            self.stoi(self.x) + self.p.runner_size[0] // 2,
            self.stoi(self.y) - self.p.runner_size[1] // 2)


class SetX(Widget):
    TEXT = "SetX          座標ｘに移動する"
    OPTION = False
    TYPE = "normal"
    VALUES = {"x": "0"}

    def set_data(self, data):
        if data is None:
            self.x = self.VALUES["x"]
        else:
            if "x" in data:
                self.x = data["x"]
            else:
                self.x = self.VALUES["x"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"x": self.x}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="a = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.x = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.setx(self.stoi(self.x) + self.p.runner_size[0] // 2)


class SetY(Widget):
    TEXT = "SetY          座標ｙに移動する"
    OPTION = False
    TYPE = "normal"
    VALUES = {"y": "0"}

    def set_data(self, data):
        if data is None:
            self.y = self.VALUES["y"]
        else:
            if "y" in data:
                self.y = data["y"]
            else:
                self.y = self.VALUES["y"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="y = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.y)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.y = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.sety(self.stoi(self.y) - self.p.runner_size[1] // 2)


class SetHeading(Widget):
    TEXT = "SetHeading    角度をａ度に変更する"
    OPTION = False
    TYPE = "normal"
    VALUES = {"angle": "0"}

    def set_data(self, data):
        if data is None:
            self.angle = self.VALUES["angle"]
        else:
            if "angle" in data:
                self.angle = data["angle"]
            else:
                self.angle = self.VALUES["angle"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="a = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.angle = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.setheading(self.stoi(self.angle))


class Home(Widget):
    TEXT = "Home          初期座標・角度に戻る"
    OPTION = False
    TYPE = "normal"

    def set_data(self, data):
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        pass

    def do(self, tur):
        self.save_data()
        tur.goto(self.p.runner_size[0] // 2, self.p.runner_size[1] // -2)


class Circle(Widget):
    TEXT = "Circle        半径ｒの円をｅ度描く"
    OPTION = False
    TYPE = "normal"
    VALUES = {"radius": "0", "extent": "360"}

    def set_data(self, data):
        if data is None:
            self.radius = self.VALUES["radius"]
            self.extent = self.VALUES["extent"]
        else:
            if "radius" in data:
                self.radius = data["radius"]
            else:
                self.radius = self.VALUES["radius"]
            if "extent" in data:
                self.extent = data["extent"]
            else:
                self.extent = self.VALUES["extent"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({
            "radius": self.radius,
            "extent": self.extent}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="r = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.radius)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text=", e = ", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.extent)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(280), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.radius = self.ent1.get()
        self.extent = self.ent2.get()

    def do(self, tur):
        self.save_data()
        tur.circle(
            self.stoi(self.radius),
            self.stoi(self.extent))


class Dot(Widget):
    TEXT = "Dot           直径ｒの円を描く"
    OPTION = False
    TYPE = "normal"
    VALUES = {"size": "0"}

    def set_data(self, data):
        if data is None:
            self.size = self.VALUES["size"]
        else:
            if "size" in data:
                self.size = data["size"]
            else:
                self.size = self.VALUES["size"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"size": self.size}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="r = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.size)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.size = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.dot(self.stoi(self.size))


class Stamp(Widget):
    TEXT = "Stamp         亀のスタンプを押す"
    OPTION = False
    TYPE = "normal"

    def set_data(self, data):
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        pass

    def do(self, tur):
        self.save_data()
        tur.stamp()


class Speed(Widget):
    TEXT = "Speed         速度ｓに変更する"
    OPTION = False
    TYPE = "normal"
    VALUES = {"speed": "3"}

    def set_data(self, data):
        if data is None:
            self.speed = self.VALUES["speed"]
        else:
            if "speed" in data:
                self.speed = data["speed"]
            else:
                self.speed = self.VALUES["speed"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"speed": self.speed}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="s = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.speed)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.speed = self.ent1.get()

    def do(self, tur):
        self.save_data()
        self.p.runner_speed = self.stoi(self.speed)
        tur.speed(self.p.runner_speed)


class PenDown(Widget):
    TEXT = "PenDown       動いた線を引く"
    OPTION = False
    TYPE = "normal"

    def set_data(self, data):
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        pass

    def do(self, tur):
        self.save_data()
        tur.pendown()


class PenUp(Widget):
    TEXT = "PenUp         動いた線を引かない"
    OPTION = False
    TYPE = "normal"

    def set_data(self, data):
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        pass

    def do(self, tur):
        self.save_data()
        tur.penup()


class PenSize(Widget):
    TEXT = "PenSize       先の太さをｗにする"
    OPTION = False
    TYPE = "normal"
    VALUES = {"width": "1"}

    def set_data(self, data):
        if data is None:
            self.width = self.VALUES["width"]
        else:
            if "width" in data:
                self.width = data["width"]
            else:
                self.width = self.VALUES["width"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"width": self.width}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="w = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.width)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.width = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.pensize(self.stoi(self.width))


class Color(Widget):
    TEXT = "Color         色をｃに変更する"
    OPTION = True
    TYPE = "normal"
    VALUES = {"color": "black"}

    def set_data(self, data):
        if data is None:
            self.color = self.VALUES["color"]
        else:
            if "color" in data:
                self.color = data["color"]
            else:
                self.color = self.VALUES["color"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="c = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.color)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def option(self):
        color = self.ent1.get()
        try:
            color = colorchooser.askcolor(
                color=self.stos(color), parent=self.p.root)
        except tk.TclError:
            color = colorchooser.askcolor(parent=self.p.root)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())

    def save_data(self):
        self.color = self.ent1.get()
        if self.color == "":
            self.color = "black"
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, self.color)

    def do(self, tur):
        self.save_data()
        try:
            tur.color(self.stos(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした。', parent=self.p.root)


class BGColor(Widget):
    TEXT = "BGColor       背景色をｃに変更する"
    OPTION = True
    TYPE = "normal"
    VALUES = {"color": "white"}

    def set_data(self, data):
        if data is None:
            self.color = self.VALUES["color"]
        else:
            if "color" in data:
                self.color = data["color"]
            else:
                self.color = self.VALUES["color"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="c = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.color)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def option(self):
        color = self.ent1.get()
        try:
            color = colorchooser.askcolor(
                color=self.stos(color), parent=self.p.root)
        except tk.TclError:
            color = colorchooser.askcolor(parent=self.p.root)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())

    def save_data(self):
        self.color = self.ent1.get()
        if self.color == "":
            self.color = "black"
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, self.color)

    def do(self, tur):
        self.save_data()
        try:
            tur.getscreen().bgcolor(self.stos(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした。', parent=self.p.root)


class BeginFill(Widget):
    TEXT = "BeginFill     塗りつぶしを始める"
    OPTION = False
    TYPE = "normal"

    def set_data(self, data):
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        pass

    def do(self, tur):
        self.save_data()
        tur.begin_fill()


class EndFill(Widget):
    TEXT = "EndFill       塗りつぶしを終える"
    OPTION = False
    TYPE = "normal"

    def set_data(self, data):
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        pass

    def do(self, tur):
        self.save_data()
        tur.end_fill()


class ShowTurtle(Widget):
    TEXT = "ShowTurtle    亀を表示にする"
    OPTION = False
    TYPE = "normal"

    def set_data(self, data):
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        pass

    def do(self, tur):
        self.save_data()
        tur.showturtle()


class HideTurtle(Widget):
    TEXT = "HideTurtle    亀を非表示にする"
    OPTION = False
    TYPE = "normal"

    def set_data(self, data):
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        pass

    def do(self, tur):
        self.save_data()
        tur.hideturtle()


class TurtleSize(Widget):
    TEXT = "TurtleSize    亀の大きさをｓにする"
    OPTION = False
    TYPE = "normal"
    VALUES = {"size": "1"}

    def set_data(self, data):
        if data is None:
            self.size = self.VALUES["size"]
        else:
            if "size" in data:
                self.size = data["size"]
            else:
                self.size = self.VALUES["size"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"size": self.size}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="s = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.size)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.size = self.ent1.get()

    def do(self, tur):
        self.save_data()
        tur.turtlesize(self.stoi(self.size))


class Write(Widget):
    TEXT = "Write         サイズｓの文字列ｔを書く"
    OPTION = True
    TYPE = "normal"
    VALUES = {
        "text": "Sample",
        "size": "20",
        "move": "0",
        "align": "center",
        "family": "Default",
        "weight": "bold",
        "slant": "roman"}

    def set_data(self, data):
        if data is None:
            self.text = self.VALUES["text"]
            self.size = self.VALUES["size"]
            self.move = self.VALUES["move"]
            self.align = self.VALUES["align"]
            self.family = self.VALUES["family"]
            self.weight = self.VALUES["weight"]
            self.slant = self.VALUES["slant"]
        else:
            if "text" in data:
                self.text = data["text"]
            else:
                self.text = self.VALUES["text"]
            if "size" in data:
                self.size = data["size"]
            else:
                self.size = self.VALUES["size"]
            if "move" in data:
                self.move = data["move"]
            else:
                self.move = self.VALUES["move"]
            if "align" in data:
                self.align = data["align"]
            else:
                self.align = self.VALUES["align"]
            if "family" in data:
                self.family = data["family"]
            else:
                self.family = self.VALUES["family"]
            if "weight" in data:
                self.weight = data["weight"]
            else:
                self.weight = self.VALUES["weight"]
            if "slant" in data:
                self.slant = data["slant"]
            else:
                self.slant = self.VALUES["slant"]
        self.set_check(data)

    def get_data(self, more=True):
        data = {"text": self.text, "size": self.size}
        if (str(self.move) != self.VALUES["move"]) or (more is True):
            data["move"] = self.move
        if (str(self.align) != self.VALUES["align"]) or (more is True):
            data["align"] = self.align
        if (str(self.family) != self.VALUES["family"]) or (more is True):
            data["family"] = self.family
        if (str(self.weight) != self.VALUES["weight"]) or (more is True):
            data["weight"] = self.weight
        if (str(self.slant) != self.VALUES["slant"]) or (more is True):
            data["slant"] = self.slant
        self.redraw()
        return self.get_class_data(data, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="t = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.text)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text=", s = ", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.size)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(280), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def option(self):
        self.text = self.ent1.get()
        self.size = self.ent2.get()
        self.win = tk.Toplevel(self.p.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.p.icon)
        self.win.geometry(f"{EXPAND(340)}x{EXPAND(380)}")
        self.win.resizable(0, 0)
        self.win.wait_visibility()
        self.win.grab_set()
        font = (FONT_TYPE1, EXPAND(16), "bold")
        lab0 = tk.Label(self.win, text="Options",
                        font=("", EXPAND(30), "bold"))
        lab0.place(x=EXPAND(80), y=EXPAND(20))
        lab1 = tk.Label(self.win, text="text   = ", font=font)
        lab1.place(x=EXPAND(30), y=EXPAND(90))
        ent1 = tk.Entry(self.win, font=font, width=12, justify=tk.RIGHT)
        ent1.insert(tk.END, self.text)
        ent1.bind('<Button-3>', lambda e: self.show_popup1(e, ent1))
        ent1.place(x=EXPAND(150), y=EXPAND(90))
        lab2 = tk.Label(self.win, text="move   = ", font=font)
        lab2.place(x=EXPAND(30), y=EXPAND(120))
        ent2 = tk.Entry(self.win, font=font, width=12, justify=tk.RIGHT)
        ent2.insert(tk.END, self.move)
        ent2.bind('<Button-3>', lambda e: self.show_popup1(e, ent1))
        ent2.place(x=EXPAND(150), y=EXPAND(120))
        lab3 = tk.Label(self.win, text="align  = ", font=font)
        lab3.place(x=EXPAND(30), y=EXPAND(150))
        ent3 = tk.Entry(self.win, font=font, width=12, justify=tk.RIGHT)
        ent3.insert(tk.END, self.align)
        ent3.bind('<Button-3>', lambda e: self.show_popup1(e, ent1))
        ent3.place(x=EXPAND(150), y=EXPAND(150))
        lab4 = tk.Label(self.win, text="family = ", font=font)
        lab4.place(x=EXPAND(30), y=EXPAND(180))
        ent4 = tk.Entry(self.win, font=font, width=12, justify=tk.RIGHT)
        ent4.insert(tk.END, self.family)
        ent4.bind('<Button-3>', lambda e: self.show_popup1(e, ent1))
        ent4.place(x=EXPAND(150), y=EXPAND(180))
        lab5 = tk.Label(self.win, text="size   = ", font=font)
        lab5.place(x=EXPAND(30), y=EXPAND(210))
        ent5 = tk.Entry(self.win, font=font, width=12, justify=tk.RIGHT)
        ent5.insert(tk.END, self.size)
        ent5.bind('<Button-3>', lambda e: self.show_popup1(e, ent1))
        ent5.place(x=EXPAND(150), y=EXPAND(210))
        lab6 = tk.Label(self.win, text="weight = ", font=font)
        lab6.place(x=EXPAND(30), y=EXPAND(240))
        ent6 = tk.Entry(self.win, font=font, width=12, justify=tk.RIGHT)
        ent6.insert(tk.END, self.weight)
        ent6.bind('<Button-3>', lambda e: self.show_popup1(e, ent1))
        ent6.place(x=EXPAND(150), y=EXPAND(240))
        lab7 = tk.Label(self.win, text="slant  = ", font=font)
        lab7.place(x=EXPAND(30), y=EXPAND(270))
        ent7 = tk.Entry(self.win, font=font, width=12, justify=tk.RIGHT)
        ent7.insert(tk.END, self.slant)
        ent7.bind('<Button-3>', lambda e: self.show_popup1(e, ent1))
        ent7.place(x=EXPAND(150), y=EXPAND(270))
        entries = (ent1, ent2, ent3, ent4, ent5, ent6, ent7)
        but1 = tk.Button(self.win, text="決定", font=font, width=8,
                         command=lambda: self.decide(entries))
        but1.place(x=100, y=310)
        self.win.mainloop()

    def decide(self, entries):
        self.text = entries[0].get()
        self.move = entries[1].get()
        self.align = entries[2].get()
        self.family = entries[3].get()
        self.size = entries[4].get()
        self.weight = entries[5].get()
        self.slant = entries[6].get()
        self.ent1.delete(0, tk.END)
        self.ent1.insert(0, self.text)
        self.ent2.delete(0, tk.END)
        self.ent2.insert(0, self.size)
        self.win.destroy()
        self.redraw()

    def save_data(self):
        self.text = self.ent1.get()
        self.size = self.ent2.get()

    def do(self, tur):
        self.save_data()
        tur.write(
            self.stos(self.text),
            move=bool(self.stoi(self.move)),
            align=self.stos(self.align),
            font=(
                self.stos(self.family),
                self.stoi(self.size),
                self.stos(self.weight),
                self.stos(self.slant)))


class Sleep(Widget):
    TEXT = "Sleep         操作をｄ秒停止する"
    OPTION = False
    TYPE = "normal"
    VALUES = {"second": "0"}

    def set_data(self, data):
        if data is None:
            self.second = self.VALUES["second"]
        else:
            if "second" in data:
                self.second = data["second"]
            else:
                self.second = self.VALUES["second"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"second": self.second}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="d = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.second)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.second = self.ent1.get()

    def do(self, tur):
        self.save_data()
        time.sleep(self.stof(self.second))


class Comment(Widget):
    TEXT = "Comment       実行されないコメント文"
    OPTION = False
    TYPE = "comment"
    VALUES = {"comment": "Comment"}

    def set_data(self, data):
        if data is None:
            self.comment = self.VALUES["comment"]
        else:
            if "comment" in data:
                self.comment = data["comment"]
            else:
                self.comment = self.VALUES["comment"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({"comment": self.comment}, more)

    def draw(self):
        self.draw_cv()
        self.ent1 = tk.Entry(self.cv, font=(FONT_TYPE1, EXPAND(16), "bold"),
                             fg="#B40404", width=27, justify=tk.LEFT)
        self.ent1.insert(tk.END, self.comment)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(48), y=EXPAND(HEIGHT//2+7))
        self.redraw()

    def save_data(self):
        self.comment = self.ent1.get()

    def do(self, tur):
        pass


class Undefined(Widget):
    TEXT = "Undefined     情報のない不明なクラス"
    OPTION = False
    TYPE = "undefined"

    def set_data(self, data):
        if data is None:
            pass
        else:
            self.data = data
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data(self.data, more)

    def draw(self):
        self.draw_cv()
        text = 'このバージョンでは編集できません'
        lab2 = tk.Label(self.cv, text=text, font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        pass

    def do(self, tur):
        pass


class VarNumber(Widget):
    TEXT = "VarNumber     変数ｎを数値ｖにする"
    OPTION = False
    TYPE = "variable"
    VALUES = {"name": "num", "value": "0"}

    def set_data(self, data):
        if data is None:
            self.name = self.VALUES["name"]
            self.value = self.VALUES["value"]
        else:
            if "name" in data:
                self.name = data["name"]
            else:
                self.name = self.VALUES["name"]
            if "value" in data:
                self.value = data["value"]
            else:
                self.value = self.VALUES["value"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({
            "name": self.name,
            "value": self.value}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="n = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.name)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text=", v = ", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.value)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(280), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.name = self.ent1.get()
        self.value = self.ent2.get()

    def do(self, tur):
        self.save_data()
        self.p.variable_datas[self.name] = (self.stof(self.value), "N")


class VarString(Widget):
    TEXT = "VarString     変数ｎを文字列ｖにする"
    OPTION = False
    TYPE = "variable"
    VALUES = {"name": "str", "value": "text"}

    def set_data(self, data):
        if data is None:
            self.name = self.VALUES["name"]
            self.value = self.VALUES["value"]
        else:
            if "name" in data:
                self.name = data["name"]
            else:
                self.name = self.VALUES["name"]
            if "value" in data:
                self.value = data["value"]
            else:
                self.value = self.VALUES["value"]
        self.set_check(data)

    def get_data(self, more=True):
        self.redraw()
        return self.get_class_data({
            "name": self.name,
            "value": self.value}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="n = ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.name)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(90), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text=", v = ", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.value)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(280), y=EXPAND(HEIGHT//2+8))
        self.redraw()

    def save_data(self):
        self.name = self.ent1.get()
        self.value = self.ent2.get()

    def do(self, tur):
        self.save_data()
        self.p.variable_datas[self.name] = (self.stos(self.value), "S")


Widgets = (
    VarNumber, VarString, Title, Geometry,
    Forward, Backward, Right, Left, GoTo,
    SetX, SetY, SetHeading, Home, Circle,
    Dot, Stamp, Speed, PenDown, PenUp, PenSize,
    Color, BGColor, BeginFill, EndFill,
    ShowTurtle, HideTurtle, TurtleSize,
    Write, Sleep, Comment)
Texts = tuple([c.TEXT for c in Widgets])
Names = tuple([c.__name__ for c in Widgets])


if __name__ == "__main__":
    file = sys.argv[1] if len(sys.argv) > 1 else None
    et = EasyTurtle(file=file)
