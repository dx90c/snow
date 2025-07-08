import sys
import subprocess
import os

# --- 步驟 1: 依賴檢查與自動安裝 ---
try:
    # 嘗試匯入函式庫，如果成功，什麼都不做
    from moviepy import VideoFileClip
    print("依賴套件 'moviepy' 已安裝。")

except ModuleNotFoundError:
    # 如果找不到函式庫，執行以下安裝邏輯
    print("錯誤：必要的函式庫 'moviepy' 尚未安裝。")
    
    # 詢問使用者是否同意安裝
    consent = input("是否要讓本腳本自動為您安裝 (y/n)？ ").strip().lower()

    if consent == 'y':
        print("\n正在嘗試自動安裝 'moviepy'，請稍候...")
        print("這可能需要幾分鐘時間，特別是第一次下載 FFMPEG 時。")
        
        try:
            # 使用 sys.executable 確保我們用的是當前 Python 環境的 pip
            # 這能避免多個 Python 版本導致的安裝位置錯誤
            subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
            
            print("\n========================================================")
            print("🎉 'moviepy' 已成功安裝！")
            print("為了讓新安裝的函式庫生效，請關閉此視窗並重新執行一次本腳本。")
            print("========================================================")

        except Exception as e:
            print("\n--------------------------------------------------------")
            print("❌ 自動安裝失敗！")
            print("請手動打開您的終端機 (CMD/PowerShell) 並執行以下指令：")
            print(f"   pip install moviepy")
            print(f"錯誤詳情：{e}")
            print("--------------------------------------------------------")
            
        # 無論成功或失敗，都退出腳本，讓使用者手動重啟
        input("\n按 Enter 鍵退出...")
        sys.exit()
    else:
        print("使用者取消安裝。程式即將退出。")
        input("\n按 Enter 鍵退出...")
        sys.exit()

# --- 步驟 2: 主要功能程式碼 (如果檢查通過，才會執行到這裡) ---

def convert_to_mp3(mp4_file_path):
    """
    將指定的 MP4 檔案轉換為 MP3 檔案 (使用 MoviePy v2.0+ 語法)。
    """
    if not os.path.exists(mp4_file_path):
        print(f"錯誤：找不到檔案 '{mp4_file_path}'")
        return

    if not mp4_file_path.lower().endswith('.mp4'):
        print(f"錯誤：'{mp4_file_path}' 不是一個 MP4 檔案。")
        return

    file_name_without_extension, _ = os.path.splitext(mp4_file_path)
    mp3_file_path = file_name_without_extension + ".mp3"

    print(f"\n準備轉換：'{mp4_file_path}'")
    print(f"輸出檔案：'{mp3_file_path}'")

    try:
        with VideoFileClip(mp4_file_path) as video_clip:
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(mp3_file_path) 

        print("\n轉換成功！🎉")
        print(f"MP3 檔案已儲存至：{mp3_file_path}")

    except Exception as e:
        print(f"\n轉換過程中發生錯誤：{e}")


# --- 步驟 3: 主程式執行區 ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("   MP4 to MP3 連續轉換工具 (v2.0)  ")
    print("   - 可自動安裝依賴套件           ")
    print("="*50)
    print("提示：可連續轉換多個檔案。")
    print("      若要退出，請輸入 'q' 或 'quit' 再按 Enter。")

    while True:
        input_path = input("\n請輸入 MP4 檔案路徑（或拖曳檔案進來）：").strip()
        
        if input_path.lower() in ['q', 'quit']:
            print("\n程式已結束，感謝使用！")
            break

        if not input_path:
            print("提示：未輸入任何路徑。請提供檔案路徑，或輸入 'q' 退出。")
            continue

        if input_path.startswith('"') and input_path.endswith('"'):
            input_path = input_path[1:-1]
        
        convert_to_mp3(input_path)

        print("\n" + "="*50)