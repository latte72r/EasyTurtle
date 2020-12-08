
import json, os, shutil
from tkinter import messagebox
import traceback

def converter(file, CACHE_FILE, ask=True):
    shutil.copy(file, CACHE_FILE)
    with open(CACHE_FILE, "r")as f:
        return json.load(f)

"""
from . import c25to30, c30to32, c32to41
converters = [c25to30, c30to32, c32to41]

def convert(ver, CACHE_FILE):
    et = converters[ver - 1].EasyTurtle()
    et.opener(CACHE_FILE)
    et.saver(CACHE_FILE)
    et.destroy()

def converter(file, CACHE_FILE, ask=True):
    if file == "":
        return
    with open(file, "r")as f:
        data = json.load(f)
    if "version" in data:
        ver = tuple(data["version"])
    elif ("head" in data) and ("Version" in data["head"]):
        ver = tuple(data["head"]["Version"])
    else:
        messagebox.showerror("エラー", "バージョン情報を確認してください。")
        raise Exception("バージョン情報を確認してください。")
        return
    if ver < (2, 5):    
        messagebox.showerror("エラー", "\
選択されたファイルのバージョンには対応していないかファイルが破損しています。")
        raise Exception("ファイルが破損しています。")
        return
    elif ver < (3, 0):
        fver = 1
    elif ver < (3, 2):
        fver = 2
    elif ver < (4, 1):
        fver = 3
    else:
        fver = -1
    shutil.copy(file, CACHE_FILE)
    if fver != -1:
        try:
            if fver <= 1:
                convert(1, CACHE_FILE)
            if fver <= 2:
                convert(2, CACHE_FILE)
            if fver <= 3:
                convert(3, CACHE_FILE)
        except:
            traceback.print_exc()
            messagebox.showerror("エラー", "変換エラーが発生しました。")
            raise Exception("変換エラーが発生しました")
            return
        if ask is True:
            res = messagebox.askyesno("確認", "\
選択されたファイルは古いバージョンです。\n\
このバージョン用に保存し直しますか？")
            if res is True:
                shutil.copy(CACHE_FILE, file)
    with open(CACHE_FILE, "r")as f:
        return json.load(f)
"""
