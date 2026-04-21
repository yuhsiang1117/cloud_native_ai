import os
from datetime import datetime
import asyncio
import discord
from ollama import AsyncClient

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

ollama_client = AsyncClient(host='http://ollama-server:11434')

@client.event
async def on_ready():
    print(f'✅ 成功登入為 {client.user}')

@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    if client.user in message.mentions:

        reply_msg = await message.reply("⏳ 正在讀取紀錄並生成摘要，請稍候...")
            
        history_messages = []
        async for msg in message.channel.history(limit=25):
            if msg.author.bot:
                continue
            history_messages.append(msg)
        
        history_messages.reverse()

        today = datetime.now()

        weekdays_tw = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_weekday = weekdays_tw[today.weekday()]

        today_date_str = today.strftime("%Y/%m/%d")
        today_full_info = f"{today_date_str} {current_weekday}"

        prompt_messages = [
            {
                "role": "system", 
                "content": f"""
                    Ignore all previous instructions.
                    You are a professional AI assistant for an enterprise chat room.

                    Your task is to analyze the chat records provided by the user and strictly adhere to the following requirements:

                    1. [Schedule Consolidation]: Please accurately extract the "Date" and the "Corresponding Event" from the conversation.
                        - [Current System Date]: Today is {today_full_info}.
                        - If relative times such as "tomorrow", "next week", "Saturday" appear in the conversation, or if a specific date is not specified, you must calculate the exact date (Format: YYYY/MM/DD) based on the [Current System Date].
                        - If the exact date cannot be calculated from the relative date in the conversation, add a note: "Unable to calculate exact date", don't reply relative times.
                        - If there are multiple events, please list all of them. If the same event is mentioned multiple times, only list it once.
                        - Ignore technical discussions that are unrelated to the schedule. If no dates are mentioned, please reply with "No schedule information found".
                        - List the events in chronological order.
                        - Format constraint: If no specific time is mentioned, omit the time entirely and use "[Date]: [Event]". If a specific time is mentioned, you MUST use the 24-hour format (e.g., 15:30) and use "[Date] [Time]: [Event]".
                    2. [Confidentiality Check]: Check if the content contains suspected passwords, API keys, undisclosed project architectures, or sensitive personal information. Please provide a conclusion of either "Safe" or "Risk of Leakage", and briefly state the reason.

                    [Output Specifications]
                        - You must reply entirely in Traditional Chinese.
                        - Fabricating information not mentioned in the records is strictly prohibited (No hallucination).
                        - Use a bulleted Markdown format for the output to ensure the layout is clean and easy to read.
                """
            }
        ]

        for msg in history_messages:
            clean_content = msg.clean_content 
            prompt_messages.append({
                "role": "user", 
                "content": f"[{msg.author.display_name}]: {clean_content}"
            })

        try:
            stream = await ollama_client.chat(model='gemma4:e2b', messages=prompt_messages, stream=True)
            
            collected_text = ""
            update_interval = 2.0
            last_update_time = asyncio.get_event_loop().time()

            async for chunk in stream:
                chunk_text = chunk['message']['content']
                if chunk_text:
                    collected_text += chunk_text
                    current_time = asyncio.get_event_loop().time()

                    if current_time - last_update_time > update_interval:
                        await reply_msg.edit(content=collected_text)
                        last_update_time = current_time

            if collected_text:
                await reply_msg.edit(content=collected_text)
            else:
                await reply_msg.edit(content="⚠️ 模型沒有回傳任何內容，請檢查模型狀態。")
            
        except Exception as e:
            await reply_msg.edit(content=f"❌ 呼叫模型時發生錯誤: {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ 找不到 DISCORD_TOKEN 環境變數，請確認是否已正確設定！")
    else:
        client.run(TOKEN)