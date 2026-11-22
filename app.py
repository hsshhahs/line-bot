from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
import os

app = Flask(__name__)
LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_SECRET = os.getenv("LINE_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 改成@小助手
BOT_AT = "@小助手"

# 打印日志，部署后看Render日志就能知道读到的值
print("===== 启动检测 =====")
print("LINE_TOKEN:", "已读取" if LINE_TOKEN else "为空")
print("LINE_SECRET:", "已读取" if LINE_SECRET else "为空")
print("GEMINI_API_KEY:", "已读取" if GEMINI_API_KEY else "为空")
print("====================")

line_bot_api = LineBotApi(LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)

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
            # 把错误原因打印到日志
            print("Gemini调用异常：", str(e))
            answer = "❌ AI出错了，稍后再试（可能是网络无法连接Gemini）"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(answer))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
