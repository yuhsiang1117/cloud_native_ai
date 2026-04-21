import ollama

messages = [
    {"role": "system", "content": "你是一個企業聊天室的智慧助理，負責幫忙統整聊天紀錄中的日期，以及檢查聊天紀錄是否合乎公司機密規範。"},
    {"role": "user", "content": "幫我寫一個可以列出當前目錄下所有隱藏檔案的終端機指令。"}
]

print("Thinking...")

response = ollama.chat(model='gemma4:e2b', messages=messages)

print("\nGemma:")
print(response['message']['content'])