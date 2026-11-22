from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
import os

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_SECRET"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# 改成@小助手
BOT_AT = "@小助手"

@app.route("/callback", methods=["POST"])
def callback():
    sig = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, sig)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def reply(event):
    msg = event.message.text.strip()
    if BOT_AT not in msg:
        return
    question = msg.replace(BOT_AT, "").strip()

    if not GEMINI_API_KEY:
        answer = "⚠️ 还没有填入Gemini API Key，暂时无法使用AI回答！"
    else:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            ai_result = model.generate_content(question)
            answer = ai_result.text
        except Exception as e:
            answer = "❌ AI出错了，稍后再试"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(answer))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
