import mysql.connector
import sshtunnel
import re

class MySQLConnector:
    def __init__(self):
        self.server = None
        self.cnx = None
        self.cur = None

    def connect(self):
        # SSH 接続
        self.server = sshtunnel.SSHTunnelForwarder(
            ("sv14417.xserver.jp", 10022), 
            ssh_username="xs443757", 
            ssh_private_key_password="TomoTomo0420", 
            ssh_pkey="xs443757.key", 
            remote_bind_address=("127.0.0.1", 3306)
        )

        # SSHサーバーを開始
        self.server.start()

        # SSH接続確認
        # print(f"local bind port: {self.server.local_bind_port}")

        # データベース接続
        self.cnx = mysql.connector.connect(
            host="127.0.0.1", 
            port=self.server.local_bind_port, 
            user="xs443757_root", 
            password="TomoTomo0420",  # パスワードの修正
            database="xs443757_test", 
            charset="utf8",
            use_pure=True
        )

        # 接続確認
        # print(f"sql connection status: {self.cnx.is_connected()}")

        # データベース操作用カーソル
        self.cur = self.cnx.cursor(buffered=True)

    #selectなど返り値がある場合    
    def execute_query(self, sql):
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        return rows
    
    #insertなど返り値がない場合    
    def execute_query2(self, sql):
        try:
            #ログ確認用
            print("SQL >>> {}".format(sql))

            self.cur.execute(sql)
            self.cnx.commit() # self.connをself.cnxに修正
            print("SQL文を実行しました。")
        except Exception as e:
            print(f"SQL実行エラー: {e}")
            self.cnx.rollback() # self.connをself.cnxに修正



    def close(self):
        # 終了
        self.cur.close()
        self.cnx.close()
        self.server.stop()


    #SQLインジェクション対策を行う（※要改善）
    @staticmethod
    def escape_string(input_str):
        # シングルクォートをエスケープする
        escaped_str = re.sub(r"\'", "\'\'", input_str)
        return escaped_str
