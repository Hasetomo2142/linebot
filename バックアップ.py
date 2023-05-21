from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

from test import MessageCategorizer


app = Flask(__name__)

# LINE Developersのチャネル基本情報ページで設定したアクセストークンとシークレットを入力
line_bot_api = LineBotApi('i/vmdFKh0Y4WXmoW4Yvi6hgrn9O9EW0EUeSJLwSqJCUCLnFIgoqkc/SJN05Wa5nxUHsysXfAfDTpMsv6tE1oDlGq4L9UIbxOMddyree+2eIYG357FQ/iaHp8OEtrnz/ZzGgfZTJLoIK6L+dAHwCgDwdB04t89/1O/w1cDnyilFU=')
# LINE Developersのチャネル基本情報ページで設定したWebhookのURLを入力
handler = WebhookHandler('fff74914e5c86202a53e4adc858739b6')

# LINE Messaging APIからのWebhookリクエストを受け取るエンドポイントを定義する
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名を取得する
    signature = request.headers['X-Line-Signature']
    # リクエストボディをテキスト形式で取得する
    body = request.get_data(as_text=True)
    # ログにリクエストボディを出力する
    app.logger.info("Request body: " + body)

    try:
        # LINE Messaging APIのSDKを使用して、リクエストの正当性を検証し、イベントハンドラーにリクエストを渡す
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 署名が不正であった場合はエラー400を返す
        abort(400)

    # 正常に処理された場合は'OK'を返す
    return 'OK'





# メッセージイベントを受け取るハンドラーを定義
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    # ユーザーIDを取得
    user_id = event.source.user_id


    # メッセージのカテゴリーを判定
    message_categorizer = MessageCategorizer(user_id)
    message_categorizer.categorize_message(event.message.text)

    # 返信メッセージを生成
    reply_message = message_categorizer.generate_reply()
    reply_message = message_categorizer.category_confirm()

    # LINE Platformにメッセージを返信する
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )




# メイン関数
if __name__ == "__main__":
    # アプリを起動
    app.run()


