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
    print(f"気象庁お天気Botが起動しました: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!weather"):
        args = message.content.split()
        
        # 地域名が指定されていない場合は「東京」をデフォルトにする
        target_area = "東京" if len(args) == 1 else args[1]
        
        try:
            # 気象庁の全国地域定義リスト（地域検索用マスターデータ）にアクセス
            area_url = "https://jma.go.jp"
            area_data = requests.get(area_url).json()
            
            area_code = None
            # 全国の「〇〇市」「〇〇町」「〇〇区」の名称から、気象庁の地域コードを自動検索
            for code, info in area_data.get("offices", {}).items():
                if target_area in info.get("name", ""):
                    area_code = code
                    break
            
            if not area_code:
                for code, info in area_data.get("class10s", {}).items():
                    if target_area in info.get("name", ""):
                        area_code = code[:3] + "000" if len(code) >= 3 else code
                        break

            if not area_code:
                await message.channel.send(f"❌ 「{target_area}」という地域名が気象庁のリストから見つかりません。都道府県名や有名な市、区の名前（例: 大阪、札幌、新宿区）でお試しください。")
                return
            
            # 判明した地域コードを使って、気象庁公式の最新お天気データを取得
            weather_url = f"https://jma.go.jp{area_code}.json"
            res = requests.get(weather_url).json()
            
            time_series = res[0]["timeSeries"]
            areas = time_series[0]["areas"]
            
            weather_text = "データなし"
            for area in areas:
                if "weathers" in area:
                    weather_text = area["weathers"][0]
                    break
            
            temp_text = "--"
            if len(res[0]["timeSeries"]) > 2:
                temp_areas = res[0]["timeSeries"][2]["areas"]
                for ta in temp_areas:
                    if "temps" in ta and len(ta["temps"]) > 0:
                        temp_text = f"{ta['temps'][0]}"
                        break
            
            result = f"【気象庁発表・今日のお天気（{target_area}周辺）】\n天気: {weather_text}\n予想気温: {temp_text}℃"
            await message.channel.send(result)
            
        except Exception as e:
            await message.channel.send(f"❌ お天気データの解析中にエラーが発生しました。(詳細: {e})")

client.run(os.environ.get("DISCORD_TOKEN"))
