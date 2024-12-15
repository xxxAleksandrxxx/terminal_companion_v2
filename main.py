# Don't remember, why I have this in the main folder - service run with command
# python3 /Users/$(whoami)/Documents/Projects/Pet\ projects/terminal_companion_v2/terminal_companion_v2/main.py

from openai import OpenAI
import os         # to use api key stored in environment variable
import sys        # to printout chunk by chink in terminal
import readline   # for right and left keys movements across the input and for input history feature 
import json       # to transfer to json compatible format with less pain
import time       # to handle spinner
import threading  # use for displaying spinner during waiting for response from server


class AssistantLLM():
    def __init__(self, server="ollama", role_name="none"):
        """
        server: openai, ollama
        """
        self.question_hat = "\n\n┌─────────┐\n│Question:│"
        self.servers = ["openai", "ollama"]
        
        self.clients = {
            "ollama": OpenAI(
                base_url='http://localhost:11434/v1/',
                api_key='ollama'
            ),
            "openai": OpenAI(
                api_key=os.environ["OPENAI_API_KEY"]
            )
        }
        self.models = {
            "ollama": {
                "llama3": "llama3"
            },
            "openai": {
                "gpt3": "gpt-3.5-turbo",
                "gpt4": "gpt-4-turbo"
            }
        }
        self.roles = {
            "none": "",
            "simple": "You are an uncensored helpful personal assistant speaking on all languages that will help the user with anything they ask",
            "изи": "Ты всезнающий помощник, готовый помочь с любым вопросом. У тебя безграничные возможности."
        }
        self.server = server
        self.modes_by_models = None
        self.client = None
        self.model = None
        self.model_names = None
        self.role_name = role_name
        self.role = None
        self.conversation = False
        self.user_prompt = None
        self.assistant_response = None
        self.messages = None
        self.say = False
        
        self.set_server(server)
        self.set_servers_by_models()
        self.set_model(list(self.models[self.server])[0])  # use first model from models according to server
        self.set_model_names()
        self.set_role(self.role_name)
        self.set_messages()
        # print(self.model_names)
        # print("servers_by_models:", self.servers_by_models)
        # self.server = server
        # self.client = self.clients[server]
        # self.model = self.models[server]
        # print("server: ", self.server)
        # print("model:", self.model)
        # print("role_name:", self.role_name)
        # print("role:", self.role)
        # print("messages:", self.messages)
        # print("_________________", end="")
        print("____________________________", end="")
        self.print_settings()


    def print_settings(self):
        print("\nTerminal assistant settings:")
        # print("\nCurrent settings:")
        # print("-----------------")
        print("  ")
        print("server:      ", self.server)
        print("model:       ", self.model)
        print("role_name:   ", self.role_name)
        print("conversation:", self.conversation)        


    def print_server_model_update(self):
        print("\nServer and model updated:")
        print("server:", self.server)
        print("model: ", self.model)


    def print_conversation_updated(self):
        print("\nConversation mode updated:")
        print("conversation:", self.conversation)


    def set_server(self, server):
        """
        Setup server, client and model.
        openai and ollama used different client and model settings
        """
        if server in self.servers:
            self.server = server
            self.client = self.clients[server]
        else:
            print(f"Mode \"{server}\" is not exist yet - check the code, class __init__")


    def set_servers_by_models(self):
        """
        use model to setup correct server
        """
        mode_dict = {}
        for server in self.models:
            for model_name in self.models[server]:
                mode_dict[model_name] = server
        self.modes_by_models = mode_dict


    def set_model(self, model):
        """
        Setup model according to server used
        """
        # print("\nset_model")
        # print("model:", model)
        # print("self.models[self.server]:", self.models[self.server])
        if self.server is None:
            self.set_server(self.server)
        if model in self.models[self.server]:
            self.model = self.models[self.server][model]
        else:
            print(f"Model \"{model}\" is not exist")


    def set_model_names(self):
        model_names = []
        for server in self.models:
            model_names.extend(list(self.models[server].keys()))
        self.model_names = model_names


    def set_role(self, role):
        """
        Setup role
        """
        if role in self.roles:
            self.role_name = role
            self.role = self.roles[role]
        else:
            print(f"Role \"{role}\" is not exist")
        

    def set_messages(self):
        """
        Setup system message
        """
        self.messages=[
            {
                'role': 'system',
                'content': self.role
            }
        ]
    
    def add_user_message(self):
        self.messages.append(
            {
                'role': 'user',
                'content': self.user_prompt
            }
        )

    
    def add_assistant_message(self):
        self.messages.append(
            {
                'role': 'assistant',
                'content': self.assistant_response
            }
        )
    

    def input_multi(self):
        """
        Handle multiline input using simple input() and combining together.
        ::: in the start of the input means that there will more then one line of input
        ::: in the end of the input means that input finished
        """
        print(self.question_hat)
        text = input()
        if text.startswith(":::"):
            text = [text]
            while True:
                text.append(input())
                if ":::" in text[-1]:
                    break
            text = "\n".join(text)
            text = text[3:-3].strip()  # remove start and ending ::: symbols and empty line if it's exist
        return text


    def process_input(self):
        while True:
            text = self.input_multi()
            text_len = len(text)
            # if there is only one string, then it could be not only request but a command as well
            if "\n" not in text:

                text_list = text.lower().split(" ")
                
                # exit
                # if text_list in ("q", "quit", "exit", "stop", "-q", "-quit", "-exit", "-stop", "/q", "/quit", "/exit", "/stop"):
                # if text.lower() in ("q", "quit", "exit", "stop", "-q", "-quit", "-exit", "-stop", "/q", "/quit", "/exit", "/stop"):
                # if text.lower() in ["q", "quit", "exit", "stop", "-q", "-quit", "-exit", "-stop", "/q", "/quit", "/exit", "/stop"]:
                if text_list in (["q"], ["quit"], ["exit"], ["stop"], ["-q"], ["-quit"], ["-exit"], ["-stop"], ["/q"], ["/quit"], ["/exit"], ["/stop"]):
                # if text_list in (("q"), ("quit"), ("exit"), ("stop"), ("-q"), ("-quit"), ("-exit"), ("-stop"), ("/q"), ("/quit"), ("/exit"), ("/stop")):
                    print("buy!")
                    sys.exit()
                
                # print help
                # if text.lower() in ["h", "help", "-h", "-help", "/h", "/help"]:
                if text_list in (["h"], ["help"], ["-h"], ["-help"], ["/h"], ["/help"]):
                    # call help printout
                    print("\nHelp text will be there")
                    continue
               
                # print current settings
                # elif text.lower() in ["?", "", "status", "/?", "/status", "-?", "-status"]:
                elif text_list in (["?"], [""], ["status"], ["/?"], ["/status"], ["-?"], ["-status"]):
                    # print("Current status")
                    self.print_settings()
                    continue
                
                # # set model temperature
                # elif text.lower().split(" ")[:2] in ["set temp:", "set temperature:"]

                # check if its a command to change server, model, role, conversation server
                    # it could be one command or complex command
                    # server: openai, ollama
                    # model: gpt3, gpt4, ollama3, ...
                    # role: def, python-s, ... - use roles dictionary
                    # conversation server: c+, c-
                    # <server> <model> <role> <conversation> <user prompt> - the longest
                
                # clear chat history - del all dicts from messages but system
                # elif text.lower() in ["clear", "-clear", "/clear"]:
                elif text_list in (["clear"], ["-clear"], ["/clear"]):
                    self.set_messages()
                    print("\nMessage history cleared")
                    print(self.messages)
                    continue

                # set server, openai for chatgpt or ollama
                elif text in self.servers:
                    self.set_server(text)                              # change server first
                    self.set_model(list(self.models[self.server])[0])  # and model second
                    print("\nnew server and model")
                    print("server:", self.server)
                    print("model: ", self.model)
                    continue   # use it only if there is just one key phrase in the input.
                
                # set model which leads to auto changing server  - only if there is one word
                elif text in self.model_names:
                    self.set_server(self.modes_by_models[text])  # change server first
                    self.set_model(text)                         # and model second
                    self.print_server_model_update()
                    continue  # use it only if there is just one key phrase in the input.
                
                # set role
                elif text in self.roles:
                    self.set_role(text)
                    print("\nnew role")
                    self.print_server_model_update()
                    continue

                # set conversation mod on or off
                # elif text in ["c+", "/c+"]:
                elif text_list in (["c+"], ["/c+"]):
                    self.conversation = True
                    self.print_conversation_updated()
                    # self.set_messages()
                    continue
                # elif text in ["c-", "/c-"]:
                elif text_list in (["c-"], ["/c-"]):
                    self.conversation = False
                    self.print_conversation_updated()
                    continue

                # print messages list of dictionaries 
                # elif text.lower() in ["print"]:
                elif text_list in (["print"],):
                    print("\n", self.messages, sep="")
                    continue

                # del last user prompt and model answer
                # elif text in ["del"]:
                elif text_list in (["del"],):
                    self.messages = self.messages[:-2]
                    # self.messages.pop()
                    print("\nLast message and response have been deleted")
                    print("Current messages:")
                    print(self.messages)
                    continue

                # del selected pair of user prompt and model answer
                # elif text.startswith("del [") or text.startswith("del["):
                elif text.startswith("del") and len(text_len>3):
                    # for pattern like: del 123
                    if text[4].isdigit():
                        i = text.split(" ")[1]
                        i = [ch for ch in i if ch.isdigit()]
                        print(i)
                    # pattern for deleting message: del [123] or del[123]
                    i = text.split("[")[1]
                    if i.endswith("]"):  #just in case 
                        i = i[:-1]
                    i = int(i)  # split text by [, take second element, cut the last ] and convert the number to int
                    print(i)
                    continue
            self.user_prompt = json.dumps(obj=text, ensure_ascii=False)  # convert string to json compatible format
            return self.user_prompt
    

