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

def batch_convert_folder(folder_path):
    """
    掃描指定資料夾，並將所有 MP4 檔案轉換為 MP3 (使用 MoviePy v2.0+ 語法)。
    """
    if not os.path.isdir(folder_path):
        print(f"錯誤：'{folder_path}' 不是一個有效的資料夾路徑。")
        return

    print(f"\n正在掃描資料夾：'{folder_path}'\n")
    
    mp4_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
    
    if not mp4_files:
        print("在該資料夾中沒有找到任何 MP4 檔案。")
        return

    print(f"找到 {len(mp4_files)} 個 MP4 檔案，準備開始轉換...")
    
    for filename in mp4_files:
        mp4_file_path = os.path.join(folder_path, filename)
        mp3_file_path = os.path.splitext(mp4_file_path)[0] + ".mp3"
        
        if os.path.exists(mp3_file_path):
            print(f"--- '{os.path.basename(mp3_file_path)}' 已存在，跳過。 ---")
            continue

        print(f"--- 正在轉換: {filename} ---")
        try:
            with VideoFileClip(mp4_file_path) as video_clip:
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(mp3_file_path)
            print(f"成功 -> '{os.path.basename(mp3_file_path)}'")
        except Exception as e:
            print(f"失敗 -> {filename}, 錯誤: {e}")
        print("-" * 40)

    print("\n此資料夾的所有轉換任務已完成！")


# --- 步驟 3: 主程式執行區 ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print(" MP4 to MP3 連續批次轉換工具 (v2.0) ")
    print("   - 可自動安裝依賴套件           ")
    print("="*50)
    print("提示：可連續處理多個資料夾。")
    print("      若要退出，請輸入 'q' 或 'quit' 再按 Enter。")

    while True:
        input_folder = input("\n請輸入包含 MP4 的資料夾路徑（或拖曳資料夾進來）：").strip()

        if input_folder.lower() in ['q', 'quit']:
            print("\n程式已結束，感謝使用！")
            break

        if not input_folder:
            print("提示：未輸入任何路徑。請提供資料夾路徑，或輸入 'q' 退出。")
            continue

        if input_folder.startswith('"') and input_folder.endswith('"'):
            input_folder = input_folder[1:-1]
        
        batch_convert_folder(input_folder)

        print("\n" + "="*50)