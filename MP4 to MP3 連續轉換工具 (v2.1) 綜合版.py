import sys
import subprocess
import os

# --- 步驟 1: 依賴檢查與自動安裝 ---
try:
    from moviepy import VideoFileClip
    print("依賴套件 'moviepy' 已安裝。")

except ModuleNotFoundError:
    print("錯誤：必要的函式庫 'moviepy' 尚未安裝。")
    consent = input("是否要讓本腳本自動為您安裝 (y/n)？ ").strip().lower()
    if consent == 'y':
        print("\n正在嘗試自動安裝 'moviepy'，請稍候...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
            print("\n========================================================")
            print("🎉 'moviepy' 已成功安裝！")
            print("為了讓新安裝的函式庫生效，請關閉此視窗並重新執行一次本腳本。")
            print("========================================================")
        except Exception as e:
            print(f"\n❌ 自動安裝失敗！請手動執行 'pip install moviepy'。錯誤詳情：{e}")
        input("\n按 Enter 鍵退出...")
        sys.exit()
    else:
        print("使用者取消安裝。程式即將退出。")
        input("\n按 Enter 鍵退出...")
        sys.exit()

# --- 步驟 2: 功能函式定義 ---

def convert_single_file(file_path):
    """處理單一檔案的轉換。"""
    if not file_path.lower().endswith('.mp4'):
        print(f"錯誤：檔案 '{os.path.basename(file_path)}' 不是一個 MP4 檔案。")
        return

    mp3_file_path = os.path.splitext(file_path)[0] + ".mp3"
    print(f"\n[單檔模式] 準備轉換: {os.path.basename(file_path)}")
    try:
        with VideoFileClip(file_path) as video_clip:
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(mp3_file_path)
        print(f"\n轉換成功！🎉 -> {os.path.basename(mp3_file_path)}")
    except Exception as e:
        print(f"\n轉換失敗！錯誤: {e}")

def batch_convert_folder(folder_path):
    """處理整個資料夾的批次轉換。"""
    print(f"\n[批次模式] 正在掃描資料夾：'{folder_path}'\n")
    mp4_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
    
    if not mp4_files:
        print("在該資料夾中沒有找到任何 MP4 檔案。")
        return

    print(f"找到 {len(mp4_files)} 個 MP4 檔案，準備開始轉換...")
    
    for filename in mp4_files:
        mp4_file_path = os.path.join(folder_path, filename)
        mp3_file_path = os.path.splitext(mp4_file_path)[0] + ".mp3"
        
        if os.path.exists(mp3_file_path):
            print(f"--- '{filename}' 已轉換過，跳過。 ---")
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

# --- 步驟 3: 主程式執行區 (智慧判斷核心) ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("      MP4 to MP3 智慧型轉換工具 (v3.0)      ")
    print("   - 可自動判斷檔案或資料夾，並自動安裝依賴   ")
    print("="*50)
    print("提示：可連續拖曳檔案或資料夾進行轉換。")
    print("      若要退出，請輸入 'q' 或 'quit' 再按 Enter。")

    while True:
        input_path = input("\n請拖曳 MP4 檔案或資料夾到此處後按 Enter：").strip()

        if input_path.lower() in ['q', 'quit']:
            print("\n程式已結束，感謝使用！")
            break

        if not input_path:
            print("提示：未輸入任何路徑。請提供路徑，或輸入 'q' 退出。")
            continue

        if input_path.startswith('"') and input_path.endswith('"'):
            input_path = input_path[1:-1]
        
        # --- 核心智慧判斷邏輯 ---
        if os.path.isfile(input_path):
            convert_single_file(input_path)
        elif os.path.isdir(input_path):
            batch_convert_folder(input_path)
        else:
            print(f"錯誤：提供的路徑 '{input_path}' 不存在，或不是一個有效的檔案/資料夾。")
        
        print("\n" + "="*50)