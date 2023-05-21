from server import MySQLConnector
import networkx as nx
import re
import uuid
from matplotlib import pyplot as plt



#シナリオを有向グラフとして生成
G = nx.DiGraph()

# ノードを追加する
G.add_node('Beginning')
G.add_node('Asking_Attribution')
G.add_node('Asking_User_Name')
G.add_node('Asking_Company_Name')
G.add_node('Asking_Company_Code')
G.add_node('Company_Confirmation')
G.add_node('Awaiting_Approval')
G.add_node('Input_Confirm')
G.add_node('Complete')

G.add_edge('Beginning', 'Asking_Attribution')
G.add_edge('Asking_Attribution', 'Asking_User_Name')
G.add_edge('Asking_User_Name', 'Asking_Company_Name')
G.add_edge('Asking_User_Name', 'Asking_Company_Code')
G.add_edge('Asking_Company_Name', 'Input_Confirm')
G.add_edge('Asking_Company_Code', 'Company_Confirmation')
G.add_edge('Company_Confirmation', 'Awaiting_Approval')
G.add_edge('Awaiting_Approval', 'Input_Confirm')
G.add_edge('Awaiting_Approval', 'asking_company_code')
G.add_edge('Input_Confirm', 'Complete')


class Register:

    def __init__(self,event):
        
        self.handlers = {
            "Beginning": self.Beginning,
            "Asking_Attribution": self.Asking_Attribution,
            "Asking_User_Name": self.Asking_User_Name,
            "Asking_Company_Name": self.Asking_Company_Name,
            "Asking_Company_Code": self.Asking_Company_Code,
            "Company_Confirmation": self.Company_Confirmation,
            "Awaiting_Approval": self.Awaiting_Approval,
            "Input_Confirm": self.Input_Confirm,
            "Complete": self.Complete,
        }
        #グラフを生成
        self.graph = G
        self.input = event.message.text

        # import networkx as nx
        # import matplotlib.pyplot as plt

        # def create_flowchart(graph):
        #     pos = nx.spring_layout(G, seed=42)  # グラフをレイアウトする

        #     # ノードの深さを計算する
        #     depths = nx.shortest_path_length(graph, 'Beginning')

        #     # ノードの深さごとに位置を調整する
        #     for node, depth in depths.items():
        #         pos[node][1] = -depth  # y座標を深さの負数に設定

        #     # グラフを描画する
        #     nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', edge_color='gray', arrowsize=15)

        #     # グラフを表示する
        #     plt.show()

        # # create_flowchartメソッドを実行してフローチャートを描画する
        # create_flowchart(G)



        # # 有向グラフを描画
        # pos = nx.spring_layout(G)  # ノードの配置を決定
        # nx.draw_networkx(G, pos, with_labels=True, arrows=True)

        # # プロットのカスタマイズ
        # plt.title("s")
        # plt.axis("off")  # 軸を表示しない
        # plt.show()

        # データベースに接続
        self.my_sql_connector = MySQLConnector()
        self.my_sql_connector.connect()

        # eventからuser_idを抽出
        user_id = event.source.user_id

        # クエリの実行
        sql = "SELECT * FROM `user_status` WHERE user_id = '{}'".format(user_id)
        rows = self.my_sql_connector.execute_query(sql)

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


    #シークエンスを変更
    def alter_sequence(self, sequence_name):
        # MySQLConnectorインスタンスの生成
        self.my_sql_connector = MySQLConnector()
        # データベースに接続
        self.my_sql_connector.connect()

        # クエリの実行
        sql = "UPDATE user_status SET sequence = '{}' WHERE user_id = '{}';".format(sequence_name, self.user_id)
        self.my_sql_connector.execute_query2(sql)  


    #次のシークエンスを求める
    def next_sequence(self):
        
        # 現在のsequenceを格納
        current_node = self.sequence
        
        #次のノードを求める
        next_node = list(self.graph.successors(current_node))

        result = next_node[0]

        #遷移先が一つの場合はそのノードに移行
        if len(next_node) == 1:
            result = next_node[0]
        
        #遷移先が複数ある場合
        else:

            #遷移先、遷移可能か、終点までの重みを格納する辞書を作成
            transition_dict = {}

            #遷移先のノードが条件を満たしているかを確認し、結果を辞書に格納

            for i in range(0,len(next_node)):
                handler = self.handlers.get(next_node[i])
                if handler is None:
                    raise ValueError(f"Invalid sequence")
                obj = handler(self)

                #選択されたノードから終点までの距離を計算
                start_node = next_node[i]
                end_node = "Complete" 

                # 最短距離（最短経路のエッジ数）を求める
                shortest_distance = nx.shortest_path_length(self.graph, start_node, end_node)

                #値を辞書に格納
                transition_dict[next_node[i]] = (obj.check_conditions(),shortest_distance)
            
            
            # 辞書の内容を標準出力する
            print("遷移先の候補 ")
            for key, value in transition_dict.items():
                print(f">>> {key}: {value}")


            #遷移可能かつ最小コスト
            def find_minimum_value_key(dictionary):
                min_value = float('inf')
                min_key = None

                for key, value in dictionary.items():
                    if value[0] and value[1] < min_value:
                        min_value = value[1]
                        min_key = key

                return min_key


            result = find_minimum_value_key(transition_dict)
            
        print("遷移先 : {}".format(result))
        return result

    #user_statusより適切な処理を実行する
    def message_handling(self):

        handler = self.handlers.get(self.sequence)
        if handler is None:
            raise ValueError(f"Invalid sequence: {self.sequence}")
        obj = handler(self)

        #処理を実行
        result = obj.execute()
        print("ノードの処理を実行しました。")
        if result == 'success':
            next_sequence = self.next_sequence()
            self.alter_sequence(next_sequence)

            handler = self.handlers.get(next_sequence)
            if handler is None:
                raise ValueError(f"Invalid sequence: {next_sequence}")
            obj = handler(self)

            return obj.prompt()
        else:
            reply_message = result
            return reply_message 


