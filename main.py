import os
import discord
import random
import json
from dotenv import load_dotenv

# -----変数-----
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
JSON_FILE = 'media.json'

# 説明文やプロフィールの管理
TEXT_DATA = {
    "description": (
        "【使い方】\n"
        "送信されたワードに応じて三宅美羽さんのXアカウント(@_mmiya_mm)のメディア欄のリンクを1つ返します。\n\n"
        "みやけ：全ての写真\n"
        "みー：みーの顔が写っている写真\n"
        "日付：指定した日付の写真(2024, 202501, 20260324など)\n"
    ),
    "profile": (
        "**プロフィール**\n\n"
        "生年月日\t2001/12/14\n"
        "身長\t151cm\n"
        "特技\t耳の穴に耳を入れること。\n"
        "https://x.com/_mmiya_mm\n"
        "https://www.instagram.com/miyake_miu_/"
    )
}

# ユーザーの入力と内部タグの紐付け
TRIGGER_MAP = {
    "みー": "miu",
    "食べ物": "food",
    "スクショ": "screenshot",
    "その他": "other",
    "みやけ": None  # Noneの場合は全件から抽出
}

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

media_data = []

# JSONファイルを読み込む
def load_media_json():
    global media_data
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            media_data = json.load(f)
        print(f"成功: {len(media_data)} 件のデータを読み込みました。")
    except Exception as e:
        print(f"エラー: {JSON_FILE} の読み込みに失敗しました: {e}")

def format_date_query(query):
    """数字の入力をtimestamp形式(YYYY/MM/DD)に変換する"""
    if not query.isdigit():
        return None
    
    length = len(query)
    if length == 4:    # 2024
        return query
    elif length == 6:  # 202403 -> 2024/03
        return f"{query[:4]}/{query[4:]}"
    elif length == 8:  # 20240301 -> 2024/03/01
        return f"{query[:4]}/{query[4:6]}/{query[6:]}"
    return None

def get_random_url(query):
    """条件に一致するURLをランダムに1つ返す"""
    if not media_data:
        return None
    
    # 1. TRIGGER_MAPによるタグ検索
    if query in TRIGGER_MAP:
        tag = TRIGGER_MAP[query]
        if tag:
            results = [item['url'] for item in media_data if tag in item.get("subject", [])]
        else:
            results = [item['url'] for item in media_data]
        if results: return random.choice(results)

    # 2. 数字による日付前方一致検索
    date_prefix = format_date_query(query)
    if date_prefix:
        results = [item['url'] for item in media_data if item.get("timestamp", "").startswith(date_prefix)]
        if results: return random.choice(results)

    # 3. noteフィールドの検索
    results = [item['url'] for item in media_data if query in item.get("note", [])]
    if results: return random.choice(results)

    return None

@client.event
async def on_ready():
    load_media_json()
    print(f'ログインしました: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content

    # 固定コマンドへの反応
    if content == "使い方":
        await message.channel.send(TEXT_DATA["description"])
        return
    elif content == "プロフィール":
        await message.channel.send(TEXT_DATA["profile"])
        return

    # 条件検索の実行
    url = get_random_url(content)
    if url:
        await message.channel.send(url)

client.run(DISCORD_TOKEN)