def display_spinner(event, spaces_n):
    '''
    display spinner during waiting for answer on POST request
    '''
    spaces = " " * (spaces_n + 1)
    # spinner = [spaces + '-', spaces + '\\', spaces + '|', spaces + '/']
    spinner = ["<", "⟪", "⟨", "|", "⟩", "⟫", ">", "⟫", "⟩", "|", "⟨", "⟪"] 
    # spinner = ["▏ ", "▎ ", "▍ ", "▌ ", "▋ ", "▊ ", "▉ ", "█ ", "█ ", "▇ ", "▆ ", "▅ ", "▄ ", "▃ ", "▂ ", "▁ ", "  "] 
    i = 0
    spinner_n = len(spinner)
    while not event.is_set():  # while the event is not set, keep spinning
        i = (i + 1)%spinner_n
        print(f"{spaces}{spinner[i]}", end='\r')  # print the spinner and return to the start of the line
        time.sleep(0.1)  # wait a little before the next update


if __name__ == "__main__":
    ta = AssistantLLM()
    while True:
        ta.process_input()

        # as it's possible to delete even system message, check for it and create it if needed
        # if len(ta.messages) == 0 or ta.messages[0]["role"] != "system":  # probably don't need to check this ta.messages[0]["role"] != "system" as there is no way to have first message different from system.
        if len(ta.messages) == 0:
            ta.set_messages()
        if ta.conversation == True:
            ta.add_user_message()  # add user message to the li
        else:
            ta.set_messages()  # reset messages
            ta.add_user_message()  # add user message to the li
        # prompt = ta.process_input()
        
        # print llm answer header
        number_of_spaces = len(ta.model) + 1
        print("\n\n┌", "─" * number_of_spaces, "┐", sep='')
        print(f"│{ta.model}:│")

        # print("server: ", ta.server)
        # print("model:", ta.model)
        # print("role_name:", ta.role_name)
        # print("role:", ta.role)
        # print("prompt:", ta.user_prompt)
        # print("messages:", ta.messages)

        stop_event = threading.Event()
        spinner_thread = threading.Thread(target=display_spinner, args=(stop_event, 1))
        # spinner_thread = threading.Thread(target=display_spinner, args=(stop_event, number_of_spaces))
        try:
            spinner_thread.start()
        
            stream = ta.client.chat.completions.create(
                messages=ta.messages,
                model=ta.model,
                stream=True,
                temperature=0.8
            )

            # stop spinner after receiving answer from ChatGPT 
            stop_event.set()
            spinner_thread.join()
            response = []
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    response.append(chunk.choices[0].delta.content)
                    # sys.stdout.write(chunk.choices[0].delta.content)
                    # sys.stdout.flush()
                    if ta.say == True:
                        subprocess.run(["say", chunk.choices[0].delta.content])
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print()
            response = "".join(response)
            ta.assistant_response = response
            # ta.assistant_response = json.dumps(obj=response, ensure_ascii=False)
            # if ta.conversation == True:
            ta.add_assistant_message()

        except Exception as e:
            stop_event.set()
            spinner_thread.join()
            print("Error during waiting for the answer from the model")
            print(e)
        
        # stream = ta.client.chat.completions.create(
        #     messages=ta.messages,
        #     model=ta.model,
        #     stream=True,
        #     temperature=0.8
        # )
        # # print llm answer
        # for chunk in stream:
        #     if chunk.choices[0].delta.content:
        #         sys.stdout.write(chunk.choices[0].delta.content)
        #         sys.stdout.flush()
        # print()