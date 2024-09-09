import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib
from time import sleep



def sidebar(cig):
    with st.sidebar:
        st.sidebar.header("ドキュメントアップロードと可視化")

        uploaded_file = st.sidebar.file_uploader("Upload your data file", type=['csv', 'xlsx', 'xls', 'json'])

        if 'df_list' not in st.session_state:
                st.session_state['df_list'] = {}

        df_selected_name = st.sidebar.selectbox("Select a DataFrame", list(st.session_state['df_list'].keys()))
        if st.sidebar.button("情報同期"):
            sleep(1)

        if df_selected_name:
            st.write(st.session_state['df_list'][df_selected_name])
            
            try:
                columns = st.multiselect("列を選択:", st.session_state['df_list'][df_selected_name].columns)
                if columns:

                    df = st.session_state['df_list'][df_selected_name]
                    chart_type = st.selectbox(
                        "グラフを選択：",
                        ["折れ線グラフ", "棒グラフ", "ヒストグラム", "散布図", "箱ひげ図", "円グラフ", "エリアチャート"],
                        index=0  
                    )
                    fig, ax = plt.subplots()

                    if chart_type == "折れ線グラフ":
                        df[columns].plot(ax=ax)
                        ax.set_title("折れ線グラフ")
                    elif chart_type == "棒グラフ":
                        df[columns].plot(kind='bar', ax=ax)
                        ax.set_title("棒グラフ")
                    elif chart_type == "ヒストグラム":
                        df[columns].plot(kind='hist', ax=ax, bins=20)
                        ax.set_title("ヒストグラム")
                    elif chart_type == "散布図":
                        if len(columns) == 2:
                            sns.regplot(x=columns[0], y=columns[1], data=df, ax=ax, scatter_kws={"s": 50}, line_kws={"color": "red"})
                            ax.set_title("散布図（回帰線付き）")
                        else:
                            st.write("散布図を生成する2列を選択してください")
                    elif chart_type == "箱ひげ図":
                        df[columns].plot(kind='box', ax=ax)
                        ax.set_title("箱ひげ図")
                    elif chart_type == "円グラフ":
                        if len(columns) == 1:
                            df[columns[0]].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
                            ax.set_ylabel('')
                            ax.set_title("円グラフ")
                        else:
                            st.write("円グラフを生成するには1列のみを選択してください")
                    elif chart_type == "エリアチャート":
                        df[columns].plot(kind='area', ax=ax)
                        ax.set_title("エリアチャート")

                    st.pyplot(fig)
            except:
                st.write("列が選択されていないか、可視化中にエラーが発生しました")

        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.xls'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            
            file_name = uploaded_file.name.split('.')[0]

            st.session_state['df_list'][file_name] = df

            st.sidebar.success(f"File '{file_name}' uploaded successfully!")



    return cig
