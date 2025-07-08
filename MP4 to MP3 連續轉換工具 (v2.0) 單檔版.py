import os
# v2.0 的主要變更：不再使用 moviepy.editor，而是直接從 moviepy 匯入需要的類別
from moviepy import VideoFileClip

def convert_to_mp3(mp4_file_path):
    """
    將指定的 MP4 檔案轉換為 MP3 檔案 (使用 MoviePy v2.0+ 語法)。
    """
    # 檢查檔案是否存在
    if not os.path.exists(mp4_file_path):
        print(f"錯誤：找不到檔案 '{mp4_file_path}'")
        return

    # 檢查檔案是否為 MP4
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
            # 【修改點 1】移除 logger=None，讓進度條重新出現
            audio_clip.write_audiofile(mp3_file_path) 

        print("\n轉換成功！🎉")
        print(f"MP3 檔案已儲存至：{mp3_file_path}")

    except Exception as e:
        print(f"\n轉換過程中發生錯誤：{e}")


# --- 主程式執行區 ---
if __name__ == "__main__":
    print("===================================")
    print("   MP4 to MP3 連續轉換工具 (v2.0)  ")
    print("===================================")
    # 【修改點 2】更新操作提示
    print("提示：可連續轉換多個檔案。")
    print("      若要退出，請輸入 'q' 或 'quit' 再按 Enter。")

    while True:
        input_path = input("\n請輸入 MP4 檔案路徑（或拖曳檔案進來）：").strip()
        
        # 【修改點 3】重新設計退出和空輸入的邏輯
        # 檢查是否為明確的退出指令
        if input_path.lower() in ['q', 'quit']:
            print("\n程式已結束，感謝使用！")
            break # 跳出 while 迴圈

        # 如果使用者只是按 Enter，提示他重新輸入
        if not input_path:
            print("提示：未輸入任何路徑。請提供檔案路徑，或輸入 'q' 退出。")
            continue # 跳過此次迴圈，直接要求下一次輸入

        # 移除可能的路徑引號
        if input_path.startswith('"') and input_path.endswith('"'):
            input_path = input_path[1:-1]
        
        # 呼叫轉換函式
        convert_to_mp3(input_path)
        
        print("\n" + "="*50)