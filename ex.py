from server import MySQLConnector
from categorize import MessageCategorizer

# MySQLConnectorインスタンスの生成
my_sql_connector = MySQLConnector()
# データベースに接続
my_sql_connector.connect()

sql = "SELECT * FROM `user_status` WHERE user_id = 'asdf0001'"
rows = my_sql_connector.execute_query(sql)

message_categorizer = MessageCategorizer(event)

print(rows[0][0])
