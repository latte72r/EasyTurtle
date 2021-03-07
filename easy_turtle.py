
# ©2020-2021 Ryo Fujinami.

import json
import os
import platform
import pprint
import re
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import traceback
import turtle
import urllib.request
import webbrowser
from tkinter import colorchooser, filedialog
from tkinter import font as tkfont
from tkinter import messagebox, scrolledtext, simpledialog, ttk
from typing import List as typeList
from typing import TypeVar

SIZE = 8
HEIGHT = 72
WIDTH = 520


def UPDATE_CONFIG():
    """設定を取得"""
    global CONFIG
    if os.path.exists(CONFIG_FILE) is True:
        with open(CONFIG_FILE, "r", encoding="UTF-8")as f:
            data = json.load(f)
        config = {}
        for key, value in DEFAULT_CONFIG.items():
            if key in data:
                config[key] = data[key]
            else:
                config[key] = value
    else:
        config = DEFAULT_CONFIG
    with open(CONFIG_FILE, "w", encoding="UTF-8")as f:
        json.dump(config, f, indent=4)
    CONFIG = config


SYSTEM = platform.system()
# システムがWindowsの場合
if SYSTEM == "Windows":
    from ctypes import windll

    FONT_TYPE1 = "Courier New"
    FONT_TYPE2 = "Times New Roman"

    os.chdir(os.path.dirname(sys.argv[0]))

    ICON_FILE = os.path.abspath("./Files/win_icon.gif")
    README_FILE = os.path.abspath("./Files/index.html")

    if sys.argv[0].split(".")[-1] == "exe":
        PROGRA = True
    else:
        PROGRA = False

    if PROGRA is False:
        CONFIG_FILE = os.path.abspath("./config.json")
    else:
        CONFIG_FILE = "C:/ProgramData/EasyTurtle/config.json"
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

    DEFAULT_CONFIG = {
        "save_more_info": False,
        "show_warning": True,
        "expand_window": True,
        "ask_save_new": True,
        "user_document": True,
        "auto_update": True,
        "open_last_file": False}

    CONFIG = DEFAULT_CONFIG
    UPDATE_CONFIG()

    if CONFIG["user_document"] is True:
        user = os.environ['USERPROFILE']
        if os.path.exists(os.path.join(user, "onedrive/ドキュメント/")) is True:
            DOCUMENTS = os.path.join(user, "onedrive/ドキュメント/EasyTurtle/")
        else:
            DOCUMENTS = os.path.join(user, "Documents/EasyTurtle/")
        samples = os.path.join(DOCUMENTS, "Samples")
        os.makedirs(DOCUMENTS, exist_ok=True)
        try:
            if os.path.exists(samples) is False:
                shutil.copytree('./Samples', samples)
        except FileExistsError:
            pass
    else:
        DOCUMENTS = os.path.abspath("./")
        os.makedirs(DOCUMENTS, exist_ok=True)

    SYSTEM_WIDTH = windll.user32.GetSystemMetrics(0)
    SYSTEM_HEIGHT = windll.user32.GetSystemMetrics(1)

    if CONFIG["expand_window"] is True:
        width_mag = SYSTEM_WIDTH / 1280
        height_mag = SYSTEM_HEIGHT / 720
        WIN_MAG = width_mag if width_mag < height_mag else height_mag
    else:
        WIN_MAG = 1

# システムがLinuxの場合
elif SYSTEM == "Linux":

    FONT_TYPE1 = "FreeMono"
    FONT_TYPE2 = "FreeSerif"

    os.chdir(os.getcwd())

    ICON_FILE = os.path.abspath("./Files/win_icon.gif")
    README_FILE = os.path.abspath("./Files/index.html")

    PROGRA = False

    CONFIG_FILE = os.path.abspath("./config.json")

    DEFAULT_CONFIG = {
        "save_more_info": False,
        "show_warning": True,
        "expand_window": True,
        "ask_save_new": True,
        "user_document": False,
        "auto_update": True,
        "open_last_file": False}

    CONFIG = DEFAULT_CONFIG
    UPDATE_CONFIG()

    if CONFIG["user_document"] is True:
        user = os.environ['USER']
        if os.path.exists(os.path.join("/home/", user, "/ドキュメント/")) is True:
            DOCUMENTS = os.path.join("/home/", user, "/ドキュメント/EasyTurtle/")
        else:
            DOCUMENTS = os.path.join("/home/", user, "/Documents/EasyTurtle/")
        os.makedirs(DOCUMENTS, exist_ok=True)
        samples = os.path.join(DOCUMENTS, "Samples")
        try:
            if os.path.exists(samples) is False:
                shutil.copytree('./Samples', samples)
        except FileExistsError:
            pass
    else:
        DOCUMENTS = os.path.abspath("./")
        os.makedirs(DOCUMENTS, exist_ok=True)

    response = subprocess.check_output("xrandr | fgrep '*'", shell=True)
    metrics = response.decode("utf8").split()[0].split("x")
    SYSTEM_WIDTH = int(metrics[0])
    SYSTEM_HEIGHT = int(metrics[1])

    if CONFIG["expand_window"] is True:
        width_mag = SYSTEM_WIDTH / 1280
        height_mag = SYSTEM_HEIGHT / 720
        WIN_MAG = width_mag if width_mag < height_mag else height_mag
    else:
        WIN_MAG = 1

# システムが対応OS以外の場合
else:
    messagebox.showerror("エラー", f"{SYSTEM}には対応していません。")


def EXPAND(num):
    """画面を拡大"""
    return int(round(num * WIN_MAG))


FONT = (FONT_TYPE1, EXPAND(12), "bold")

__version__ = (5, 9, "0a1")