#########################################################
#                                                       #
#        ↓     以下に各遷移先のクラスを定義       ↓   #
#                                                       #
#########################################################



    #基底クラスを定義
    class Node:
        def __init__(self,Register):
            self.user_id = Register.user_id
            self.input = Register.input
            self.my_sql_connector = Register.my_sql_connector
        #ノード遷移時にノードが選択可能かを判定する
        def check_conditions(self):
            pass
        
        #処理に必要な情報の入力を促す
        def prompt(self):
            pass

        #処理を実行する
        def execute(self):
            pass
    
    class Beginning(Node):
        pass


    class Asking_Attribution(Node):

        #文記時に処理を実行する条件を満たしているか？（ノードを選択できるか判定）
        def check_conditions(self):
            return True #常に選択可能
        
        #処理を促すメッセージを送信
        def prompt(self):
            reply_message = '初期設定：管理者or従業員を選択してください。'
            return reply_message
        
        #処理を実行する
        def execute(self):

            #管理者か従業員かの判定
            attribute = self.input
            user_id = self.user_id

            #正しい選択肢が入力されたか？
            if attribute in ['admin', 'employee']:
            
                #仮ユーザー登録用のSQLを生成
                sql = "INSERT INTO temporary_users (user_id, attribute) VALUES ('{}', '{}');".format(user_id,attribute)
                
                #処理が実行されたかを真理値で返す。
                try:
                    self.my_sql_connector.execute_query2(sql)
                    return 'success'
                except:
                    return 'ERROR:処理が実行できませんでした。'

            else:
                return '正しい選択肢を入力してください。'
            
    

    class Asking_User_Name(Node):

        def is_valid_name(self,name):
            # 入力された文字列が空でないかをチェック
            if not name:
                return False
            
            # 入力された文字列がアルファベットや日本語等の名前に適した文字列であるかをチェック
            if not re.match(r'^[A-Za-zぁ-んァ-ン一-龥\s]+$', name):
                return False
            
            # 入力された文字列の長さが適切であるかをチェック
            if len(name) > 20:
                return False
            
            return True

        def check_conditions(self):
            return True #常に選択可能
        
        def prompt(self):
            reply_message = 'あなたの名前を教えてください。'
            return reply_message
        
        def execute(self):

            user_id = self.user_id
            user_name = self.input

            #入力文字列が適切であるか判断し適切であれば仮登録
            if self.is_valid_name(user_name):
                
                #仮ユーザー登録用のSQLを生成
                sql = "UPDATE temporary_users SET user_name = '{}' WHERE user_id = '{}';".format(user_name,user_id)

                #処理が実行されたかを真理値で返す。
                try:
                    self.my_sql_connector.execute_query2(sql)
                    return 'success'
                except:
                    return 'ERROR:処理が実行できませんでした。'

            else:
                return 'もう一度入力してください。'


    class Asking_Company_Name(Node):

        def is_valid_name(self,name):
            # 入力された文字列が空でないかをチェック
            if not name:
                return False
            
            # 入力された文字列がアルファベットや日本語等の名前に適した文字列であるかをチェック
            if not re.match(r'^[A-Za-zぁ-んァ-ン一-龥\s]+$', name):
                return False
            
            # 入力された文字列の長さが適切であるかをチェック
            if len(name) > 20:
                return False
            
            return True
        
        def check_conditions(self):
            
            #attributinを参照
            sql = "SELECT attribute FROM temporary_users WHERE user_id = '{}';".format(self.user_id)
            rows = self.my_sql_connector.execute_query(sql)

            if rows[0][0] == "admin":
                return True
            else:
                return False
            
        
        def prompt(self):
            reply_message = '会社名を教えてください。'
            return reply_message

        def execute(self):

            user_id = self.user_id
            company_name = self.input

            #入力文字列が適切であるか判断し適切であれば仮登録
            if self.is_valid_name(company_name):
                
                #company_idとidentification_codeをランダムに生成
                company_id = str(uuid.uuid4())[:8]
                identification_code = str(uuid.uuid4())[:16]

                #仮ユーザー登録用のSQLを生成
                sql = "INSERT INTO temporary_companies (company_id, company_name, identification_code, admin_user_id, plan) VALUES ('{}', '{}', '{}', '{}', 'free');".format(company_id, company_name, identification_code, user_id)


                #処理が実行されたかを真理値で返す。
                try:
                    self.my_sql_connector.execute_query2(sql)
                    return 'success'
                except:
                    return 'ERROR:処理が実行できませんでした。'

            else:
                return 'もう一度入力してください。'
    

    class Asking_Company_Code(Node):

        def check_conditions(self):
            
            #attributinを参照
            sql = "SELECT attribute FROM temporary_users WHERE user_id = '{}';".format(self.user_id)
            rows = self.my_sql_connector.execute_query(sql)

            if rows[0][0] == "employee":
                return True
            else:
                return False

        def prompt(self):
            reply_message = '会社コードを入力してください。'
            return reply_message
        


    class Input_Confirm(Node):

        def prompt(self):
            reply_message = '入力内容を確認して'
            return reply_message
        
        def execute(self):
            pass


    class Company_Confirmation:
        pass

    class Awaiting_Approval:
        pass

    class Complete:
        pass