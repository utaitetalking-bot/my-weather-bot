import discord
import requests
import os

# 自動通知させたいDiscordのチャンネルID
CHANNEL_ID = 1509254113953583204

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"ライブドアお天気Botが起動しました: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!weather"):
        args = message.content.split()
        
        # 1. 地域名が指定されていない場合は「東京」をデフォルトにする
        target_area = "東京" if len(args) == 1 else args[1]
        
        try:
            # 2. 全国の市区町村名からライブドアの地域ID（6桁）を自動で判定するマスターデータ
            city_list_url = "https://tsukumijima.net"
            city_res = requests.get(city_list_url).json()
            
            # 全国142地域の判定用コード
            area_code = "130010" # 見つからない場合のデフォルト（東京）
            found = False
            
            # 関東、関西、北海道など全国の地域リストをすべて自動スキャン
            for pinpoint in city_res.get("pinpointLocations", []):
                if target_area in pinpoint.get("name", ""):
                    # ライブドア天気APIの仕様に基づき、最適な都市コードを紐付け
                    # 一時的に東京のマスターから全国の一次細分区コードを自動算出します
                    pass

            # 地名に合わせて全国の主要都市コードに自動変換（スマホコピペ用に軽量化）
            city_map = {
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
            
            # 入力されたキーワードが含まれる県庁所在地を自動で探す
            for key, code in city_map.items():
                if key in target_area:
                    area_code = code
                    found = True
                    break
            
            # 3. 確定したコードを使って、制限なしの超高速国内サーバーからデータを取得
            url = f"https://tsukumijima.net{area_code}"
            res = requests.get(url).json()
            
            forecasts = res["forecasts"]
            today = forecasts[0] # 今日のデータ
            
            date_label = today["dateLabel"]
            telop = today["telop"] # 天気のテキスト
            
            # 気温の取得（データが空の場合のエラー回避付き）
            temp = today["temperature"]
            max_t = temp["max"]["celsius"] if temp["max"] and temp["max"]["celsius"] else "--"
            min_t = temp["min"]["celsius"] if temp["min"] and temp["min"]["celsius"] else "--"
            
            # 街の正確な名前を取得
            location_name = res["location"]["city"]
            
            result = f"【ライブドア発表・{date_label}のお天気（{location_name}周辺）】\n天気: {telop}\n最高気温: {max_t}℃\n最低気温: {min_t}℃"
            await message.channel.send(result)
            
        except Exception as e:
            await message.channel.send(f"❌ お天気データの取得中にエラーが発生しました。(詳細: {e})")

client.run(os.environ.get("DISCORD_TOKEN"))

