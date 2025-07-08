import os
# v2.0 的主要變更：不再使用 moviepy.editor，而是直接從 moviepy 匯入需要的類別
from moviepy import VideoFileClip

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
    
    # 遍歷資料夾中的所有檔案
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
                # 【修改點 1】移除 logger=None，讓進度條重新出現
                audio_clip.write_audiofile(mp3_file_path)
            print(f"成功 -> '{os.path.basename(mp3_file_path)}'")
        except Exception as e:
            print(f"失敗 -> {filename}, 錯誤: {e}")
        print("-" * 40)

    print("\n此資料夾的所有轉換任務已完成！")


# --- 主程式執行區 ---
if __name__ == "__main__":
    print("=========================================")
    print(" MP4 to MP3 連續批次轉換工具 (v2.0) ")
    print("=========================================")
    # 【修改點 2】更新操作提示
    print("提示：可連續處理多個資料夾。")
    print("      若要退出，請輸入 'q' 或 'quit' 再按 Enter。")

    while True:
        input_folder = input("\n請輸入包含 MP4 的資料夾路徑（或拖曳資料夾進來）：").strip()

        # 【修改點 3】加入與單一檔案版相同的退出和空輸入邏輯
        if input_folder.lower() in ['q', 'quit']:
            print("\n程式已結束，感謝使用！")
            break

        if not input_folder:
            print("提示：未輸入任何路徑。請提供資料夾路徑，或輸入 'q' 退出。")
            continue

        if input_folder.startswith('"') and input_folder.endswith('"'):
            input_folder = input_folder[1:-1]
        
        # 呼叫批次轉換函式
        batch_convert_folder(input_folder)

        print("\n" + "="*50)