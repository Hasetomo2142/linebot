from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FollowEvent
)

from categorize import MessageCategorizer
from server import MySQLConnector
from register_graph import Register


app = Flask(__name__)

# LINE Developersのチャネル基本情報ページで設定したアクセストークンとシークレットを入力
line_bot_api = LineBotApi('*********')
# LINE Developersのチャネル基本情報ページで設定したWebhookのURLを入力
handler = WebhookHandler('*********')

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

#フォローイベントを受け取るハンドラーを定義
@handler.add(FollowEvent)
def handle_follow(event):
    # フォローされた場合の処理
    # ユーザーIDを用いてuser_statusにデータを挿入

    user_id = event.source.user_id
    
    # MySQLConnectorインスタンスの生成
    my_sql_connector = MySQLConnector()
    # データベースに接続
    my_sql_connector.connect()

    # クエリの実行
    sql = "INSERT INTO user_status (user_id, category, sequence) VALUES ('{}', '{}', '{}');".format(user_id,'register','Asking_Attribution')
    print(sql)
    rows = my_sql_connector.execute_query2(sql)


    reply_message = "初期設定：管理者or従業員を選択してください。"

    # LINE Platformにメッセージを返信する
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )




# メッセージイベントを受け取るハンドラーを定義
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):


    user_id = event.source.user_id
    
    # 返信メッセージを生成
    message_categorizer = MessageCategorizer(event)

    if message_categorizer.system_call(event):
        reply_message = 'リセットします。'
        handle_follow(event)
        return
    
    #前回の処理が完了しているか
    if message_categorizer.sequence_cheker(event):
        #処理が完了している場合

        #入力文字列がコマンドかどうか確認
        if message_categorizer.command_cheker(event):
            #コマンドの場合
            reply_message = 'コマンドが入力されました。'
        else:
            #自然言語の場合
            reply_message = '自然言語をコマンドに変換します。'
    else:
        #処理が完了していない場合

        #入力文字列がコマンドかどうか確認
        if message_categorizer.command_cheker(event):
            #コマンドの場合
            reply_message = '前回の処理が完了していないため、コマンドを実行できません。'
        else:
            #自然言語の場合
            #各クラスに処理を依頼
            if message_categorizer.category == 'register':
                process = Register(event)
            else:
                print("------------EROOR-----")
            
            reply_message = process.message_handling()


    # LINE Platformにメッセージを返信する
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )




# メイン関数
if __name__ == "__main__":
    # アプリを起動
    app.run()


