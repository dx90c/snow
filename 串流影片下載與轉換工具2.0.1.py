# ======================================================================================
# 腳本名稱: 全功能媒體下載與轉換工具
# 用途說明: 一個多功能的 Python 腳本，能夠：
#             1. 從 YouTube/Bilibili 等網站下載影片 (MP4) 或純音訊 (MP3)。
#             2. 將本地的 MP4/MKV/WEBM 檔案轉換為 MP3。
#             3. 在背景監控剪貼簿，自動快取有效連結。
#             4. 提供一個永远在线的动态仪表盘，实时显示和处理任务。
#             5. 透過自動安裝依賴套件和檢查 FFmpeg，實現開箱即用。
#
# 版本號系統 (語意化版本):
#   - 修補 (2.0.Z): 用於修復不影響功能的 Bug。
#   - 次要 (2.Y.0): 用於增加新功能或進行優化，且向下相容。
#   - 主要 (X.0.0): 用於進行重大的架構改動或不向下相容的更新。
#
# 版本: 2.0.1
#   - [重構] v2.0.1: 進行全面的繁體中文化，提升程式碼可讀性。
#   - [修正] v2.0.1: 修復了因 moviepy 匯入路徑錯誤導致的 ModuleNotFoundError 啟動錯誤。
#   - [架構革命] v2.0.0: 重構成為一个“永远在线”的动态仪表盘。
#
# 使用備註:
#   - 首次執行可能會提示安裝必要的 Python 函式庫。
#   - 強烈建議安裝 FFmpeg 並設定好環境變數，以確保所有功能正常。
#   - 按下 Enter 键处理当前列表的任务。
#   - 按下 Ctrl+C 退出程序。
# ======================================================================================

import sys
import subprocess
import os
import re
import time
import threading
import shutil
import json
from concurrent.futures import ThreadPoolExecutor