class EasyTurtle:
    def __init__(self, file=None):
        """初期化"""
        # 変数を初期化する
        self.index = 0
        self.last_shown: typeList[typeWidget] = []
        self.widgets: typeList[typeWidget] = []
        self.copied_widgets: typeList[typeWidget] = []
        self.default_data: typeList[typeWidget] = []
        self.backed_up = []
        self.canceled_changes = []
        self.warning_ignore = False
        self.running_program = False
        self.program_name = None
        self.basename = "無題"

        # 画面を設定する
        self.setup()

        # アップデート確認をする
        if CONFIG["auto_update"] is True:
            thread = threading.Thread(target=self.update_starting)
            thread.start()

        # ファイルが指定されていれば開く
        if file is not None:
            self.open_program(file)

        elif CONFIG["open_last_file"] is True:
            if PROGRA is True:
                file = "C:/ProgramData/EasyTurtle/config/boot.json"
                os.makedirs("C:/ProgramData/EasyTurtle/cache/", exist_ok=True)
            else:
                file = os.path.abspath("./cache/boot.json")
            if os.path.exists(file):
                self.open_program(file)

        self.root.mainloop()

    def __repr__(self):
        """コンストラクタの文字列定義"""
        data = self.get_data()
        return f"EasyTurtle(self, data={data})"

    def version_info(self, event=None):
        """設定を編集"""
        self.win = tk.Toplevel(self.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.icon)
        self.win.title("バージョン情報 - EasyTurtle")
        self.win.wait_visibility()
        self.win.grab_set()
        lab1 = tk.Label(self.win, text="Version",
                        font=(FONT_TYPE2, EXPAND(30)))
        lab1.pack(padx=EXPAND(20), pady=EXPAND(10))
        py_version = '.'.join(platform.python_version_tuple())
        et_version = '.'.join([str(v) for v in __version__])
        os_version = platform.system() + str(platform.release())
        tcl_version = tk.Tcl().eval('info patchlevel')
        lab2 = tk.Label(self.win, font=FONT,
                        text=f"EasyTurtleバージョン\t：{et_version}")
        lab2.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        lab3 = tk.Label(self.win, font=FONT,
                        text=f"Pythonバージョン\t\t：{py_version}")
        lab3.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        lab4 = tk.Label(self.win, font=FONT,
                        text=f"OSバージョン\t\t：{os_version}")
        lab4.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        lab5 = tk.Label(self.win, font=FONT,
                        text=f"Tclバージョン\t\t：{tcl_version}")
        lab5.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        font = (FONT_TYPE1, EXPAND(12), "bold", "underline")
        lab6 = tk.Label(self.win, font=font, fg="blue", cursor="hand2",
                        text="アップデートの確認")
        lab6.bind("<Button-1>", self.check_update)
        lab6.pack(side=tk.RIGHT, anchor=tk.NW,
                  padx=EXPAND(20), pady=(0, EXPAND(10)))
        self.win.resizable(0, 0)

    def edit_config(self, event=None):
        """設定を編集"""
        UPDATE_CONFIG()
        self.win = tk.Toplevel(self.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.icon)
        self.win.title("設定 - EasyTurtle")
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
        self.var2.set(CONFIG["ask_save_new"])
        text = "古いファイルを変更するか確認する"
        chb2 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var2)
        chb2.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        self.var3 = tk.BooleanVar()
        self.var3.set(CONFIG["show_warning"])
        text = "警告と追加情報を表示する"
        chb3 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var3)
        chb3.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        self.var4 = tk.BooleanVar()
        self.var4.set(CONFIG["expand_window"])
        text = "画面の大きさをを調整する"
        chb4 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var4)
        chb4.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        self.var5 = tk.BooleanVar()
        self.var5.set(CONFIG["user_document"])
        text = "ユーザードキュメントを使用する"
        chb5 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var5)
        chb5.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        self.var6 = tk.BooleanVar()
        self.var6.set(CONFIG["auto_update"])
        text = "起動時にアップデートを確認する"
        chb6 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var6)
        chb6.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        self.var7 = tk.BooleanVar()
        self.var7.set(CONFIG["open_last_file"])
        text = "前回開いていたファイルを開く"
        chb7 = tk.Checkbutton(self.win, text=text,
                              font=FONT, variable=self.var7)
        chb7.pack(padx=EXPAND(10), pady=(0, EXPAND(10)), anchor=tk.NW)
        but1 = tk.Button(self.win, text="決定", width=20,
                         font=FONT, command=self.decide_config)
        but1.pack(padx=EXPAND(10), pady=(0, EXPAND(20)))
        lab1 = tk.Label(self.win, text="\
※画面サイズなどの一部の変更は　\n\
　次回起動時より有効になります。",
                        font=(FONT_TYPE1, EXPAND(10), "bold"), fg="red")
        lab1.pack(padx=EXPAND(20), pady=(0, EXPAND(10)))
        self.win.resizable(0, 0)

    def decide_config(self):
        """設定を決定"""
        global CONFIG
        CONFIG = {
            "save_more_info":   self.var1.get(),
            "ask_save_new":     self.var2.get(),
            "show_warning":     self.var3.get(),
            "expand_window":    self.var4.get(),
            "user_document":    self.var5.get(),
            "auto_update":      self.var6.get(),
            "open_last_file":   self.var7.get()}
        with open(CONFIG_FILE, "w", encoding="UTF-8")as f:
            json.dump(CONFIG, f, indent=4)
        self.win.destroy()

    def close_window(self, event=None):
        """終了時の定義"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return

        # 保存するか確認する
        data = [d.get_data(more=False) for d in self.widgets]
        if self.default_data != data:
            res = messagebox.askyesnocancel("確認", "保存しますか？")
            if res is None:
                return
            elif res is True:
                if self.save_program() == 1:
                    return

        # ファイルを保存
        if CONFIG["open_last_file"] is True:
            # ファイルを決定
            if PROGRA is True:
                file = "C:/ProgramData/EasyTurtle/config/boot.json"
                os.makedirs("C:/ProgramData/EasyTurtle/cache/", exist_ok=True)
            else:
                file = os.path.abspath("./cache/boot.json")

            # データを保存
            self.save_file(file, boot=True)

        # 画面を閉じる
        self.root.destroy()
        sys.exit()

    def redraw_widgets(self, change=True):
        """全部描き直し"""
        UPDATE_CONFIG()
        data = self.widgets

        if (self.index < 0) or (len(data) < SIZE):
            self.index = 0
        elif self.index > len(data) - SIZE:
            self.index = len(data) - SIZE

        shown = data[self.index: self.index + SIZE]
        for d in self.last_shown:
            d.place_cv()
        for d in shown:
            d.place_cv()
        self.last_shown = shown
        self.set_scrollbar_posision()
        if change is True:
            self.check_length()
            self.set_title()
            self.back_up()

    def set_title(self):
        """タイトルを設定する"""
        if [d.get_data(more=False) for d in self.widgets] == self.default_data:
            self.root.title(f"{self.basename} - EasyTurtle")
        else:
            self.root.title(f"*{self.basename}* - EasyTurtle")

    def back_up(self):
        """バックアップ"""
        # データを取得
        data = self.get_data()

        # バックアップがなければ追加
        if len(self.backed_up) == 0:
            self.backed_up.append(data)

        # 前回と違ければ追加
        elif self.backed_up[-1]["body"] != data["body"]:
            self.backed_up.append(data)

    def undo_change(self, event=None):
        """一回戻る"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return

        # データを取得
        self.back_up()
        data = self.get_data()

        # バックアップがあり、変更されているとき
        if (len(self.backed_up) > 0) and \
           (self.backed_up[-1]["body"] != data["body"]):
            self.canceled_changes.append(data)
            self.set_data(self.backed_up[-1])
            self.backed_up = self.backed_up[:-1]

        # バックアップが２つ以上あり、変更されているとき
        elif (len(self.backed_up) > 1) and \
             (self.backed_up[-2]["body"] != data["body"]):
            self.canceled_changes.append(data)
            self.set_data(self.backed_up[-2])
            self.backed_up = self.backed_up[:-2]

        # それ以外ならエラー音
        else:
            self.root.bell()
            return 1

        self.redraw_widgets()

    def redo_change(self, event=None):
        """やり直し"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return

        # データを取得
        self.back_up()
        data = self.get_data()

        # キャンセルがあり、変更されているとき
        if (len(self.canceled_changes) > 0) and \
           (self.canceled_changes[-1]["body"] != data["body"]):
            self.set_data(self.canceled_changes[-1])
            self.canceled_changes = self.canceled_changes[:-1]
        # それ以外ならエラー音
        else:
            self.root.bell()
            return 1

        self.redraw_widgets()

    def get_data(self):
        """データを取得"""
        return {"index": self.index,
                "copy": self.copied_widgets,
                "body": [d.get_data() for d in self.widgets]}

    def set_data(self, data):
        """データをセット"""
        self.delete_all_widgets()
        self.index = data["index"]
        self.copied_widgets = data["copy"]
        self.widgets = []
        for d in data["body"]:
            self.make_match_class(d)
        self.index = data["index"]

    def check_length(self):
        """データの大きさをチェック"""
        if (len(self.widgets) > 999) and \
           (CONFIG["show_warning"] is True) and \
           (self.warning_ignore is False):
            messagebox.showwarning(
                "警告", "大量のデータを保持すると正常に動作しなくなる可能性があります。")
            self.warning_ignore = True

    def set_scrollbar_posision(self):
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

    def append_new_widget(self, event):
        """リストボックス選択時の動作"""
        before_index = self.index

        mode = self.var2.get()
        if mode == 1:
            index = 0
        elif mode == 2:
            index = len(self.widgets)
        elif mode == 3:
            index = self.get_add_index()
            if index is None:
                return 1

        class_index = -1
        for i in self.lsb1.curselection():
            class_index = Texts.index(self.lsb1.get(i))
            break
        if class_index == -1:
            return 1
        Widgets[class_index](parent=self, index=index)

        if (index < before_index) or (index > before_index + SIZE - 1):
            self.index = index
        else:
            self.index = before_index

        if ((mode == 1) or (mode == 3)) and (self.var3.get() is True):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, str(index + 2))
            self.var2.set(3)

        self.redraw_widgets()

    def scroll_on_windows(self, event):
        """Windowsでのスクロール時の動作"""
        data = self.widgets
        index = self.index - (event.delta // 120)
        max_size = (len(data) - SIZE)
        self.index = (0 if index <= 0 else max_size
                      if (index > max_size) and (len(data) > SIZE)
                      else self.index
                      if len(data) <= SIZE else index)
        self.redraw_widgets(change=False)

    def scroll_on_linux(self, event):
        """Linuxでのスクロール時の動作"""
        data = self.widgets
        index = self.index - (1 if event.num == 4 else -1)
        max_size = (len(data) - SIZE)
        self.index = (0 if index <= 0 else max_size
                      if (index > max_size) and (len(data) > SIZE)
                      else self.index
                      if len(data) <= SIZE else index)
        self.redraw_widgets(change=False)

    def scroll_button_clicked(self, *event):
        """スクロールバーボタンが押された時の動作"""
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
        self.redraw_widgets(change=False)

    def kill_runner(self, event=None):
        """実行停止の動作"""
        self.killed_runner = True
        self.running_program = False
        if hasattr(self, "win") is True:
            self.win.destroy()

    def run_standard_mode(self, event=None):
        """標準実行"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        self.run_program(fastest=False)

    def run_fastest_mode(self, event=None):
        """高速実行"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        self.run_program(fastest=True)

    def run_program(self, fastest=False):
        """実行"""
        # 変数の格納場所
        self.variable_datas = {}

        # プログラムの情報
        self.runner_size = (600, 600)
        self.killed_runner = False
        self.runner_pendown = True
        self.running_program = True
        if fastest is True:
            self.runner_speed = 0
            self.running_fastest = True
        else:
            self.runner_speed = 3
            self.running_fastest = False

        # ウインドウを作成
        self.win = tk.Toplevel(self.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.icon)
        self.win.protocol("WM_DELETE_WINDOW", self.kill_runner)
        self.win.wait_visibility(self.win)
        self.win.grab_set()
        self.win.focus_set()
        self.win.title("EasyTurtle")

        # キーをバインド
        self.win.bind("<Control-Key-q>", self.kill_runner)

        # Windowsでは透過を有効にする
        if SYSTEM == "Windows":
            self.win.wm_attributes("-transparentcolor", "snow")

        # キャンバスを作成
        canvas = tk.Canvas(self.win, width=0, height=0, bg="snow")
        canvas.pack()
        tur = turtle.RawTurtle(canvas)
        tur.shape("turtle")
        tur.getscreen().colormode(255)
        self.win.geometry(f"{self.runner_size[0]}x{self.runner_size[1]}")
        canvas.config(width=self.runner_size[0], height=self.runner_size[1])
        tur.penup()
        tur.speed(0)
        tur.goto(self.runner_size[0] // 2, self.runner_size[1] // -2)
        tur.pendown()
        tur.speed(self.runner_speed)
        if fastest is True:
            tur.getscreen().delay(0)

        # それぞれのウィジェットを実行
        try:
            for index, widget in enumerate(self.widgets):
                if self.killed_runner is False:
                    if widget.enabled is True:
                        widget.run(tur)
                else:
                    return 0
        except Exception:
            if self.killed_runner is True:
                return 0
            else:
                self.kill_runner()
                traceback.print_exc()
                messagebox.showerror("エラー", f'\
line: {index+1}, {widget.__class__.__name__}\n\
エラーが発生しました。\n\n{traceback.format_exc()}')
                return 1

    def delete_all_widgets(self, event=None):
        """全て削除"""
        widgets = [w for w in self.widgets]
        for d in widgets:
            d.delete(back_up=False)
        self.redraw_widgets(change=False)

    def save_program(self, file=None):
        """上書き保存"""
        # キーバインドから実行された場合
        if type(file) == tk.Event:
            file = None
        elif (type(file) == tk.Event) and (self.running_program is True):
            return

        # ファイル名を質問する
        if file is None:
            if self.program_name is not None:
                file = self.program_name
            else:
                file = filedialog.asksaveasfilename(
                    parent=self.root, initialdir=DOCUMENTS,
                    filetypes=[("Jsonファイル", "*.json")])

        # ファイルが選択されていなければ終了
        if file == "":
            return 1

        # 拡張子をつける
        elif file[-5:] != ".json":
            file += ".json"

        # 保存する
        self.save_file(file)

    def save_program_as(self, file=None):
        """名前を付けて保存"""
        # キーバインドから実行された場合
        if type(file) == tk.Event:
            file = None
        elif (type(file) == tk.Event) and (self.running_program is True):
            return

        # ファイル名を質問する
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

        # ファイルが選択されていなければ終了
        if file == "":
            return 1

        # 拡張子をつける
        elif file[-5:] != ".json":
            file += ".json"

        # 保存する
        self.save_file(file)

    def save_file(self, file, boot=None):
        """ファイルを保存する"""
        # データを取得
        body = [d.get_data(more=(boot or CONFIG["save_more_info"]))
                for d in self.widgets]

        # データを決定
        if boot is True:
            data = {
                "version": __version__[:2],
                "copy": self.copied_widgets,
                "index": self.index,
                "backedup": self.backed_up,
                "canceled": self.canceled_changes,
                "addmode": self.var2.get(),
                "adjust": self.var3.get(),
                "position": self.ent1.get(),
                "name": self.program_name,
                "default": self.default_data,
                "body": body}
        elif CONFIG["save_more_info"] is True:
            data = {
                "version": __version__[:2],
                "copy": self.copied_widgets,
                "index": self.index,
                "backedup": self.backed_up,
                "canceled": self.canceled_changes,
                "addmode": self.var2.get(),
                "adjust": self.var3.get(),
                "position": self.ent1.get(),
                "body": body}
        else:
            data = {"version": __version__[:2], "body": body}

        # フォルダを作成
        os.makedirs(os.path.dirname(file), exist_ok=True)

        # データを書き込み
        with open(file, "w")as f:
            json.dump(data, f, indent=2)

        if boot is not True:
            # プログラムの名称設定
            self.program_name = file
            self.basename = os.path.basename(self.program_name)

            # 基本データを設定
            self.default_data = [d.get_data(more=False) for d in self.widgets]

        self.set_title()

    def open_program(self, file=None):
        """開く動作"""
        # キーバインドから実行された場合
        if type(file) == tk.Event:
            file = None
        elif (type(file) == tk.Event) and (self.running_program is True):
            return

        # データが変更されていれば保存するか確認する
        data = [d.get_data(more=False) for d in self.widgets]
        if self.default_data != data:
            res = messagebox.askyesnocancel("確認", "保存しますか？")
            if res is None:
                return
            elif res is True:
                if self.save_program() == 1:
                    return

        # ファイル名を質問する
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

        # ファイルが選択されていなければ終了
        if file == "":
            return 1

        # ファイルを開く
        with open(file, "r")as f:
            data = json.load(f)

        # すべてのウィジェットを削除
        self.delete_all_widgets()
        try:
            # データを複製
            if len(self.backed_up) > 0:
                backed_cp = self.backed_up[-1]
            else:
                backed_cp = self.get_data()

            # データを空にする
            self.data = []

            # サイズ警告を初期化
            self.warning_ignore = False

            # ウィジェットを作成
            version = tuple(data["version"])
            for d in data["body"]:
                self.make_match_class(d, version=version)

            # インデックスを変更
            self.index = data["index"] if "index" in data else 0

            # コピーされたウィジェットを設定
            self.copied_widgets = data["copy"] if "copy" in data else []

            # バックアップデータを設定
            self.backed_up = data["backedup"] if "backedup" in data else []
            self.canceled_changes = data["canceled"]\
                if "canceled" in data else []

            # 追加位置を設定
            addmode = data["addmode"] if "addmode" in data else 2
            adjust = data["adjust"] if "adjust" in data else True
            position = data["position"] if "position" in data else ""
            self.var2.set(addmode)
            self.var3.set(adjust)
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, position)

            self.redraw_widgets()

            # データを上書き
            if (CONFIG["ask_save_new"] is True) and (version < (4, 11)):
                res = messagebox.askyesno("確認", "\
選択されたファイルは古いバージョンです。\n\
このバージョン用に保存し直しますか？")
                if res is True:
                    self.save_file(file)

            # 基本データを設定
            if "default" in data:
                self.default_data = data["default"]
            else:
                self.default_data = [d.get_data(
                    more=False) for d in self.widgets]

            # プログラムの名称設定
            if "name" in data:
                self.program_name = data["name"]
            else:
                self.program_name = file
            if self.program_name is None:
                self.basename = "無題"
            else:
                self.basename = os.path.basename(self.program_name)

            self.set_title()

        except Exception:
            # コピーを復元
            self.set_data(backed_cp)

            # エラー表示
            messagebox.showerror("エラー", "変換エラーが発生しました。")
            traceback.print_exc()
            return 1

    def make_match_class(self, data, index=-1, version=tuple(__version__[:2])):
        """ウィジェットを作成"""
        name = data["_name"]
        if name in Names:
            Widgets[Names.index(name)](self, data, index)
        elif (name == "Geometry") and (version < (5, 0)):
            ScreenSize(self, data, index)
        else:
            Undefined(self, {"_name": name, **data}, index)

    def paste_widgets(self, event=None):
        """ペースト時の動作"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return

        before_index = self.index

        mode = self.var2.get()
        if mode == 1:
            index = 0
        elif mode == 2:
            index = len(self.widgets)
        elif mode == 3:
            index = self.get_add_index()
            if index is None:
                return 1
        next_index = index

        for d in reversed(self.copied_widgets):
            self.make_match_class(d, index=index)
            next_index += 1

        if (index < before_index) or (index > before_index + SIZE - 1):
            self.index = index
        else:
            self.index = before_index

        if ((mode == 1) or (mode == 3)) and (self.var3.get() is True):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, str(next_index + 1))
            self.var2.set(3)

        self.redraw_widgets()

    def get_selected(self):
        """選ばれたデータ一覧を取得"""
        selected = []
        for d in self.widgets:
            if d.bln1.get() is True:
                selected.append(d)
        return selected

    def select_all(self, event=None):
        """すべて選択"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        for d in self.widgets:
            d.bln1.set(True)
        self.back_up()

    def clear_selected(self, event=None):
        """選択を解除"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        for d in self.get_selected():
            d.bln1.set(False)
        self.back_up()

    def delete_selected(self, event=None):
        """選択されたデータを削除"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        for d in self.get_selected():
            d.delete(back_up=False)
        self.redraw_widgets()

    def copy_selected(self, event=None):
        """選択されたデータをコピー"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        copy = []
        if len(self.get_selected()) == 0:
            return
        for d in self.get_selected():
            data = d.get_data()
            data["_check"] = False
            copy.append(data)
        self.copied_widgets = copy

    def cut_selected(self, event=None):
        """選択されたデータをカット"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        self.copy_selected()
        self.delete_selected()

    def enable_selected(self, event=None):
        """選択されたデータを有効化"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        if len(self.get_selected()) == 0:
            return
        for d in self.get_selected():
            d.enable(back_up=False)
        self.back_up()

    def disable_selected(self, event=None):
        """選択されたデータを無効化"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        if len(self.get_selected()) == 0:
            return
        for d in self.get_selected():
            d.disable(back_up=False)
        self.back_up()

    def destroy(self):
        """ウィンドウを削除"""
        self.root.destroy()

    def delete_menu(self, event=None):
        "メニューを消す"
        if hasattr(self, "menu") is True:
            self.menu.destroy()

    def get_new_release(self):
        "更新を取得"
        url = "http://github.com/RyoFuji2005/EasyTurtle/releases/latest"
        try:
            with urllib.request.urlopen(url)as f:
                text = f.geturl()
        except (urllib.error.URLError, AttributeError):
            return "ConnectionError"
        try:
            data = text.split("/")
            data = data[-1].replace("v", "")
            data = data.split(".")
            data = tuple([int(d) for d in data])
        except (AttributeError, ValueError):
            return "OtherError"
        return data

    def show_online_document(self, event=None):
        """詳しい情報の表示"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        webbrowser.open_new("https://ryofuji2005.github.io/EasyTurtle/")

    def show_offline_document(self, event=None):
        """詳しい情報の表示"""
        if (type(event) == tk.Event) and (self.running_program is True):
            return
        webbrowser.open_new(README_FILE)

    def show_release_page(self, event=None):
        """リリースページの表示"""
        url = "http://github.com/RyoFuji2005/EasyTurtle/releases/latest"
        webbrowser.open_new(url)

    def show_github_page(self, event=None):
        """GitHubページの表示"""
        url = "http://github.com/RyoFuji2005/EasyTurtle/"
        webbrowser.open_new(url)

    def update_starting(self):
        "開始時に確認"
        new_version = self.get_new_release()

        try:
            if type(new_version) == str:
                return 1
            elif new_version <= __version__:
                return 0
            elif sys.argv[0][-14:] == "EasyTurtle.exe":
                self.ask_update_msi(new_version, start=True)
            else:
                self.ask_update_page(new_version, start=True)
        except TypeError:
            pass

    def check_update(self, event=None):
        "アップデートを確認"
        new_version = self.get_new_release()
        old_joined_version = '.'.join([str(n) for n in __version__])

        try:
            if new_version == "ConnectionError":
                messagebox.showerror("エラー", "\
エラーが発生しました。\n\
ネットワーク接続を確認してください。")
            elif new_version == "OtherError":
                messagebox.showerror("\
エラーが発生しました。\n\
しばらくしてからもう一度お試しください。")
            elif new_version <= __version__:
                messagebox.showinfo("アップデート", f"\
バージョン：{old_joined_version}\n\
お使いのバージョンは最新です。")
            elif sys.argv[0][-14:] == "EasyTurtle.exe":
                self.ask_update_msi(new_version)
            else:
                self.ask_update_page(new_version)
        except TypeError:
            messagebox.showerror("エラー", "\
正規リリースでないため確認できません。")

    def ask_update_msi(self, new_version, start=False):
        """自動アップデートするか尋ねる"""
        new_joined_version = '.'.join([str(n) for n in new_version])
        old_joined_version = '.'.join([str(n) for n in __version__])

        if start is True:
            self.win2 = tk.Toplevel(self.root)
        else:
            self.win2 = tk.Toplevel(self.win)

        self.win2.tk.call('wm', 'iconphoto', self.win2, self.icon)
        self.win2.title("アップデート - EasyTurtle")
        self.win2.grab_set()
        lab1 = tk.Label(self.win2, font=FONT,
                        text="新しいバージョンが見つかりました")
        lab1.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        lab2 = tk.Label(self.win2, font=FONT,
                        text=f"お使いのバージョン：{old_joined_version}")
        lab2.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        lab3 = tk.Label(self.win2, font=FONT,
                        text=f"最新のバージョン　：{new_joined_version}")
        lab3.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        font = (FONT_TYPE1, EXPAND(12), "bold", "underline")
        lab5 = tk.Label(self.win2, font=font, fg="blue", cursor="hand2",
                        text="今すぐアップデートする")
        lab5.bind("<Button-1>", lambda e: self.auto_update_msi(new_version))
        lab5.pack(anchor=tk.N, pady=(0, EXPAND(10)))
        self.win2.resizable(0, 0)

    def auto_update_msi(self, new_version):
        """MSI自動アップデート"""
        joined_version = '.'.join([str(n) for n in new_version])

        url = f"\
https://github.com/RyoFuji2005/EasyTurtle/releases/\
download/v{joined_version}/EasyTurtle-{joined_version}-amd64.msi"
        file_name = os.path.join(os.environ['USERPROFILE'], "downloads",
                                 f"EasyTurtle-{joined_version}-amd64.msi")
        try:
            urllib.request.urlretrieve(url, file_name)
        except AttributeError:
            messagebox.showerror("\
エラーが発生しました。\n\
しばらくしてからもう一度お試しください。")
            traceback.print_exc()

        subprocess.Popen(["cmd", "/c", file_name])

        self.close_window()

    def ask_update_page(self, new_version, start=False):
        """アップデートページを表示するか尋ねる"""
        new_joined_version = '.'.join([str(n) for n in new_version])
        old_joined_version = '.'.join([str(n) for n in __version__])

        if start is True:
            self.win2 = tk.Toplevel(self.root)
        else:
            self.win2 = tk.Toplevel(self.win)

        self.win2.tk.call('wm', 'iconphoto', self.win2, self.icon)
        self.win2.title("アップデート - EasyTurtle")
        self.win2.grab_set()
        lab1 = tk.Label(self.win2, font=FONT,
                        text="新しいバージョンが見つかりました")
        lab1.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        lab2 = tk.Label(self.win2, font=FONT,
                        text=f"お使いのバージョン：{old_joined_version}")
        lab2.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        lab3 = tk.Label(self.win2, font=FONT,
                        text=f"最新のバージョン　：{new_joined_version}")
        lab3.pack(anchor=tk.NW, padx=EXPAND(20), pady=(0, EXPAND(10)))
        font = (FONT_TYPE1, EXPAND(12), "bold", "underline")
        lab5 = tk.Label(self.win2, font=font, fg="blue", cursor="hand2",
                        text="今すぐ確認する")
        lab5.bind("<Button-1>", self.show_release_page)
        lab5.pack(anchor=tk.N, pady=(0, EXPAND(10)))
        self.win2.resizable(0, 0)

    def convert_rgb(self, color):
        """RGB値に変換する"""
        if type(color) == str:
            return color
        else:
            rgb = "#"
            red = hex(int(color[0]))[2:]
            rgb += red if len(red) == 2 else "0" + red
            green = hex(int(color[1]))[2:]
            rgb += green if len(green) == 2 else "0" + green
            blue = hex(int(color[2]))[2:]
            rgb += blue if len(blue) == 2 else "0" + blue
            return rgb.upper()

    def get_add_index(self):
        """追加先の取得"""
        text = self.ent1.get()
        if text == "":
            messagebox.showerror("エラー", '位置が指定されていません。')
            return None
        try:
            index = int(text)
        except ValueError:
            messagebox.showerror("エラー", '位置は半角数字のみで指定してください。')
            return None
        if index > len(self.widgets) + 1:
            messagebox.showwarning("警告", '\
位置が最大値を超えています。\n自動で最後に追加します。')
            return len(self.widgets)
        elif index < 1:
            messagebox.showerror("エラー", '位置は正の数で入力してください。')
            return None
        else:
            return index - 1

    def goto_line(self, event=None):
        """行に移動"""
        text = simpledialog.askstring("行へ移動", '\
数値を入力してください。\n\
"-1"でプログラムの最後に移動します。')
        if text == "":
            return 0
        try:
            line = int(text)
        except ValueError:
            messagebox.showerror("エラー", '数値で入力してください。')
            return 1
        if line == -1:
            self.index = len(self.widgets) - SIZE
        elif line > len(self.widgets):
            messagebox.showwarning("警告", '\
位置が最大値を超えています。\n\
自動で最後に移動します。')
            self.index = len(self.widgets) - SIZE
        elif line < 1:
            messagebox.showerror("エラー", '正の数値で入力してください。')
            return 1
        elif self.index <= line - 1 < self.index + SIZE:
            pass
        else:
            self.index = line - 1
        self.redraw_widgets(change=False)

    def new_program(self, event=None):
        """新規プログラム"""
        # データが変更されていれば保存するか確認する
        data = [d.get_data(more=False) for d in self.widgets]
        if self.default_data != data:
            res = messagebox.askyesnocancel("確認", "保存しますか？")
            if res is None:
                return 1
            elif res is True:
                if self.save_program() == 1:
                    return 1

        # データを初期化
        self.delete_all_widgets()
        self.index = 0
        self.last_shown = []
        self.widgets = []
        self.copied_widgets = []
        self.default_data = []
        self.backed_up = []
        self.canceled_changes = []
        self.warning_ignore = False
        self.running_program = False
        self.program_name = None
        self.basename = "無題"
        self.var2.set(2)
        self.var3.set(True)
        self.ent1.delete(0, tk.END)

        self.redraw_widgets()

        # 基本データを設定
        self.default_data = [d.get_data(more=False)
                             for d in self.widgets]

    def new_window(self, event=None):
        """新規ウィンドウを起動"""
        if sys.argv[0][-14:] == "EasyTurtle.exe":
            command = [sys.argv[0]]
        else:
            command = [sys.executable, sys.argv[0]]
        subprocess.Popen(command)

    def reboot_program(self, event=None):
        """再起動"""
        # ファイルを決定
        if PROGRA is True:
            file = "C:/ProgramData/EasyTurtle/config/cache.json"
            os.makedirs("C:/ProgramData/EasyTurtle/cache/", exist_ok=True)
        else:
            file = os.path.abspath("./cache/cache.json")

        # データを保存
        self.save_file(file, boot=True)

        # 新規ウィンドウを起動
        if sys.argv[0][-14:] == "EasyTurtle.exe":
            command = [sys.argv[0], file]
        else:
            command = [sys.executable, sys.argv[0], file]
        subprocess.Popen(command)

        # 画面を閉じる
        self.close_window()

    def setup(self):
        """セットアップ"""
        # 基本ウィンドウを作成
        self.root = tk.Tk()
        self.root.title("無題 - EasyTurtle")
        self.root.geometry(f"{EXPAND(1240)}x{EXPAND(620)}")
        self.root.minsize(EXPAND(1240), EXPAND(600))
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self.root.focus_set()
        self.icon = tk.PhotoImage(file=ICON_FILE)
        self.root.tk.call('wm', 'iconphoto', self.root._w, self.icon)
        frame1 = tk.Frame(self.root)
        frame1.pack()

        # キーをバインド
        self.root.bind('<Button-1>', self.delete_menu)
        self.root.bind("<Control-Shift-Key-C>", self.copy_selected)
        self.root.bind("<Control-Shift-Key-V>", self.paste_widgets)
        self.root.bind("<Control-Shift-Key-X>", self.cut_selected)
        self.root.bind("<Control-Shift-Key-A>", self.select_all)
        self.root.bind("<Control-Shift-Key-S>", self.save_program_as)
        self.root.bind("<Control-Shift-Key-Z>", self.redo_change)
        self.root.bind("<Control-Shift-Key-N>", self.new_window)
        self.root.bind("<Control-Shift-Key-E>", self.enable_selected)
        self.root.bind("<Control-Shift-Key-D>", self.disable_selected)
        self.root.bind("<Control-Key-z>", self.undo_change)
        self.root.bind("<Control-Key-l>", self.clear_selected)
        self.root.bind("<Control-Key-n>", self.new_program)
        self.root.bind("<Control-Key-d>", self.delete_selected)
        self.root.bind("<Control-Key-o>", self.open_program)
        self.root.bind("<Control-Key-s>", self.save_program)
        self.root.bind("<Control-Key-g>", self.goto_line)
        self.root.bind("<Control-Key-q>", self.close_window)
        self.root.bind("<Control-Key-r>", self.reboot_program)
        self.root.bind("<Control-Key-comma>", self.edit_config)
        self.root.bind("<Key-F1>", self.show_offline_document)
        self.root.bind("<Key-F5>", self.run_standard_mode)
        self.root.bind("<Shift-Key-F5>", self.run_fastest_mode)

        # Menubarの作成
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        menu_font = (FONT_TYPE1, 10)

        # FILEメニューの作成
        filemenu = tk.Menu(self.menubar, tearoff=0, font=menu_font)
        filemenu.add_command(label="新規ファイル", accelerator="Ctrl+N",
                             command=self.new_program)
        filemenu.add_command(label="新しいウィンドウ", accelerator="Ctrl+Shift+N",
                             command=self.new_window)
        filemenu.add_separator()
        filemenu.add_command(label="ファイルを開く", accelerator="Ctrl+O",
                             command=self.open_program)
        filemenu.add_command(label="上書き保存", accelerator="Ctrl+S",
                             command=self.save_program)
        filemenu.add_command(label="名前を付けて保存", accelerator="Ctrl+Shift+S",
                             command=self.save_program_as)
        filemenu.add_separator()
        filemenu.add_command(label="再起動", accelerator="Ctrl+R",
                             command=self.reboot_program)
        filemenu.add_command(label="終了", accelerator="Ctrl+Q",
                             command=self.close_window)
        self.menubar.add_cascade(label="ファイル", menu=filemenu)

        # EDITメニューの作成
        editmenu = tk.Menu(self.menubar, tearoff=0, font=menu_font)
        editmenu.add_command(label="取り消し", accelerator="Ctrl+Z",
                             command=self.undo_change)
        editmenu.add_command(label="やり直し", accelerator="Ctrl+Shift+Z",
                             command=self.redo_change)
        editmenu.add_separator()
        editmenu.add_command(label="コピー", accelerator="Ctrl+Shift+C",
                             command=self.copy_selected)
        editmenu.add_command(label="切り取り", accelerator="Ctrl+Shift+X",
                             command=self.cut_selected)
        editmenu.add_command(label="貼り付け", accelerator="Ctrl+Shift+V",
                             command=self.paste_widgets)
        editmenu.add_command(label="削除", accelerator="Ctrl+D",
                             command=self.delete_selected)
        editmenu.add_separator()
        editmenu.add_command(label="有効化", accelerator="Ctrl+Shift+E",
                             command=self.enable_selected)
        editmenu.add_command(label="無効化", accelerator="Ctrl+Shift+D",
                             command=self.disable_selected)
        editmenu.add_separator()
        editmenu.add_command(label="すべて選択", accelerator="Ctrl+Shift+A",
                             command=self.select_all)
        editmenu.add_command(label="選択解除", accelerator="Ctrl+L",
                             command=self.clear_selected)
        editmenu.add_separator()
        editmenu.add_command(label="行へ移動", accelerator="Ctrl+G",
                             command=self.goto_line)
        self.menubar.add_cascade(label="編集", menu=editmenu)

        # RUNメニューの作成
        runmenu = tk.Menu(self.menubar, tearoff=0, font=menu_font)
        runmenu.add_command(label="実行", accelerator="F5",
                            command=self.run_standard_mode)
        runmenu.add_command(label="最速実行", accelerator="Shift+F5",
                            command=self.run_fastest_mode)
        self.menubar.add_cascade(label="実行", menu=runmenu)

        # OPTIONSメニューの追加
        othermenu = tk.Menu(self.menubar, tearoff=0, font=menu_font)
        othermenu.add_command(label="設定", accelerator="Ctrl+,",
                              command=self.edit_config)
        othermenu.add_separator()
        othermenu.add_command(label="オンラインヘルプ",
                              command=self.show_online_document)
        othermenu.add_command(label="オフラインヘルプ", accelerator="F1",
                              command=self.show_offline_document)
        othermenu.add_command(label="バージョン情報", command=self.version_info)
        othermenu.add_command(label="GitHubの表示", command=self.show_github_page)
        self.menubar.add_cascade(label="オプション", menu=othermenu)

        # 画面の左側を作成
        frame2 = tk.Frame(frame1)
        frame2.pack(side=tk.LEFT, padx=(10, 0))
        frame2.bind("<MouseWheel>", self.scroll_on_windows)
        self.cv1 = tk.Canvas(frame2, width=EXPAND(
            WIDTH), height=EXPAND(HEIGHT*SIZE), bg="#E6E6E6")
        self.cv1.pack(side=tk.LEFT)
        self.cv1.bind("<MouseWheel>", self.scroll_on_windows)
        self.cv1.create_rectangle(EXPAND(4), EXPAND(4),
                                  EXPAND(WIDTH), EXPAND(HEIGHT*SIZE),
                                  width=EXPAND(2))
        self.scr2 = ttk.Scrollbar(frame2, orient=tk.VERTICAL,
                                  command=self.scroll_button_clicked)
        self.scr2.pack(fill='y', side=tk.RIGHT)
        frame3 = tk.Frame(frame1)
        frame3.pack(side=tk.RIGHT, padx=EXPAND(10))
        lab0 = tk.Label(self.cv1, text="EasyTurtle",
                        fg="#D8D8D8", bg="#E6E6E6",
                        font=(FONT_TYPE2, EXPAND(56), "bold", "italic"))
        lab0.place(x=EXPAND(80), y=EXPAND(250))

        # 画面右側下段を作成
        frame4 = tk.Frame(frame3)
        frame4.pack(fill="x", side=tk.BOTTOM)
        lab1 = tk.Label(frame4, text='©2020-2021 Ryo Fujinami.',
                        font=(FONT_TYPE2, EXPAND(12), "italic"))
        lab1.pack(side=tk.RIGHT, padx=EXPAND(20))
        joined_version = ".".join([str(n) for n in __version__])
        lab2 = tk.Label(frame4, text="v"+joined_version,
                        font=(FONT_TYPE1, EXPAND(12)))
        lab2.pack(side=tk.RIGHT, padx=EXPAND(10))

        # 画面右側中段を作成
        lfr1 = tk.LabelFrame(frame3, text="ウィジェットの追加位置",
                             font=(FONT_TYPE1, EXPAND(18), "bold"),
                             labelanchor=tk.N)
        lfr1.pack(side=tk.BOTTOM, pady=EXPAND(10), fill=tk.X)
        self.var2 = tk.IntVar()
        self.var2.set(2)
        font = (FONT_TYPE1, EXPAND(16), "bold")
        rad1 = tk.Radiobutton(lfr1, value=1, variable=self.var2,
                              text="プログラムの最初", font=font)
        rad1.pack(anchor=tk.W, padx=EXPAND(80))
        rad2 = tk.Radiobutton(lfr1, value=2, variable=self.var2,
                              text="プログラムの最後", font=font)
        rad2.pack(anchor=tk.W, padx=EXPAND(80))
        frame8 = tk.Frame(lfr1)
        frame8.pack(anchor=tk.W, padx=EXPAND(80))
        rad3 = tk.Radiobutton(frame8, value=3, variable=self.var2,
                              text="指定位置：", font=font)
        rad3.pack(anchor=tk.W, side=tk.LEFT)
        self.ent1 = tk.Entry(frame8, font=font, width=8)
        self.ent1.pack(anchor=tk.W, side=tk.LEFT)
        self.var3 = tk.BooleanVar()
        self.var3.set(True)
        chk1 = tk.Checkbutton(lfr1, text="位置の自動調整",
                              font=font, variable=self.var3)
        chk1.pack(anchor=tk.E, padx=80, pady=(0, EXPAND(10)))

        # 画面右側上段を作成
        frame7 = tk.Frame(frame3)
        frame7.pack(side=tk.TOP, pady=(0, EXPAND(10)))
        var1 = tk.StringVar(self.root, value=Texts)
        height = 12 if SYSTEM == "Windows" else 14
        self.lsb1 = tk.Listbox(frame7, listvariable=var1, height=height,
                               width=44, selectmode='single',
                               bg="#FFEFD7", font=(FONT_TYPE1, EXPAND(18)),
                               selectbackground="#2F4FAF",
                               selectforeground="#FFFFFF")
        self.lsb1.bind('<<ListboxSelect>>', self.append_new_widget)
        self.lsb1.pack(fill='y', side=tk.LEFT)
        scr1 = ttk.Scrollbar(frame7, orient=tk.VERTICAL,
                             command=self.lsb1.yview)
        self.lsb1['yscrollcommand'] = scr1.set
        scr1.pack(fill='y', side=tk.RIGHT)

        self.redraw_widgets()


