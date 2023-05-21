from server import MySQLConnector
class MessageCategorizer:
    
    def __init__(self, event):

        #eventからuser_idを抽出
        user_id = event.source.user_id
        # MySQLConnectorインスタンスの生成
        my_sql_connector = MySQLConnector()
        # データベースに接続
        my_sql_connector.connect()

        # クエリの実行
        sql = "SELECT * FROM `user_status` WHERE user_id = '{}'".format(user_id)
        rows = my_sql_connector.execute_query(sql)

        # 実行結果が存在する場合にフィールドに格納
        if rows:
            self.user_id = rows[0][0]
            self.category = rows[0][1]
            self.sequence = rows[0][2]
        else:
            # 実行結果が存在しない場合は、初期値を設定
            self.user_id = user_id
            self.category = "NULL"
            self.sequence = "NULL"


    #処理が完了しているかを判定        
    def sequence_cheker(self,event):
        if self.sequence == 'complete':
            return True
        else:
            return False
        
    
    #コマンドの判定
    def command_cheker(self, event):
        #コマンドの場合はTureを返す
        if event.message.text == 'register':
            return True
        elif event.message.text == 'shift_request':
            return True
        #コマンドでない場合はFalseを返す
        else:
            return False


    #categoryを変更
    def alter_category(self,event): 
        return True
    
    #入力されたコマンドの種類を識別し適切なクラス名を返す
    def comand_categoriz(self,event):
        #コマンドの場合はTureを返す
        if event.message.text == 'register':
            self.category = 'register'
            return True
        elif event.message.text == 'shift_request':
            self.category = 'shift_request'
            return True
        #コマンドでない場合はFalseを返す
        else:
            return False

    #入力されたメッセージの種類を判別し適切なクラス名を返す  
    def message_categorize(self,event):
        current_category = self.category


    def system_call(self,event):

        # データベースに接続
        my_sql_connector = MySQLConnector()
        my_sql_connector.connect()
        
        user_id = event.source.user_id
        

        if event.message.text == 'reset':
            sql = "DELETE FROM user_status WHERE user_id = '{}';".format(user_id)
            my_sql_connector.execute_query2(sql)
            
            sql = "DELETE FROM temporary_users WHERE user_id = '{}';".format(user_id)
            my_sql_connector.execute_query2(sql)

            my_sql_connector.close()
            return True
        else:
            return False     