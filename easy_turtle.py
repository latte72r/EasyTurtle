
# ©2020-2021 Ryo Fujinami.

import atexit
import glob
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
import webbrowser
from functools import partial
from subprocess import CalledProcessError
from tkinter import colorchooser, filedialog
from tkinter import font as tkFont
from tkinter import messagebox, scrolledtext, simpledialog, ttk
from urllib import request
from urllib.error import URLError

SIZE = 8
HEIGHT = 64
WIDTH = 520


def UPDATE_CONFIG():
    """設定を取得"""
    global CONFIG
    if os.path.exists(CONFIG_FILE):
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


def EXPAND(num):
    """画面を拡大"""
    return int(round(num * WIN_MAG))


SYSTEM = platform.system()
PYVERSION = sys.version_info[:2]

# ROOTウィンドウの作成
ROOT = tk.Tk()

# Pythonバージョンがサポートされていない場合
if PYVERSION < (3, 7):
    ROOT.withdraw()
    ver = str(PYVERSION[0]) + "." + str(PYVERSION[1])
    messagebox.showerror("エラー", "Python" + ver + "には対応していません")
    ROOT.destroy()
    sys.exit()
else:
    from typing import Any, Dict, List, Tuple, Union

# システムがWindowsの場合
if SYSTEM == "Windows":
    import ctypes
    from ctypes import windll

    ctypes.OleDLL('shcore').SetProcessDpiAwareness(1)

    if float(ROOT.tk.call('tk', 'scaling')) > 1.4:
        for name in tkFont.names(ROOT):
            font = tkFont.Font(root=ROOT, name=name, exists=True)
            size = int(font['size'])
            if size < 0:
                font['size'] = round(-0.75*size)

    FONT_TYPE1 = "Courier New"
    FONT_TYPE2 = "Times New Roman"

    CURSOR = "arrow"
    GRAY = "#CDCDCD"
    BGCOLOR = "#F0F0F0"

    os.chdir(os.path.dirname(sys.argv[0]))

    ICON_FILE = os.path.abspath("./Files/win_icon.gif")
    README_FILE = os.path.abspath("./Files/index.html")

    if sys.argv[0] == sys.executable:
        EXECUTABLE = True
    else:
        EXECUTABLE = False

    if not EXECUTABLE:
        CONFIG_FILE = os.path.abspath("./config.json")
        BOOT_FOLDER = os.path.abspath("./boot/")
    else:
        CONFIG_FILE = os.path.join(
            os.environ["ALLUSERSPROFILE"],
            "EasyTurtle/config.json")
        BOOT_FOLDER = os.path.join(
            os.environ["ALLUSERSPROFILE"],
            "EasyTurtle/boot/")
    os.makedirs(BOOT_FOLDER, exist_ok=True)

    DEFAULT_CONFIG = {
        "save_more_info": False,
        "ask_save_new": True,
        "show_warning": True,
        "expand_window": True,
        "user_document": EXECUTABLE,
        "auto_update": True,
        "open_last_file": True,
        "share_copy": False,
        "scroll_center": True,
        "enable_backup": True}

    CONFIG = DEFAULT_CONFIG
    UPDATE_CONFIG()

    user = os.environ['USERPROFILE']
    if os.path.exists(os.path.join(user, "onedrive/ドキュメント/")):
        USER_DOCUMENT = os.path.join(user, "onedrive/ドキュメント/EasyTurtle/")
    else:
        USER_DOCUMENT = os.path.join(user, "Documents/EasyTurtle/")
    samples = os.path.join(USER_DOCUMENT, "Samples")
    os.makedirs(USER_DOCUMENT, exist_ok=True)
    try:
        if not os.path.exists(samples):
            shutil.copytree('./Samples', samples)
    except FileExistsError:
        pass
    ACTIVE_DOCUMENT = os.path.abspath("./")
    os.makedirs(ACTIVE_DOCUMENT, exist_ok=True)

    SYSTEM_WIDTH = windll.user32.GetSystemMetrics(0)
    SYSTEM_HEIGHT = windll.user32.GetSystemMetrics(1)

    if CONFIG["expand_window"]:
        width_mag = SYSTEM_WIDTH / 1280
        height_mag = SYSTEM_HEIGHT / 720
        WIN_MAG = width_mag if width_mag < height_mag else height_mag
    else:
        WIN_MAG = 1

    MIN_WIDTH = EXPAND(1240)
    MIN_HEIGHT = EXPAND(640)

# システムがLinuxの場合
elif SYSTEM == "Linux":

    if float(ROOT.tk.call('tk', 'scaling')) > 1.4:
        for name in tkFont.names(ROOT):
            font = tkFont.Font(root=ROOT, name=name, exists=True)
            size = int(font['size'])
            if size < 0:
                font['size'] = round(-0.75*size)

    fonts = tkFont.families()

    if "FreeMono" in fonts and "FreeSerif" in fonts:
        FONT_TYPE1 = "FreeMono"
        FONT_TYPE2 = "FreeSerif"
    else:
        FONT_TYPE1 = "Courier"
        FONT_TYPE2 = "Times"

    CURSOR = "left_ptr"
    GRAY = "#BDBDBD"
    BGCOLOR = "#D9D9D9"

    os.chdir(os.getcwd())

    ICON_FILE = os.path.abspath("./Files/win_icon.gif")
    README_FILE = os.path.abspath("./Files/index.html")

    if sys.argv[0] == sys.executable:
        EXECUTABLE = True
    else:
        EXECUTABLE = False

    CONFIG_FILE = os.path.abspath("./config.json")
    BOOT_FOLDER = os.path.abspath("./boot/")
    os.makedirs(BOOT_FOLDER, exist_ok=True)

    DEFAULT_CONFIG = {
        "save_more_info": False,
        "ask_save_new": True,
        "show_warning": True,
        "expand_window": True,
        "user_document": EXECUTABLE,
        "auto_update": True,
        "open_last_file": True,
        "share_copy": False,
        "scroll_center": False,
        "enable_backup": True}

    CONFIG = DEFAULT_CONFIG
    UPDATE_CONFIG()

    user = os.environ['USER']
    if os.path.exists(os.path.join("/home", user, "ドキュメント/")):
        USER_DOCUMENT = os.path.join("/home", user, "ドキュメント/EasyTurtle/")
    else:
        USER_DOCUMENT = os.path.join("/home", user, "Documents/EasyTurtle/")
    os.makedirs(USER_DOCUMENT, exist_ok=True)
    samples = os.path.join(USER_DOCUMENT, "Samples")
    try:
        if not os.path.exists(samples):
            shutil.copytree('./Samples', samples)
    except FileExistsError:
        pass
    ACTIVE_DOCUMENT = os.path.abspath("./")
    os.makedirs(ACTIVE_DOCUMENT, exist_ok=True)

    try:
        response = subprocess.check_output("xrandr | fgrep '*'", shell=True)
        metrics = response.decode("utf8").split()[0].split("x")
        SYSTEM_WIDTH = int(metrics[0])
        SYSTEM_HEIGHT = int(metrics[1])

        if CONFIG["expand_window"]:
            width_mag = SYSTEM_WIDTH / 1280
            height_mag = SYSTEM_HEIGHT / 720
            WIN_MAG = width_mag if width_mag < height_mag else height_mag
        else:
            WIN_MAG = 1
    except CalledProcessError:
        messagebox.showwarning("警告", '\
"x11-xserver-utils"がインストールされていません\n\
画面の大きさの調整は無効になります')
        WIN_MAG = 1

    MIN_WIDTH = EXPAND(1240)
    MIN_HEIGHT = EXPAND(640)

# オペレーションシステムがサポートされていない場合
else:
    ROOT.withdraw()
    messagebox.showerror("エラー", f"{SYSTEM}には対応していません")
    ROOT.destroy()
    sys.exit()


FONT = (FONT_TYPE1, EXPAND(12), "bold")

__version__ = (5, 15, 1)


