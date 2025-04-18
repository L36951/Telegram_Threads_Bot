
"""
1 抓取 <meta name="description"> 的 content

2 抓取 Threads 貼文第一個 `data-pressable-container`，
    2.1 下載其中 <video> 標籤的 src
    2.2 下載其中 <picture> → <img> 的 src
3 上傳到 groupchat
4 Delete file

"""
import os
import uuid
import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from telegram import Update
from telegram import InputMediaPhoto, InputMediaVideo
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Set web drive options
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# driver = webdriver.Chrome(options=options)
# driver.implicitly_wait(5)

# Create folder if not exists
download_folder = "downloads"
os.makedirs(download_folder, exist_ok=True)


# download image/video with stream mode
def download_file(url,extension):
    try:
        unique_filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(download_folder,unique_filename)
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filepath,'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"✅ 已下載: {unique_filename}")
        return filepath
    except Exception as e:
        print(f"❗ 下載失敗: {url}, 錯誤: {e}")
        return None

def process_threads_link(url):
    result_data = {
        "text": "",
        "videos": [],
        "images": []
        }
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        driver.get(url)
        
        #找 meta name="description"
        mata_description = driver.find_element(By.CSS_SELECTOR, "meta[name='description']")
        description_content = mata_description.get_attribute('content')
        result_data['text']=(description_content)
        print(result_data['text'])

        # 找第一個 data‑pressable‑container
        container = driver.find_elements(By.XPATH, "//div[@data-pressable-container]")
        if not container:
            raise RuntimeError("找不到 data‑pressable‑container")

        first = container[0]
        print("✅ 已取得第一個 data‑pressable‑container")
        # 1️⃣ 影片 src
        videos = first.find_elements(By.TAG_NAME, "video")
        if videos:
            print(f"🎬 共有 {len(videos)} 個 <video>：")
            for i, v in enumerate(videos, 1):
                #print(f"{i}. {v.get_attribute('src')}" )
                vdo_path = download_file(v.get_attribute('src'), "mp4")
                result_data["videos"].append(vdo_path)
        else:
            print("😕 沒有找到 <video>")

        # 2️⃣ 圖片 src（<picture><img>）
        img_srcs = []
        pictures = first.find_elements(By.TAG_NAME, "picture")
        for pic in pictures:
            imgs = pic.find_elements(By.TAG_NAME, "img")
            for img in imgs:
                src = img.get_attribute("src")
                if src:
                    img_path = download_file(src, "jpg")

                    result_data["images"].append(img_path)
    except Exception as e:
        print("發生錯誤:", e)
    finally:
        driver.quit()
    return result_data
    
async def handle_threads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "threads.com" not in url and "threads.net" not in url:
        await update.message.reply_text("❗ 請提供有效的 Threads 的貼文連結。")
        return
    try:
        
        result_data = process_threads_link(url)
        media_group = []
        caption_sent = False
        # 添加影片
        for video_path in result_data["videos"]:
            if os.path.exists(video_path):
                if not caption_sent and result_data["text"]:
                    media_group.append(InputMediaVideo(open(video_path, "rb"), caption=result_data["text"]))
                    caption_sent = True
                else:
                    media_group.append(InputMediaVideo(open(video_path, "rb")))
        # 添加圖片
        for image_path in result_data["images"]:
            if os.path.exists(image_path):
                if not caption_sent and result_data["text"]:
                    media_group.append(InputMediaPhoto(open(image_path, "rb"), caption=result_data["text"]))
                    caption_sent = True
                else:
                    media_group.append(InputMediaPhoto(open(image_path, "rb")))
                # 發送媒體群組
        if media_group:
            print("正在上傳 圖片/影片 (如有)")
            await update.message.reply_media_group(media=media_group)
            print("✅ 所有媒體已發送完成！")
        for video_path in result_data["videos"]:
            if os.path.exists(video_path):
                os.remove(video_path)
                print(f"{video_path} 已刪除")
        for image_path in result_data["images"]:
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"{image_path} 已刪除")

    except Exception as e:
        print(f"發生錯誤: {e}")
        await update.message.reply_text("❗ 抱歉，處理過程中發生錯誤。")
                    

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (filters.ChatType.GROUPS | filters.ChatType.PRIVATE), handle_threads))
print("✅ Bot 已啟動")
app.run_polling()