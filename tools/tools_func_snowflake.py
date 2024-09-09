import pandas as pd
import snowflake.connector
import streamlit as st
import json

class ToolsList:
    def __init__(self):
        self.con = snowflake.connector.connect(
        user='',
        password='',
        account='',
        database='',
        session_parameters={
        'QUERY_TAG': '',
            })
    
    def get_snowflake_tables(self,input_text):
        print(input_text)
        cur = self.con.cursor()
        sql_query = " SELECT table_schema || '.' || table_name AS full_table_name FROM BANK_DATA.information_schema.tables WHERE table_type = 'BASE TABLE';"
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        df = pd.DataFrame(results, columns=columns)

        print(df)

        with open('table_info.json', 'r', encoding='utf-8') as f:
            table_info = str(json.load(f))

        result = str(df)
        return {"response_text": sql_query +"\n" + result + "\n" + table_info + "以上の情報に従って、get_snowflake_tables_columnsを実行してください。", "response_df_info": df}
    

    def get_snowflake_tables_columns(self,schema_name,table_name):
        print(f"schema_name: {schema_name}, table_name: {table_name}")
        sql_query = f"""
                    SELECT column_name, data_type, character_maximum_length, numeric_precision, numeric_scale, is_nullable
                    FROM BANK_DATA.information_schema.columns
                    WHERE table_schema = '{schema_name}'
                    AND table_name = '{table_name}'; 
                    """
        cur = self.con.cursor()
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        df = pd.DataFrame(results, columns=columns)

        print(df)

        result = str(df.iloc[:,0:2])
        return {"response_text": sql_query +"\n" + result + "\n" + "以上の情報に従って、ユーザーの要望を満たすまでにTOOL USEを止まらないでください。", "response_df_info": df}
    


    def get_snowflake_query_result(self,sql_text,df_name):
        print(sql_text)
        sql_query = sql_text
        try:
            cur = self.con.cursor()
            cur.execute(sql_query)
            columns = [desc[0] for desc in cur.description]
            results = cur.fetchall()
            
            df = pd.DataFrame(results, columns=columns)

            result = str(df.head(100))
            return {"response_text": sql_query +"\n" + result + "\n" + "抽出されたdf_name:" + df_name + "以上の情報に従って、ユーザーの要望を満たすまでにTOOL USEを止まらないでください。", "response_df": df, "response_df_name": df_name, "sqlcode": sql_query}
        except Exception as e:
            return {"response_text": f"エラーが発生しました。エラーメッセージは: {e},SQlをしっかり確認して再度実行してください。0.最優先注意事項！！！sql文を入力際は日本語或いは漢字或いは純数字を含むのカラム書く時に必ず\"\"で囲んでください。例：SELECT \"ユーザーID\", \"年齢\",\"201501\" FROM BANK_DATA.PUBLIC.\"顧客情報\" 。カラム名が純英数字の場合は\"\"を付けないでください！以上の情報に従って、ユーザーの要望を満たすまでにTOOL USEを止まらないでください。" }
 
    def get_dataframe_info(self,input_text):
        print(input_text)
        df_dict = st.session_state['df_list']
        df_names = list(df_dict.keys())
        
        df = pd.DataFrame(df_names, columns=['DataFrame_Name'])

        print(df)
        result = str(df)
        
        return {
            "response_text": f"以下は df_dict 中で利用可能な DataFrame 一覧:\n{result}\n以上の情報に従って、ユーザーの要望を満たすまでにTOOL USEを止まらないでください。",
            "response_df_info": df
        }
    

    def get_dataframe_columns_info(self, df_name):
        print(f"DataFrame 名: {df_name}")

        df_dict = st.session_state['df_list']
        if df_name in df_dict:
            df = df_dict[df_name]
            
            columns_info = [(col, df[col].dtype) for col in df.columns]
            columns_df = pd.DataFrame(columns_info, columns=['Column_Name', 'Data_Type'])

            print(columns_df)

            result = str(columns_df)
            return {
                "response_text": f"以下は DataFrame '{df_name}' の列情報:\n{result}\n以上の情報に従って、ユーザーの要望を満たすまでにTOOL USEを止まらないでください。",
                "response_df_info": columns_df
            }
        else:
            return {"response_text": f"エラー: DataFrame '{df_name}' が見つかりません。以上の情報に従って、ユーザーの要望を満たすまでにTOOL USEを止まらないでください。"}

    def execute_python_code(self, func_code, df_name):
        print(func_code)
        try:
            try:
                df_dict = st.session_state['df_list']
            except KeyError:
                df_dict = {'result_df': pd.DataFrame()}
            
            exec_globals = df_dict.copy()
            
            exec(func_code, globals(), exec_globals)
            
            result_df = exec_globals.get('result_df', pd.DataFrame())
            print(result_df)
            
            try:
                result = str(result_df.head(100))
            except:
                result = "結果のDataFrameが空です。"
            
            if not result_df.empty:
                return {
                    "response_text": func_code + "\n" + result + "\n" + "抽出されたdf_name:" + df_name + "以上の情報に従って、ユーザーの要望を満たすまでにTOOL USEを止まらないでください。",
                    "response_df": result_df,
                    "response_df_name": df_name,
                    "pythoncode": func_code
                }
            else:
                raise ValueError("結果のresult_dfが空です。")
        except Exception as e:
            return {
                "response_text": f"func_codeは: {func_code} です。エラーが発生しました。エラーメッセージは: {e}, 実行を中止して、func_codeとエラーメッセージをユーザーに報告してください。"
            }


    
    