class Widget:
    def __init__(self, parent: EasyTurtle, data={}, index=-1):
        """初期化"""
        self.p = parent
        self.info = GET_WIDGET_INFO(self)
        self.pressed_x = self.pressed_y = 0
        self.item_id = -1

        self.TYPE: str

        if self.TYPE == "variable":
            self.background = "#F7C7A7"
        elif self.TYPE == "normalset":
            self.background = "#B7E7F7"
        elif self.TYPE == "normalget":
            self.background = "#A7F7A7"
        elif self.TYPE == "comment":
            self.background = "#F7A7A7"
        elif self.TYPE == "undefined":
            self.background = "#E7C7F7"

        tops = len(self.p.widgets)
        self.p.index = 0 if tops < SIZE else tops
        if index == -1:
            self.p.widgets.append(self)
        else:
            self.p.widgets.insert(index, self)

        self.set_data(data)

        self.draw()

    def __repr__(self):
        """コンストラクタの文字列定義"""
        data = self.get_data()
        return f"{data['_name']}(self, data={data})"

    def set_data(self, data):
        """データの設定（サブクラスで宣言される関数）"""

    def get_data(self, more=True):
        """データの取得（サブクラスで宣言される関数）"""

    def draw(self):
        """ウィジェットの絵画（サブクラスで宣言される関数）"""

    def save_data(self):
        """データの保存（サブクラスで宣言される関数）"""

    def run(self, tur: turtle.RawTurtle):
        """データの実行（サブクラスで宣言される関数）"""

    def binder(self, widget):
        """ボタンのバインド"""
        widget.bind('<Button-3>', self.show_popup2)
        widget.bind("<B1-Motion>", self.dragged)
        if SYSTEM == "Windows":
            widget.bind("<MouseWheel>", self.p.scroll_on_windows)
        elif SYSTEM == "Linux":
            widget.bind("<Button-4>", self.p.scroll_on_linux)
            widget.bind("<Button-5>", self.p.scroll_on_linux)

    def draw_cv(self):
        """キャンバスを描く"""
        # キャンバスを表示
        self.cv = tk.Canvas(self.p.cv1, width=EXPAND(WIDTH),
                            height=EXPAND(HEIGHT), bg=self.background)
        self.binder(self.cv)

        # キャンバスの枠を表示
        self.cv.create_rectangle(EXPAND(42), EXPAND(4),
                                 EXPAND(WIDTH), EXPAND(HEIGHT//2+2),
                                 width=EXPAND(2))
        self.cv.create_rectangle(EXPAND(42), EXPAND(HEIGHT//2+2),
                                 EXPAND(WIDTH), EXPAND(HEIGHT),
                                 width=EXPAND(2))
        self.cv.create_rectangle(EXPAND(4), EXPAND(4),
                                 EXPAND(42), EXPAND(HEIGHT), width=EXPAND(2))

        # ウィジェットの説明を表示
        lab1 = tk.Label(self.cv, text=self.info, font=FONT, bg=self.background)
        self.binder(lab1)
        lab1.place(x=EXPAND(50), y=EXPAND(10))
        self.check_enabled()

        # インデックスを表示
        self.lab4 = tk.Label(self.cv, font=FONT, bg=self.background,
                             text=f"{self.p.widgets.index(self)+1:03}")
        self.binder(self.lab4)
        self.lab4.place(x=EXPAND(5), y=EXPAND(HEIGHT//2-8))

        # チェックボックスを表示
        self.bln1 = tk.BooleanVar()
        self.bln1.set(self.check)
        chk1 = tk.Checkbutton(self.cv, variable=self.bln1,
                              cursor="hand2", bg=self.background,
                              font=(FONT_TYPE2, EXPAND(10)))
        self.binder(chk1)
        chk1.bind("<Button-1>", self.check_clicked)
        chk1.place(x=EXPAND(12), y=EXPAND(HEIGHT//2+8))

    def check_clicked(self, event):
        if (hasattr(event, "state")) and (event.state == 1):
            self.shift_check()
        else:
            self.p.back_up()

    def shift_check(self):
        """Shift+右クリック"""
        selected = self.p.get_selected()
        sindex = self.p.widgets.index(self)
        if len(selected) == 0:
            return
        elif len(selected) == 1:
            dindex = self.p.widgets.index(selected[0])
            if sindex < dindex:
                self.range_check(sindex, dindex, exc=sindex)
            else:
                self.range_check(dindex, sindex, exc=sindex)
        else:
            lindex = None
            for new in selected:
                nindex = self.p.widgets.index(new)
                if lindex is None:
                    if sindex < nindex:
                        self.range_check(sindex, nindex, exc=sindex)
                        return
                elif lindex < sindex < nindex:
                    if (sindex - lindex) < (nindex - sindex):
                        self.range_check(lindex, sindex, exc=sindex)
                    else:
                        self.range_check(sindex, nindex, exc=sindex)
                    return
                lindex = nindex
            if sindex > lindex:
                self.range_check(lindex, sindex, exc=sindex)

    def range_check(self, first, last, exc=None):
        """指定範囲をチェック"""
        for widget in self.p.widgets:
            widget.bln1.set(False)
        for widget in self.p.widgets[first: last + 1]:
            widget.bln1.set(True)
        if exc is not None:
            self.p.widgets[exc].bln1.set(False)

    def check_enabled(self):
        """有効・無効の表示"""
        self.cv.delete("enabled")
        color = "blue" if self.enabled is True else "red"
        self.cv.create_oval(EXPAND(14), EXPAND(10),
                            EXPAND(30), EXPAND(HEIGHT//2-10),
                            width=2, outline="lightgray",
                            fill=color, tag="enabled")

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

    def paste_up(self):
        """上へのペースト"""
        before_index = self.p.index

        index = self.p.widgets.index(self)
        for d in reversed(self.p.copied_widgets):
            self.p.make_match_class(d, index=index)

        if (index < before_index) or (index > before_index + SIZE - 1):
            self.p.index = index
        else:
            self.p.index = before_index

        self.p.redraw_widgets()

    def paste_down(self):
        """下へのペースト"""
        before_index = self.p.index

        index = self.p.widgets.index(self) + 1
        for d in reversed(self.p.copied_widgets):
            self.p.make_match_class(d, index=index)

        if (index < before_index) or (index > before_index + SIZE - 1):
            self.p.index = index
        else:
            self.p.index = before_index

        self.p.redraw_widgets()

    def duplicate(self):
        """複製"""
        before_index = self.p.index

        index = self.p.widgets.index(self) + 1
        self.p.make_match_class(self.get_data(), index=index)

        if (index < before_index) or (index > before_index + SIZE - 1):
            self.p.index = index
        else:
            self.p.index = before_index

        self.p.redraw_widgets()

    def show_popup2(self, event):
        "ポップアップメニュー"
        if hasattr(self.p, "menu") is True:
            self.p.menu.destroy()

        index = self.p.widgets.index(self)

        menu_font = (FONT_TYPE1, 10)
        self.p.menu = tk.Menu(self.p.root, tearoff=0, font=menu_font)

        states = ["active" for i in range(5)]
        if index <= 0:
            states[0] = states[2] = "disabled"
        if index >= len(self.p.widgets) - 1:
            states[1] = states[3] = "disabled"
        if len(self.p.copied_widgets) == 0:
            states[4] = "disabled"

        self.p.menu.add_command(label='１番上に移動', command=self.top,
                                state=states[0])
        self.p.menu.add_command(label='１番下に移動', command=self.bottom,
                                state=states[1])
        self.p.menu.add_command(label='１個上に移動', command=self.up,
                                state=states[2])
        self.p.menu.add_command(label='１個下に移動', command=self.down,
                                state=states[3])

        self.p.menu.add_separator()
        self.p.menu.add_command(label='コピー', command=self.copy)
        self.p.menu.add_command(label='切り取り', command=self.cut)
        self.p.menu.add_command(label='削除', command=self.delete)

        self.p.menu.add_separator()
        self.p.menu.add_command(label='複製', command=self.duplicate)

        if hasattr(self, "show_option") is True:
            self.p.menu.add_separator()
            self.p.menu.add_command(label='オプション', command=self.show_option)

        self.p.menu.add_separator()
        if (self.TYPE == "undefined") or (self.TYPE == "comment"):
            self.p.menu.add_command(label='有効化', state="disabled")
        elif self.enabled is True:
            self.p.menu.add_command(label='無効化', command=self.disable)
        else:
            self.p.menu.add_command(label='有効化', command=self.enable)

        self.p.menu.add_separator()
        self.p.menu.add_command(label='上にペースト', command=self.paste_up,
                                state=states[4])
        self.p.menu.add_command(label='下にペースト', command=self.paste_down,
                                state=states[4])

        self.p.menu.post(event.x_root, event.y_root)

    def enable(self, back_up=True):
        "ウィジェットの有効化"
        self.enabled = True
        self.check_enabled()
        if back_up is True:
            self.p.back_up()

    def disable(self, back_up=True):
        "ウィジェットの無効化"
        self.enabled = False
        self.check_enabled()
        if back_up is True:
            self.p.back_up()

    def delete(self, back_up=True):
        """ウィジェットの削除"""
        if self in self.p.last_shown:
            self.p.last_shown.remove(self)
        self.cv.place_forget()
        self.p.widgets.remove(self)
        self.p.redraw_widgets(back_up)

    def place_cv(self):
        """キャンバスを描き直す"""
        index = self.p.widgets.index(self) - self.p.index
        if 0 <= index < SIZE:
            self.cv.place(x=0, y=EXPAND(HEIGHT*index))
            self.lab4.config(text=f"{self.p.widgets.index(self)+1:03}")
        else:
            self.cv.place_forget()

    def copy(self):
        """ウィジェットをコピーする"""
        data = self.get_data()
        data["_check"] = False
        self.p.copied_widgets = [data]

    def cut(self):
        """ウィジェットをカットする"""
        self.copy()
        self.delete()

    def top(self):
        """ウィジェットを一番上に移動"""
        self.p.widgets.remove(self)
        self.p.widgets.insert(0, self)
        self.p.index = 0
        self.p.redraw_widgets()

    def bottom(self):
        """ウィジェットを一番下に移動"""
        self.p.widgets.remove(self)
        self.p.widgets.append(self)
        bottom = len(self.p.widgets)
        self.p.index = bottom if bottom > SIZE else 0
        self.p.redraw_widgets()

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
        self.p.redraw_widgets()

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
        self.p.redraw_widgets()

    def set_common(self, data):
        """共通変数に値をセットする"""
        if data is None:
            self.check = False
        else:
            if "_check" in data:
                self.check = data["_check"]
            else:
                self.check = False

        if (self.TYPE == "comment") or (self.TYPE == "undefined"):
            self.enabled = False
        else:
            if (data is None) or ("_enabled" not in data):
                self.enabled = True
            else:
                self.enabled = data["_enabled"]

    def get_class_data(self, data, more):
        """クラスのデータを追加する"""
        if more is True:
            data["_check"] = self.bln1.get()
        elif "_check" in data:
            del data["_check"]

        data["_enabled"] = self.enabled

        if self.__class__.__name__ != "Undefined":
            data["_name"] = self.__class__.__name__
        return data

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
        if hasattr(self.p, "menu") is True:
            self.p.menu.destroy()
        try:
            if self.p.root.clipboard_get() != "":
                paste = "active"
            else:
                paste = "disabled"
        except tk.TclError:
            paste = "disabled"

        menu_font = (FONT_TYPE1, 10)
        self.p.menu = tk.Menu(self.p.root, tearoff=0, font=menu_font)

        self.p.menu.add_command(
            label='コピー', command=lambda: self.copy_entry(entry))
        self.p.menu.add_command(label='ペースト', state=paste,
                                command=lambda: self.paste_entry(entry))
        self.p.menu.post(event.x_root, event.y_root)

    def str2str(self, string):
        """変数を埋め込み"""
        for var in re.findall(r'\[\w*\]', string):
            name = var[1:-1] if len(var) > 2 else ""
            if name not in self.p.variable_datas:
                messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"は定義されていません。')
                self.p.kill_runner()
            elif (self.p.variable_datas[name][1] == "S") or \
                 (CONFIG["show_warning"] is False):
                string = string.replace(
                    var, str(self.p.variable_datas[name][0]))
            else:
                messagebox.showwarning("警告", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"はString型ではありません。')
                string = string.replace(
                    var, str(self.p.variable_datas[name][0]))
        return string

    def str2bool(self, string):
        """変数を埋め込み"""
        match = re.fullmatch(r'\[\w*\]', string)
        if match is not None:
            var = match.group()
            name = var[1:-1]
            if name not in self.p.variable_datas:
                messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"は定義されていません。')
                self.p.kill_runner()
            elif (self.p.variable_datas[name][1] == "B") or \
                 (CONFIG["show_warning"] is False):
                string = string.replace(
                    var, str(self.p.variable_datas[name][0]))
            else:
                messagebox.showwarning("警告", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"はBoolean型ではありません。')
                string = string.replace(
                    var, str(self.p.variable_datas[name][0]))
        if string == "True":
            boolean = True
        elif string == "False":
            boolean = False
        else:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
{string}はBoolean型ではありません。')
            self.p.kill_runner()
        return boolean

    def var_converter(self, string):
        """変数を埋め込み"""
        for var in re.findall(r'\[\w*\]', string):
            name = var[1:-1] if len(var) > 2 else ""
            if name not in self.p.variable_datas:
                messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"は定義されていません。')
                self.p.kill_runner()
            elif (self.p.variable_datas[name][1] == "N") or \
                 (CONFIG["show_warning"] is False):
                string = string.replace(
                    var, str(self.p.variable_datas[name][0]))
            else:
                messagebox.showwarning("警告", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"はNumber型ではありません。')
                string = string.replace(
                    var, str(self.p.variable_datas[name][0]))
        return string

    def calculator(self, string):
        """数列の計算"""
        string = self.var_converter(string)
        if string == "":
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
値が入力されていません。')
            self.p.kill_runner()
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

    def str2float(self, string):
        """文字列を小数に変換"""
        try:
            return self.calculator(string)
        except Exception:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{string}"を数値に変換できませんでした。')
            self.p.kill_runner()

    def str2int(self, string):
        """文字列を整数に変換"""
        num = self.str2float(string)
        if (float(num).is_integer() is False) and \
           (CONFIG["show_warning"] is True):
            messagebox.showwarning("警告", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
値は整数でなければなりません。')
        return int(round(num))

    def str2uint(self, string):
        """文字列を符号なし整数に変換"""
        num = self.str2int(string)
        if num < 0:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
値は正の整数でなければなりません。')
            self.p.kill_runner()
        else:
            return num

    def str2ufloat(self, string):
        """文字列を符号なし小数に変換"""
        num = self.str2float(string)
        if num < 0:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
値は正の小数でなければなりません。')
            self.p.kill_runner()
        else:
            return num


class VarNumber(Widget):
    TEXT = "変数①を数値②にする"
    TYPE = "variable"
    VALUES = {"name": "num", "value": "0"}

    def set_data(self, data):
        if "name" in data:
            self.name = data["name"]
        else:
            self.name = self.VALUES["name"]
        if "value" in data:
            self.value = data["value"]
        else:
            self.value = self.VALUES["value"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({
            "name": self.name,
            "value": self.value}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.name)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.value)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.name = self.ent1.get()
        self.value = self.ent2.get()

    def run(self, tur):
        self.save_data()
        self.p.variable_datas[self.name] = (self.str2float(self.value), "N")


class VarString(Widget):
    TEXT = "変数①を文字列②にする"
    TYPE = "variable"
    VALUES = {"name": "str", "value": "text"}

    def set_data(self, data):
        if "name" in data:
            self.name = data["name"]
        else:
            self.name = self.VALUES["name"]
        if "value" in data:
            self.value = data["value"]
        else:
            self.value = self.VALUES["value"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({
            "name": self.name,
            "value": self.value}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.name)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.value)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.name = self.ent1.get()
        self.value = self.ent2.get()

    def run(self, tur):
        self.save_data()
        self.p.variable_datas[self.name] = (self.str2str(self.value), "S")


class VarBoolean(Widget):
    TEXT = "変数①を真理値②にする"
    TYPE = "variable"
    VALUES = {"name": "bool", "value": "True"}

    def set_data(self, data):
        if "name" in data:
            self.name = data["name"]
        else:
            self.name = self.VALUES["name"]
        if "value" in data:
            self.value = data["value"]
        else:
            self.value = self.VALUES["value"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({
            "name": self.name,
            "value": self.value}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.name)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.var1 = tk.StringVar()
        cb1 = ttk.Combobox(self.cv, textvariable=self.var1,
                           font=FONT, width=10)
        cb1['values'] = ("True", "False")
        cb1.set(self.value)
        self.binder(cb1)
        cb1.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.name = self.ent1.get()
        self.value = self.var1.get()

    def run(self, tur):
        self.save_data()
        self.p.variable_datas[self.name] = (self.str2bool(self.value), "B")


class Title(Widget):
    TEXT = "画面タイトルを①にする"
    TYPE = "normalset"
    VALUES = {"title": "Turtle"}

    def set_data(self, data):
        if "title" in data:
            self.title = data["title"]
        else:
            self.title = self.VALUES["title"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"title": self.title}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.title)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.title = self.ent1.get()

    def run(self, tur):
        self.save_data()
        self.p.win.title(self.str2str(self.title))


class ScreenSize(Widget):
    TEXT = "画面を横幅①、高さ②にする"
    TYPE = "normalset"
    VALUES = {"width": "600", "height": "600"}

    def set_data(self, data):
        if "width" in data:
            self.width = data["width"]
        else:
            self.width = self.VALUES["width"]
        if "height" in data:
            self.height = data["height"]
        else:
            self.height = self.VALUES["height"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({
            "width": self.width,
            "height": self.height}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.width)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.height)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.width = self.ent1.get()
        self.height = self.ent2.get()

    def run(self, tur):
        # データを保存する
        self.save_data()

        # 画面サイズを取得
        width = self.str2uint(self.width)
        height = self.str2uint(self.height)

        # 警告を表示
        if width > SYSTEM_WIDTH:
            if CONFIG["show_warning"] is True:
                messagebox.showwarning("警告", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
画面の横幅（{SYSTEM_WIDTH}）以上の数値が指定されました。')
            width = SYSTEM_WIDTH
        if height > SYSTEM_HEIGHT:
            if CONFIG["show_warning"] is True:
                messagebox.showwarning("警告", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
画面の高さ（{SYSTEM_HEIGHT}）以上の数値が指定されました。')
            height = SYSTEM_HEIGHT

        # 画面サイズを変更
        self.p.win.geometry(f"{width}x{height}")

        # 亀を移動
        canvas = tur.getscreen().getcanvas()
        canvas.config(
            width=width, height=height)
        tur.penup()
        tur.speed(0)
        tur.goto(width // 2, height // -2)
        tur.speed(self.p.runner_speed)
        if self.p.runner_pendown is True:
            tur.pendown()

        # すべての要素を移動
        for element_id in canvas.find_all():
            canvas.move(element_id,
                        (width - self.p.runner_size[0]) // 2,
                        (height - self.p.runner_size[1]) // 2)

        # データを変更
        self.p.runner_size = (width, height)


class Forward(Widget):
    TEXT = "前方向に①移動する"
    TYPE = "normalset"
    VALUES = {"distance": "0"}

    def set_data(self, data):
        if "distance" in data:
            self.distance = data["distance"]
        else:
            self.distance = self.VALUES["distance"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"distance": self.distance}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.distance)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.distance = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.forward(self.str2int(self.distance))


class Backward(Widget):
    TEXT = "後方向に①移動する"
    TYPE = "normalset"
    VALUES = {"distance": "0"}

    def set_data(self, data):
        if "distance" in data:
            self.distance = data["distance"]
        else:
            self.distance = self.VALUES["distance"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"distance": self.distance}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="d <= ", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.distance)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.distance = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.backward(self.str2int(self.distance))


class Right(Widget):
    TEXT = "右方向に①度曲げる"
    TYPE = "normalset"
    VALUES = {"angle": "0"}

    def set_data(self, data):
        if "angle" in data:
            self.angle = data["angle"]
        else:
            self.angle = self.VALUES["angle"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.angle = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.right(self.str2int(self.angle))


class Left(Widget):
    TEXT = "左方向に①度曲げる"
    TYPE = "normalset"
    VALUES = {"angle": "0"}

    def set_data(self, data):
        if "angle" in data:
            self.angle = data["angle"]
        else:
            self.angle = self.VALUES["angle"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.angle = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.left(self.str2int(self.angle))


class GoTo(Widget):
    TEXT = "ｘ座標①、ｙ座標②に移動する"
    TYPE = "normalset"
    VALUES = {"x": "0", "y": "0"}

    def set_data(self, data):
        if "x" in data:
            self.x = data["x"]
        else:
            self.x = self.VALUES["x"]
        if "y" in data:
            self.y = data["y"]
        else:
            self.y = self.VALUES["y"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x, "y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.y)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.x = self.ent1.get()
        self.y = self.ent2.get()

    def run(self, tur):
        self.save_data()
        tur.goto(
            self.str2int(self.x) + self.p.runner_size[0] // 2,
            self.str2int(self.y) - self.p.runner_size[1] // 2)


class SetX(Widget):
    TEXT = "ｘ座標①に移動する"
    TYPE = "normalset"
    VALUES = {"x": "0"}

    def set_data(self, data):
        if "x" in data:
            self.x = data["x"]
        else:
            self.x = self.VALUES["x"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.x = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.setx(self.str2int(self.x) + self.p.runner_size[0] // 2)


class SetY(Widget):
    TEXT = "ｙ座標①に移動する"
    TYPE = "normalset"
    VALUES = {"y": "0"}

    def set_data(self, data):
        if "y" in data:
            self.y = data["y"]
        else:
            self.y = self.VALUES["y"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.y)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.y = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.sety(self.str2int(self.y) - self.p.runner_size[1] // 2)


class SetHeading(Widget):
    TEXT = "向きを①度に変更する"
    TYPE = "normalset"
    VALUES = {"angle": "0"}

    def set_data(self, data):
        if "angle" in data:
            self.angle = data["angle"]
        else:
            self.angle = self.VALUES["angle"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.angle = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.setheading(self.str2int(self.angle))


class Home(Widget):
    TEXT = "座標と角度を初期状態に戻す"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        tur.goto(self.p.runner_size[0] // 2, self.p.runner_size[1] // -2)


class Position(Widget):
    TEXT = "座標ｘを①、ｙを②に代入する"
    TYPE = "normalget"
    VALUES = {"x": "xcor", "y": "ycor"}

    def set_data(self, data):
        if "x" in data:
            self.x = data["x"]
        else:
            self.x = self.VALUES["x"]
        if "y" in data:
            self.y = data["y"]
        else:
            self.y = self.VALUES["y"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x, "y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.y)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.x = self.ent1.get()
        self.y = self.ent2.get()

    def run(self, tur):
        self.save_data()
        xval, yval = tur.position()
        self.p.variable_datas[self.x] = (
            xval - self.p.runner_size[0] // 2, "N")
        self.p.variable_datas[self.y] = (
            yval + self.p.runner_size[1] // 2, "N")


class ToWards(Widget):
    TEXT = "ｘ①、ｙ②への角度を③に代入する"
    TYPE = "normalget"
    VALUES = {"x": "0",
              "y": "0",
              "angle": "angle"}

    def set_data(self, data):
        if "x" in data:
            self.x = data["x"]
        else:
            self.x = self.VALUES["x"]
        if "y" in data:
            self.y = data["y"]
        else:
            self.y = self.VALUES["y"]
        if "angle" in data:
            self.angle = data["angle"]
        else:
            self.angle = self.VALUES["angle"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x,
                                    "y": self.y,
                                    "angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.y)
        self.binder(self.ent1)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))
        lab4 = tk.Label(self.cv, text="③", font=FONT, bg=self.background)
        self.binder(lab4)
        lab4.place(x=EXPAND(350), y=EXPAND(HEIGHT//2+8))
        self.ent3 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent3.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent3.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent3.place(x=EXPAND(370), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.x = self.ent1.get()
        self.y = self.ent2.get()
        self.angle = self.ent3.get()

    def run(self, tur):
        self.save_data()
        angle = tur.towards(
            self.str2int(self.x) + self.p.runner_size[0] // 2,
            self.str2int(self.y) - self.p.runner_size[1] // 2)
        self.p.variable_datas[self.angle] = (angle, "N")


class Distance(Widget):
    TEXT = "ｘ①、ｙ②への距離を③に代入する"
    TYPE = "normalget"
    VALUES = {"x": "0",
              "y": "0",
              "distance": "distance"}

    def set_data(self, data):
        if "x" in data:
            self.x = data["x"]
        else:
            self.x = self.VALUES["x"]
        if "y" in data:
            self.y = data["y"]
        else:
            self.y = self.VALUES["y"]
        if "distance" in data:
            self.distance = data["distance"]
        else:
            self.distance = self.VALUES["distance"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x,
                                    "y": self.y,
                                    "distance": self.distance}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.y)
        self.binder(self.ent1)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))
        lab4 = tk.Label(self.cv, text="③", font=FONT, bg=self.background)
        self.binder(lab4)
        lab4.place(x=EXPAND(350), y=EXPAND(HEIGHT//2+8))
        self.ent3 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent3.insert(tk.END, self.distance)
        self.binder(self.ent1)
        self.ent3.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent3.place(x=EXPAND(370), y=EXPAND(HEIGHT // 2 + 8))

    def save_data(self):
        self.x = self.ent1.get()
        self.y = self.ent2.get()
        self.distance = self.ent3.get()

    def run(self, tur):
        self.save_data()
        distance = tur.distance(
            self.str2int(self.x) + self.p.runner_size[0] // 2,
            self.str2int(self.y) - self.p.runner_size[1] // 2)
        self.p.variable_datas[self.distance] = (distance, "N")


class XCor(Widget):
    TEXT = "ｘ座標を①に代入する"
    TYPE = "normalget"
    VALUES = {"x": "xcor"}

    def set_data(self, data):
        if "x" in data:
            self.x = data["x"]
        else:
            self.x = self.VALUES["x"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.x = self.ent1.get()

    def run(self, tur):
        self.save_data()
        xval = tur.xcor()
        self.p.variable_datas[self.x] = (
            xval - self.p.runner_size[0] // 2, "N")


class YCor(Widget):
    TEXT = "ｙ座標を①に代入する"
    TYPE = "normalget"
    VALUES = {"y": "ycor"}

    def set_data(self, data):
        if "y" in data:
            self.y = data["y"]
        else:
            self.y = self.VALUES["y"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.y)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.y = self.ent1.get()

    def run(self, tur):
        self.save_data()
        yval = tur.ycor()
        self.p.variable_datas[self.y] = (
            yval + self.p.runner_size[1] // 2, "N")


class Heading(Widget):
    TEXT = "角度を①に代入する"
    TYPE = "normalget"
    VALUES = {"angle": "angle"}

    def set_data(self, data):
        if "angle" in data:
            self.angle = data["angle"]
        else:
            self.angle = self.VALUES["angle"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.angle = self.ent1.get()

    def run(self, tur):
        self.save_data()
        aval = tur.heading()
        self.p.variable_datas[self.angle] = (aval, "N")


class Circle(Widget):
    TEXT = "半径①の円を角度②度描く"
    TYPE = "normalset"
    VALUES = {"radius": "0", "extent": "360"}

    def set_data(self, data):
        if "radius" in data:
            self.radius = data["radius"]
        else:
            self.radius = self.VALUES["radius"]
        if "extent" in data:
            self.extent = data["extent"]
        else:
            self.extent = self.VALUES["extent"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({
            "radius": self.radius,
            "extent": self.extent}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.radius)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.extent)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.radius = self.ent1.get()
        self.extent = self.ent2.get()

    def run(self, tur):
        self.save_data()
        tur.circle(
            self.str2int(self.radius),
            self.str2int(self.extent))


class Dot(Widget):
    TEXT = "直径①の円を描く"
    TYPE = "normalset"
    VALUES = {"size": "0"}

    def set_data(self, data):
        if "size" in data:
            self.size = data["size"]
        else:
            self.size = self.VALUES["size"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"size": self.size}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.size)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.size = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.dot(self.str2uint(self.size))


class Stamp(Widget):
    TEXT = "亀のスタンプを押す"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        tur.stamp()


class Speed(Widget):
    TEXT = "速度を①に変更する"
    TYPE = "normalset"
    VALUES = {"speed": "3"}

    def set_data(self, data):
        if "speed" in data:
            self.speed = data["speed"]
        else:
            self.speed = self.VALUES["speed"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"speed": self.speed}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.speed)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.speed = self.ent1.get()

    def run(self, tur):
        self.save_data()
        if self.p.running_fastest is False:
            self.p.runner_speed = self.str2int(self.speed)
            tur.speed(self.p.runner_speed)


class PenDown(Widget):
    TEXT = "動いた線を引くようにする"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        self.p.runner_pendown = True
        tur.pendown()


class PenUp(Widget):
    TEXT = "動いた線を引かなくする"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        self.p.runner_pendown = False
        tur.penup()


class IsDown(Widget):
    TEXT = "動いた線を引くか①に代入する"
    TYPE = "normalget"
    VALUES = {"down": "down"}

    def set_data(self, data):
        if "down" in data:
            self.down = data["down"]
        else:
            self.down = self.VALUES["down"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"down": self.down}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.down)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.down = self.ent1.get()

    def run(self, tur):
        self.save_data()
        down = tur.isdown()
        self.p.variable_datas[self.down] = (down, "B")


class PenSize(Widget):
    TEXT = "ペン先の太さを①にする"
    TYPE = "normalset"
    VALUES = {"width": "1"}

    def set_data(self, data):
        if "width" in data:
            self.width = data["width"]
        else:
            self.width = self.VALUES["width"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"width": self.width}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.width)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.width = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.pensize(self.str2uint(self.width))


class Color(Widget):
    TEXT = "ペンと背景の色を①にする"
    TYPE = "normalset"
    VALUES = {"color": "black"}

    def set_data(self, data):
        if "color" in data:
            self.color = data["color"]
        else:
            self.color = self.VALUES["color"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        strvar = tk.StringVar()
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT,
                             validate='all', textvariable=strvar,
                             vcmd=self.preview_color)
        strvar.set(self.color)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.bind("<KeyPress>", self.preview_color)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        self.preview_color()

    def preview_color(self, event=None):
        text = self.ent1.get()
        if event is not None:
            if event.char == "\x08":
                text = text[:-1]
            elif repr(event.char)[1] != "\\":
                text += repr(event.char)[1:-1]
        color = self.str2str(text)
        if color == "":
            color = "white"
        self.cv.delete("highlight")
        try:
            self.cv.create_rectangle(EXPAND(280), EXPAND(HEIGHT//2+10),
                                     EXPAND(300), EXPAND(HEIGHT-6),
                                     fill=color, outline="lightgray",
                                     width=2, tag="highlight")
        except tk.TclError:
            self.cv.create_rectangle(EXPAND(280), EXPAND(HEIGHT//2+10),
                                     EXPAND(300), EXPAND(HEIGHT-6),
                                     fill="black", outline="lightgray",
                                     width=2, tag="highlight")

    def show_option(self):
        color = self.ent1.get()
        try:
            color = colorchooser.askcolor(
                color=self.str2str(color), parent=self.p.root)
        except tk.TclError:
            color = colorchooser.askcolor(parent=self.p.root)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())
        self.preview_color()

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur):
        self.save_data()
        try:
            tur.color(self.str2str(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした。', parent=self.p.root)
            self.p.kill_runner()


class PenColor(Widget):
    TEXT = "ペンの色を①にする"
    TYPE = "normalset"
    VALUES = {"color": "black"}

    def set_data(self, data):
        if "color" in data:
            self.color = data["color"]
        else:
            self.color = self.VALUES["color"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        strvar = tk.StringVar()
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT,
                             validate='all', textvariable=strvar,
                             vcmd=self.preview_color)
        strvar.set(self.color)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.bind("<KeyPress>", self.preview_color)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        self.preview_color()

    def preview_color(self, event=None):
        text = self.ent1.get()
        if event is not None:
            if event.char == "\x08":
                text = text[:-1]
            elif repr(event.char)[1] != "\\":
                text += repr(event.char)[1:-1]
        color = self.str2str(text)
        if color == "":
            color = "white"
        self.cv.delete("highlight")
        try:
            self.cv.create_rectangle(EXPAND(280), EXPAND(HEIGHT//2+10),
                                     EXPAND(300), EXPAND(HEIGHT-6),
                                     fill=color, outline="lightgray",
                                     width=2, tag="highlight")
        except tk.TclError:
            self.cv.create_rectangle(EXPAND(280), EXPAND(HEIGHT//2+10),
                                     EXPAND(300), EXPAND(HEIGHT-6),
                                     fill="black", outline="lightgray",
                                     width=2, tag="highlight")

    def show_option(self):
        color = self.ent1.get()
        try:
            color = colorchooser.askcolor(
                color=self.str2str(color), parent=self.p.root)
        except tk.TclError:
            color = colorchooser.askcolor(parent=self.p.root)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())
        self.preview_color()

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur):
        self.save_data()
        try:
            tur.pencolor(self.str2str(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした。', parent=self.p.root)
            self.p.kill_runner()


class FillColor(Widget):
    TEXT = "塗りつぶしの色を①にする"
    TYPE = "normalset"
    VALUES = {"color": "black"}

    def set_data(self, data):
        if "color" in data:
            self.color = data["color"]
        else:
            self.color = self.VALUES["color"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        strvar = tk.StringVar()
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT,
                             validate='all', textvariable=strvar,
                             vcmd=self.preview_color)
        strvar.set(self.color)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.bind("<KeyPress>", self.preview_color)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        self.preview_color()

    def preview_color(self, event=None):
        text = self.ent1.get()
        if event is not None:
            if event.char == "\x08":
                text = text[:-1]
            elif repr(event.char)[1] != "\\":
                text += repr(event.char)[1:-1]
        color = self.str2str(text)
        if color == "":
            color = "white"
        self.cv.delete("highlight")
        try:
            self.cv.create_rectangle(EXPAND(280), EXPAND(HEIGHT//2+10),
                                     EXPAND(300), EXPAND(HEIGHT-6),
                                     fill=color, outline="lightgray",
                                     width=2, tag="highlight")
        except tk.TclError:
            self.cv.create_rectangle(EXPAND(280), EXPAND(HEIGHT//2+10),
                                     EXPAND(300), EXPAND(HEIGHT-6),
                                     fill="black", outline="lightgray",
                                     width=2, tag="highlight")

    def show_option(self):
        color = self.ent1.get()
        try:
            color = colorchooser.askcolor(
                color=self.str2str(color), parent=self.p.root)
        except tk.TclError:
            color = colorchooser.askcolor(parent=self.p.root)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())
        self.preview_color()

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur):
        self.save_data()
        try:
            tur.fillcolor(self.str2str(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした。', parent=self.p.root)
            self.p.kill_runner()


class BGColor(Widget):
    TEXT = "背景色を①に変更する"
    TYPE = "normalset"
    VALUES = {"color": "white"}

    def set_data(self, data):
        if "color" in data:
            self.color = data["color"]
        else:
            self.color = self.VALUES["color"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        strvar = tk.StringVar()
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT,
                             validate='all', textvariable=strvar,
                             vcmd=self.preview_color)
        strvar.set(self.color)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.bind("<KeyPress>", self.preview_color)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        self.preview_color()

    def preview_color(self, event=None):
        text = self.ent1.get()
        if event is not None:
            if event.char == "\x08":
                text = text[:-1]
            elif repr(event.char)[1] != "\\":
                text += repr(event.char)[1:-1]
        color = self.str2str(text)
        if color == "":
            color = "white"
        self.cv.delete("highlight")
        try:
            self.cv.create_rectangle(EXPAND(280), EXPAND(HEIGHT//2+10),
                                     EXPAND(300), EXPAND(HEIGHT-6),
                                     fill=color, outline="lightgray",
                                     width=2, tag="highlight")
        except tk.TclError:
            self.cv.create_rectangle(EXPAND(280), EXPAND(HEIGHT//2+10),
                                     EXPAND(300), EXPAND(HEIGHT-6),
                                     fill="white", outline="lightgray",
                                     width=2, tag="highlight")

    def show_option(self):
        color = self.ent1.get()
        try:
            color = colorchooser.askcolor(
                color=self.str2str(color), parent=self.p.root)
        except tk.TclError:
            color = colorchooser.askcolor(parent=self.p.root)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())
        self.preview_color()

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur):
        self.save_data()
        try:
            tur.getscreen().bgcolor(self.str2str(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.p.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした。', parent=self.p.root)
            self.p.kill_runner()


class GetPenColor(Widget):
    TEXT = "ペンの色を①に代入する"
    TYPE = "normalget"
    VALUES = {"color": "color"}

    def set_data(self, data):
        if "color" in data:
            self.color = data["color"]
        else:
            self.color = self.VALUES["color"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.color)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur):
        self.save_data()
        cval = tur.pencolor()
        self.p.variable_datas[self.color] = (self.p.convert_rgb(cval), "S")


class GetFillColor(Widget):
    TEXT = "塗りつぶしの色を①に代入する"
    TYPE = "normalget"
    VALUES = {"color": "color"}

    def set_data(self, data):
        if "color" in data:
            self.color = data["color"]
        else:
            self.color = self.VALUES["color"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.color)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur):
        self.save_data()
        cval = tur.fillcolor()
        self.p.variable_datas[self.color] = (self.p.convert_rgb(cval), "S")


class GetBGColor(Widget):
    TEXT = "背景色を①に代入する"
    TYPE = "normalget"
    VALUES = {"color": "color"}

    def set_data(self, data):
        if "color" in data:
            self.color = data["color"]
        else:
            self.color = self.VALUES["color"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.color)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur):
        self.save_data()
        cval = tur.getscreen().bgcolor()
        self.p.variable_datas[self.color] = (self.p.convert_rgb(cval), "S")


class BeginFill(Widget):
    TEXT = "塗りつぶしを始める"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        tur.begin_fill()


class EndFill(Widget):
    TEXT = "塗りつぶしを終える"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        tur.end_fill()


class Filling(Widget):
    TEXT = "塗りつぶしするか①に代入する"
    TYPE = "normalget"
    VALUES = {"fill": "fill"}

    def set_data(self, data):
        if "fill" in data:
            self.fill = data["fill"]
        else:
            self.fill = self.VALUES["fill"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"fill": self.fill}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.fill)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.fill = self.ent1.get()

    def run(self, tur):
        self.save_data()
        fill = tur.filling()
        self.p.variable_datas[self.fill] = (fill, "B")


class ShowTurtle(Widget):
    TEXT = "カメを表示モードにする"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        tur.showturtle()


class HideTurtle(Widget):
    TEXT = "カメを非表示モードにする"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        tur.hideturtle()


class IsVisible(Widget):
    TEXT = "表示モードか①に代入する"
    TYPE = "normalget"
    VALUES = {"shown": "shown"}

    def set_data(self, data):
        if "shown" in data:
            self.shown = data["shown"]
        else:
            self.shown = self.VALUES["shown"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"shown": self.shown}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.shown)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.shown = self.ent1.get()

    def run(self, tur):
        self.save_data()
        shown = tur.isvisible()
        self.p.variable_datas[self.shown] = (shown, "B")


class TurtleSize(Widget):
    TEXT = "亀の大きさを①にする"
    TYPE = "normalset"
    VALUES = {"size": "1"}

    def set_data(self, data):
        if "size" in data:
            self.size = data["size"]
        else:
            self.size = self.VALUES["size"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"size": self.size}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.size)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.size = self.ent1.get()

    def run(self, tur):
        self.save_data()
        tur.turtlesize(self.str2int(self.size))


class Write(Widget):
    TEXT = "文字列①を大きさ②で書く"
    TYPE = "normalset"
    VALUES = {
        "text": "Sample",
        "size": "20",
        "move": "False",
        "align": "center",
        "family": "Default",
        "weight": "bold",
        "slant": "roman",
        "sideway": "False"}

    def set_data(self, data):
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
        if "sideway" in data:
            self.sideway = data["sideway"]
        else:
            self.sideway = self.VALUES["sideway"]
        self.set_common(data)

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
        if (str(self.sideway) != self.VALUES["sideway"]) or (more is True):
            data["sideway"] = self.sideway
        self.save_data()
        return self.get_class_data(data, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.text)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+8))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.size)
        self.binder(self.ent2)
        self.ent2.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent2))
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+8))

    def show_option(self):
        # データを取得する
        self.text = self.ent1.get()
        self.size = self.ent2.get()

        # ウィンドウを作成する
        self.win = tk.Toplevel(self.p.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.p.icon)
        self.win.wait_visibility()
        self.win.grab_set()
        frame0 = tk.Frame(self.win)
        frame0.pack(anchor=tk.N, side=tk.TOP)
        font = (FONT_TYPE1, EXPAND(16), "bold")

        # タイトル
        lab0 = tk.Label(frame0, text="Options",
                        font=(FONT_TYPE2, EXPAND(32), "bold"))
        lab0.pack(side=tk.TOP, pady=EXPAND(10))

        # 決定ボタン
        but1 = tk.Button(frame0, text="決定", font=font, width=12,
                         command=self.decide_option)
        but1.pack(side=tk.BOTTOM, pady=(EXPAND(10), EXPAND(20)))

        # 下側のライン
        frame3 = tk.Frame(frame0)
        frame3.pack(anchor=tk.N, side=tk.BOTTOM)

        self.cv1 = tk.Canvas(frame3, width=640, height=160, bg="white")
        self.cv1.pack()

        # 左側のライン
        frame1 = tk.Frame(frame0)
        frame1.pack(anchor=tk.NW, side=tk.LEFT, padx=(EXPAND(60), 0))

        fra1 = tk.Frame(frame1)
        fra1.pack(anchor=tk.W, pady=EXPAND(10))
        lab1 = tk.Label(fra1, text="text    = ", font=font)
        lab1.pack(side=tk.LEFT)
        self.opt1 = tk.Entry(fra1, font=font, width=12, justify=tk.RIGHT)
        self.opt1.insert(tk.END, self.text)
        self.opt1.bind('<Button-3>', lambda e: self.show_popup1(e, self.opt1))
        self.opt1.pack(side=tk.LEFT)

        fra2 = tk.Frame(frame1)
        fra2.pack(anchor=tk.W, pady=EXPAND(10))
        lab2 = tk.Label(fra2, text="move    = ", font=font)
        lab2.pack(side=tk.LEFT)
        self.opt2 = ttk.Combobox(fra2, font=font, width=12)
        self.opt2['values'] = ("True", "False")
        self.opt2.set(self.move)
        self.opt2.pack(side=tk.LEFT)

        fra3 = tk.Frame(frame1)
        fra3.pack(anchor=tk.W, pady=EXPAND(10))
        lab3 = tk.Label(fra3, text="align   = ", font=font)
        lab3.pack(side=tk.LEFT)
        self.opt3 = tk.Entry(fra3, font=font, width=12, justify=tk.RIGHT)
        self.opt3.insert(tk.END, self.align)
        self.opt3.bind('<Button-3>', lambda e: self.show_popup1(e, self.opt3))
        self.opt3.pack(side=tk.LEFT)

        fra4 = tk.Frame(frame1)
        fra4.pack(anchor=tk.W, pady=EXPAND(10))
        lab4 = tk.Label(fra4, text="sideway = ", font=font)
        lab4.pack(side=tk.LEFT)
        self.opt4 = ttk.Combobox(fra4, font=font, width=12)
        self.opt4['values'] = ("True", "False")
        self.opt4.set(self.move)
        self.opt4.bind("<KeyPress>", self.preview_font)
        self.opt4.pack(side=tk.LEFT)

        fra6 = tk.Frame(frame1)
        fra6.pack(anchor=tk.W, pady=EXPAND(10))
        lab6 = tk.Label(fra6, text="weight  = ", font=font)
        lab6.pack(side=tk.LEFT)
        self.opt6 = tk.Entry(fra6, font=font, width=12, justify=tk.RIGHT)
        self.opt6.insert(tk.END, self.weight)
        self.opt6.bind('<Button-3>', lambda e: self.show_popup1(e, self.opt6))
        self.opt6.pack(side=tk.LEFT)

        fra7 = tk.Frame(frame1)
        fra7.pack(anchor=tk.W, pady=EXPAND(10))
        lab7 = tk.Label(fra7, text="slant   = ", font=font)
        lab7.pack(side=tk.LEFT)
        self.opt7 = tk.Entry(fra7, font=font, width=12, justify=tk.RIGHT)
        self.opt7.insert(tk.END, self.slant)
        self.opt7.bind('<Button-3>', lambda e: self.show_popup1(e, self.opt7))
        self.opt7.pack(side=tk.LEFT)

        # 右側のライン
        frame2 = tk.Frame(frame0)
        frame2.pack(anchor=tk.NW, side=tk.LEFT, padx=EXPAND(20))

        fra5 = tk.Frame(frame2)
        fra5.pack(anchor=tk.W, pady=EXPAND(10))
        lab5 = tk.Label(fra5, text="size    = ", font=font)
        lab5.pack(side=tk.LEFT)
        self.opt5 = tk.Entry(fra5, font=font, width=12, justify=tk.RIGHT)
        self.opt5.insert(tk.END, self.size)
        self.opt5.bind('<Button-3>', lambda e: self.show_popup1(e, self.opt5))
        self.opt5.bind("<KeyPress>", self.preview_font)
        self.opt5.pack(side=tk.LEFT)

        fra8 = tk.Frame(frame2)
        fra8.pack(anchor=tk.W, pady=EXPAND(10))
        lab8 = tk.Label(fra8, text="family  = ", font=font)
        lab8.pack(side=tk.LEFT)
        self.opt8 = tk.Entry(fra8, font=font, width=12, justify=tk.RIGHT)
        self.opt8.insert(tk.END, self.family)
        self.opt8.bind('<Button-3>', lambda e: self.show_popup1(e, self.opt8))
        self.opt8.bind("<KeyPress>", self.preview_font)
        self.opt8.pack(side=tk.LEFT)

        fra9 = tk.Frame(frame2)
        fra9.pack(anchor=tk.W, pady=EXPAND(10))
        self.font_list = self.without_atmark()
        var1 = tk.StringVar()
        var1.set(value=self.font_list)
        self.lsb1 = tk.Listbox(fra9, listvariable=var1, height=6,
                               width=24, selectmode='single',
                               font=(FONT_TYPE2, EXPAND(18)))
        self.lsb1.bind('<<ListboxSelect>>', self.append_new_widget)
        self.lsb1.pack(fill='y', side=tk.LEFT)
        scr1 = ttk.Scrollbar(fra9, orient=tk.VERTICAL,
                             command=self.lsb1.yview)
        self.lsb1['yscrollcommand'] = scr1.set
        scr1.pack(fill='y', side=tk.LEFT)

        self.preview_font()
        self.win.resizable(0, 0)

    def without_atmark(self):
        new = []
        for font in tkfont.families():
            if font[0] != "@":
                new.append(font)
        return new

    def preview_font(self, event=None):
        mark = "@" if self.opt4.get() == "True" else ""
        try:
            size = int(self.opt5.get())
        except ValueError:
            size = int(self.VALUES["size"])
        font = (mark + self.opt8.get(), size, self.opt6.get(), self.opt7.get())

        self.cv1.delete("preview")
        self.cv1.create_text(320, 80, text="abc ABC 123\nあいう 甲乙",
                             font=font, tag="preview")

    def append_new_widget(self, event):
        selected = self.lsb1.curselection()
        if len(selected) > 0:
            font = self.font_list[selected[0]]
        else:
            return 1
        self.opt8.delete(0, tk.END)
        self.opt8.insert(0, font)
        self.preview_font()

    def decide_option(self):
        self.text = self.opt1.get()
        self.move = self.opt2.get()
        self.align = self.opt3.get()
        self.sideway = self.opt4.get()
        self.size = self.opt5.get()
        self.weight = self.opt6.get()
        self.slant = self.opt7.get()
        self.family = self.opt8.get()
        self.ent1.delete(0, tk.END)
        self.ent1.insert(0, self.text)
        self.ent2.delete(0, tk.END)
        self.ent2.insert(0, self.size)
        self.win.destroy()
        self.save_data()

    def save_data(self):
        self.text = self.ent1.get()
        self.size = self.ent2.get()

    def run(self, tur):
        self.save_data()
        mark = "@" if self.str2bool(self.sideway) else ""
        tur.write(
            self.str2str(self.text),
            move=self.str2bool(self.move),
            align=self.str2str(self.align),
            font=(
                mark + self.str2str(self.family),
                self.str2int(self.size),
                self.str2str(self.weight),
                self.str2str(self.slant)))


class Bye(Widget):
    TEXT = "プログラムを終了する"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        self.p.kill_runner()


class ExitOnClick(Widget):
    TEXT = "クリックで終了する"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def kill(self, x, y):
        self.p.kill_runner()

    def run(self, tur):
        self.save_data()
        tur.getscreen().onclick(self.kill)


class Bell(Widget):
    TEXT = "システムサウンドを鳴らす"
    TYPE = "normalset"

    def set_data(self, data):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        pass

    def run(self, tur):
        self.save_data()
        self.p.win.bell()


class Sleep(Widget):
    TEXT = "操作を①秒停止する"
    TYPE = "normalset"
    VALUES = {"second": "0"}

    def set_data(self, data):
        if "second" in data:
            self.second = data["second"]
        else:
            self.second = self.VALUES["second"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"second": self.second}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.second)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+8))

    def save_data(self):
        self.second = self.ent1.get()

    def run(self, tur):
        self.save_data()
        time.sleep(self.str2ufloat(self.second))


class Comment(Widget):
    TEXT = "実行されないコメント文"
    TYPE = "comment"
    VALUES = {"comment": "Comment"}

    def set_data(self, data):
        if "comment" in data:
            self.comment = data["comment"]
        else:
            self.comment = self.VALUES["comment"]
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"comment": self.comment}, more)

    def draw(self):
        self.draw_cv()
        self.ent1 = tk.Entry(self.cv, font=(FONT_TYPE1, EXPAND(16), "bold"),
                             fg="#B40404", width=30, justify=tk.LEFT)
        text = self.comment.split("\n")[0]
        self.ent1.insert(tk.END, text)
        self.binder(self.ent1)
        self.ent1.bind('<Button-3>', lambda e: self.show_popup1(e, self.ent1))
        self.ent1.place(x=EXPAND(46), y=EXPAND(HEIGHT//2+5))

    def show_option(self):
        self.save_data()
        self.win = tk.Toplevel(self.p.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.p.icon)
        self.win.wait_visibility()
        self.win.grab_set()
        lab1 = tk.Label(self.win, text="Option",
                        font=(FONT_TYPE2, EXPAND(30), "bold"))
        lab1.pack(padx=EXPAND(20), pady=EXPAND(20))
        font_scr = (FONT_TYPE1, EXPAND(16), "bold")
        self.scr1 = scrolledtext.ScrolledText(self.win, font=font_scr,
                                              width=24, height=6)
        self.scr1.pack(padx=EXPAND(20), pady=EXPAND(0))
        self.scr1.insert("0.0", self.comment)
        but1 = tk.Button(self.win, text="決定", font=FONT, width=10,
                         command=self.decide_option)
        but1.pack(padx=EXPAND(36), pady=EXPAND(20))
        self.win.resizable(0, 0)

    def decide_option(self):
        self.comment = self.scr1.get("0.0", tk.END)[:-1]
        text = self.comment.split("\n")[0]
        self.ent1.delete(0, tk.END)
        self.ent1.insert(0, text)
        self.win.destroy()

    def save_data(self):
        self.comment = "\n".join([self.ent1.get()] +
                                 self.comment.split("\n")[1:])

    def run(self, tur):
        pass


class Undefined(Widget):
    TEXT = "対応していない不明なクラス"
    TYPE = "undefined"

    def set_data(self, data):
        self.data = data
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data(self.data, more)

    def draw(self):
        self.draw_cv()
        text = 'このバージョンでは編集できません'
        lab2 = tk.Label(self.cv, text=text, font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+8))

    def show_option(self):
        self.win = tk.Toplevel(self.p.root)
        self.win.tk.call('wm', 'iconphoto', self.win._w, self.p.icon)
        self.win.wait_visibility()
        self.win.grab_set()
        lab1 = tk.Label(self.win, text="Option",
                        font=(FONT_TYPE2, EXPAND(30), "bold"))
        lab1.pack(padx=20, pady=20)
        data = self.get_class_data(self.data, CONFIG["save_more_info"])
        text = pprint.pformat(data, width=12, indent=2)
        font = (FONT_TYPE1, EXPAND(16), "bold")
        scr1 = scrolledtext.ScrolledText(self.win, font=font,
                                         width=24, height=6)
        scr1.pack(padx=20, pady=(0, 20))
        scr1.insert("0.0", text)
        scr1.config(state="disabled")
        self.win.resizable(0, 0)

    def save_data(self):
        pass

    def run(self, tur):
        pass


def GET_WIDGET_INFO(widget):
    length = 14
    if type(widget) == type:
        name = widget.__name__
    else:
        name = widget.__class__.__name__
    space = " " * (length - len(name))
    info = name + space + widget.TEXT
    return info


# クラスをまとめる
Widgets = (
    VarNumber, VarString, VarBoolean, Title, ScreenSize,
    Forward, Backward, Right, Left, GoTo,
    SetX, SetY, SetHeading, Home, Position,
    ToWards, XCor, YCor, Heading, Distance, Circle,
    Dot, Stamp, Speed, PenDown, PenUp, IsDown, PenSize,
    Color, PenColor, FillColor, BGColor,
    GetPenColor, GetFillColor, GetBGColor,
    BeginFill, EndFill, Filling,
    ShowTurtle, HideTurtle, IsVisible,
    TurtleSize, Write, Bye, ExitOnClick,
    Bell, Sleep, Comment)
Texts = tuple([GET_WIDGET_INFO(c) for c in Widgets])
Names = tuple([c.__name__ for c in Widgets])

# 型チェック用
typeWidget = TypeVar("typeWidget", bound=Widget)


# 実行
if __name__ == "__main__":
    file = sys.argv[1] if len(sys.argv) > 1 else None
    EasyTurtle(file=file)
