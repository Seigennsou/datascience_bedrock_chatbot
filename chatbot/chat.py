import copy
import json
from pprint import pprint

import streamlit as st
from tools.tools_func import ToolsList


class ChatInterfaceStreaming:
    def __init__(self, bedrock, cfg):
        self.bedrock = bedrock
        self.cfg = cfg
        self.tool_use_args = {
            "input": {},
            "name": "",
            "toolUseId": "",
        }
        self.tool_use_mode = False
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def run(self):
        st.title("user_DEMO:DWHと対話するAI Chatbot-AWS Bedrock")

        self.display_history(st.session_state.messages)

        if prompt := st.chat_input("会話内容を入力"):
            input_msg = {"role": "user", "content": [{"text": prompt}]}
            self.display_msg_content(input_msg)
            self.update_chat_history(input_msg)

            response = self.bedrock.generate_response(
                st.session_state.messages, self.cfg
            )
            generated_text: str = self.display_streaming_msg_content(response["stream"])
            while self.tool_use_mode:
                output_msg = self.create_tool_request_msg(
                    generated_text, self.tool_use_args
                )
                self.update_chat_history(output_msg)

                tool_result_msg = self.execute_tool()
                try:
                    if self.response_df_info is not None and not self.response_df_info.empty:
                        st.dataframe(self.response_df_info)
                except:
                    pass
                try:
                    if self.response_df is not None and not self.response_df.empty:
                        st.dataframe(self.response_df)
                        df = self.response_df
                        df_name = self.response_df_name
                        st.session_state['df_list'][df_name] = df
                        tool_result_msg["content"].append({"df": df})
                except:
                    pass

                try:
                    if self.sqlcode is not None:
                        st.code(self.sqlcode, language="sql", line_numbers=False)
                        tool_result_msg["content"].append({"sqlcode": self.sqlcode})
                except:
                    pass

                try:
                    if self.pythoncode is not None:
                        st.code(self.pythoncode, language="python", line_numbers=False)
                        tool_result_msg["content"].append({"pythoncode": self.pythoncode})
                except:
                    pass
                self.update_chat_history(tool_result_msg)
            
                

                response = self.bedrock.generate_response(
                    st.session_state.messages, self.cfg
                )
                generated_text = self.display_streaming_msg_content(response["stream"])
        
            output_msg = {"role": "assistant", "content": [{"text": generated_text}]}
            self.update_chat_history(output_msg) 

    def update_chat_history(self, message):
        st.session_state.messages.append(copy.deepcopy(message))

    def display_history(self, messages):
        for message in messages:
            if "text" in message["content"][0]:
                self.display_msg_content(message)
            else:
                self.display_tool_content(message)

    def display_msg_content(self, message):
        with st.chat_message(message["role"]):
            for content in message["content"]:
                if "text" in content:
                    st.markdown(content["text"])
                if "df" in content:
                    st.dataframe(content["df"])
                if "sqlcode" in content:
                    st.code(content["sqlcode"], language="sql", line_numbers=False)
                if "pythoncode" in content:
                    st.code(content["pythoncode"], language="python", line_numbers=False)
    
    def display_tool_content(self, message):
        for content in message["content"]:
            if "text" in content:
                st.markdown(content["text"])
            if "df" in content:
                st.dataframe(content["df"])
            if "sqlcode" in content:
                st.code(content["sqlcode"], language="sql", line_numbers=False)
            if "pythoncode" in content:
                st.code(content["pythoncode"], language="python", line_numbers=False)


    def parse_stream(self, response_stream):
        tool_use_input = ""
        for event in response_stream:
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"]["delta"]
                if "text" in delta:
                    yield delta["text"]
                if "toolUse" in delta:
                    tool_use_input += delta["toolUse"]["input"]
            if "contentBlockStart" in event:
                self.tool_use_args.update(
                    event["contentBlockStart"]["start"]["toolUse"]
                )
            if "messageStop" in event:
                stop_reason = event["messageStop"]["stopReason"]
                if stop_reason == "tool_use":
                    self.tool_use_args["input"] = json.loads(tool_use_input)
                    self.tool_use_mode = True
                else:
                    self.tool_use_mode = False

    def tinking_stream(self):
        message = "Using Tools..."
        for word in message.split():
            yield word + " "

    def display_streaming_msg_content(self, response_stream):
        if response_stream:
            with st.chat_message("assistant"):
                generated_text = st.write_stream(self.parse_stream(response_stream))
                if not generated_text:
                    generated_text = st.write_stream(self.tinking_stream())
        return generated_text

    def create_tool_request_msg(self, generated_text, tool_use_args):
        # tool_use_args includes name, input, and toolUseId
        return {
            "role": "assistant",
            "content": [
                {"text": generated_text},
                {"toolUse": tool_use_args},
            ],
        }

    def create_tool_result_msg(self, tool_use_id, tool_response):
        return {
            "role": "user",
            "content": [
                {
                    "toolResult": {
                        "toolUseId": tool_use_id,
                        "content": [{"text": tool_response}],
                    }
                }
            ],
        }

    def run_tool(self, tool_name, tool_args):
        return getattr(ToolsList(), tool_name)(**tool_args)

    def execute_tool(self):
        tool_name = self.tool_use_args["name"]
        tool_args = self.tool_use_args["input"] or {}
        tool_use_id = self.tool_use_args["toolUseId"]
        tool_return = self.run_tool(tool_name, tool_args)
        tool_response = tool_return["response_text"]
        try:
            self.response_df = tool_return["response_df"]
        except:
            self.response_df = None
        try:
            self.response_df_name = tool_return["response_df_name"]
        except:
            self.response_df_name = None
        try:
            self.sqlcode = tool_return["sqlcode"]
        except:
            self.sqlcode = None
        try:
            self.pythoncode = tool_return["pythoncode"]
        except:
            self.pythoncode = None
        try:
            self.response_df_info = tool_return["response_df_info"]
        except:
            self.response_df_info = None
        tool_result_msg = self.create_tool_result_msg(tool_use_id, tool_response)
        return tool_result_msg
