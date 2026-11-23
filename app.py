from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
import os
import time

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_SECRET)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("Gemini 初始化成功")
except Exception as err:
    print("Gemini 初始化失败：", err)
    model = None

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    print("拿到消息：", text)
    if "@小助手" in text:
        question = text.replace("@小助手", "").strip()
        if not question:
            reply = "请输入问题！"
        elif model is None:
            reply = "❌ Gemini初始化失败"
        else:
            try:
                print("准备调用Gemini，问题：", question)
                res = model.generate_content(question, timeout=10)
                reply = res.text
                print("Gemini返回成功")
            except Exception as e:
                reply = "❌ 错误：" + str(e)
                print("Gemini报错：", str(e))
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
