from server import MySQLConnector

class Register:
    def __init__(self, event):
        # eventからuser_idを抽出
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
            self.scenario = rows[0][3]
        else:
            # 実行結果が存在しない場合は、初期値を設定
            self.user_id = user_id
            self.category = "NULL"
            self.sequence = "NULL"
            self.scenario = "NULL"

    #シークエンスを変更
    def alter_sequence(self, sequence_name):
        # MySQLConnectorインスタンスの生成
        my_sql_connector = MySQLConnector()
        # データベースに接続
        my_sql_connector.connect()

        # クエリの実行
        sql = "UPDATE user_status SET sequence = '{}' WHERE user_id = '{}';".format(sequence_name, self.user_id)
        my_sql_connector.execute_query2(sql)

    

    #シナリオを変更
    def alter_scenario(self, scenario_name):
        # MySQLConnectorインスタンスの生成
        my_sql_connector = MySQLConnector()
        # データベースに接続
        my_sql_connector.connect()

        # クエリの実行
        sql = "UPDATE user_status SET scenario = '{}' WHERE user_id = '{}';".format(scenario_name, self.user_id)
        my_sql_connector.execute_query2(sql)    



    #次のシークエンスを求める（正しい順序で変更されているかチェック）
    def next_sequence(self, event):

        #初期設定シナリオ
        setup_scenario = ['asking_attribute','next_scenario']
        
        # 管理者のシナリオ
        register_admin_scenario = ['asking_user_name', 'asking_company_name', 'input_confirmation', 'complete']

        # 従業員のシナリオ
        register_employee_scenario = ['asking_user_name', 'asking_company_code', 'input_confirmation', 'complete']

        # 現在のcategory, sequence, scenarioを格納
        current_category = self.category
        current_sequence = self.sequence_employee_scenario"
        
            if current_sequence in register_employee_scenario:
                next_sequence = register_employee_scenario
                [register_employee_scenario.index(current_sequence) + 1]
            else:
                #シナリオがそれ以上進めない場合、次のシナリオに移行
                next_sequence = 'sking_user_name'
        
        elif current_scenario == "register_admin_scenario":
            if current_sequence in register_admin_scenario:
                next_sequence = register_admin_scenario[register_admin_scenario.index(current_sequence) + 1]
            else:
                next_sequence = 'asking_user_name'
        
        elif current_scenario == "setup_scenario":
            if current_sequence in setup_scenario:
                next_sequence = setup_scenario[setup_scenario.index(current_sequence) + 1]
            else:
                next_sequence = 'None3'

        else:
            next_sequence = 'None4'

        return next_sequence


    #user_statusより適切な処理を実行する
    def message_handling(self, sequence, scenario, event):
        #友達登録後の処理

        # データベースに接続
        my_sql_connector = MySQLConnector()
        my_sql_connector.connect()

        reply_message = 'ERROR'
        user_id = event.source.user_id


        #setup_scenarioの処理
        if scenario == 'setup_scenario':
            if sequence == 'asking_attribute':
                # 管理者か従業員かの判定
                attribute = event.message.text
                if attribute in ['admin', 'employee']:
                    sql = "INSERT INTO temporary_users (user_id, attribute) VALUES ('{}', '{}');".format(user_id,attribute)
                    try:
                        my_sql_connector.execute_query2(sql)
                        self.alter_sequence(self.next_sequence(event))

                        #次の処理を促すメッセージを送信
                        reply_message = '処理が実行されました。'
                    except:
                        reply_message = 'データベース処理で問題が発生しました。'
                    finally:
                        # MySQLConnectorインスタンスの破棄
                        my_sql_connector.close()
                else:
                    reply_message = '正しい値を入力してください。'
            
            elif sequence == 'next_scenario':
                #仮ユーザー属性を参照（管理者orユーザー）
                sql = "SELECT attribute FROM `temporary_users` WHERE user_id = '{}'".format(user_id)

                #SQLを実行しユーザー属性を取得
                rows = my_sql_connector.execute_query(sql)
                attribute = rows[0][0]


                #ユーザー属性より適切なシナリオを選択                
                if attribute == 'admin':
                    self.alter_scenario('register_admin_scenario')
                elif attribute == 'employee':
                    self.alter_scenario('register_employee_scenario')
                else:
                    reply_message = 'ERROR:ATTRIBUTE'
                
                self.alter_sequence('asking_user_name')


                reply_message = '名前を入力してください。'

            else:
                return 'SEQUENCE_ERROR'


        elif scenario in ['register_admin_scenario', 'register_employee_scenario']:
            #管理者と従業員の共通の処理

            if sequence == 'asking_user_name':
                
                #入力文字列に対しての処理
                user_name = event.message.text
                
                
                sql = "UPDATE `temporary_users` SET `name`= '{}' WHERE user_id = '{}'".format(user_name,user_id)
                try:
                    my_sql_connector.execute_query2(sql)
                    self.alter_sequence(self.next_sequence(event))
                    reply_message = '処理が実行されました。'
                except:
                    reply_message = 'データベース処理で問題が発生しました。'
                finally:
                    # MySQLConnectorインスタンスの破棄
                    my_sql_connector.close()
            
            elif sequence == 'input_confirmation':
                reply_message = 'まだ実装されていません。'
            
            elif sequence == 'asking_company_code':
                reply_message = 'まだ実装されていません。'

                

            
            
            
            else:
                reply_message = '正しい値を入力してください。'




        else:
            return 'SCENARIO_ERROR'        
            
        return reply_message

