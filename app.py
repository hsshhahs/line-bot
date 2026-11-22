from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
import os

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_SECRET"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# 改成你机器人的@ID
BOT_AT = "@188syzg"

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
    # 没有@机器人直接跳过，不说话
    if BOT_AT not in msg:
        return
    # 去掉@标记，拿到问题
    question = msg.replace(BOT_AT, "").strip()
    try:
        # 叫Gemini回答
        ai_result = model.generate_content(question)
        answer = ai_result.text
    except Exception as e:
        answer = "抱歉，AI暂时无法回答这个问题"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(answer))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