class EasyTurtle:
    def __init__(self, file=None):
        """初期化"""
        # 変数を設定する
        self.tabs: List[IndividualTab] = []
        self.untitled_tabs: Dict[ProgrammingTab, int] = {}
        self.copied_widgets: List[Dict[str, Any]] = []
        self.recent_files: List[str] = []
        self.running_program = False
        self.last_directory = None
        self.killed_program = False
        self.menu: tk.Menu

        # 画面を設定する
        self.setup()

        # アップデート確認をする
        if CONFIG["auto_update"]:
            thread = threading.Thread(target=self.update_starting)
            thread.start()

        # 画面データを開く
        self.open_window_data()

        # ファイルが指定されていれば開く
        if file is not None and os.path.exists(file):
            self.open_file(file)

        else:
            file_open = False

            for file in glob.glob(os.path.join(BOOT_FOLDER, "reboot*.json")):
                file_open = True
                self.open_file(file, boot=True)
                os.remove(file)

            if not file_open and CONFIG["open_last_file"]:
                for file in glob.glob(os.path.join(BOOT_FOLDER, "boot*.json")):
                    file_open = True
                    self.open_file(file, boot=True)
                    os.remove(file)

            if not file_open:
                ProgrammingTab(self)

        atexit.register(self.forced_termination)
        ROOT.mainloop()

    def __repr__(self):
        """コンストラクタの文字列定義"""
        return "EasyTurtle()"

    def save_boot_file(self):
        """起動時のファイルを保存"""
        shutil.rmtree(BOOT_FOLDER)
        os.mkdir(BOOT_FOLDER)

        if CONFIG["open_last_file"]:
            data = {
                "copy": self.copied_widgets if CONFIG["share_copy"] else [],
                "dirname": self.last_directory,
                "recent": self.recent_files}

            with open(os.path.join(BOOT_FOLDER, "windata.json"), "w")as f:
                json.dump(data, f, indent=2)

            for num, tab in enumerate(self.tabs):
                tab.save_file(
                    os.path.join(BOOT_FOLDER, f"boot{num}.json"), boot=True)

    def version_info(self, event=None):
        """設定を編集"""
        self.win = tk.Toplevel(ROOT)
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
        self.win.resizable(False, False)

    def forced_termination(self):
        """強制終了時の動作"""
        if self.killed_program:
            return

        # フォルダーを作成
        shutil.rmtree(BOOT_FOLDER)
        os.mkdir(BOOT_FOLDER)

        data = {
            "copy": self.copied_widgets if CONFIG["share_copy"] else [],
            "dirname": self.last_directory,
            "recent": self.recent_files}

        with open(os.path.join(BOOT_FOLDER, "windata.json"), "w")as f:
            json.dump(data, f, indent=2)

        for num, tab in enumerate(self.tabs):
            tab.forced_save_file(
                os.path.join(BOOT_FOLDER, f"boot{num}.json"))

        # 画面を閉じる
        try:
            ROOT.destroy()
        except tk.TclError:
            pass
        sys.exit()

    def close_window(self, event=None):
        """終了時の定義"""
        if self.running_program:
            return

        # 保存するか確認する
        if not CONFIG["open_last_file"]:
            for tab in self.tabs:
                tab.close_window()

        # ファイルを保存
        self.save_boot_file()

        # 画面を閉じる
        ROOT.destroy()
        self.killed_program = True
        sys.exit()

    def get_currently_selected(self):
        try:
            return self.tabs[self.notebook.get_selected()]
        except (tk.TclError, TypeError):
            return None

    def destroy(self):
        """ウィンドウを削除"""
        ROOT.destroy()

    def delete_menu(self, event=None):
        "メニューを消す"
        if hasattr(self, "menu"):
            self.menu.destroy()

    def open_window_data(self):
        """画面情報の読み込み"""
        # ファイルを開く
        file = os.path.join(BOOT_FOLDER, "windata.json")

        if not os.path.exists(file):
            return

        with open(file, "r")as f:
            data: dict = json.load(f)

        if CONFIG["share_copy"]:
            self.copied_widgets = data.get("copy", [])

        self.last_directory = data.get("dirname")
        self.recent_files = data.get("recent", [])

        with open(file, "w")as f:
            json.dump({"recent": self.recent_files}, f)

    def append_recent_files(self, file):
        """最近のファイルリストに追加"""
        name = os.path.abspath(file).replace("\\", "/")
        if name in self.recent_files:
            self.recent_files.remove(name)
        self.recent_files.insert(0, name)
        self.recent_files = self.recent_files[:10]

    def get_document_path(self):
        if CONFIG["user_document"]:
            return USER_DOCUMENT
        else:
            return ACTIVE_DOCUMENT

    def open_file(self, file=None, boot=False):
        """ファイルを開く動作"""
        # キーバインドから実行された場合
        if isinstance(file, tk.Event):
            file = None
        elif self.running_program:
            return

        # ファイル名を質問する
        if file is None:
            if self.last_directory is not None:
                file = filedialog.askopenfilename(
                    parent=ROOT, initialdir=self.last_directory,
                    filetypes=[("Jsonファイル", "*.json")])
            else:
                file = filedialog.askopenfilename(
                    parent=ROOT, initialdir=self.get_document_path(),
                    filetypes=[("Jsonファイル", "*.json")])

        # ファイルが選択されていなければ終了
        if file == "":
            return

        # ファイルを開く
        if os.path.exists(file):
            with open(file, "r")as f:
                data: dict = json.load(f)
        else:
            messagebox.showerror("エラー", "ファイルが存在しません")
            return 1

        # タブのタイプで分別する
        tabtype = data.get("tabtype", "program")

        # タブを開く
        if tabtype == "program":
            self.open_program(file=file, data=data, boot=boot)
        elif tabtype == "configure":
            self.open_config(data=data)

    def open_config(self, data: dict):
        """設定を開く動作"""
        # タブがすでにあれば選択する
        for tab in self.tabs:
            if isinstance(tab, ConfigureTab):
                tab.select_tab()
                return

        # 新しいタブを作成する
        newtab = ConfigureTab(self, select=data.get("selected", True))

        # データを設定する
        newtab.set_data(data)

    def open_program(self, file, data: dict, boot=False):
        """プログラムを開く動作"""
        # タブがすでにあれば選択する
        for tab in self.tabs:
            if tab.program_name == file:
                tab.select_tab()
                return

        # 新しいタブを作成する
        newtab = ProgrammingTab(self, select=data.get("selected", True))

        try:
            # サイズ警告を初期化
            newtab.warning_ignore = False

            # ウィジェットを作成
            version = tuple(data["version"])
            for d in data["body"]:
                newtab.make_match_class(d, version=version)

            # インデックスを変更
            newtab.index = data.get("index", 0)

            # コピーされたウィジェットを設定
            if not CONFIG["share_copy"]:
                newtab.copied_widgets = data.get("copy", [])

            # バックアップデータを設定
            newtab.backed_up = data.get("backedup", [])
            newtab.canceled_changes = data.get("canceled", [])

            # 追加位置を設定
            addmode = data.get("addmode", 2)
            adjust = data.get("adjust", True)
            position = data.get("position", "")
            newtab.set_radio_value(addmode)
            newtab.chk1.set(adjust)
            newtab.ent1.delete(0, tk.END)
            newtab.ent1.insert(0, position)

            newtab.redraw_widgets()

            # データを上書き
            if CONFIG["ask_save_new"] and version < (4, 11):
                res = messagebox.askyesno("確認", "\
選択されたファイルは古いバージョンです\n\
このバージョン用に保存し直しますか？")
                if res:
                    newtab.save_file(file)

            # 基本データを設定
            newtab.default_data = data.get(
                "default", [d.get_data(more=False) for d in newtab.widgets])

            # 最後にチェックされたウィジェット
            newtab.last_checked = data.get("last", -1)

            # プログラムの名称設定
            newtab.program_name = data.get("name", file)
            newtab.decide_title(data.get("untitled", None))

            # タイトルを更新
            newtab.set_title()

            # ディレクトリ名を保存
            if newtab.program_name is not None:
                self.last_directory = os.path.dirname(newtab.program_name)

            # 最近のファイルリストに追加
            if not boot:
                self.append_recent_files(file)

        except Exception:
            # タブを削除
            newtab.close_tab()

            # エラー表示
            messagebox.showerror("エラー", "変換エラーが発生しました")
            traceback.print_exc()
            return 1

    def get_new_release(self):
        "更新を取得"
        url = "http://github.com/RyoFuji2005/EasyTurtle/releases/latest"
        try:
            with request.urlopen(url) as f:
                text: str = f.geturl()
        except (URLError, AttributeError):
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
        if self.running_program:
            return
        webbrowser.open_new("https://ryofuji2005.github.io/EasyTurtle/")

    def show_offline_document(self, event=None):
        """詳しい情報の表示"""
        if self.running_program:
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
            if isinstance(new_version, str):
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
エラーが発生しました\n\
ネットワーク接続を確認してください")
            elif new_version == "OtherError":
                messagebox.showerror("\
エラーが発生しました\n\
しばらくしてからもう一度お試しください")
            elif new_version <= __version__:
                messagebox.showinfo("アップデート", f"\
バージョン：{old_joined_version}\n\
お使いのバージョンは最新です")
            elif sys.argv[0][-14:] == "EasyTurtle.exe":
                self.ask_update_msi(new_version)
            else:
                self.ask_update_page(new_version)
        except TypeError:
            messagebox.showerror("エラー", "\
正規リリースでないため確認できません")

    def ask_update_msi(self, new_version, start=False):
        """自動アップデートするか尋ねる"""
        new_joined_version = '.'.join([str(n) for n in new_version])
        old_joined_version = '.'.join([str(n) for n in __version__])

        if start:
            self.win2 = tk.Toplevel(ROOT)
        else:
            self.win2 = tk.Toplevel(self.win)

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
        self.win2.resizable(False, False)

    def auto_update_msi(self, new_version):
        """MSI自動アップデート"""
        joined_version = '.'.join([str(n) for n in new_version])

        url = f"\
https://github.com/RyoFuji2005/EasyTurtle/releases/\
download/v{joined_version}/EasyTurtle-{joined_version}-amd64.msi"
        file_name = os.path.join(os.environ['USERPROFILE'], "downloads",
                                 f"EasyTurtle-{joined_version}-amd64.msi")
        try:
            request.urlretrieve(url, file_name)
        except AttributeError:
            messagebox.showerror("\
エラーが発生しました\n\
しばらくしてからもう一度お試しください")
            traceback.print_exc()

        subprocess.Popen(["cmd", "/c", file_name])

        self.close_window()

    def ask_update_page(self, new_version, start=False):
        """アップデートページを表示するか尋ねる"""
        new_joined_version = '.'.join([str(n) for n in new_version])
        old_joined_version = '.'.join([str(n) for n in __version__])

        if start:
            self.win2 = tk.Toplevel(ROOT)
        else:
            self.win2 = tk.Toplevel(self.win)

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
        self.win2.resizable(False, False)

    def new_program(self, event=None):
        """新規プログラム"""
        ProgrammingTab(self)

    def new_window(self, event=None):
        """新規ウィンドウを起動"""
        if sys.argv[0][-14:] == "EasyTurtle.exe":
            command = [sys.argv[0]]
        else:
            command = [sys.executable, sys.argv[0]]
        subprocess.Popen(command)

    def reboot_program(self, event=None):
        """再起動"""
        # データを保存
        shutil.rmtree(BOOT_FOLDER)
        os.mkdir(BOOT_FOLDER)

        data = {
            "copy": self.copied_widgets if CONFIG["share_copy"] else [],
            "dirname": self.last_directory,
            "recent": self.recent_files}

        with open(os.path.join(BOOT_FOLDER, "windata.json"), "w")as f:
            json.dump(data, f, indent=2)

        for num, tab in enumerate(self.tabs):
            tab.save_file(
                os.path.join(BOOT_FOLDER, f"reboot{num}.json"), boot=True)

        # 新規ウィンドウを起動
        if EXECUTABLE:
            command = [sys.argv[0]]
        else:
            command = [sys.executable, sys.argv[0]]
        subprocess.Popen(command)

        # 画面を閉じる
        self.close_window()

    def close_saved_tab(self, event=None):
        """保存済みのタブを閉じる"""
        unchanged: List[IndividualTab] = []
        for tab in self.tabs:
            if not tab.changed_or_not():
                unchanged.append(tab)
        for tab in unchanged:
            tab.close_tab()

    def close_tab(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.close_tab()
        elif isinstance(tab, ConfigureTab):
            tab.close_tab()
        else:
            ROOT.bell()

    def save_program(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.save_program()
        elif isinstance(tab, ConfigureTab):
            tab.decide_config()
        else:
            ROOT.bell()

    def save_program_as(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.save_program_as()
        else:
            ROOT.bell()

    def copy_selected(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.copy_selected()
        else:
            ROOT.bell()

    def paste_widgets(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.paste_widgets()
        else:
            ROOT.bell()

    def cut_selected(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.cut_selected()
        else:
            ROOT.bell()

    def delete_selected(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.delete_selected()
        else:
            ROOT.bell()

    def select_all(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.select_all()
        else:
            ROOT.bell()

    def undo_change(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.undo_change()
        else:
            ROOT.bell()

    def redo_change(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.redo_change()
        else:
            ROOT.bell()

    def enable_selected(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.enable_selected()
        else:
            ROOT.bell()

    def disable_selected(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.disable_selected()
        else:
            ROOT.bell()

    def clear_selected(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.clear_selected()
        else:
            ROOT.bell()

    def goto_line(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.goto_line()
        else:
            ROOT.bell()

    def run_standard_mode(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.run_standard_mode()
        else:
            ROOT.bell()

    def run_fastest_mode(self, event=None):
        tab = self.get_currently_selected()
        if isinstance(tab, ProgrammingTab):
            tab.run_fastest_mode()
        else:
            ROOT.bell()

    def edit_config(self, event=None):
        """設定タブを開く"""
        config_tab = False
        for tab in self.tabs:
            if isinstance(tab, ConfigureTab):
                tab.select_tab()
                config_tab = True
                break
        if not config_tab:
            ConfigureTab(self)

    def show_recent_files(self, event=None):
        # Menubarの作成
        menu_font = (FONT_TYPE1, EXPAND(10), "bold")
        self.menu = tk.Menu(ROOT, tearoff=0, font=menu_font)

        if len(self.recent_files) == 0:
            messagebox.showwarning("警告", "ファイル履歴がありません")
            return

        for file in self.recent_files:
            self.menu.add_command(
                label=file, command=partial(self.open_file, file))

        self.menu.post(EXPAND(100), EXPAND(100))

    def get_shape(self, shape, x1: int, y1: int, size: int = -1):
        """カメの形を決定"""
        for x2, y2 in shape:
            x3 = x2 * size
            y3 = (y2 - 5) * size
            yield x3 - y3 + x1
            yield x3 + y3 + y1

    def setup(self):
        """セットアップ"""
        # 基本ウィンドウを作成
        ROOT.title("EasyTurtle")
        ROOT.geometry(f"{MIN_WIDTH}x{MIN_HEIGHT}")
        ROOT.minsize(MIN_WIDTH, MIN_HEIGHT)
        ROOT.protocol("WM_DELETE_WINDOW", self.close_window)
        ROOT.focus_set()
        self.icon = tk.PhotoImage(file=ICON_FILE)
        ROOT.iconphoto(True, self.icon)
        frame0 = tk.Frame(ROOT)
        frame0.pack()

        # キーをバインド
        ROOT.bind('<Button-1>', self.delete_menu)
        ROOT.bind("<Control-Shift-Key-A>", self.select_all)
        ROOT.bind("<Control-Shift-Key-C>", self.copy_selected)
        ROOT.bind("<Control-Shift-Key-D>", self.disable_selected)
        ROOT.bind("<Control-Shift-Key-E>", self.enable_selected)
        ROOT.bind("<Control-Shift-Key-N>", self.new_window)
        ROOT.bind("<Control-Shift-Key-S>", self.save_program_as)
        ROOT.bind("<Control-Shift-Key-V>", self.paste_widgets)
        ROOT.bind("<Control-Shift-Key-X>", self.cut_selected)
        ROOT.bind("<Control-Shift-Key-Z>", self.redo_change)
        ROOT.bind("<Control-Key-d>", self.delete_selected)
        ROOT.bind("<Control-Key-g>", self.goto_line)
        ROOT.bind("<Control-Key-h>", self.show_recent_files)
        ROOT.bind("<Control-Key-l>", self.clear_selected)
        ROOT.bind("<Control-Key-n>", self.new_program)
        ROOT.bind("<Control-Key-o>", self.open_file)
        ROOT.bind("<Control-Key-q>", self.close_window)
        ROOT.bind("<Control-Key-r>", self.reboot_program)
        ROOT.bind("<Control-Key-s>", self.save_program)
        ROOT.bind("<Control-Key-t>", self.close_saved_tab)
        ROOT.bind("<Control-Key-w>", self.close_tab)
        ROOT.bind("<Control-Key-z>", self.undo_change)
        ROOT.bind("<Control-Key-comma>", self.edit_config)
        ROOT.bind("<Key-F1>", self.show_offline_document)
        ROOT.bind("<Key-F5>", self.run_standard_mode)
        ROOT.bind("<Shift-Key-F5>", self.run_fastest_mode)

        # Menubarの作成
        menu_font = (FONT_TYPE1, EXPAND(10), "bold")
        self.menubar = tk.Menu(ROOT)
        ROOT.config(menu=self.menubar)

        # Notebookの作成
        self.notebook = Notebook(self, ROOT)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # FILEメニューの作成
        filemenu = tk.Menu(self.menubar, tearoff=0, font=menu_font)
        filemenu.add_command(
            label="新しいタブ", accelerator="Ctrl+N", command=self.new_program)
        filemenu.add_command(
            label="新しいウィンドウ", accelerator="Ctrl+Shift+N",
            command=self.new_window)
        filemenu.add_separator()
        filemenu.add_command(
            label="ファイルを開く", accelerator="Ctrl+O", command=self.open_file)
        filemenu.add_command(
            label="最近使用した項目", accelerator="Ctrl+H",
            command=self.show_recent_files)
        filemenu.add_separator()
        filemenu.add_command(
            label="上書き保存", accelerator="Ctrl+S", command=self.save_program)
        filemenu.add_command(
            label="名前を付けて保存", accelerator="Ctrl+Shift+S",
            command=self.save_program_as)
        filemenu.add_separator()
        filemenu.add_command(
            label="現在のタブを閉じる", accelerator="Ctrl+W",
            command=self.close_tab)
        filemenu.add_command(
            label="保存済みのタブを閉じる", accelerator="Ctrl+T",
            command=self.close_saved_tab)
        filemenu.add_separator()
        filemenu.add_command(
            label="再起動", accelerator="Ctrl+R", command=self.reboot_program)
        filemenu.add_command(
            label="終了", accelerator="Ctrl+Q", command=self.close_window)
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

        # カメの形状データ
        shape = (
            (0, 16), (-2, 14), (-1, 10), (-4, 7), (-7, 9), (-9, 8),
            (-6, 5), (-7, 1), (-5, -3), (-8, -6), (-6, -8), (-4, -5),
            (0, -7), (4, -5), (6, -8), (8, -6), (5, -3), (7, 1),
            (6, 5), (9, 8), (7, 9), (4, 7), (1, 10), (2, 14))

        # 背景のキャンバス
        cv = tk.Canvas(ROOT, width=MIN_WIDTH, height=MIN_HEIGHT)
        cv.pack()
        cv.create_text(
            MIN_WIDTH // 2 - EXPAND(80), MIN_HEIGHT // 2 - EXPAND(40),
            text="EasyTurtle", fill="green",
            font=(FONT_TYPE2, EXPAND(80), "bold", "italic"))
        cv.create_polygon(*self.get_shape(
            shape, MIN_WIDTH // 2 + EXPAND(260),
            MIN_HEIGHT // 2 - EXPAND(50), EXPAND(-4)), fill="green")

        # 背景の右下
        frame = tk.Frame(ROOT)
        frame.place(x=MIN_WIDTH - EXPAND(340), y=MIN_HEIGHT - EXPAND(50))
        lab1 = tk.Label(frame, text='©2020-2021 Ryo Fujinami.',
                        font=(FONT_TYPE2, EXPAND(12), "italic"))
        lab1.pack(side=tk.RIGHT, padx=EXPAND(20))
        joined_version = ".".join([str(n) for n in __version__])
        lab2 = tk.Label(frame, text="v"+joined_version,
                        font=(FONT_TYPE1, EXPAND(12), "bold"))
        lab2.pack(side=tk.RIGHT, padx=EXPAND(10))


class ConfigureTab:
    def __init__(self, parent: EasyTurtle, select=True):
        """初期化"""
        self.et = parent

        # 変数を初期化する
        self.program_name = None

        # タブ一覧に追加
        self.et.tabs.append(self)

        # 画面を設定する
        self.setup()

        # タブを選択する
        if select is True:
            self.select_tab()

    def __repr__(self):
        """コンストラクタの文字列定義"""
        return "ConfigureTab()"

    def close_tab(self, ask=True):
        """タブ終了時の定義"""
        # 保存するか確認する
        if self.changed_or_not() and ask:
            res = messagebox.askyesnocancel("確認", "設定を保存しますか？")
            if res is None:
                return
            elif res:
                self.decide_config()

        # タブを削除
        self.et.notebook.forget(self.et.tabs.index(self))

        # リストから削除
        self.et.tabs.remove(self)

        return 0

    def changed_or_not(self, event=None) -> bool:
        """変更されているか確認する"""
        return CONFIG != self.get_current_data()

    def close_window(self, event=None):
        """アプリ終了時の定義"""
        if self.changed_or_not():
            res = messagebox.askyesnocancel("確認", "設定を保存しますか？")
            if res is None:
                return
            elif res:
                self.decide_config()

    def set_title(self, event=None):
        """タイトルを設定する"""
        index = self.et.tabs.index(self)
        if CONFIG == self.get_current_data():
            self.et.notebook.set_title(index, "設定")
        else:
            self.et.notebook.set_title(index, "*設定*")

    def set_data(self, data: dict):
        """データをセット"""
        # データを取得
        config = {}
        for key, value in DEFAULT_CONFIG.items():
            if key in data:
                config[key] = data[key]
            else:
                config[key] = value

        # データを設定
        self.tgb1.set(config["save_more_info"])
        self.tgb2.set(config["ask_save_new"])
        self.tgb3.set(config["show_warning"])
        self.tgb4.set(config["expand_window"])
        self.tgb5.set(config["user_document"])
        self.tgb6.set(config["auto_update"])
        self.tgb7.set(config["open_last_file"])
        self.tgb8.set(config["share_copy"])
        self.tgb9.set(config["scroll_center"])
        self.tgb10.set(config["enable_backup"])

        # タイトルを設定
        self.set_title()

    def initialize(self):
        """データを初期化"""
        # データを設定
        self.tgb1.set(DEFAULT_CONFIG["save_more_info"])
        self.tgb2.set(DEFAULT_CONFIG["ask_save_new"])
        self.tgb3.set(DEFAULT_CONFIG["show_warning"])
        self.tgb4.set(DEFAULT_CONFIG["expand_window"])
        self.tgb5.set(DEFAULT_CONFIG["user_document"])
        self.tgb6.set(DEFAULT_CONFIG["auto_update"])
        self.tgb7.set(DEFAULT_CONFIG["open_last_file"])
        self.tgb8.set(DEFAULT_CONFIG["share_copy"])
        self.tgb9.set(DEFAULT_CONFIG["scroll_center"])
        self.tgb10.set(DEFAULT_CONFIG["enable_backup"])

        # タイトルを設定
        self.set_title()

    def select_tab(self):
        """タブを選択"""
        self.et.notebook.select(self.et.notebook.index(self.mainframe))

    def forced_save_file(self, file):
        # データを決定
        try:
            config = self.get_current_data()
        except tk.TclError:
            config = CONFIG
        data = {
            "tabtype": "configure",
            "selected": self == self.et.get_currently_selected(),
            "version": __version__[:2],
            **config}

        # フォルダを作成
        os.makedirs(os.path.dirname(file), exist_ok=True)

        # データを書き込み
        with open(file, "w")as f:
            json.dump(data, f, indent=2)

    def save_file(self, file, boot=None):
        """ファイルを保存する"""
        # データを決定
        config = self.get_current_data() if boot is True else CONFIG
        data = {
            "tabtype": "configure",
            "selected": self == self.et.get_currently_selected(),
            "version": __version__[:2],
            **config}

        # フォルダを作成
        os.makedirs(os.path.dirname(file), exist_ok=True)

        # データを書き込み
        with open(file, "w")as f:
            json.dump(data, f, indent=2)

    def get_current_data(self):
        """現在の入力データを取得する"""
        return {
            "save_more_info":   self.tgb1.get(),
            "ask_save_new":     self.tgb2.get(),
            "show_warning":     self.tgb3.get(),
            "expand_window":    self.tgb4.get(),
            "user_document":    self.tgb5.get(),
            "auto_update":      self.tgb6.get(),
            "open_last_file":   self.tgb7.get(),
            "share_copy":       self.tgb8.get(),
            "scroll_center":    self.tgb9.get(),
            "enable_backup":    self.tgb10.get()}

    def decide_config(self):
        """設定を決定"""
        global CONFIG
        last_config = {c: CONFIG[c] for c in CONFIG}
        CONFIG = self.get_current_data()

        self.save_file(CONFIG_FILE)
        self.set_title()

        if CONFIG["enable_backup"] != last_config["enable_backup"]:
            for tab in self.et.tabs:
                if isinstance(tab, ProgrammingTab):
                    tab.backed_up = []
                    tab.canceled_changes = []
                    tab.back_up()

        if (CONFIG["expand_window"] != last_config["expand_window"]) or \
           (CONFIG["scroll_center"] != last_config["scroll_center"]):
            res = messagebox.askyesno("確認", "\
変更された設定には再起動後に反映されるものが含まれています\n\
今すぐこのアプリを再起動しますか？")
            if res:
                self.et.reboot_program()

    def setup(self):
        """セットアップ"""
        # 基本ウィンドウを作成
        self.mainframe = tk.Frame(self.et.notebook)
        self.et.notebook.add_tab(self.mainframe)
        frame0 = tk.Frame(self.mainframe)
        frame0.pack()

        font = (FONT_TYPE1, EXPAND(16), "bold")

        # 画面の左側を作成
        frame2 = tk.Frame(frame0)
        frame2.pack(side=tk.LEFT, padx=20, anchor=tk.N)

        # 開始時
        lfm1 = tk.LabelFrame(
            frame2, text="開始時", font=(FONT_TYPE1, EXPAND(28), "bold"))
        lfm1.pack(side=tk.TOP, pady=EXPAND(20))

        tfm6 = tk.Frame(lfm1)
        tfm6.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab6 = tk.Label(tfm6, text="起動時にアップデートを確認する　", font=font)
        lab6.pack(side=tk.LEFT)
        self.tgb6 = ToggleButton(
            tfm6, start=CONFIG["auto_update"], command=self.set_title)
        self.tgb6.pack(side=tk.LEFT)

        tfm7 = tk.Frame(lfm1)
        tfm7.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab7 = tk.Label(tfm7, text="前回開いていたファイルを開く　　", font=font)
        lab7.pack(side=tk.LEFT)
        self.tgb7 = ToggleButton(
            tfm7, start=CONFIG["open_last_file"], command=self.set_title)
        self.tgb7.pack(side=tk.LEFT)

        tfm4 = tk.Frame(lfm1)
        tfm4.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab4 = tk.Label(tfm4, text="画面の大きさをを調整する　　　　", font=font)
        lab4.pack(side=tk.LEFT)
        self.tgb4 = ToggleButton(
            tfm4, start=CONFIG["expand_window"], command=self.set_title)
        self.tgb4.pack(side=tk.LEFT)

        # ファイル
        lfm2 = tk.LabelFrame(
            frame2, text="ファイル", font=(FONT_TYPE1, EXPAND(28), "bold"))
        lfm2.pack(side=tk.TOP, pady=EXPAND(20))

        tfm1 = tk.Frame(lfm2)
        tfm1.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab1 = tk.Label(tfm1, text="より多くの情報を保存する　　　　", font=font)
        lab1.pack(side=tk.LEFT)
        self.tgb1 = ToggleButton(
            tfm1, start=CONFIG["save_more_info"], command=self.set_title)
        self.tgb1.pack(side=tk.LEFT)

        tfm2 = tk.Frame(lfm2)
        tfm2.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab2 = tk.Label(tfm2, text="古いファイルを変更するか確認する", font=font)
        lab2.pack(side=tk.LEFT)
        self.tgb2 = ToggleButton(
            tfm2, start=CONFIG["ask_save_new"], command=self.set_title)
        self.tgb2.pack(side=tk.LEFT)

        tfm5 = tk.Frame(lfm2)
        tfm5.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab5 = tk.Label(tfm5, text="ユーザードキュメントを使用する　", font=font)
        lab5.pack(side=tk.LEFT)
        self.tgb5 = ToggleButton(
            tfm5, start=CONFIG["user_document"], command=self.set_title)
        self.tgb5.pack(side=tk.LEFT)

        tfm10 = tk.Frame(lfm2)
        tfm10.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab10 = tk.Label(tfm10, text="バックアップを有効化する　　　　", font=font)
        lab10.pack(side=tk.LEFT)
        self.tgb10 = ToggleButton(
            tfm10, start=CONFIG["enable_backup"], command=self.set_title)
        self.tgb10.pack(side=tk.LEFT)

        # 画面右側を作成
        frame3 = tk.Frame(frame0)
        frame3.pack(side=tk.RIGHT, padx=10, anchor=tk.N)

        # その他
        lfm3 = tk.LabelFrame(
            frame3, text="その他", font=(FONT_TYPE1, EXPAND(28), "bold"))
        lfm3.pack(side=tk.TOP, pady=EXPAND(20))

        tfm3 = tk.Frame(lfm3)
        tfm3.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab3 = tk.Label(tfm3, text="警告と追加情報を表示する　　　　", font=font)
        lab3.pack(side=tk.LEFT)
        self.tgb3 = ToggleButton(
            tfm3, start=CONFIG["show_warning"], command=self.set_title)
        self.tgb3.pack(side=tk.LEFT)

        tfm8 = tk.Frame(lfm3)
        tfm8.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab8 = tk.Label(tfm8, text="コピーを他のタブと共有する　　　", font=font)
        lab8.pack(side=tk.LEFT)
        self.tgb8 = ToggleButton(
            tfm8, start=CONFIG["share_copy"], command=self.set_title)
        self.tgb8.pack(side=tk.LEFT)

        tfm9 = tk.Frame(lfm3)
        tfm9.pack(side=tk.TOP, anchor=tk.W, padx=EXPAND(10), pady=EXPAND(10))
        lab9 = tk.Label(tfm9, text="中クリックでの移動を有効化する　", font=font)
        lab9.pack(side=tk.LEFT)
        self.tgb9 = ToggleButton(
            tfm9, start=CONFIG["scroll_center"], command=self.set_title)
        self.tgb9.pack(side=tk.LEFT)

        frame4 = tk.Frame(frame3)
        frame4.pack(side=tk.TOP, pady=(EXPAND(80), 0))

        but2 = tk.Button(
            frame4, text="初期化",
            width=20, font=font, command=self.initialize)
        but2.pack(padx=EXPAND(10), pady=(0, EXPAND(20)))

        but1 = tk.Button(
            frame4, text="決定",
            width=20, font=font, command=self.decide_config)
        but1.pack(padx=EXPAND(10), pady=(0, EXPAND(20)))

        lab1 = tk.Label(
            frame4, font=font, fg="red", text="\
※画面サイズなどの一部の変更は\n　次回起動時より有効になります")
        lab1.pack(padx=EXPAND(20), pady=(0, EXPAND(10)))

        # タイトルを設定
        self.set_title()


class ProgrammingTab:
    def __init__(self, parent: EasyTurtle, select=True):
        """初期化"""
        self.et = parent

        # 変数を初期化する
        self.index = 0
        self.last_shown: List[WidgetType] = []
        self.widgets: List[WidgetType] = []
        self.copied_widgets: List[Dict[str, Any]] = []
        self.default_data: List[Dict[str, Any]] = []
        self.backed_up: List[Dict[str, Any]] = []
        self.canceled_changes: List[Dict[str, Any]] = []
        self.radio2int: Dict[RadioButton, int] = {}
        self.int2radio: Dict[int, RadioButton] = {}
        self.warning_ignore = False
        self.program_name = None
        self.center_clicked = False
        self.center_distance = 0
        self.last_checked = -1
        self.decide_title()

        # タブ一覧に追加
        self.et.tabs.append(self)

        # 画面を設定する
        self.setup()

        # タブを選択する
        if select is True:
            self.select_tab()

    def __repr__(self):
        """コンストラクタの文字列定義"""
        return "ProgrammingTab()"

    def close_tab(self, ask=True):
        """タブ終了時の定義"""
        if self.et.running_program:
            return

        # 保存するか確認する
        if self.changed_or_not() and ask:
            res = messagebox.askyesnocancel("確認", "保存しますか？")
            if res is None:
                return 1
            elif res:
                if self.save_program(close=True) == 1:
                    return 1

        # すべて削除
        self.delete_all_widgets()

        # タブを削除
        self.et.notebook.forget(self.et.tabs.index(self))

        # リストから削除
        self.et.tabs.remove(self)
        if self in self.et.untitled_tabs:
            self.et.untitled_tabs.pop(self)

        return 0

    def changed_or_not(self, event=None) -> bool:
        """変更されているか確認する"""
        data = [d.get_data(more=False) for d in self.widgets]
        return self.default_data != data

    def close_window(self, event=None):
        """アプリ終了時の定義"""
        if self.changed_or_not():
            res = messagebox.askyesnocancel("確認", "保存しますか？")
            if res is None:
                return 1
            elif res:
                if self.save_program(close=True) == 1:
                    return 1

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
        if change:
            self.check_length()
            self.set_title()
            self.back_up()

        self.set_header()
        self.chk0.sync_myself()

    def set_header(self):
        self.var1.set(f"選択：{len(self.get_selected())}／合計：{len(self.widgets)}")

    def set_title(self):
        """タイトルを設定する"""
        index = self.et.tabs.index(self)
        if [d.get_data(more=False) for d in self.widgets] == self.default_data:
            self.et.notebook.set_title(index, f"{self.basename}")
        else:
            self.et.notebook.set_title(index, f"*{self.basename}*")

    def decide_title(self, index=None):
        if self.program_name is None:
            if index is not None:
                self.et.untitled_tabs[self] = index
            elif self not in self.et.untitled_tabs:
                index = 1
                while True:
                    if index in self.et.untitled_tabs.values():
                        index += 1
                        continue
                    else:
                        self.et.untitled_tabs[self] = index
                        break
            else:
                index = self.et.untitled_tabs[self]
            self.basename = f"無題 ({index})"
        else:
            if self in self.et.untitled_tabs:
                self.et.untitled_tabs.pop(self)
            self.basename = os.path.basename(self.program_name)

    def select_tab(self):
        """タブを選択"""
        self.et.notebook.select(self.et.notebook.index(self.mainframe))

    def back_up(self):
        """バックアップ"""
        if not CONFIG["enable_backup"]:
            return

        # データを取得
        data = self.get_data()

        # バックアップがなければ追加
        if len(self.backed_up) == 0:
            self.backed_up.append(data)

        # 前回と違ければ追加
        elif self.backed_up[-1]["body"] != data["body"]:
            self.backed_up.append(data)

    def undo_change(self):
        """一回戻る"""
        if self.et.running_program:
            return
        elif not CONFIG["enable_backup"]:
            ROOT.bell()
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
            ROOT.bell()
            return 1

        self.redraw_widgets()

    def redo_change(self):
        """やり直し"""
        if self.et.running_program:
            return
        elif not CONFIG["enable_backup"]:
            ROOT.bell()
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
            ROOT.bell()
            return 1

        self.redraw_widgets()

    def get_data(self):
        """データを取得"""
        if CONFIG["share_copy"]:
            return {"index": self.index,
                    "body": [d.get_data() for d in self.widgets]}
        else:
            return {"index": self.index,
                    "copy": self.copied_widgets,
                    "body": [d.get_data() for d in self.widgets]}

    def set_data(self, data: dict):
        """データをセット"""
        self.delete_all_widgets()
        self.index = data["index"]
        if not CONFIG["share_copy"]:
            self.copied_widgets = data["copy"]
        self.widgets = []
        for d in data["body"]:
            self.make_match_class(d)
        self.index = data["index"]

    def check_length(self):
        """データの大きさをチェック"""
        if (len(self.widgets) > 999) and \
                CONFIG["show_warning"] and not self.warning_ignore:
            messagebox.showwarning(
                "警告", "大量のデータを保持すると正常に動作しなくなる可能性があります")
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

    def append_new_widget(self, event: tk.Event):
        """リストボックス選択時の動作"""
        before_index = self.index

        mode = self.get_radio_value()
        if mode == 1:
            index = 0
        elif mode == 2:
            index = len(self.widgets)
        elif mode == 3:
            index = self.get_add_index()
            if index is None:
                return 1
        else:
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

        if ((mode == 1) or (mode == 3)) and (self.chk1.get()):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, str(index + 2))
            self.set_radio_value(3)

        self.redraw_widgets()

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
        self.et.running_program = False
        if hasattr(self, "win"):
            self.win.destroy()

    def run_standard_mode(self):
        """標準実行"""
        if self.et.running_program:
            return
        self.run_program(fastest=False)

    def run_fastest_mode(self):
        """高速実行"""
        if self.et.running_program:
            return
        self.run_program(fastest=True)

    def run_program(self, fastest=False):
        """実行"""
        # 変数の格納場所
        self.variable_datas = {}

        # プログラムの情報
        self.runner_size: Tuple[int, int] = (600, 600)
        self.killed_runner = False
        self.runner_pendown = True
        self.et.running_program = True
        if fastest:
            self.runner_speed = 0
            self.running_fastest = True
            self.runner_mode = "fastest"
        else:
            self.runner_speed = 3
            self.running_fastest = False
            self.runner_mode = "standard"

        # ウインドウを作成
        self.win = tk.Toplevel(ROOT)
        self.win.protocol("WM_DELETE_WINDOW", self.kill_runner)
        self.win.wait_visibility(self.win)
        self.win.grab_set()
        self.win.focus_set()
        self.win.title("EasyTurtle")

        # キーをバインド
        self.win.bind("<Control-Key-q>", self.kill_runner)

        # Windowsでは透過を有効にする
        if SYSTEM == "Windows":
            self.win.attributes("-transparentcolor", "snow")

        # フレームにキャンバスとスクロールバーを配置
        frame = tk.Frame(self.win)
        frame.pack()
        bary = tk.Scrollbar(frame, orient=tk.VERTICAL)
        bary.pack(side=tk.RIGHT, fill=tk.Y)
        barx = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        barx.pack(side=tk.BOTTOM, fill=tk.X)
        self.scrollbar_width = barx.winfo_reqheight() + 4
        canvas = tk.Canvas(frame, bg="snow")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH)

        # キャンバスとスクロールバーの関連付け
        bary.config(command=canvas.yview)
        canvas.config(yscrollcommand=bary.set)
        barx.config(command=canvas.xview)
        canvas.config(xscrollcommand=barx.set)

        # 中心に移動
        tur = turtle.RawTurtle(canvas)
        tur.shape("turtle")
        tur.getscreen().colormode(255)
        winx = self.runner_size[0] + self.scrollbar_width
        winy = self.runner_size[1] + self.scrollbar_width
        self.win.geometry(f"{winx}x{winy}")
        canvas.config(width=self.runner_size[0],
                      height=self.runner_size[1],
                      scrollregion=(0, 0,
                                    self.runner_size[0],
                                    self.runner_size[1]))
        tur.penup()
        tur.speed(0)
        tur.goto(self.runner_size[0] // 2, self.runner_size[1] // -2)
        tur.pendown()
        tur.speed(self.runner_speed)
        if fastest:
            tur.getscreen().delay(0)

        # それぞれのウィジェットを実行
        for index, widget in enumerate(self.widgets):
            if not self.killed_runner:
                try:
                    if widget.enabled:
                        widget.run(tur)
                except Exception:
                    if self.killed_runner:
                        return
                    else:
                        self.kill_runner()
                        traceback.print_exc()
                        messagebox.showerror("エラー", f'\
line: {index+1}, {widget.__class__.__name__}\n\
エラーが発生しました\n\n{traceback.format_exc()}')
                        return
            else:
                return

    def delete_all_widgets(self):
        """全て削除"""
        widgets = [w for w in self.widgets]
        for d in widgets:
            d.delete(back_up=False)
        self.redraw_widgets(change=False)

    def save_program(self, file=None, close=False):
        """上書き保存"""
        if self.et.running_program:
            return

        # ファイル名を質問する
        if file is None:
            if self.program_name is not None:
                file = self.program_name
            elif self.et.last_directory is not None:
                file = filedialog.asksaveasfilename(
                    parent=ROOT, initialdir=self.et.last_directory,
                    filetypes=[("Jsonファイル", "*.json")])
            else:
                file = filedialog.asksaveasfilename(
                    parent=ROOT, initialdir=self.et.get_document_path(),
                    filetypes=[("Jsonファイル", "*.json")])

        # ファイルが選択されていなければ終了
        if file == "":
            return 1

        # 拡張子をつける
        elif file[-5:] != ".json":
            file += ".json"

        # 保存する
        self.save_file(file)

        # 最近のファイルリストに追加
        if not close:
            self.et.append_recent_files(file)

    def save_program_as(self, file=None, close=False):
        """名前を付けて保存"""
        if self.et.running_program:
            return

        # ファイル名を質問する
        if file is None:
            if self.program_name is not None:
                directory = os.path.dirname(self.program_name)
                name = self.basename
                file = filedialog.asksaveasfilename(
                    parent=ROOT, initialdir=directory,
                    initialfile=name, filetypes=[("Jsonファイル", "*.json")])
            elif self.et.last_directory is not None:
                file = filedialog.asksaveasfilename(
                    parent=ROOT, initialdir=self.et.last_directory,
                    filetypes=[("Jsonファイル", "*.json")])
            else:
                file = filedialog.asksaveasfilename(
                    parent=ROOT, initialdir=self.et.get_document_path(),
                    filetypes=[("Jsonファイル", "*.json")])

        # ファイルが選択されていなければ終了
        if file == "":
            return 1

        # 拡張子をつける
        elif file[-5:] != ".json":
            file += ".json"

        # 保存する
        self.save_file(file)

        # 最近のファイルリストに追加
        if not close:
            self.et.append_recent_files(file)

    def forced_save_file(self, file):
        """ファイルを保存する"""
        # データを取得
        try:
            body = [d.get_data(more=True) for d in self.widgets]
        except tk.TclError:
            body = self.backed_up[-1]["body"] if self.backed_up != [] else []

        # データを決定
        data = {
            "tabtype": "program",
            "version": __version__[:2],
            "copy": [] if CONFIG["share_copy"] else self.copied_widgets,
            "index": self.index,
            "backedup": self.backed_up,
            "canceled": self.canceled_changes,
            "name": self.program_name,
            "default": self.default_data,
            "untitled": (self.et.untitled_tabs[self]
                         if self in self.et.untitled_tabs else None),
            "last": self.last_checked,
            "body": body}

        # フォルダを作成
        os.makedirs(os.path.dirname(file), exist_ok=True)

        # 同じ名前のタブを削除
        for tab in self.et.tabs:
            if tab != self and tab.program_name == file:
                tab.close_tab(ask=False)

        # データを書き込み
        with open(file, "w")as f:
            json.dump(data, f, indent=2)

    def save_file(self, file, boot=False):
        """ファイルを保存する"""
        # データを取得
        body = [d.get_data(more=(boot or CONFIG["save_more_info"]))
                for d in self.widgets]

        # データを決定
        if boot:
            data = {
                "tabtype": "program",
                "version": __version__[:2],
                "copy": [] if CONFIG["share_copy"] else self.copied_widgets,
                "index": self.index,
                "backedup": self.backed_up,
                "canceled": self.canceled_changes,
                "addmode": self.get_radio_value(),
                "adjust": self.chk1.get(),
                "position": self.ent1.get(),
                "name": self.program_name,
                "default": self.default_data,
                "untitled": (self.et.untitled_tabs[self]
                             if self in self.et.untitled_tabs else None),
                "selected": self == self.et.get_currently_selected(),
                "last": self.last_checked,
                "body": body}
        elif CONFIG["save_more_info"]:
            data = {
                "tabtype": "program",
                "version": __version__[:2],
                "copy": [] if CONFIG["share_copy"] else self.copied_widgets,
                "index": self.index,
                "backedup": self.backed_up,
                "canceled": self.canceled_changes,
                "addmode": self.get_radio_value(),
                "adjust": self.chk1.get(),
                "position": self.ent1.get(),
                "last": self.last_checked,
                "body": body}
        else:
            data = {
                "tabtype": "program",
                "version": __version__[:2],
                "body": body}

        # フォルダを作成
        os.makedirs(os.path.dirname(file), exist_ok=True)

        # 同じ名前のタブを削除
        for tab in self.et.tabs:
            if tab != self and tab.program_name == file:
                tab.close_tab(ask=False)

        # データを書き込み
        with open(file, "w")as f:
            json.dump(data, f, indent=2)

        if not boot:
            # プログラムの名称設定
            self.program_name = file
            self.decide_title()

            # 基本データを設定
            self.default_data = [d.get_data(more=False) for d in self.widgets]

        # タイトルを設定
        self.set_title()

        # ディレクトリ名を保存
        if self.program_name is not None:
            self.last_directory = os.path.dirname(self.program_name)

    def make_match_class(self, data, index=-1, version=tuple(__version__[:2])):
        """ウィジェットを作成"""
        name = data["_name"]
        if name in Names:
            Widgets[Names.index(name)](self, data, index)
        else:
            Undefined(self, {"_name": name, **data}, index)

    def paste_widgets(self):
        """ペースト時の動作"""
        if self.et.running_program:
            return

        before_index = self.index

        mode = self.get_radio_value()
        if mode == 1:
            index = 0
        elif mode == 2:
            index = len(self.widgets)
        elif mode == 3:
            index = self.get_add_index()
            if index is None:
                return 1
        else:
            return 1
        next_index = index

        if CONFIG["share_copy"]:
            for d in reversed(self.et.copied_widgets):
                self.make_match_class(d, index=index)
                next_index += 1
        else:
            for d in reversed(self.copied_widgets):
                self.make_match_class(d, index=index)
                next_index += 1

        if (index < before_index) or (index > before_index + SIZE - 1):
            self.index = index
        else:
            self.index = before_index

        if ((mode == 1) or (mode == 3)) and self.chk1.get():
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, str(next_index + 1))
            self.set_radio_value(3)

        self.redraw_widgets()

    def get_selected(self):
        """選ばれたデータ一覧を取得"""
        selected: List[WidgetType] = []
        for d in self.widgets:
            if d.chk1.get():
                selected.append(d)
        return selected

    def select_all(self):
        """すべて選択"""
        if self.et.running_program:
            return
        for d in self.widgets:
            d.chk1.set(True)
        self.back_up()

    def clear_selected(self):
        """選択を解除"""
        if self.et.running_program:
            return
        for d in self.get_selected():
            d.chk1.set(False)
        self.back_up()

    def delete_selected(self):
        """選択されたデータを削除"""
        if self.et.running_program:
            return
        for d in self.get_selected():
            d.delete(back_up=False)
        self.redraw_widgets()

    def copy_selected(self):
        """選択されたデータをコピー"""
        if self.et.running_program:
            return

        copy = []

        if len(self.get_selected()) == 0:
            return

        for d in self.get_selected():
            data = d.get_data()
            data["_check"] = False
            copy.append(data)

        if CONFIG["share_copy"]:
            self.et.copied_widgets = copy
        else:
            self.copied_widgets = copy

    def cut_selected(self):
        """選択されたデータをカット"""
        if self.et.running_program:
            return
        self.copy_selected()
        self.delete_selected()

    def enable_selected(self):
        """選択されたデータを有効化"""
        if self.et.running_program:
            return
        if len(self.get_selected()) == 0:
            return
        for d in self.get_selected():
            d.enable(back_up=False)
        self.back_up()

    def disable_selected(self):
        """選択されたデータを無効化"""
        if self.et.running_program:
            return
        if len(self.get_selected()) == 0:
            return
        for d in self.get_selected():
            d.disable(back_up=False)
        self.back_up()

    def convert_rgb(self, color):
        """RGB値に変換する"""
        if isinstance(color, str):
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
            messagebox.showerror("エラー", '位置が指定されていません')
            return None
        try:
            index = int(text)
        except ValueError:
            messagebox.showerror("エラー", '位置は半角数字のみで指定してください')
            return None
        if index > len(self.widgets) + 1:
            messagebox.showwarning("警告", '\
位置が最大値を超えています\n自動で最後に追加します')
            return len(self.widgets)
        elif index < 1:
            messagebox.showerror("エラー", '位置は正の数で入力してください')
            return None
        else:
            return index - 1

    def goto_line(self):
        """行に移動"""
        text = simpledialog.askstring("行へ移動", '\
数値を入力してください\n\
"-1"でプログラムの最後に移動します')
        if (text == "") or (text is None):
            return 0
        try:
            line = int(text)
        except ValueError:
            messagebox.showerror("エラー", '数値で入力してください')
            return 1
        if line == -1:
            self.index = len(self.widgets) - SIZE
        elif line > len(self.widgets):
            messagebox.showwarning("警告", '\
位置が最大値を超えています\n\
自動で最後に移動します')
            self.index = len(self.widgets) - SIZE
        elif line < 1:
            messagebox.showerror("エラー", '正の数値で入力してください')
            return 1
        elif self.index <= line - 1 < self.index + SIZE:
            pass
        else:
            self.index = line - 1
        self.redraw_widgets(change=False)

    def get_radio_value(self):
        return self.radio2int[self.var2.get()]

    def set_radio_value(self, num):
        self.var2.set(self.int2radio[num])

    def setup(self):
        """セットアップ"""
        # 基本ウィンドウを作成
        self.mainframe = tk.Frame(self.et.notebook)
        self.et.notebook.add_tab(self.mainframe)
        frame0 = tk.Frame(self.mainframe)
        frame0.pack()

        # 画面の左側上段を作成
        frame1 = tk.Frame(frame0)
        frame1.pack(side=tk.LEFT, padx=(10, 0))
        self.cv0 = tk.Canvas(
            frame1, width=EXPAND(WIDTH+20),
            height=EXPAND(32), bg="#E6E6E6")
        self.cv0.pack(side=tk.TOP, fill=tk.X)
        self.chk0 = CheckButton(
            self.cv0, width=EXPAND(16), bg="#E6E6E6", margin=EXPAND(6))
        self.chk0.set_command(self.set_header)
        self.chk0.pack(
            side=tk.LEFT, padx=EXPAND(12), pady=(EXPAND(8), EXPAND(4)))
        self.var1 = tk.StringVar()
        lab1 = tk.Label(
            self.cv0, textvariable=self.var1, bg="#E6E6E6",
            font=(FONT_TYPE1, EXPAND(12), "bold"))
        lab1.pack(side=tk.LEFT, padx=EXPAND(12), pady=(EXPAND(8), EXPAND(4)))

        # 画面の左側下段を作成
        frame2 = tk.Frame(frame1)
        frame2.pack(side=tk.TOP)
        self.cv1 = tk.Canvas(frame2, width=EXPAND(WIDTH),
                             height=EXPAND(HEIGHT*SIZE), bg="#E6E6E6")
        self.cv1.pack(side=tk.LEFT)
        self.cv1.create_rectangle(EXPAND(4), EXPAND(4),
                                  EXPAND(WIDTH), EXPAND(HEIGHT*SIZE),
                                  width=EXPAND(2))
        self.scr2 = ttk.Scrollbar(frame2, orient=tk.VERTICAL,
                                  command=self.scroll_button_clicked)
        self.scr2.pack(fill=tk.Y, side=tk.LEFT)
        frame3 = tk.Frame(frame0)
        frame3.pack(side=tk.RIGHT, padx=EXPAND(10))
        lab0 = tk.Label(self.cv1, text="EasyTurtle",
                        fg="#D8D8D8", bg="#E6E6E6",
                        font=(FONT_TYPE2, EXPAND(56), "bold", "italic"))
        lab0.place(x=EXPAND(80), y=EXPAND(210))

        # 画面右側中段を作成
        lfr1 = tk.LabelFrame(frame3, text="ウィジェットの追加位置",
                             font=(FONT_TYPE1, EXPAND(18), "bold"),
                             labelanchor=tk.N)
        lfr1.pack(side=tk.BOTTOM, pady=EXPAND(30), fill=tk.X)
        self.var2 = RadioVar()
        font = (FONT_TYPE1, EXPAND(16), "bold")
        frm1 = tk.Frame(lfr1)
        frm1.pack(anchor=tk.W, padx=EXPAND(80))
        rad1 = RadioButton(frm1, variable=self.var2, binding=False)
        rad1.pack(anchor=tk.W, side=tk.LEFT)
        lab1 = tk.Label(frm1, text="プログラムの最初", font=font)
        lab1.pack(anchor=tk.W, side=tk.LEFT)
        rad1.bind_instead_master(frm1)
        rad1.bind_instead_child(rad1)
        rad1.bind_instead_child(lab1)
        frm2 = tk.Frame(lfr1)
        frm2.pack(anchor=tk.W, padx=EXPAND(80))
        rad2 = RadioButton(frm2, variable=self.var2, binding=False)
        rad2.pack(anchor=tk.W, side=tk.LEFT)
        lab2 = tk.Label(frm2, text="プログラムの最後", font=font)
        lab2.pack(anchor=tk.W, side=tk.LEFT)
        rad2.bind_instead_master(frm2)
        rad2.bind_instead_child(rad2)
        rad2.bind_instead_child(lab2)
        frm3 = tk.Frame(lfr1)
        frm3.pack(anchor=tk.W, padx=EXPAND(80))
        rad3 = RadioButton(frm3, variable=self.var2, binding=False)
        rad3.pack(anchor=tk.W, side=tk.LEFT)
        lab3 = tk.Label(frm3, text="指定位置：", font=font)
        lab3.pack(anchor=tk.W, side=tk.LEFT)
        self.ent1 = tk.Entry(frm3, font=font, width=8)
        self.ent1.pack(anchor=tk.W, side=tk.LEFT)
        rad3.bind_instead_master(frm3)
        rad3.bind_instead_child(rad3)
        rad3.bind_instead_child(lab3)
        frm0 = tk.Frame(lfr1)
        frm0.pack(anchor=tk.E, padx=EXPAND(60), pady=(0, EXPAND(10)))
        self.chk1 = CheckButton(
            frm0, width=EXPAND(12), bg=BGCOLOR, start=True, binding=False)
        self.chk1.pack(side=tk.LEFT)
        lab1 = tk.Label(frm0, text="位置の自動調整", font=font)
        lab1.pack(side=tk.LEFT)
        self.chk1.bind_instead_master(frm0)
        self.chk1.bind_instead_child(self.chk1)
        self.chk1.bind_instead_child(lab1)
        self.radio2int = {rad1: 1, rad2: 2, rad3: 3}
        self.int2radio = {1: rad1, 2: rad2, 3: rad3}
        self.set_radio_value(2)

        # 画面右側上段を作成
        frame7 = tk.Frame(frame3)
        frame7.pack(side=tk.TOP, pady=(0, EXPAND(10)))
        var1 = tk.StringVar(self.mainframe, value=Texts)
        height = 12 if SYSTEM == "Windows" else 14
        self.lsb1 = tk.Listbox(frame7, listvariable=var1, height=height,
                               width=44, selectmode=tk.SINGLE,
                               bg="#FFEFD7", font=(FONT_TYPE1, EXPAND(18)),
                               selectbackground="#2F4FAF",
                               selectforeground="#FFFFFF")
        self.lsb1.bind('<<ListboxSelect>>', self.append_new_widget)
        self.lsb1.pack(fill=tk.Y, side=tk.LEFT)
        scr1 = ttk.Scrollbar(frame7, orient=tk.VERTICAL,
                             command=self.lsb1.yview)
        self.lsb1['yscrollcommand'] = scr1.set
        scr1.pack(fill=tk.Y, side=tk.RIGHT)

        self.redraw_widgets()


class ToggleButton(tk.Canvas):
    def __init__(
            self, master=None,
            fg="white", bg1=GRAY, bg2="lightgreen",
            radius=EXPAND(10), width=EXPAND(18), height=EXPAND(28),
            start=False, smooth=12, outline=False, margin=EXPAND(4),
            gray=False, binding=True, command=None):

        self.foreground = fg
        self.background1 = bg1
        self.background2 = bg2
        self.radius = radius
        self.width = width
        self.height = height
        self.current = start
        self.smooth = smooth
        self.outline = "silver" if outline else fg
        self.margin = margin
        self.binding = binding
        self.command = command

        self.cvh = (radius*2 if radius*2 > height else height)+self.margin*2
        self.cvw = self.cvh + width

        if master is not None:
            tk.Canvas.__init__(
                self, master, width=self.cvw, height=self.cvh,
                takefocus=self.binding, highlightbackground=BGCOLOR)
        else:
            tk.Canvas.__init__(
                self, width=self.cvw, height=self.cvh,
                takefocus=self.binding, highlightbackground=BGCOLOR)

        if gray:
            self.draw_gray()

        self.redraw_background()

        self.position = self.width if self.current else 0
        self.redraw_slider()

        if self.binding is True:
            self.bind("<KeyRelease-space>", self.slider_press)

            self.tag_bind("background", "<Enter>", self.check_hand_enter)
            self.tag_bind("background", "<Leave>", self.check_hand_leave)
            self.tag_bind("background", "<ButtonPress-1>", self.slider_press)

            self.tag_bind("slider", "<Enter>", self.check_hand_enter)
            self.tag_bind("slider", "<Leave>", self.check_hand_leave)
            self.tag_bind("slider", "<ButtonPress-1>", self.slider_press)

    def bind_instead_master(self, widget: tk.Widget):
        widget.bind("<KeyRelease-space>", self.slider_press)
        widget.bind("<ButtonPress-1>", self.slider_press)
        widget.configure(
            cursor="hand2", takefocus=True,
            highlightthickness=2,
            highlightbackground=self.color1)

    def bind_instead_child(self, widget: tk.Widget):
        widget.bind("<ButtonPress-1>", self.slider_press)

    def draw_gray(self):
        self.delete("gray")
        background = "silver"
        width = 2
        if self.radius*2 >= self.height:
            self.create_rectangle(
                self.radius+self.margin,
                self.radius+self.margin-self.height//2-width,
                self.radius+self.width+self.margin,
                self.radius+self.margin+self.height//2+width+1,
                width=0, fill=background, tag="gray")

            self.create_arc(
                self.radius-self.height//2+self.margin-width,
                self.radius-self.height//2+self.margin-width,
                self.radius+self.height//2+self.margin+width,
                self.radius+self.height//2+self.margin+width,
                outline=background, fill=background,
                start=90, extent=180, tag="gray")

            self.create_arc(
                self.radius-self.height//2+self.margin+self.width-width,
                self.radius-self.height//2+self.margin-width,
                self.radius+self.height//2+self.margin+self.width+width,
                self.radius+self.height//2+self.margin+width,
                outline=background, fill=background,
                start=-90, extent=180, tag="gray")
        else:
            self.create_rectangle(
                self.height//2+self.margin, self.margin-width,
                self.height//2+self.width+self.margin,
                self.height+self.margin+width+1,
                width=0, fill="gray", tag="gray")

            self.create_arc(
                self.margin-width, self.margin-width,
                self.height+self.margin+width, self.height+self.margin+width,
                outline="gray", fill="gray",
                start=90, extent=180, tag="gray")

            self.create_arc(
                self.margin+self.width-width, self.margin-width,
                self.height+self.margin+self.width+width,
                self.height+self.margin+width,
                outline="gray", fill="gray",
                start=-90, extent=180, tag="gray")

    def redraw_background(self):
        self.delete("background")
        background = self.background2 if self.current else self.background1
        if self.radius*2 > self.height:
            self.create_rectangle(
                self.radius+self.margin,
                self.radius+self.margin-self.height//2,
                self.radius+self.width+self.margin,
                self.radius+self.margin+self.height//2+1,
                width=0, fill=background, tag="background")

            self.create_arc(
                self.radius-self.height//2+self.margin,
                self.radius-self.height//2+self.margin,
                self.radius+self.height//2+self.margin,
                self.radius+self.height//2+self.margin,
                outline=background, fill=background,
                start=90, extent=180, tag="background")

            self.create_arc(
                self.radius-self.height//2+self.margin+self.width,
                self.radius-self.height//2+self.margin,
                self.radius+self.height//2+self.margin+self.width,
                self.radius+self.height//2+self.margin,
                outline=background, fill=background,
                start=-90, extent=180, tag="background")
        else:
            self.create_rectangle(
                self.height//2+self.margin, self.margin,
                self.height//2+self.width+self.margin,
                self.height+self.margin+1,
                width=0, fill=background, tag="background")

            self.create_arc(
                self.margin, self.margin,
                self.height+self.margin, self.height+self.margin,
                outline=background, fill=background,
                start=90, extent=180, tag="background")

            self.create_arc(
                self.margin+self.width, self.margin,
                self.height+self.margin+self.width, self.height+self.margin,
                outline=background, fill=background,
                start=-90, extent=180, tag="background")

    def redraw_slider(self):
        self.delete("slider")
        if self.radius*2 > self.height:
            self.slider = self.create_oval(
                self.margin+self.position, self.margin,
                self.radius*2+self.margin+self.position,
                self.radius*2+self.margin,
                fill=self.foreground, tag="slider",
                outline=self.outline, width=2)
        else:
            self.slider = self.create_oval(
                self.height//2-self.radius+self.margin+self.position,
                self.height//2-self.radius+self.margin,
                self.height//2+self.radius+self.margin+self.position,
                self.height//2+self.radius+self.margin,
                fill=self.foreground, tag="slider",
                outline=self.outline, width=2)

    def slider_press(self, event):
        self.frompos = self.width if self.current else 0
        self.current = not self.current
        self.topos = self.width if self.current else 0
        self.redraw_background()
        self.move = 0
        self.move_slider()
        if self.command is not None:
            self.command()

    def move_slider(self):
        if self.move >= self.smooth:
            return
        self.move += 1
        self.position = (self.frompos * (
            self.smooth - self.move) + self.topos * self.move) // self.smooth
        self.redraw_slider()
        self.after(10, self.move_slider)

    def check_hand_enter(self, event):
        self.config(cursor="hand2")

    def check_hand_leave(self, event):
        self.config(cursor="")

    def set_command(self, command):
        self.command = command

    def set(self, value):
        if value == self.current:
            return
        self.frompos = self.width if self.current else 0
        self.current = value
        self.topos = self.width if self.current else 0
        self.redraw_background()
        self.move = 0
        self.move_slider()
        if self.command is not None:
            self.command()

    def get(self):
        return self.current


class CheckButton(tk.Canvas):
    UNCHECKED = 0
    CHECKED = 1
    INDETERMINATE = 2

    def __init__(
            self, master=None,
            bg=BGCOLOR, width=EXPAND(24), start=False,
            margin=EXPAND(4), binding=True, command=None):

        self.color1 = "white"
        self.color2 = bg
        self.width = width
        self.current = int(start)
        self.margin = margin
        self.binding = binding
        self.command = command

        self.parent_widget: CheckButton = None
        self.children_widget: CheckButton = []
        self.change_command = None

        if master is not None:
            tk.Canvas.__init__(
                self, master, width=width+self.margin*2,
                height=width+self.margin*2, takefocus=self.binding,
                bg=bg, highlightbackground=bg)
        else:
            tk.Canvas.__init__(
                self, width=width+self.margin*2,
                height=width+self.margin*2, takefocus=self.binding,
                bg=bg, highlightbackground=bg)

        # Base64のDataURI
        self.image = tk.PhotoImage(
            data="""
            iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAA
            Af5JREFUeF7tmlGywiAMRXVnLK1LY2c6dMSptUASbiBQ/HnOmxpyDoFi6vNx89fz
            5vyPJWBVwM0NrCVw8wKYexP03r/CBDvnkpU+7RII8N77vcCdc0kJUwqI8Nu27QLC
            35SE6QSc4eMel5IwlYAUfE7CNAJK8CkJUwigwl9JGF4AF/68KQ4toBY+yBhWAAJ+
            WAEo+CEFIOGHE4CGH0qABvwwArTghxCgCW9egDa8aQEt4M0KaAVvUkBL+KIASk8N
            2VRtDZ8VQO2poQT0gE8K4PTUEAJ6wV8K4PbUagX0hP8TUEom112ViCiNdxUTncO3
            H0BNBpUAdbyjBNTYx5i7AG4ytYlwxyv19iXVFz8jElCTkCX4nz2gRWItxuBWw09P
            UDNBzdhc6L894PgPjUQ1YtZAZwVINsXcnmAZnnQUjk9YKcbPdwfr8KQvQ+EZu0TC
            p5JEn839oIEyEZxrig9GpLMYlwU1mdqzBXWc83VFAdI9gZNQL/jiEqi9O1Ak9IRn
            CdCohN7wbAFICRbgRQIQEqzAiwXUSLAEXyVAIsEafLUAjgSL8BABVAnhRNnyhEe5
            BcME5CRYnfkoiHQSpNps3U6n5pW7DirgWAnhfe5HyojkETHgAqKEjwCV+AhwlSWA
            TKxVLPMzpC1iCdA2bD3+qgDrM6Sd36oAbcPW49++At5aYFBfS24sggAAAABJRU5E
            rkJggg=="""
        ).zoom(self.width).subsample(72)
        self.minus = tk.PhotoImage(
            data="""
            iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAA
            AOZJREFUeF7tmEEOgzAMBM3P/DQ/LT+j4tBWFSRIveEZrlyym5k4yhbwb4PnDwuQ
            AHgDKgAHwENQBVQA3oAKwAFwCqiACsAbUAE4AE4BFVABeAMqAAfAKbBUoKr2qno0
            JMf6q2qac/qjQ/j3zq1KuCygU/i7Ek4FjDH2zHw09rPFjzEiM38ynwrouPsrCq4U
            2Ftu/zfUmoCIYBeAVwB/CB6qdKRgdhfwIrQ68TuQ8PdVuPko/MTzPYCy07OcEiAB
            8AZUAA6Aj6IqoALwBlQADoBTQAVUAN6ACsABcAqogArAG1ABOADxAn6KSEGt6UZn
            AAAAAElFTkSuQmCC"""
        ).zoom(self.width).subsample(72)

        self.redraw_check()

        self.bind("<KeyRelease-space>", self.check_press)

        if self.binding is True:
            self.bind("<KeyRelease-space>", self.check_press)
            self.tag_bind("check", "<Enter>", self.check_hand_enter)
            self.tag_bind("check", "<Leave>", self.check_hand_leave)
            self.tag_bind("check", "<ButtonPress-1>", self.check_press)

    def bind_instead_master(self, widget: tk.Widget):
        widget.bind("<KeyRelease-space>", self.check_press)
        widget.bind("<ButtonPress-1>", self.check_press)
        widget.configure(
            cursor="hand2", takefocus=True,
            highlightthickness=2,
            highlightbackground=self.color2)

    def bind_instead_child(self, widget: tk.Widget):
        widget.bind("<ButtonPress-1>", self.check_press)

    def redraw_check(self):
        self.delete("check")
        width = int(round(self.width / 12))
        if self.current == self.CHECKED:
            self.create_rectangle(
                self.margin, self.margin,
                self.width+self.margin, self.width+self.margin,
                width=width, fill=self.color1, tag="check")
            self.create_image(
                self.width//2+self.margin, self.width//2+self.margin,
                image=self.image, tag="check")
        elif self.current == self.INDETERMINATE:
            self.create_rectangle(
                self.margin, self.margin,
                self.width+self.margin, self.width+self.margin,
                width=width, fill=self.color1, tag="check")
            self.create_image(
                self.width//2+self.margin, self.width//2+self.margin,
                image=self.minus, tag="check")
        else:
            self.create_rectangle(
                self.margin, self.margin,
                self.width+self.margin, self.width+self.margin,
                width=width, fill=self.color1, tag="check")

    def check_press(self, event):
        self.current = int(not bool(self.current))
        self.redraw_check()
        self.sync_children()
        self.sync_parent()
        if self.change_command is not None:
            self.change_command()
        if self.command is not None:
            self.command()

    def check_hand_enter(self, event):
        self.config(cursor="hand2")

    def check_hand_leave(self, event):
        self.config(cursor="")

    def set_command(self, command):
        self.command = command

    def set_change_command(self, command):
        self.change_command = command

    def set_parent(self, widget):
        self.parent_widget = widget
        self.parent_widget.sync_myself()

    def set_children(self, widget):
        if widget not in self.children_widget:
            self.children_widget.append(widget)
            self.sync_myself()

    def forget_children(self, widget):
        if widget in self.children_widget:
            self.children_widget.remove(widget)
            self.sync_myself()

    def sync_children(self):
        if self.current == self.UNCHECKED:
            for child in self.children_widget:
                child.set(self.UNCHECKED)
        elif self.current == self.CHECKED:
            for child in self.children_widget:
                child.set(self.CHECKED)

    def sync_parent(self):
        if self.parent_widget is not None:
            self.parent_widget.sync_myself()

    def sync_myself(self):
        unchecked = False
        checked = False
        for child in self.children_widget:
            data = child.get_state()
            if data == self.UNCHECKED:
                unchecked = True
            elif (data == self.CHECKED) or (data == self.INDETERMINATE):
                checked = True
        if checked and not unchecked:
            self.set(self.CHECKED)
        elif checked and unchecked:
            self.set(self.INDETERMINATE)
        else:
            self.set(self.UNCHECKED)

    def set(self, value):
        if int(value) == self.current:
            return
        self.current = int(value)
        self.redraw_check()
        self.sync_children()
        self.sync_parent()
        if self.change_command is not None:
            self.change_command()

    def get(self):
        return bool(self.current)

    def get_state(self):
        return self.current


class RadioButton(tk.Canvas):
    def __init__(
            self, master=None,
            bg=BGCOLOR, width=EXPAND(8), variable=None,
            radius=EXPAND(2), line=EXPAND(1), margin=EXPAND(4), binding=True):

        self.color1 = bg
        self.color2 = "black"
        self.color3 = "white"
        self.width = width
        self.radius = radius
        self.line = line
        self.current = False
        self.variable: RadioVar = variable
        self.margin = margin
        self.binding = binding
        self.button_widget: RadioButton = []

        self.variable.widgets.append(self)

        if master is not None:
            tk.Canvas.__init__(
                self, master, width=width+self.margin*2,
                height=width+self.margin*2, takefocus=self.binding,
                bg=self.color1, highlightbackground=self.color1)
        else:
            tk.Canvas.__init__(
                self, width=width+self.margin*2,
                height=width+self.margin*2, takefocus=self.binding,
                bg=self.color1, highlightbackground=self.color1)

        self.redraw_check()

        if self.binding is True:
            self.bind("<KeyRelease-space>", self.check_press)
            self.tag_bind("radio", "<Enter>", self.check_hand_enter)
            self.tag_bind("radio", "<Leave>", self.check_hand_leave)
            self.tag_bind("radio", "<ButtonPress-1>", self.check_press)

    def bind_instead_master(self, widget: tk.Widget):
        widget.bind("<KeyRelease-space>", self.check_press)
        widget.bind("<ButtonPress-1>", self.check_press)
        widget.configure(
            cursor="hand2", takefocus=True,
            highlightthickness=2,
            highlightbackground=self.color1)

    def bind_instead_child(self, widget: tk.Widget):
        widget.bind("<ButtonPress-1>", self.check_press)

    def redraw_check(self):
        self.delete("radio")
        if self.current:
            self.create_oval(
                self.margin, self.margin,
                self.width+self.margin, self.width+self.margin,
                width=self.line, fill=self.color3, tag="radio")
            self.create_oval(
                self.margin+self.width//2-self.radius,
                self.margin+self.width//2-self.radius,
                self.margin+self.width//2+self.radius,
                self.margin+self.width//2+self.radius,
                fill=self.color2, tag="radio")
        else:
            self.create_oval(
                self.margin, self.margin,
                self.width+self.margin, self.width+self.margin,
                width=self.line, fill=self.color3, tag="radio")

    def check_press(self, event):
        self.variable.set(self)

    def check_hand_enter(self, event):
        self.config(cursor="hand2")

    def check_hand_leave(self, event):
        self.config(cursor="")

    def set_variable(self, widget):
        self.variable = widget
        self.sync_variable()

    def forget_variable(self):
        self.variable = None

    def set(self, value):
        if value == self.current:
            return
        self.current = value
        self.redraw_check()
        if self.variable is not None:
            self.variable.current = self


class RadioVar:
    def __init__(self):
        self.widgets: List[RadioButton] = []
        self.current: RadioButton = None
        self.command = None

    def set(self, widget: RadioButton):
        if widget not in self.widgets:
            return
        for w in self.widgets:
            w.set(False)
        widget.set(True)
        self.current = widget
        if self.command is not None:
            self.command()

    def get(self):
        return self.current

    def set_command(self, command):
        self.command = command


class Notebook(tk.Canvas):
    def __init__(
            self, parent: EasyTurtle, master=None,
            height=EXPAND(32), margin=EXPAND(8),
            font=(FONT_TYPE1, EXPAND(12), "bold")):

        self.et = parent

        self.height = height
        self.margin = margin
        self.font = tkFont.Font(font=font)

        self.selected = None
        self.adjust = EXPAND(2)
        self.drag_point = 0
        self.image = tk.PhotoImage(width=1, height=1)

        self.tabs: dict[tk.Canvas, tk.Frame] = {}

        if master is not None:
            tk.Canvas.__init__(self, master, height=height)
        else:
            tk.Canvas.__init__(self, height=height)

        self.frame = tk.Frame(self, takefocus=True, height=height)
        self.frame.pack(side=tk.TOP, anchor=tk.NW)

        self.frame.bind("<Left>", self.go_left)
        self.frame.bind("<Right>", self.go_right)

        self.create_plus()

    def create_plus(self):
        pixel = self.font.measure("+") + self.margin
        self.plus = tk.Button(
            self.frame, text="+", width=pixel, height=pixel, image=self.image,
            fg="gray", bg="#E6E6E6", font=self.font, cursor="hand2",
            compound=tk.CENTER, command=self.et.new_program)

    def add_tab(self, frame):
        width = self.font.measure("×") + self.margin * 3
        cv = tk.Canvas(
            self.frame, height=self.height, width=width, bg=GRAY,
            cursor="hand2", relief=tk.RAISED, bd=2)
        cv.title = ""
        cv.bind("<Button-1>", lambda e: self.clicked_left(cv))
        cv.bind("<ButtonRelease-1>", lambda e: self.release_left(cv))
        cv.bind(
            "<B1-Motion>", lambda e: self.drag_move(e, cv, self.drag_point))
        cv.tag_bind(
            "close", "<Button-1>", lambda e: self.clicked_close(cv))
        self.tabs[cv] = frame
        self.redraw()

    def drag_move(self, event: tk.Event, cv, point):
        if self.drag_point != point:
            return
        self.drag_point += 1
        width = self.font.measure(cv.title+"×")+self.margin*3
        index = tuple(self.tabs.keys()).index(cv)
        if index != 0:
            pre = tuple(self.tabs.keys())[index - 1]
            pwidth = self.font.measure(pre.title+"×")+self.margin*3
            if -pwidth > event.x:
                self.move_to(index, index - 1)
        if index != len(self.tabs.keys()) - 1:
            nex = tuple(self.tabs.keys())[index + 1]
            nwidth = self.font.measure(nex.title+"×")+self.margin*3
            if width + nwidth < event.x:
                self.move_to(index, index + 1)
        self.redraw()

    def move_to(self, from_index, to_index):
        keys = list(self.tabs.keys())
        values = list(self.tabs.values())
        key = keys.pop(from_index)
        value = values.pop(from_index)
        tab = self.et.tabs.pop(from_index)
        if from_index < to_index:
            keys.insert(to_index, key)
            values.insert(to_index, value)
            self.et.tabs.insert(to_index, tab)
        else:
            keys.insert(to_index, key)
            values.insert(to_index, value)
            self.et.tabs.insert(to_index, tab)
        self.tabs = {k: v for k, v in zip(keys, values)}

    def go_left(self, event):
        index = self.get_selected()
        if index != 0:
            self.select(index-1)

    def go_right(self, event):
        index = self.get_selected()
        if index != len(self.tabs) - 1:
            self.select(index+1)

    def clicked_left(self, cv):
        if SYSTEM == "Windows":
            cv.config(cursor="sb_h_double_arrow")
            cv.config(relief=tk.SUNKEN)
        index = tuple(self.tabs.keys()).index(cv)
        self.select(index)

    def release_left(self, cv):
        cv.config(cursor="hand2")
        cv.config(relief=tk.RAISED)

    def clicked_close(self, cv):
        index = tuple(self.tabs.keys()).index(cv)
        self.et.tabs[index].close_tab()

    def select(self, index):
        if len(self.tabs.keys()) > index:
            self.selected = tuple(self.tabs.keys())[index]
        self.redraw()

    def index(self, frame):
        return tuple(self.tabs.values()).index(frame)

    def redraw(self):
        index = self.get_selected()
        for cv in self.tabs.keys():
            cv.pack_forget()
        for num, cv in enumerate(self.tabs.keys()):
            if num == index:
                cv.config(bg="white")
                self.tabs[cv].pack(side=tk.TOP)
            else:
                cv.config(bg=GRAY)
                self.tabs[cv].pack_forget()
            cv.pack(side=tk.LEFT)
            self.draw_close(num)
        self.plus.pack_forget()
        self.plus.pack(side=tk.LEFT, anchor=tk.CENTER)

    def get_selected(self):
        if self.selected is None:
            return None
        else:
            return tuple(self.tabs.keys()).index(self.selected)

    def forget(self, index):
        cv = tuple(self.tabs.keys())[index]
        if len(self.tabs) == 1:
            self.selected = None
        elif self.get_selected() == index:
            if index == 0:
                self.select(1)
            else:
                self.select(index-1)
        self.tabs[cv].pack_forget()
        cv.destroy()
        self.tabs.pop(cv)

    def draw_close(self, index):
        cv = tuple(self.tabs.keys())[index]
        cv.delete("close")
        twidth = self.font.measure(cv.title)
        cwidth = self.font.measure("×")
        bg = "white" if index == self.get_selected() else GRAY
        cv.create_rectangle(
            twidth+int(self.margin*1.5)+cwidth//2,
            (self.height-self.margin)//2+self.adjust,
            twidth+cwidth+int(self.margin*2.5)-cwidth//2,
            (self.height+self.margin)//2+self.adjust,
            fill=bg, outline=bg, tag="close")
        cv.create_text(
            twidth+self.margin*2+cwidth//2, self.height//2+self.adjust,
            text="×", font=self.font, fill="red", tag="close")

    def set_title(self, index, title):
        twidth = self.font.measure(title)
        cwidth = self.font.measure("×")
        cv = tuple(self.tabs.keys())[index]
        cv.title = title
        cv.config(width=twidth+cwidth+self.margin*3)
        cv.delete("title")
        cv.create_text(
            twidth//2+self.margin, self.height//2+self.adjust,
            text=title, font=self.font, tag="title")
        self.draw_close(index)


class Widget:
    def __init__(self, parent: ProgrammingTab, data={}, index=-1):
        """初期化"""
        self.tab = parent
        self.et = self.tab.et
        self.info = GET_WIDGET_INFO(self)
        self.pressed_x = self.pressed_y = 0
        self.item_id = -1
        self.mouse_position = 0

        self.TEXT: str
        self.TYPE: str
        self.OPTION: bool

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

        tops = len(self.tab.widgets)
        self.tab.index = 0 if tops < SIZE else tops
        if index == -1:
            self.tab.widgets.append(self)
        else:
            self.tab.widgets.insert(index, self)

        self.set_data(data)

        self.draw()

    def __repr__(self):
        """コンストラクタの文字列定義"""
        data = self.get_data()
        return f"{data['_name']}(self, data={data})"

    def set_data(self, data: dict):
        """データの設定（サブクラスで宣言される関数）"""

    def get_data(self, more=True) -> Dict[str, Any]:
        """データの取得（サブクラスで宣言される関数）"""

    def draw(self):
        """ウィジェットの絵画（サブクラスで宣言される関数）"""

    def save_data(self):
        """データの保存（サブクラスで宣言される関数）"""

    def show_option(self):
        """オプションの表示（サブクラスで宣言される関数）"""

    def run(self, tur: turtle.RawTurtle):
        """データの実行（サブクラスで宣言される関数）"""

    def binder(self, widget: tk.Widget):
        """ボタンのバインド"""
        # 右クリックのバインド
        if isinstance(widget, tk.Entry):
            widget.bind('<Button-3>', lambda e: self.show_popup1(e, widget))
        else:
            widget.bind('<Button-3>', self.show_popup2)
            widget.bind("<Button-1>", self.click_left)
            widget.bind("<ButtonRelease-1>", self.release_left)

        # ドラッグのバインド
        widget.bind("<B1-Motion>", self.drag_move)

        # 中スクロールのバインド
        if CONFIG["scroll_center"]:
            widget.bind("<Button-2>", self.click_center)
            widget.bind("<ButtonRelease-2>", self.release_center)
            widget.bind("<B2-Motion>", self.scroll_center)

        # スクロールのバインド
        if SYSTEM == "Windows":
            widget.bind("<MouseWheel>", self.scroll_on_windows)
        elif SYSTEM == "Linux":
            widget.bind("<Button-4>", self.scroll_on_linux)
            widget.bind("<Button-5>", self.scroll_on_linux)

    def draw_cv(self):
        """キャンバスを描く"""
        # キャンバスを表示
        self.cv = tk.Canvas(self.tab.cv1, width=EXPAND(WIDTH),
                            height=EXPAND(HEIGHT), bg=self.background)
        self.binder(self.cv)

        # キャンバスの枠を表示
        self.cv.create_rectangle(EXPAND(42), EXPAND(4),
                                 EXPAND(WIDTH), EXPAND(HEIGHT//2+2),
                                 width=EXPAND(2))
        self.cv.create_rectangle(EXPAND(42), EXPAND(HEIGHT//2+2),
                                 EXPAND(WIDTH), EXPAND(HEIGHT-2),
                                 width=EXPAND(2))
        self.cv.create_rectangle(EXPAND(4), EXPAND(4),
                                 EXPAND(42), EXPAND(HEIGHT-2), width=EXPAND(2))

        # ウィジェットの説明を表示
        lab1 = tk.Label(self.cv, text=self.info, font=FONT, bg=self.background)
        self.binder(lab1)
        lab1.place(x=EXPAND(50), y=EXPAND(10))
        self.check_enabled()

        # インデックスを表示
        self.lab4 = tk.Label(self.cv, font=FONT, bg=self.background,
                             text=f"{self.tab.widgets.index(self)+1:03}")
        self.binder(self.lab4)
        self.lab4.place(x=EXPAND(6), y=EXPAND(HEIGHT//2-12))

        # チェックボックスを表示
        self.chk1 = CheckButton(
            self.cv, width=EXPAND(12), bg=self.background, margin=EXPAND(4))
        self.chk1.set_parent(self.tab.chk0)
        self.binder(self.chk1)
        self.chk1.set(self.check)
        self.chk1.set_command(self.tab.set_header)
        self.chk1.bind("<Button-1>", self.check_clicked)
        self.chk1.place(x=EXPAND(12), y=EXPAND(HEIGHT//2+6))
        self.tab.chk0.set_children(self.chk1)

    def click_left(self, event: tk.Event):
        """マウスの左ボタンをクリック"""
        # カーソルを上下矢印に設定
        self.cv.config(cursor="sb_v_double_arrow")

    def release_left(self, event: tk.Event):
        """マウスの左ボタンを離す"""
        # カーソルをデフォルトに設定
        self.cv.config(cursor=CURSOR)

    def click_center(self, event: tk.Event):
        """中ボタンでのスクロール開始"""
        if self.tab.center_clicked:
            return

        # カーソルを十字矢印に設定
        self.cv.config(cursor="fleur")

        self.mouse_position = self.cv.winfo_pointery()
        self.center_start = self.tab.index
        self.tab.center_clicked = True
        self.scroll_center()

    def release_center(self, event: tk.Event):
        """中ボタンでのスクロール終了"""
        # カーソルをデフォルトに設定
        self.cv.config(cursor=CURSOR)

        self.tab.center_clicked = False

    def scroll_center(self, event=None):
        """中ボタンでのスクロール時の動作"""
        move = self.cv.winfo_pointery() - self.mouse_position
        self.tab.center_distance += round(move / EXPAND(HEIGHT))
        distance = self.tab.center_distance // 8
        self.tab.center_distance = self.tab.center_distance % 8
        if distance != 0:
            self.tab.index += distance
            self.tab.redraw_widgets(change=False)
        if self.tab.center_clicked:
            self.cv.after(100, self.scroll_center)

    def scroll_on_windows(self, event: tk.Event):
        """Windowsでのスクロール時の動作"""
        data = self.tab.widgets
        index = self.tab.index - (event.delta // 120)
        max_size = (len(data) - SIZE)
        self.tab.index = (0 if index <= 0 else max_size
                          if (index > max_size) and (len(data) > SIZE)
                          else self.tab.index
                          if len(data) <= SIZE else index)
        self.tab.redraw_widgets(change=False)

    def scroll_on_linux(self, event: tk.Event):
        """Linuxでのスクロール時の動作"""
        data = self.tab.widgets
        index = self.tab.index - (1 if event.num == 4 else -1)
        max_size = (len(data) - SIZE)
        self.tab.index = (0 if index <= 0 else max_size
                          if (index > max_size) and (len(data) > SIZE)
                          else self.tab.index
                          if len(data) <= SIZE else index)
        self.tab.redraw_widgets(change=False)

    def drag_move(self, event: tk.Event):
        """ドラッグ時の動作"""
        index = self.tab.widgets.index(self) - self.tab.index
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

    def check_clicked(self, event: tk.Event):
        """クリックを確認する"""
        index = self.tab.widgets.index(self)

        # Shiftと同時に押された時
        if (hasattr(event, "state")) and (event.state == 1):
            if self.tab.last_checked == -1:
                self.tab.last_checked = index
            if index < self.tab.last_checked:
                self.range_check(index, self.tab.last_checked, exc=index)
            else:
                self.range_check(self.tab.last_checked, index, exc=index)

        # 最後にチェックされたウィジェットを更新
        elif not self.tab.widgets[index].chk1.get():
            self.tab.last_checked = index

    def range_check(self, first: int, last: int, exc=None):
        """指定範囲をチェック"""
        # 一度全てチェックを外しておく
        for widget in self.tab.widgets:
            widget.chk1.set(False)

        # 指定範囲をチェックする
        for widget in self.tab.widgets[first: last + 1]:
            widget.chk1.set(True)

        # excは除外する
        if exc is not None:
            self.tab.widgets[exc].chk1.set(False)

    def check_enabled(self):
        """有効・無効の表示"""
        self.cv.delete("enabled")
        color = "blue" if self.enabled else "red"
        self.cv.create_oval(EXPAND(16), EXPAND(8),
                            EXPAND(28), EXPAND(HEIGHT//2-12),
                            width=2, outline="lightgray",
                            fill=color, tag="enabled")

    def paste_up(self):
        """上へのペースト"""
        before_index = self.tab.index

        index = self.tab.widgets.index(self)

        if CONFIG["share_copy"]:
            for d in reversed(self.et.copied_widgets):
                self.tab.make_match_class(d, index=index)
        else:
            for d in reversed(self.tab.copied_widgets):
                self.tab.make_match_class(d, index=index)

        if (index < before_index) or (index > before_index + SIZE - 1):
            self.tab.index = index
        else:
            self.tab.index = before_index

        self.tab.redraw_widgets()

    def paste_down(self):
        """下へのペースト"""
        before_index = self.tab.index

        index = self.tab.widgets.index(self) + 1

        if CONFIG["share_copy"]:
            for d in reversed(self.et.copied_widgets):
                self.tab.make_match_class(d, index=index)
        else:
            for d in reversed(self.tab.copied_widgets):
                self.tab.make_match_class(d, index=index)

        if (index < before_index) or (index > before_index + SIZE - 1):
            self.tab.index = index
        else:
            self.tab.index = before_index

        self.tab.redraw_widgets()

    def duplicate(self):
        """複製"""
        before_index = self.tab.index

        index = self.tab.widgets.index(self) + 1
        self.tab.make_match_class(self.get_data(), index=index)

        if (index < before_index) or (index > before_index + SIZE - 1):
            self.tab.index = index
        else:
            self.tab.index = before_index

        self.tab.redraw_widgets()

    def show_popup2(self, event: tk.Event):
        "ポップアップメニュー"
        if hasattr(self.et, "menu"):
            self.et.menu.destroy()

        index = self.tab.widgets.index(self)

        menu_font = (FONT_TYPE1, EXPAND(10), "bold")
        self.et.menu = tk.Menu(ROOT, tearoff=0, font=menu_font)

        states = ["active" for i in range(5)]
        if index <= 0:
            states[0] = states[2] = "disabled"
        if index >= len(self.tab.widgets) - 1:
            states[1] = states[3] = "disabled"

        if CONFIG["share_copy"]:
            if len(self.tab.copied_widgets) == 0:
                states[4] = "disabled"
        else:
            if len(self.tab.copied_widgets) == 0:
                states[4] = "disabled"

        self.et.menu.add_command(label='１番上に移動', command=self.top,
                                 state=states[0])
        self.et.menu.add_command(label='１番下に移動', command=self.bottom,
                                 state=states[1])
        self.et.menu.add_command(label='１個上に移動', command=self.up,
                                 state=states[2])
        self.et.menu.add_command(label='１個下に移動', command=self.down,
                                 state=states[3])

        self.et.menu.add_separator()
        self.et.menu.add_command(label='コピー', command=self.copy)
        self.et.menu.add_command(label='切り取り', command=self.cut)
        self.et.menu.add_command(label='削除', command=self.delete)

        self.et.menu.add_separator()
        self.et.menu.add_command(label='複製', command=self.duplicate)

        if self.OPTION:
            self.et.menu.add_separator()
            self.et.menu.add_command(label='オプション', command=self.show_option)

        self.et.menu.add_separator()
        if (self.TYPE == "undefined") or (self.TYPE == "comment"):
            self.et.menu.add_command(label='有効化', state="disabled")
        elif self.enabled:
            self.et.menu.add_command(label='無効化', command=self.disable)
        else:
            self.et.menu.add_command(label='有効化', command=self.enable)

        self.et.menu.add_separator()
        self.et.menu.add_command(label='上にペースト', command=self.paste_up,
                                 state=states[4])
        self.et.menu.add_command(label='下にペースト', command=self.paste_down,
                                 state=states[4])

        self.et.menu.post(event.x_root, event.y_root)

    def enable(self, back_up=True):
        "ウィジェットの有効化"
        if (self.TYPE == "undefined") or (self.TYPE == "comment"):
            return
        self.enabled = True
        self.check_enabled()
        if back_up:
            self.tab.back_up()

    def disable(self, back_up=True):
        "ウィジェットの無効化"
        self.enabled = False
        self.check_enabled()
        if back_up:
            self.tab.back_up()

    def delete(self, back_up=True):
        """ウィジェットの削除"""
        if self in self.tab.last_shown:
            self.tab.last_shown.remove(self)
        self.tab.chk0.forget_children(self.chk1)
        self.cv.place_forget()
        self.tab.widgets.remove(self)
        self.tab.redraw_widgets(back_up)

    def place_cv(self):
        """キャンバスを描き直す"""
        index = self.tab.widgets.index(self) - self.tab.index
        if 0 <= index < SIZE:
            self.cv.place(x=0, y=EXPAND(HEIGHT*index))
            self.lab4.config(text=f"{self.tab.widgets.index(self)+1:03}")
        else:
            self.cv.place_forget()

    def copy(self):
        """ウィジェットをコピーする"""
        data = self.get_data()
        data["_check"] = False

        if CONFIG["share_copy"]:
            self.et.copied_widgets = [data]
        else:
            self.tab.copied_widgets = [data]

    def cut(self):
        """ウィジェットをカットする"""
        self.copy()
        self.delete()

    def top(self):
        """ウィジェットを一番上に移動"""
        self.tab.widgets.remove(self)
        self.tab.widgets.insert(0, self)
        self.tab.index = 0
        self.tab.redraw_widgets()

    def bottom(self):
        """ウィジェットを一番下に移動"""
        self.tab.widgets.remove(self)
        self.tab.widgets.append(self)
        bottom = len(self.tab.widgets)
        self.tab.index = bottom if bottom > SIZE else 0
        self.tab.redraw_widgets()

    def up(self):
        """ウィジェットを一個上に移動"""
        index = self.tab.widgets.index(self)
        if index == 0:
            return
        upper = self.tab.widgets[index - 1]
        self.tab.widgets[index - 1] = self
        self.tab.widgets[index] = upper
        if index == self.tab.index:
            self.tab.index -= 1
        self.tab.redraw_widgets()

    def down(self):
        """ウィジェットを一個下に移動"""
        index = self.tab.widgets.index(self)
        if index + 1 >= len(self.tab.widgets):
            return
        under = self.tab.widgets[index + 1]
        self.tab.widgets[index + 1] = self
        self.tab.widgets[index] = under
        if index == self.tab.index + SIZE - 1:
            self.tab.index += 1
        self.tab.redraw_widgets()

    def set_common(self, data: dict):
        """共通変数に値をセットする"""
        self.check = data.get("_check", False)
        if (self.TYPE == "comment") or (self.TYPE == "undefined"):
            self.enabled = False
        else:
            self.enabled = data.get("_enabled", True)

    def get_class_data(self, data: dict, more: bool):
        """クラスのデータを追加する"""
        if more:
            data["_check"] = self.chk1.get()
        elif "_check" in data:
            del data["_check"]

        data["_enabled"] = self.enabled

        if self.__class__.__name__ != "Undefined":
            data["_name"] = self.__class__.__name__
        return data

    def copy_entry(self, entry: tk.Entry):
        """テキストをコピーする"""
        if entry.selection_present():
            text = entry.selection_get()
        else:
            text = entry.get()
        ROOT.clipboard_clear()
        ROOT.clipboard_append(text)

    def paste_entry(self, entry: tk.Entry):
        """テキストを表示する"""
        text = ROOT.clipboard_get()
        entry.insert("insert", text)

    def show_popup1(self, event: tk.Event, entry: tk.Entry):
        """ポップアップを表示する（tk.Entry用）"""
        if hasattr(self.et, "menu"):
            self.et.menu.destroy()
        try:
            if ROOT.clipboard_get() != "":
                paste = "active"
            else:
                paste = "disabled"
        except tk.TclError:
            paste = "disabled"

        menu_font = (FONT_TYPE1, EXPAND(10), "bold")
        self.et.menu = tk.Menu(ROOT, tearoff=0, font=menu_font)

        self.et.menu.add_command(
            label='コピー', command=lambda: self.copy_entry(entry))
        self.et.menu.add_command(label='ペースト', state=paste,
                                 command=lambda: self.paste_entry(entry))
        self.et.menu.post(event.x_root, event.y_root)

    def str2str(self, string: str):
        """変数を埋め込み"""
        for var in re.findall(r'\[\w*\]', string):
            name = var[1:-1] if len(var) > 2 else ""
            if name not in self.tab.variable_datas:
                messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"は定義されていません')
                self.tab.kill_runner()
                return ""
            elif self.tab.variable_datas[name][1] == "S" or\
                    not CONFIG["show_warning"]:
                string = string.replace(
                    var, str(self.tab.variable_datas[name][0]))
            else:
                messagebox.showwarning("警告", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"はString型ではありません')
                string = string.replace(
                    var, str(self.tab.variable_datas[name][0]))
        return string

    def str2bool(self, string: str):
        """変数を埋め込み"""
        match = re.fullmatch(r'\[\w*\]', string)
        if match is not None:
            var = match.group()
            name = var[1:-1]
            if name not in self.tab.variable_datas:
                messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"は定義されていません')
                self.tab.kill_runner()
                return False
            elif self.tab.variable_datas[name][1] == "B" or \
                    not CONFIG["show_warning"]:
                string = string.replace(
                    var, str(self.tab.variable_datas[name][0]))
            else:
                messagebox.showwarning("警告", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"はBoolean型ではありません')
                string = string.replace(
                    var, str(self.tab.variable_datas[name][0]))
        if string == "True":
            boolean = True
        elif string == "False":
            boolean = False
        else:
            messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
{string}はBoolean型ではありません')
            self.tab.kill_runner()
            return False
        return boolean

    def var_converter(self, string: str):
        """変数を埋め込み"""
        for var in re.findall(r'\[\w*\]', string):
            name = var[1:-1] if len(var) > 2 else ""
            if name not in self.tab.variable_datas:
                messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"は定義されていません')
                self.tab.kill_runner()
            elif self.tab.variable_datas[name][1] == "N" or \
                    not CONFIG["show_warning"]:
                string = string.replace(
                    var, str(self.tab.variable_datas[name][0]))
            else:
                messagebox.showwarning("警告", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
変数"{name}"はNumber型ではありません')
                string = string.replace(
                    var, str(self.tab.variable_datas[name][0]))
        return string

    def calculator(self, string: str):
        """数列の計算"""
        string = self.var_converter(string)
        if string == "":
            messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
値が入力されていません')
            self.tab.kill_runner()
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

    def str2float(self, string: str):
        """文字列を小数に変換"""
        try:
            return self.calculator(string)
        except Exception:
            messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{string}"を数値に変換できませんでした')
            self.tab.kill_runner()
            return 0.0

    def str2int(self, string: str):
        """文字列を整数に変換"""
        num = self.str2float(string)
        if not float(num).is_integer() and CONFIG["show_warning"]:
            messagebox.showwarning("警告", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
値は整数でなければなりません')
        return int(round(num))

    def str2uint(self, string: str):
        """文字列を符号なし整数に変換"""
        num = self.str2int(string)
        if num < 0:
            messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
値は正の整数でなければなりません')
            self.tab.kill_runner()
            return 0
        else:
            return num

    def str2ufloat(self, string: str):
        """文字列を符号なし小数に変換"""
        num = self.str2float(string)
        if num < 0:
            messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
値は正の小数でなければなりません')
            self.tab.kill_runner()
            return 0.0
        else:
            return num


class VarNumber(Widget):
    TEXT = "変数①を数値②にする"
    TYPE = "variable"
    OPTION = False
    VALUES = {"name": "num", "value": "0"}

    def set_data(self, data: dict):
        self.name = data.get("name", self.VALUES["name"])
        self.value = data.get("value", self.VALUES["value"])
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
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.name)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.value)
        self.binder(self.ent2)
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.name = self.ent1.get()
        self.value = self.ent2.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        self.tab.variable_datas[self.name] = (self.str2float(self.value), "N")


class VarString(Widget):
    TEXT = "変数①を文字列②にする"
    TYPE = "variable"
    OPTION = False
    VALUES = {"name": "str", "value": "text"}

    def set_data(self, data: dict):
        self.name = data.get("name", self.VALUES["name"])
        self.value = data.get("value", self.VALUES["value"])
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
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.name)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.value)
        self.binder(self.ent2)
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.name = self.ent1.get()
        self.value = self.ent2.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        self.tab.variable_datas[self.name] = (self.str2str(self.value), "S")


class VarBoolean(Widget):
    TEXT = "変数①を真偽値②にする"
    TYPE = "variable"
    OPTION = False
    VALUES = {"name": "bool", "value": "True"}

    def set_data(self, data: dict):
        self.name = data.get("name", self.VALUES["name"])
        self.value = data.get("value", self.VALUES["value"])
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
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.name)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.var1 = tk.StringVar()
        cb1 = ttk.Combobox(self.cv, textvariable=self.var1,
                           font=FONT, width=10)
        cb1['values'] = ("True", "False")
        cb1.set(self.value)
        self.binder(cb1)
        cb1.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.name = self.ent1.get()
        self.value = self.var1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        self.tab.variable_datas[self.name] = (self.str2bool(self.value), "B")


class Title(Widget):
    TEXT = "画面タイトルを①にする"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"title": "Turtle"}

    def set_data(self, data: dict):
        self.title = data.get("title", self.VALUES["title"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"title": self.title}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.title)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.title = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        self.tab.win.title(self.str2str(self.title))


class ScreenSize(Widget):
    TEXT = "画面を横幅①、高さ②にする"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"width": "600", "height": "600"}

    def set_data(self, data: dict):
        self.width = data.get("width", self.VALUES["width"])
        self.height = data.get("height", self.VALUES["height"])
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
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.width)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.height)
        self.binder(self.ent2)
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.width = self.ent1.get()
        self.height = self.ent2.get()

    def run(self, tur: turtle.RawTurtle):
        # データを保存する
        self.save_data()

        # 画面サイズを取得
        width = maxwidth = self.str2uint(self.width)
        height = maxheight = self.str2uint(self.height)

        # 元の位置を取得
        xcor = tur.xcor() - self.tab.runner_size[0] // 2
        ycor = tur.ycor() + self.tab.runner_size[1] // 2

        # 警告を表示
        if width > SYSTEM_WIDTH:
            width = SYSTEM_WIDTH
        if height > SYSTEM_HEIGHT:
            height = SYSTEM_HEIGHT

        # 画面サイズの変更
        canvas = tur.getscreen().getcanvas()
        winx = maxwidth + self.tab.scrollbar_width
        winy = maxheight + self.tab.scrollbar_width
        self.tab.win.geometry(f"{winx}x{winy}")
        canvas.config(
            width=width, height=height,
            scrollregion=(0, 0, maxwidth, maxheight))
        canvas.xview_moveto((1 - width / maxwidth) / 2)
        canvas.yview_moveto((1 - height / maxheight) / 2)

        # 亀を移動
        tur.penup()
        tur.speed(0)
        tur.goto(maxwidth // 2 + xcor, maxheight // -2 + ycor)
        tur.speed(self.tab.runner_speed)
        if self.tab.runner_pendown:
            tur.pendown()

        # すべての要素を移動
        for element_id in canvas.find_all():
            canvas.move(element_id,
                        (maxwidth - self.tab.runner_size[0]) // 2,
                        (maxheight - self.tab.runner_size[1]) // 2)

        # データを変更
        self.tab.runner_size = (maxwidth, maxheight)

        tur.getscreen().update()


class Forward(Widget):
    TEXT = "前方向に①移動する"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"distance": "0"}

    def set_data(self, data: dict):
        self.distance = data.get("distance", self.VALUES["distance"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"distance": self.distance}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.distance)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.distance = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.forward(self.str2int(self.distance))


class Backward(Widget):
    TEXT = "後方向に①移動する"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"distance": "0"}

    def set_data(self, data: dict):
        self.distance = data.get("distance", self.VALUES["distance"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"distance": self.distance}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.distance)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.distance = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.backward(self.str2int(self.distance))


class Right(Widget):
    TEXT = "右方向に①度曲げる"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"angle": "0"}

    def set_data(self, data: dict):
        self.angle = data.get("angle", self.VALUES["angle"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.angle = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.right(self.str2int(self.angle))


class Left(Widget):
    TEXT = "左方向に①度曲げる"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"angle": "0"}

    def set_data(self, data: dict):
        self.angle = data.get("angle", self.VALUES["angle"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.angle = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.left(self.str2int(self.angle))


class GoTo(Widget):
    TEXT = "ｘ座標①、ｙ座標②に移動する"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"x": "0", "y": "0"}

    def set_data(self, data: dict):
        self.x = data.get("x", self.VALUES["x"])
        self.y = data.get("y", self.VALUES["y"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x, "y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.y)
        self.binder(self.ent2)
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.x = self.ent1.get()
        self.y = self.ent2.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.goto(
            self.str2int(self.x) + self.tab.runner_size[0] // 2,
            self.str2int(self.y) - self.tab.runner_size[1] // 2)


class SetX(Widget):
    TEXT = "ｘ座標①に移動する"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"x": "0"}

    def set_data(self, data: dict):
        self.x = data.get("x", self.VALUES["x"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.x = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.setx(self.str2int(self.x) + self.tab.runner_size[0] // 2)


class SetY(Widget):
    TEXT = "ｙ座標①に移動する"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"y": "0"}

    def set_data(self, data: dict):
        self.y = data.get("y", self.VALUES["y"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.y)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.y = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.sety(self.str2int(self.y) - self.tab.runner_size[1] // 2)


class SetHeading(Widget):
    TEXT = "向きを①度に変更する"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"angle": "0"}

    def set_data(self, data: dict):
        self.angle = data.get("angle", self.VALUES["angle"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.angle = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.setheading(self.str2int(self.angle))


class Home(Widget):
    TEXT = "座標と角度を初期状態に戻す"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.goto(self.tab.runner_size[0] // 2, self.tab.runner_size[1] // -2)


class Position(Widget):
    TEXT = "座標ｘを①、ｙを②に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"x": "xcor", "y": "ycor"}

    def set_data(self, data: dict):
        self.x = data.get("x", self.VALUES["x"])
        self.y = data.get("y", self.VALUES["y"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x, "y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.y)
        self.binder(self.ent2)
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.x = self.ent1.get()
        self.y = self.ent2.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        xval, yval = tur.position()
        self.tab.variable_datas[self.x] = (
            xval - self.tab.runner_size[0] // 2, "N")
        self.tab.variable_datas[self.y] = (
            yval + self.tab.runner_size[1] // 2, "N")


class ToWards(Widget):
    TEXT = "ｘ①、ｙ②への角度を③に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"x": "0",
              "y": "0",
              "angle": "angle"}

    def set_data(self, data: dict):
        self.x = data.get("x", self.VALUES["x"])
        self.y = data.get("y", self.VALUES["y"])
        self.angle = data.get("angle", self.VALUES["angle"])
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
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.y)
        self.binder(self.ent1)
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))
        lab4 = tk.Label(self.cv, text="③", font=FONT, bg=self.background)
        self.binder(lab4)
        lab4.place(x=EXPAND(350), y=EXPAND(HEIGHT//2+6))
        self.ent3 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent3.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent3.place(x=EXPAND(370), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.x = self.ent1.get()
        self.y = self.ent2.get()
        self.angle = self.ent3.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        angle = tur.towards(
            self.str2int(self.x) + self.tab.runner_size[0] // 2,
            self.str2int(self.y) - self.tab.runner_size[1] // 2)
        self.tab.variable_datas[self.angle] = (angle, "N")


class Distance(Widget):
    TEXT = "ｘ①、ｙ②への距離を③に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"x": "0",
              "y": "0",
              "distance": "distance"}

    def set_data(self, data: dict):
        self.x = data.get("x", self.VALUES["x"])
        self.y = data.get("y", self.VALUES["y"])
        self.distance = data.get("distance", self.VALUES["distance"])
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
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.y)
        self.binder(self.ent1)
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))
        lab4 = tk.Label(self.cv, text="③", font=FONT, bg=self.background)
        self.binder(lab4)
        lab4.place(x=EXPAND(350), y=EXPAND(HEIGHT//2+6))
        self.ent3 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent3.insert(tk.END, self.distance)
        self.binder(self.ent1)
        self.ent3.place(x=EXPAND(370), y=EXPAND(HEIGHT // 2 + 8))

    def save_data(self):
        self.x = self.ent1.get()
        self.y = self.ent2.get()
        self.distance = self.ent3.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        distance = tur.distance(
            self.str2int(self.x) + self.tab.runner_size[0] // 2,
            self.str2int(self.y) - self.tab.runner_size[1] // 2)
        self.tab.variable_datas[self.distance] = (distance, "N")


class XCor(Widget):
    TEXT = "ｘ座標を①に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"x": "xcor"}

    def set_data(self, data: dict):
        self.x = data.get("x", self.VALUES["x"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"x": self.x}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.x)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.x = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        xval = tur.xcor()
        self.tab.variable_datas[self.x] = (
            xval - self.tab.runner_size[0] // 2, "N")


class YCor(Widget):
    TEXT = "ｙ座標を①に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"y": "ycor"}

    def set_data(self, data: dict):
        self.y = data.get("y", self.VALUES["y"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"y": self.y}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.y)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.y = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        yval = tur.ycor()
        self.tab.variable_datas[self.y] = (
            yval + self.tab.runner_size[1] // 2, "N")


class Heading(Widget):
    TEXT = "角度を①に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"angle": "angle"}

    def set_data(self, data: dict):
        self.angle = data.get("angle", self.VALUES["angle"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"angle": self.angle}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.angle)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.angle = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        aval = tur.heading()
        self.tab.variable_datas[self.angle] = (aval, "N")


class Circle(Widget):
    TEXT = "半径①の円を角度②度描く"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"radius": "0", "extent": "360"}

    def set_data(self, data: dict):
        self.radius = data.get("radius", self.VALUES["radius"])
        self.extent = data.get("extent", self.VALUES["extent"])
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
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.radius)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.extent)
        self.binder(self.ent2)
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.radius = self.ent1.get()
        self.extent = self.ent2.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.circle(
            self.str2int(self.radius),
            self.str2int(self.extent))


class Dot(Widget):
    TEXT = "直径①の円を描く"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"size": "0"}

    def set_data(self, data: dict):
        self.size = data.get("size", self.VALUES["size"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"size": self.size}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.size)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.size = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.dot(self.str2uint(self.size))


class Stamp(Widget):
    TEXT = "亀のスタンプを押す"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.stamp()


class Speed(Widget):
    TEXT = "速度を①に変更する"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"speed": "3"}

    def set_data(self, data: dict):
        self.speed = data.get("speed", self.VALUES["speed"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"speed": self.speed}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.speed)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.speed = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        if not self.tab.running_fastest:
            self.tab.runner_speed = self.str2int(self.speed)
            tur.speed(self.tab.runner_speed)


class PenDown(Widget):
    TEXT = "動いた線を引くようにする"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        self.tab.runner_pendown = True
        tur.pendown()


class PenUp(Widget):
    TEXT = "動いた線を引かなくする"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        self.tab.runner_pendown = False
        tur.penup()


class IsDown(Widget):
    TEXT = "動いた線を引くか①に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"down": "down"}

    def set_data(self, data: dict):
        self.isdown = data.get("down", self.VALUES["down"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"down": self.isdown}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.isdown)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.isdown = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        isdown = tur.isdown()
        self.tab.variable_datas[self.isdown] = (isdown, "B")


class PenSize(Widget):
    TEXT = "ペン先の太さを①にする"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"width": "1"}

    def set_data(self, data: dict):
        self.width = data.get("width", self.VALUES["width"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"width": self.width}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.width)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.width = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.pensize(self.str2uint(self.width))


class Color(Widget):
    TEXT = "ペンと背景の色を①にする"
    TYPE = "normalset"
    OPTION = True
    VALUES = {"color": "black"}

    def set_data(self, data: dict):
        self.color = data.get("color", self.VALUES["color"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        strvar = tk.StringVar()
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT,
                             validate='all', textvariable=strvar)
        self.ent1.config(vcmd=(self.ent1.register(self.preview_color)))
        strvar.set(self.color)
        self.binder(self.ent1)
        self.ent1.bind("<KeyPress>", self.preview_color)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        self.preview_color()

    def preview_color(self, event: tk.Event = None):
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
            self.cv.create_rectangle(
                EXPAND(280), EXPAND(HEIGHT//2+6),
                EXPAND(300), EXPAND(HEIGHT-6),
                fill=color, outline="lightgray", width=2, tag="highlight")
        except tk.TclError:
            self.cv.create_rectangle(
                EXPAND(280), EXPAND(HEIGHT//2+6),
                EXPAND(300), EXPAND(HEIGHT-6),
                fill="black", outline="lightgray", width=2, tag="highlight")

    def show_option(self):
        color = self.ent1.get()
        try:
            color = colorchooser.askcolor(
                color=self.str2str(color), parent=ROOT)
        except tk.TclError:
            color = colorchooser.askcolor(parent=ROOT)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())
        self.preview_color()

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        try:
            tur.color(self.str2str(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした', parent=ROOT)
            self.tab.kill_runner()


class PenColor(Widget):
    TEXT = "ペンの色を①にする"
    TYPE = "normalset"
    OPTION = True
    VALUES = {"color": "black"}

    def set_data(self, data: dict):
        self.color = data.get("color", self.VALUES["color"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        strvar = tk.StringVar()
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT,
                             validate='all', textvariable=strvar)
        self.ent1.config(vcmd=(self.ent1.register(self.preview_color)))
        strvar.set(self.color)
        self.binder(self.ent1)
        self.ent1.bind("<KeyPress>", self.preview_color)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        self.preview_color()

    def preview_color(self, event: tk.Event = None):
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
            self.cv.create_rectangle(
                EXPAND(280), EXPAND(HEIGHT//2+6),
                EXPAND(300), EXPAND(HEIGHT-6),
                fill=color, outline="lightgray", width=2, tag="highlight")
        except tk.TclError:
            self.cv.create_rectangle(
                EXPAND(280), EXPAND(HEIGHT//2+6),
                EXPAND(300), EXPAND(HEIGHT-6),
                fill="black", outline="lightgray", width=2, tag="highlight")

    def show_option(self):
        color = self.ent1.get()
        try:
            color = colorchooser.askcolor(
                color=self.str2str(color), parent=ROOT)
        except tk.TclError:
            color = colorchooser.askcolor(parent=ROOT)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())
        self.preview_color()

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        try:
            tur.pencolor(self.str2str(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした', parent=ROOT)
            self.tab.kill_runner()


class FillColor(Widget):
    TEXT = "塗りつぶしの色を①にする"
    TYPE = "normalset"
    OPTION = True
    VALUES = {"color": "black"}

    def set_data(self, data: dict):
        self.color = data.get("color", self.VALUES["color"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        strvar = tk.StringVar()
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT,
                             validate='all', textvariable=strvar)
        self.ent1.config(vcmd=(self.ent1.register(self.preview_color)))
        strvar.set(self.color)
        self.binder(self.ent1)
        self.ent1.bind("<KeyPress>", self.preview_color)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        self.preview_color()

    def preview_color(self, event: tk.Event = None):
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
            self.cv.create_rectangle(
                EXPAND(280), EXPAND(HEIGHT//2+6),
                EXPAND(300), EXPAND(HEIGHT-6),
                fill=color, outline="lightgray", width=2, tag="highlight")
        except tk.TclError:
            self.cv.create_rectangle(
                EXPAND(280), EXPAND(HEIGHT//2+6),
                EXPAND(300), EXPAND(HEIGHT-6),
                fill="black", outline="lightgray", width=2, tag="highlight")

    def show_option(self):
        color = self.ent1.get()
        try:
            color = colorchooser.askcolor(
                color=self.str2str(color), parent=ROOT)
        except tk.TclError:
            color = colorchooser.askcolor(parent=ROOT)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())
        self.preview_color()

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        try:
            tur.fillcolor(self.str2str(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした', parent=ROOT)
            self.tab.kill_runner()


class BGColor(Widget):
    TEXT = "背景色を①に変更する"
    TYPE = "normalset"
    OPTION = True
    VALUES = {"color": "white"}

    def set_data(self, data: dict):
        self.color = data.get("color", self.VALUES["color"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        strvar = tk.StringVar()
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT,
                             validate='all', textvariable=strvar)
        self.ent1.config(vcmd=(self.ent1.register(self.preview_color)))
        strvar.set(self.color)
        self.binder(self.ent1)
        self.ent1.bind("<KeyPress>", self.preview_color)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        self.preview_color()

    def preview_color(self, event: tk.Event = None):
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
                color=self.str2str(color), parent=ROOT)
        except tk.TclError:
            color = colorchooser.askcolor(parent=ROOT)
        if color != (None, None):
            self.ent1.delete(0, tk.END)
            self.ent1.insert(0, color[1].upper())
        self.preview_color()

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        try:
            tur.getscreen().bgcolor(self.str2str(self.color))
        except turtle.TurtleGraphicsError:
            messagebox.showerror("エラー", f'\
line: {self.tab.widgets.index(self)+1}, {self.__class__.__name__}\n\
"{self.color}"を色として認識できませんでした', parent=ROOT)
            self.tab.kill_runner()


class GetPenColor(Widget):
    TEXT = "ペンの色を①に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"color": "color"}

    def set_data(self, data: dict):
        self.color = data.get("color", self.VALUES["color"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.color)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        cval = tur.pencolor()
        self.tab.variable_datas[self.color] = (self.tab.convert_rgb(cval), "S")


class GetFillColor(Widget):
    TEXT = "塗りつぶしの色を①に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"color": "color"}

    def set_data(self, data: dict):
        self.color = data.get("color", self.VALUES["color"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.color)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        cval = tur.fillcolor()
        self.tab.variable_datas[self.color] = (self.tab.convert_rgb(cval), "S")


class GetBGColor(Widget):
    TEXT = "背景色を①に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"color": "color"}

    def set_data(self, data: dict):
        self.color = data.get("color", self.VALUES["color"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"color": self.color}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.color)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.color = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        cval = tur.getscreen().bgcolor()
        self.tab.variable_datas[self.color] = (self.tab.convert_rgb(cval), "S")


class BeginFill(Widget):
    TEXT = "塗りつぶしを始める"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.begin_fill()


class EndFill(Widget):
    TEXT = "塗りつぶしを終える"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.end_fill()


class Filling(Widget):
    TEXT = "塗りつぶしするか①に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"fill": "fill"}

    def set_data(self, data: dict):
        self.fill = data.get("fill", self.VALUES["fill"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"fill": self.fill}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.fill)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.fill = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        fill = tur.filling()
        self.tab.variable_datas[self.fill] = (fill, "B")


class ShowTurtle(Widget):
    TEXT = "カメを表示モードにする"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.showturtle()


class HideTurtle(Widget):
    TEXT = "カメを非表示モードにする"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.hideturtle()


class IsVisible(Widget):
    TEXT = "表示モードか①に代入する"
    TYPE = "normalget"
    OPTION = False
    VALUES = {"shown": "shown"}

    def set_data(self, data: dict):
        self.shown = data.get("shown", self.VALUES["shown"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"shown": self.shown}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.shown)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.shown = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        shown = tur.isvisible()
        self.tab.variable_datas[self.shown] = (shown, "B")


class TurtleSize(Widget):
    TEXT = "亀の大きさを①にする"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"size": "1"}

    def set_data(self, data: dict):
        self.size = data.get("size", self.VALUES["size"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"size": self.size}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.size)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.size = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.turtlesize(self.str2int(self.size))


class Write(Widget):
    TEXT = "文字列①を大きさ②で書く"
    TYPE = "normalset"
    OPTION = True
    VALUES = {
        "text": "Sample",
        "size": "20",
        "move": "False",
        "align": "center",
        "family": "Default",
        "weight": "bold",
        "slant": "roman",
        "sideway": "False"}

    def set_data(self, data: dict):
        self.text = data.get("text", self.VALUES["text"])
        self.size = data.get("size", self.VALUES["size"])
        self.move = data.get("move", self.VALUES["move"])
        self.align = data.get("align", self.VALUES["align"])
        self.family = data.get("family", self.VALUES["family"])
        self.weight = data.get("weight", self.VALUES["weight"])
        self.slant = data.get("slant", self.VALUES["slant"])
        self.sideway = data.get("sideway", self.VALUES["sideway"])
        self.set_common(data)

    def get_data(self, more=True):
        data = {"text": self.text, "size": self.size}
        if str(self.move) != self.VALUES["move"] or more:
            data["move"] = self.move
        if str(self.align) != self.VALUES["align"] or more:
            data["align"] = self.align
        if str(self.family) != self.VALUES["family"] or more:
            data["family"] = self.family
        if str(self.weight) != self.VALUES["weight"] or more:
            data["weight"] = self.weight
        if str(self.slant) != self.VALUES["slant"] or more:
            data["slant"] = self.slant
        if str(self.sideway) != self.VALUES["sideway"] or more:
            data["sideway"] = self.sideway
        self.save_data()
        return self.get_class_data(data, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.text)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))
        lab3 = tk.Label(self.cv, text="②", font=FONT, bg=self.background)
        self.binder(lab3)
        lab3.place(x=EXPAND(200), y=EXPAND(HEIGHT//2+6))
        self.ent2 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent2.insert(tk.END, self.size)
        self.binder(self.ent2)
        self.ent2.place(x=EXPAND(220), y=EXPAND(HEIGHT//2+6))

    def show_option(self):
        # データを取得する
        self.text = self.ent1.get()
        self.size = self.ent2.get()

        # ウィンドウを作成する
        self.win = tk.Toplevel(ROOT)
        self.win.wait_visibility()
        self.win.grab_set()
        frame0 = tk.Frame(self.win)
        frame0.pack(anchor=tk.N, side=tk.TOP)
        font = (FONT_TYPE1, EXPAND(16), "bold")
        list_font = (FONT_TYPE1, EXPAND(10))

        # タイトル
        lab0 = tk.Label(
            frame0, text="Options", font=(FONT_TYPE2, EXPAND(32), "bold"))
        lab0.pack(side=tk.TOP, pady=EXPAND(10))

        # 決定ボタン
        but1 = tk.Button(
            frame0, text="決定", font=font, width=12, command=self.decide_option)
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
        self.opt1.bind("<KeyPress>", self.preview_font)
        self.opt1.pack(side=tk.LEFT)

        fra2 = tk.Frame(frame1)
        fra2.pack(anchor=tk.W, pady=EXPAND(10))
        lab2 = tk.Label(fra2, text="move    = ", font=font)
        lab2.pack(side=tk.LEFT)
        self.opt2 = ttk.Combobox(fra2, font=font, width=12)
        self.opt2.option_add('*TCombobox*Listbox.font', list_font)
        self.opt2['values'] = ("True", "False")
        self.opt2.set(self.move)
        self.opt2.bind("<KeyPress>", self.preview_font)
        self.opt2.bind("<<ComboboxSelected>>", self.preview_font)
        self.opt2.pack(side=tk.LEFT)

        fra3 = tk.Frame(frame1)
        fra3.pack(anchor=tk.W, pady=EXPAND(10))
        lab3 = tk.Label(fra3, text="align   = ", font=font)
        lab3.pack(side=tk.LEFT)
        self.opt3 = tk.Entry(fra3, font=font, width=12, justify=tk.RIGHT)
        self.opt3.insert(tk.END, self.align)
        self.opt3.bind("<KeyPress>", self.preview_font)
        self.opt3.pack(side=tk.LEFT)

        fra4 = tk.Frame(frame1)
        fra4.pack(anchor=tk.W, pady=EXPAND(10))
        lab4 = tk.Label(fra4, text="sideway = ", font=font)
        lab4.pack(side=tk.LEFT)
        self.opt4 = ttk.Combobox(fra4, font=font, width=12)
        self.opt4.option_add('*TCombobox*Listbox.font', list_font)
        self.opt4['values'] = ("True", "False")
        self.opt4.set(self.sideway)
        self.opt4.bind("<KeyPress>", self.preview_font)
        self.opt4.bind("<<ComboboxSelected>>", self.preview_font)
        self.opt4.pack(side=tk.LEFT)

        fra6 = tk.Frame(frame1)
        fra6.pack(anchor=tk.W, pady=EXPAND(10))
        lab6 = tk.Label(fra6, text="weight  = ", font=font)
        lab6.pack(side=tk.LEFT)
        self.opt6 = ttk.Combobox(fra6, font=font, width=12)
        self.opt6.option_add('*TCombobox*Listbox.font', list_font)
        self.opt6['values'] = ("normal", "bold")
        self.opt6.set(self.weight)
        self.opt6.bind("<KeyPress>", self.preview_font)
        self.opt6.bind("<<ComboboxSelected>>", self.preview_font)
        self.opt6.pack(side=tk.LEFT)

        fra7 = tk.Frame(frame1)
        fra7.pack(anchor=tk.W, pady=EXPAND(10))
        lab7 = tk.Label(fra7, text="slant   = ", font=font)
        lab7.pack(side=tk.LEFT)
        self.opt7 = ttk.Combobox(fra7, font=font, width=12)
        self.opt7.option_add('*TCombobox*Listbox.font', list_font)
        self.opt7['values'] = ("roman", "italic")
        self.opt7.set(self.slant)
        self.opt7.bind("<KeyPress>", self.preview_font)
        self.opt7.bind("<<ComboboxSelected>>", self.preview_font)
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
        self.opt5.bind("<KeyPress>", self.preview_font)
        self.opt5.pack(side=tk.LEFT)

        fra8 = tk.Frame(frame2)
        fra8.pack(anchor=tk.W, pady=EXPAND(10))
        lab8 = tk.Label(fra8, text="family  = ", font=font)
        lab8.pack(side=tk.LEFT)
        self.opt8 = tk.Entry(fra8, font=font, width=12, justify=tk.RIGHT)
        self.opt8.insert(tk.END, self.family)
        self.opt8.bind("<KeyPress>", self.preview_font)
        self.opt8.pack(side=tk.LEFT)

        fra9 = tk.Frame(frame2)
        fra9.pack(anchor=tk.W, pady=EXPAND(10))
        self.font_list = self.without_atmark()
        var1 = tk.StringVar(value=self.font_list)
        self.lsb1 = tk.Listbox(
            fra9, listvariable=var1, height=6, width=24,
            selectmode='single', font=(FONT_TYPE2, EXPAND(18)))
        self.lsb1.bind('<<ListboxSelect>>', self.change_font)
        self.lsb1.pack(fill=tk.Y, side=tk.LEFT)
        scr1 = ttk.Scrollbar(
            fra9, orient=tk.VERTICAL, command=self.lsb1.yview)
        self.lsb1['yscrollcommand'] = scr1.set
        scr1.pack(fill=tk.Y, side=tk.LEFT)

        self.preview_font()
        self.win.resizable(False, False)

    def without_atmark(self):
        new = []
        for font in tkFont.families():
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

    def change_font(self, event: tk.Event):
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

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        mark = "@" if self.str2bool(self.sideway) else ""
        font = (mark + self.str2str(self.family),
                self.str2int(self.size), self.str2str(self.weight),
                self.str2str(self.slant))
        tur.write(
            self.str2str(self.text),
            move=self.str2bool(self.move),
            align=self.str2str(self.align),
            font=font)


class Bye(Widget):
    TEXT = "プログラムを終了する"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        self.tab.kill_runner()


class ExitOnClick(Widget):
    TEXT = "クリックで終了する"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def kill(self, x, y):
        self.tab.kill_runner()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        tur.getscreen().onclick(self.kill)


class Bell(Widget):
    TEXT = "システムサウンドを鳴らす"
    TYPE = "normalset"
    OPTION = False

    def set_data(self, data: dict):
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="引数なし", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        self.tab.win.bell()


class Sleep(Widget):
    TEXT = "操作を①秒停止する"
    TYPE = "normalset"
    OPTION = False
    VALUES = {"second": "0"}

    def set_data(self, data: dict):
        self.second = data.get("second", self.VALUES["second"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"second": self.second}, more)

    def draw(self):
        self.draw_cv()
        lab2 = tk.Label(self.cv, text="①", font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))
        self.ent1 = tk.Entry(self.cv, font=FONT, width=12, justify=tk.RIGHT)
        self.ent1.insert(tk.END, self.second)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(70), y=EXPAND(HEIGHT//2+6))

    def save_data(self):
        self.second = self.ent1.get()

    def run(self, tur: turtle.RawTurtle):
        self.save_data()
        if self.tab.runner_mode == "standard":
            time.sleep(self.str2ufloat(self.second))


class Comment(Widget):
    TEXT = "実行されないコメント文"
    TYPE = "comment"
    OPTION = True
    VALUES = {"comment": "Comment"}

    def set_data(self, data: dict):
        self.comment = data.get("comment", self.VALUES["comment"])
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        return self.get_class_data({"comment": self.comment}, more)

    def draw(self):
        self.draw_cv()
        self.ent1 = tk.Entry(
            self.cv, font=(FONT_TYPE1, EXPAND(14), "bold"), fg="#B40404",
            width=30, justify=tk.LEFT)
        text = self.comment.split("\n")[0]
        self.ent1.insert(tk.END, text)
        self.binder(self.ent1)
        self.ent1.place(x=EXPAND(46), y=EXPAND(HEIGHT//2+4))

    def show_option(self):
        self.save_data()
        self.win = tk.Toplevel(ROOT)
        self.win.wait_visibility()
        self.win.grab_set()
        lab1 = tk.Label(
            self.win, text="Option", font=(FONT_TYPE2, EXPAND(30), "bold"))
        lab1.pack(padx=EXPAND(20), pady=EXPAND(20))
        font_scr = (FONT_TYPE1, EXPAND(16), "bold")
        self.scr1 = scrolledtext.ScrolledText(
            self.win, font=font_scr, width=24, height=6)
        self.scr1.pack(padx=EXPAND(20), pady=EXPAND(0))
        self.scr1.insert("0.0", self.comment)
        but1 = tk.Button(
            self.win, text="決定", font=FONT, width=10,
            command=self.decide_option)
        but1.pack(padx=EXPAND(36), pady=EXPAND(20))
        self.win.resizable(False, False)

    def decide_option(self):
        self.comment = self.scr1.get("0.0", tk.END)[:-1]
        text = self.comment.split("\n")[0]
        self.ent1.delete(0, tk.END)
        self.ent1.insert(0, text)
        self.win.destroy()

    def save_data(self):
        self.comment = "\n".join(
            [self.ent1.get()] + self.comment.split("\n")[1:])

    def run(self, tur: turtle.RawTurtle):
        pass


class Undefined(Widget):
    TEXT = "対応していない不明なクラス"
    TYPE = "undefined"
    OPTION = True

    def set_data(self, data: dict):
        self.data = data
        self.set_common(data)

    def get_data(self, more=True):
        self.save_data()
        data = {}
        for key, value in self.get_class_data(self.data, more).items():
            if more or key != "_check":
                data[key] = value
        return data

    def draw(self):
        self.draw_cv()
        text = 'このバージョンでは編集できません'
        lab2 = tk.Label(self.cv, text=text, font=FONT, bg=self.background)
        self.binder(lab2)
        lab2.place(x=EXPAND(50), y=EXPAND(HEIGHT//2+6))

    def show_option(self):
        self.win = tk.Toplevel(ROOT)
        self.win.wait_visibility()
        self.win.grab_set()
        lab1 = tk.Label(
            self.win, text="Option", font=(FONT_TYPE2, EXPAND(30), "bold"))
        lab1.pack(padx=20, pady=20)
        data = self.get_class_data(self.data, CONFIG["save_more_info"])
        text = pprint.pformat(data, width=12, indent=2)
        font = (FONT_TYPE1, EXPAND(16), "bold")
        scr1 = scrolledtext.ScrolledText(
            self.win, font=font, width=24, height=6)
        scr1.pack(padx=20, pady=(0, 20))
        scr1.insert("0.0", text)
        scr1.config(state="disabled")
        self.win.resizable(False, False)

    def save_data(self):
        pass

    def run(self, tur: turtle.RawTurtle):
        pass


# 型チェック用
WidgetType = Union[Widget, VarNumber, VarString, VarBoolean, Title, ScreenSize,
                   Forward, Backward, Right, Left, GoTo, SetX, SetY,
                   SetHeading, Home, Position, ToWards, XCor, YCor, Heading,
                   Distance, Circle, Dot, Stamp, Speed, PenDown, PenUp, IsDown,
                   PenSize, Color, PenColor, FillColor, BGColor,
                   GetPenColor, GetFillColor, GetBGColor, BeginFill, EndFill,
                   Filling, ShowTurtle, HideTurtle, IsVisible, TurtleSize,
                   Write, Bye, ExitOnClick, Bell, Sleep, Comment, Undefined]
IndividualTab = Union[ProgrammingTab, ConfigureTab]


def GET_WIDGET_INFO(widget: WidgetType) -> str:
    length = 14
    if isinstance(widget, type):
        name = widget.__name__
    else:
        name = widget.__class__.__name__
    space = " " * (length - len(name))
    info = name + space + widget.TEXT
    return info


# クラスをまとめる
Widgets = (
    VarNumber, VarString, VarBoolean, Title, ScreenSize, Forward, Backward,
    Right, Left, GoTo, SetX, SetY, SetHeading, Home, Position, ToWards,
    XCor, YCor, Heading, Distance, Circle, Dot, Stamp, Speed, PenDown, PenUp,
    IsDown, PenSize, Color, PenColor, FillColor, BGColor,
    GetPenColor, GetFillColor, GetBGColor, BeginFill, EndFill, Filling,
    ShowTurtle, HideTurtle, IsVisible, TurtleSize, Write, Bye, ExitOnClick,
    Bell, Sleep, Comment)
Texts = tuple([GET_WIDGET_INFO(c) for c in Widgets])
Names = tuple([c.__name__ for c in Widgets])


# 実行
if __name__ == "__main__":
    file = sys.argv[1] if len(sys.argv) > 1 else None
    EasyTurtle(file=file)