# --- 步驟 1: 依賴檢查與自動安裝 ---
def 安裝依賴套件(套件列表):
    """檢查並安裝所有必要的套件。"""
    缺少的套件 = []
    for 套件 in 套件列表:
        try:
            模組名稱 = 套件.replace('-', '_') if 套件 == 'yt-dlp' else 套件
            __import__(模組名稱)
        except ImportError:
            缺少的套件.append(套件)
    if not 缺少的套件:
        print("所有必要的依賴套件均已安裝。")
        return True
    print(f"錯誤：缺少以下必要的函式庫：{', '.join(缺少的套件)}")
    同意與否 = input("是否要讓本腳本自動為您安裝 (y/n)？ ").strip().lower()
    if 同意與否 == 'y':
        print("\n正在嘗試自動安裝，請稍候...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + 缺少的套件)
            print("\n========================================================")
            print("🎉 依賴套件已成功安裝！")
            print("為了讓新安裝的函式庫生效，請關閉此視窗並重新執行一次本腳本。")
            print("========================================================")
        except Exception as e:
            print(f"\n❌ 自動安裝失敗！請手動執行 'pip install {' '.join(缺少的套件)}'。錯誤詳情：{e}")
        input("\n按 Enter 鍵退出...")
        sys.exit()
    else:
        print("使用者取消安裝。程式即將退出。")
        input("\n按 Enter 鍵退出...")
        sys.exit()

必需的套件 = ['moviepy', 'yt-dlp', 'pyperclip', 'keyboard']
安裝依賴套件(必需的套件)

from moviepy import VideoFileClip
import pyperclip
import keyboard

# --- 步驟 2: 功能函式與全域變數 ---

下載資料夾 = "Downloader_Files"
連結快取 = {}
待轉換檔案佇列 = set()
執行緒鎖 = threading.Lock()
程式是否執行中 = True
主執行緒是否忙碌 = threading.Event()

# 【被遺漏的函式定義在這裡】
def 檢查_ffmpeg():
    """啟動時檢查 FFmpeg 是否存在於系統 PATH 中"""
    if shutil.which("ffmpeg") is None:
        print("\n" + "!"*60)
        print("!【重要提示】系統未檢測到 FFmpeg。請務必完成安裝與設定！")
        print("!  - 若已設定環境變數，請嘗試重新開機電腦。")
        print("!"*60)
        time.sleep(3)

def 設定下載資料夾():
    """確保下載資料夾存在。"""
    if not os.path.exists(下載資料夾):
        os.makedirs(下載資料夾)

def 處理下載任務(連結, 下載類型='video'):
    print(f"\n[處理任務] 連結: {連結} (模式: {下載類型.upper()})")
    
    輸出模板 = os.path.join(下載資料夾, '%(title)s.%(ext)s')
    基礎指令參數 = ['--output', 輸出模板]
    
    影片格式 = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    影片指令 = ['yt-dlp', '--format', 影片格式, '--merge-output-format', 'mp4'] + 基礎指令參數
    音訊指令 = ['yt-dlp', '-x', '--audio-format', 'mp3'] + 基礎指令參數
    兩者都要指令 = ['yt-dlp', '--format', 影片格式, '--merge-output-format', 'mp4', '-k'] + 基礎指令參數

    def 執行指令(指令, 連結):
        完整指令 = 指令 + [連結]
        try:
            程序 = subprocess.Popen(完整指令, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', errors='replace')
            for 行 in 程序.stdout:
                print(行, end='')
            程序.wait()
            if 程序.returncode != 0:
                raise subprocess.CalledProcessError(程序.returncode, 完整指令)
            return True
        except Exception as e:
            print(f"\n--- 指令執行失敗！錯誤：{e} ---")
            return False

    def 執行並擷取輸出(指令, 連結):
        完整指令 = 指令 + [連結]
        try:
            程序 = subprocess.Popen(完整指令, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', errors='replace')
            輸出內容串列 = []
            for 行 in 程序.stdout:
                print(行, end='')
                輸出內容串列.append(行)
            程序.wait()
            if 程序.returncode != 0:
                raise subprocess.CalledProcessError(程序.returncode, 完整指令)
            return "".join(輸出內容串列)
        except Exception as e:
            print(f"\n--- 指令執行失敗！錯誤：{e} ---")
            return None

    if 下載類型 == 'video':
        print("\n--- 開始下載 影片 (MP4) ---")
        執行指令(影片指令, 連結)
        
    elif 下載類型 == 'audio':
        print("\n--- 開始下載 音訊 (MP3) ---")
        執行指令(音訊指令, 連結)

    elif 下載類型 == 'both':
        print("\n--- 開始下載 影片 (MP4) + 原始音訊 ---")
        輸出內容 = 執行並擷取輸出(兩者都要指令, 連結)
        if 輸出內容:
            音訊匹配列表 = re.findall(r'\[download\] Destination: (.+\.(m4a|webm))', 輸出內容)
            if 音訊匹配列表:
                原始音訊路徑 = 音訊匹配列表[-1][0].strip()
                MP3路徑 = os.path.splitext(原始音訊路徑)[0] + ".mp3"
                print(f"\n--- 開始從 '{os.path.basename(原始音訊路徑)}' 轉換為 MP3 ---")
                try:
                    subprocess.run(['ffmpeg', '-i', 原始音訊路徑, '-codec:a', 'libmp3lame', '-qscale:a', '2', MP3路徑], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"音訊 '{os.path.basename(MP3路徑)}' 轉換成功！")
                    if os.path.exists(原始音訊路徑):
                        os.remove(原始音訊路徑)
                except Exception as e:
                    print(f"從原始音訊轉換 MP3 失敗！錯誤: {e}")
            else:
                 print("未找到原始音訊流，將單獨下載 MP3。")
                 執行指令(音訊指令, 連結)

def 將影片轉為MP3(檔案路徑):
    if not (os.path.exists(檔案路徑) and 檔案路徑.lower().endswith(('.mp4', '.mkv', 'webm'))):
        return
    MP3檔案路徑 = os.path.splitext(檔案路徑)[0] + ".mp3"
    print(f"\n[轉換模式] 正在轉換: {os.path.basename(檔案路徑)}")
    try:
        with VideoFileClip(檔案路徑) as 影片片段:
            影片片段.audio.write_audiofile(MP3檔案路徑, logger=None)
        print(f"轉換成功！🎉 -> {os.path.basename(MP3檔案路徑)}")
    except Exception as e:
        print(f"\n轉換失敗！錯誤: {e}")

# --- 步驟 3: 背景工作執行緒 ---

執行緒池 = ThreadPoolExecutor(max_workers=4)
上次剪貼簿內容 = ""

def 擷取標題任務(連結):
    try:
        程序 = subprocess.run(['yt-dlp', '--dump-json', 連結], capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True, timeout=15)
        資料 = json.loads(程序.stdout)
        標題 = 資料.get('title', '無法擷取標題')
        with 執行緒鎖:
            連結快取[連結] = 標題
    except Exception:
        with 執行緒鎖:
            if 連結 in 連結快取 and 連結快取[連結] == "正在擷取標題...":
                del 連結快取[連結]

def 剪貼簿監控任務():
    global 上次剪貼簿內容
    while 程式是否執行中:
        try:
            剪貼簿內容 = pyperclip.paste()
            if 剪貼簿內容 and 剪貼簿內容 != 上次剪貼簿內容:
                上次剪貼簿內容 = 剪貼簿內容
                if len(剪貼簿內容) > 5000: continue
                可能的連結列表 = re.findall(r'https?://[^\s/$.?#].[^\s]*', 剪貼簿內容)
                if not 可能的連結列表: continue
                待擷取的全新連結 = []
                with 執行緒鎖:
                    for 連結 in 可能的連結列表:
                        if 連結 not in 連結快取:
                            待擷取的全新連結.append(連結)
                            連結快取[連結] = "正在擷取標題..." 
                for 連結 in 待擷取的全新連結:
                    執行緒池.submit(擷取標題任務, 連結)
        except pyperclip.PyperclipException:
            pass
        time.sleep(1)

# --- 步驟 4: 互動式選單函式 ---

def 互動式審核連結():
    global 程式是否執行中
    主執行緒是否忙碌.set()
    try:
        with 執行緒鎖:
            待審核的連結 = list(連結快取.items())
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print("--- 審核連結 (选择要處理的) ---")
        if not 待審核的連結:
            print("佇列為空...")
            time.sleep(1)
            return

        for 索引, (連結, 標題) in enumerate(待審核的連結):
            print(f"  [{索引+1}] {標題}")
        
        使用者選擇 = input(
            "\n請輸入選項：\n"
            "  - 編號(1, 2, 3) - 處理指定編號的項目\n"
            "  - 'n' - 不處理並移除本次選單中的項目\n"
            "  - 'c' - 清空所有待處理項目\n"
            "  - [Enter] - 處理本次選單中的所有項目\n"
            "您的選擇："
        ).strip().lower()

        if 使用者選擇 == '': 使用者選擇 = 'all'
        if 使用者選擇 == 'n':
            待移除的連結 = [項目[0] for 項目 in 待審核的連結]
            with 執行緒鎖:
                for 連結 in 待移除的連結:
                    if 連結 in 連結快取: del 連結快取[連結]
            return
        if 使用者選擇 == 'c':
            with 執行緒鎖: 連結快取.clear()
            return
            
        待處理的連結列表 = []
        if 使用者選擇 == 'all':
            待處理的連結列表 = [項目[0] for 項目 in 待審核的連結]
        else:
            try:
                索引列表 = {int(i.strip()) - 1 for i in 使用者選擇.split(',')}
                待處理的連結列表 = [待審核的連結[i][0] for i in sorted(list(索引列表)) if 0 <= i < len(待審核的連結)]
            except ValueError: print("輸入無效！"); return
        if not 待處理的連結列表: return

        os.system('cls' if os.name == 'nt' else 'clear')
        print("--- 選擇下載內容 ---")
        print(" 1. 僅影片 (MP4)")
        print(" 2. 僅音訊 (MP3)")
        print(" 3. 兩者都要 (最高效)")
        下載選擇 = input("請選擇 [Enter = 3. 兩者都要]：").strip()
        
        類型對應 = {'1': 'video', '2': 'audio', '3': 'both'}
        下載類型 = 類型對應.get(下載選擇, 'both')

        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"準備處理 {len(待處理的連結列表)} 個連結，模式為：{下載類型.upper()}")
        
        with 執行緒鎖:
            for 連結 in 待處理的連結列表:
                if 連結 in 連結快取: del 連結快取[連結]
                
        for 連結 in 待處理的連結列表:
            if not 程式是否執行中: break
            處理下載任務(連結, 下載類型)
        
        print("\n所有選定任務已完成，按任意鍵返回主畫面...")
        if os.name == 'nt':
            os.system('pause >nul')
        else:
            input()

    finally:
        主執行緒是否忙碌.clear()

def 互動式審核檔案():
    # TODO: 此功能待未來版本實現
    print("\n檔案轉換功能待實現...")
    time.sleep(2)
    pass

# --- 步驟 5: 主程式執行區 ---
def 主迴圈():
    global 程式是否執行中
    上次顯示的狀態 = None

    while 程式是否執行中:
        try:
            if 主執行緒是否忙碌.is_set():
                time.sleep(0.5)
                continue

            with 執行緒鎖:
                目前的連結 = list(連結快取.items())
                目前的檔案 = list(待轉換檔案佇列)
            
            目前狀態 = (
                tuple(sorted([項目 for 項目 in 目前的連結 if 項目[1] != "正在擷取標題..."])), 
                tuple(sorted(目前的檔案))
            )

            if 目前狀態 != 上次顯示的狀態:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("="*60)
                print("      全功能媒體下載與轉換工具 (v2.0.1)      ")
                print("      - 動態儀表板 (按 Enter 處理, Ctrl+C 退出)      ")
                print("="*60)

                if 目前的連結:
                    print("\n--- 待處理連結 ---")
                    for 索引, (連結, 標題) in enumerate(目前的連結):
                        print(f"  [{索引+1}] {標題}")
                    print("\n[提示] 正在等待更多連結... (按 Enter 鍵立即處理當前列表)")
                elif 目前的檔案:
                    print("\n--- 待轉換檔案 ---")
                    for 索引, 檔案路徑 in enumerate(目前的檔案):
                         print(f"  [{索引+1}] {os.path.basename(檔案路徑)}")
                    print("\n[提示] 按 Enter 鍵處理檔案轉換...")
                else:
                    print("\n佇列為空，等待從剪貼簿複製連結...")

                上次顯示的狀態 = 目前狀態

            if keyboard.is_pressed('enter'):
                if 目前的連結:
                    互動式審核連結()
                elif 目前的檔案:
                    互動式審核檔案()
                上次顯示的狀態 = None
                time.sleep(0.5)

            time.sleep(0.1)

        except KeyboardInterrupt:
            程式是否執行中 = False
            break
        except Exception as e:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" + "="*60)
            print("發生意外錯誤，請將以下資訊回報給開發者：")
            print(str(e))
            print("程式將在10秒後自動退出...")
            print("="*60)
            time.sleep(10)
            程式是否執行中 = False
            break

if __name__ == "__main__":
    檢查_ffmpeg()
    設定下載資料夾()

    monitor_thread = threading.Thread(target=剪貼簿監控任務)
    monitor_thread.daemon = True
    monitor_thread.start()

    主迴圈()

    print("\n正在關閉執行緒池與程式，請稍候...")
    執行緒池.shutdown(wait=True)
    print("程式已成功退出。")