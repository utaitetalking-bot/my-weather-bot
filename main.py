import discord
import requests
import os

# 自動通知・動作させたいDiscordのチャンネルID
CHANNEL_ID = 1509254113953583204

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 全国47都道府県・主要地域とライブドア天気コードの対応表
CITY_MAP = {
    "札幌": "016010", "青森": "020010", "盛岡": "030010", "仙台": "040010", "秋田": "050010",
    "山形": "060010", "福島": "070010", "水戸": "080010", "宇都宮": "090010", "前橋": "100010",
    "さいたま": "110010", "千葉": "120010", "東京": "130010", "横浜": "140010", "新潟": "150010",
    "富山": "160010", "金沢": "170010", "福井": "180010", "甲府": "190010", "長野": "200010",
    "岐阜": "210010", "静岡": "220010", "名古屋": "230010", "津": "240010", "大津": "250010",
    "京都": "260010", "大阪": "270000", "神戸": "280010", "奈良": "290010", "和歌山": "300010",
    "鳥取": "310010", "松江": "320010", "岡山": "330010", "広島": "340010", "山口": "350020",
    "徳島": "360010", "高松": "370010", "松山": "380010", "高知": "390010", "福岡": "400010",
    "佐賀": "410010", "長崎": "420010", "熊本": "430010", "大分": "440010", "宮崎": "450010",
    "鹿児島": "460010", "那覇": "471010"
}

@client.event
async def on_ready():
    print(f"お天気Botが正常に起動しました: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!weather"):
        args = message.content.split()
        
        # 地域名が指定されていない場合は「東京」をデフォルトにする
        target_area = "東京" if len(args) == 1 else args[1]
        
        # 入力されたキーワードから地域コードを探す
        area_code = None
        location_name = None
        for key, code in CITY_MAP.items():
            if key in target_area:
                area_code = code
                location_name = key
                break
                
        if not area_code:
            await message.channel.send(f"❌ 「{target_area}」はお天気リストに見つかりません。都道府県名や有名な主要都市名（例: 大阪、札幌、那覇）を漢字で入力してください。")
            return
            
        # URLの記号ズレが絶対に起きないように、あらかじめスラッシュを結合して指定
        url = "https://tsukumijima.net" + area_code
        
        try:
            res = requests.get(url).json()
            forecasts = res["forecasts"]
            today = forecasts[0]  # 今日のデータを指定
            
            date_label = today["dateLabel"]
            telop = today["telop"]
            
            # 気温データの抽出（NULLチェック）
            temp = today["temperature"]
            max_t = temp["max"]["celsius"] if temp.get("max") and temp["max"].get("celsius") else "--"
            min_t = temp["min"]["celsius"] if temp.get("min") and temp["min"].get("celsius") else "--"
            
            result = f"【ライブドア天気発表・{date_label}のお天気（{location_name}周辺）】\n天気: {telop}\n最高気温: {max_t}℃\n最低気温: {min_t}℃"
            await message.channel.send(result)
            
        except Exception as e:
            await message.channel.send(f"❌ お天気データの読み込み中にエラーが発生しました。(詳細: {e})")

client.run(os.environ.get("DISCORD_TOKEN"))
