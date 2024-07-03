# replace openai library with requests library to communicate to openai, anthropic, ollama - openai lib supports ollama api but doesn't support anthropic api

import requests   # to communicate to APIs
import os         # to use api key stored in environment variable
import sys        # to printout chunk by chink in terminal
import readline   # for right and left keys movements across the input and for input history feature 
import json       # to transfer to json compatible format with less pain
import time       # to handle spinner
import threading  # use for displaying spinner during waiting for response from server
import queue
import subprocess


class AssistantLLM():
    def __init__(self, server="ollama", role_name="none"):
        """
        server: openai, ollama, anthropic
        """
        self.servers = [ 
            "ollama",
            "openai",
            "anthropic"
        ]

        self.urls = {
            "ollama": "http://localhost:11434/api/chat",
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages"
        }

        self.headers = {
            "ollama": {
                "Content-Type": "application/json"
            },
            "openai": {
                "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
                "Content-Type": "application/json"
            },
            "anthropic": {
                'x-api-key': os.environ["ANTHROPIC_API_KEY"],
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json',
            }
        }

        self.models = {
            "ollama": {
                "llama3": "llama3"       # free of charge ^_^
            },
            "openai": {                               # https://platform.openai.com/docs/models
                "gpt3": "gpt-3.5-turbo",              # input  0.50 USD, output  1.50 USD per 1M tokens
                "gpt4o": "gpt-4o",                    # input  5.00 USD, output 15.00 USD per 1M tokens
                "gpt4": "gpt-4-turbo",                # input 10.00 USD, output 30.00 USD per 1M tokens
            },
            "anthropic": {                            # https://www.anthropic.com/pricing#anthropic-api
                "ha3": "claude-3-haiku-20240307",     # input  0.25 USD, output  1.25 USD per 1M tokens                
                "sn35": "claude-3-5-sonnet-20240620", # input  3.00 USD, output 15.00 USD per 1M tokens
                "op3": "claude-3-opus-20240229"       # input 15.00 USD, output 75.00 USD per 1M tokens
            }
        }

        self.roles = {
            "none": "",
            "coder": '###INSTRUCTIONS###\n\nYou MUST follow the instructions for answering:\n\n- ALWAYS answer in the language of my message.\n- Read the entire convo history line by line before answering.\n- I have no fingers and the placeholders trauma. Return the entire code template for an answer when needed. NEVER use placeholders.\n- If you encounter a character limit, DO an ABRUPT stop, and I will send a "continue" as a new message.\n- You ALWAYS will be PENALIZED for wrong and low-effort answers. \n- ALWAYS follow "Answering rules."\n\n###Answering Rules###\n\nFollow in the strict order:\n\n1. USE the language of my message.\n2. **ONCE PER CHAT** assign a real-world expert role to yourself before answering, e.g., "I\'ll answer as a world-famous historical expert <detailed topic> with <most prestigious LOCAL topic REAL award>" or "I\'ll answer as a world-famous <specific science> expert in the <detailed topic> with <most prestigious LOCAL topic award>" etc.\n3. You MUST combine your deep knowledge&nbsp;of the topic and&nbsp;clear thinking to quickly and accurately decipher the answer step-by-step with CONCRETE details.\n4. I\'m going to tip $1,000,000 for the best reply.&nbsp;\n5. Your answer&nbsp;is critical for my career.\n6. Answer the question in a natural, human-like manner.\n7. ALWAYS use an answering example for a first message structure.\n\n##Answering in English example##\n\nI\'ll answer as the world-famous <specific field> scientists with <most prestigious LOCAL award>\n\n<Deep knowledge step-by-step answer, with CONCRETE details>'
        }
### how to communicate to API
        # to send requests we ned to setup
        # - self.url
        # - self.headers
        # - self.data  # stores model, temperature (if any), max tokens
        #   - self.models
        #   - self.roles
        self.clients = {
            # it was just OpenAI() to send request so now it should be probably a function that sends request to API
            "ollama": "response = requests.post(self.url, data=json.dumps(data), headers=headers)",
            "openai": "response = requests.post(self.url, data=json.dumps(data), headers=headers)",
            "anthropic": "response = requests.post(self.url, data=json.dumps(data), headers=headers)"
        }

        

        self.question_hat = "\n\n┌─────────┐\n│Question:│"
        self.modes_by_models = None
###        
        self.server = server 
#-      self.client = None   # it looks like we don't need it
###
        self.temperature = 0.3
        self.max_tokens = 1024
        self.header = None
        self.url = None
        self.data = None
        self.model = None
        self.model_names = None
        self.role_name = role_name
        self.role = None
        self.conversation = False
        self.user_prompt = None
        self.assistant_response = None
        self.messages = None
        self.pronunciation = False

        self.set_server(server)
        self.set_servers_by_models()
        self.set_model(list(self.models[self.server])[0])  # use first model from models according to server
        self.set_model_names()
        self.set_role(self.role_name)
        self.set_messages()
        self.set_url()
        self.set_header()
        # self.set_data()
        print("____________________________", end="")
        self.print_settings()


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
        Setup model according to the chosen server
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
 ###    # ollama needs firs message to be a role - setup in set_data()
        # openai needs firs message to be a role - setup in set_data()
        # anthropic needs to have system in data as a separate key - setup in set_data()
        self.messages=[]

####
####
    def set_url(self):
        """Setup url according to chosen server"""
        print("You are going to change URL!")
        self.url = self.urls[self.server]
        print("URL changed.\nNew URL:", self.url)


    def set_header(self):
        """Setup header according to chosen server"""
        self.header = self.headers[self.server]

    
    def set_data(self):
        """
        Setup data field for API requests
        """
        data = {
            "ollama": {
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True,
                "messages": [{'role': 'system', 'content': self.role}] + self.messages
            },
            "openai": {
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True,
                "messages": [{'role': 'system', 'content': self.role}] + self.messages
            },
            "anthropic": {
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": True,
                "system": self.role,
                "messages": self.messages
            }
        }
        self.data = data[self.server]


    def add_user_message(self):
        self.messages.append(
            {
                'role': 'user',
                'content': self.user_prompt
            }
        )
    
### dont need probably...
    def add_assistant_message(self):
        self.messages.append(
            {
                'role': 'assistant',
                'content': self.assistant_response
            }
        )


    def del_messages_pair(self, n):
        # print pair assistant + user messages
        if self.messages:
            print("No messages")
            return
        print(n)
        i_max = len(self.messages)//2 - 1
        # if n < 0:
        #     print("It's not possible to delete system prompt. Here it is for your reference:")
        #     print(self.messages[0])
        #     return False
        if n > i_max:
            print(f"The index \"{n}\" is too high. Max index: {i_max}")
            return False
        else:
            del self.messages[n*2]
            try:
                del self.messages[n*2]  # as after first delete the length of the messages decreased
                return True
            except Exception as e:
                print("Error from del_messages_pair():", e)
                return False
            # finally:
            #     return True


    def print_settings(self):
        print("\nTerminal assistant settings:")
        # print("\nCurrent settings:")
        # print("-----------------")
        print("  ")
        print("server:       ", self.server)
        print("model:        ", self.model)
        print("role_name:    ", self.role_name)
        print("conversation: ", "on" if self.conversation else "off")    
        print("pronunciation:", "on" if self.pronunciation else "off")    
        ###
        # print("url:          ", self.url)
        # print("header:       ", self.header)


    def print_server_model_update(self):
        print("\nServer and model updated:")
        print("server:", self.server)
        print("model: ", self.model)


    def print_conversation_updated(self):
        print("\nConversation mode updated:")
        print("conversation:", "on" if self.conversation else "off")


    def print_pronunciation_updated(self):
        print("\nPronunciation mode updated:")
        print("pronunciation:", "on" if self.pronunciation else "off")        


    def print_messages(self):
        if not self.messages:
            print("No messages")
            return
        len_messages = len(self.messages)
        for i in range(0, len_messages, 2):
            print(i//2 + i%2)
            print(self.messages[i])
            try:  # just in case one message will be missed. shouldn't happen but just in case
                print(self.messages[i+1])
                print()
            except Exception as e:
                print("Error in print_messages():", e)
                continue
    

    def print_messages_pair(self, n):
        # print pair assistant + user messages
        if not self.messages:
            print("No messages")
            return
        i_max = len(self.messages)//2 - 1
        if n > i_max:
            print(f"The index \"{n}\" too high. Max index: {i_max}")
        else:
            print(self.messages[n*2])
            try:
                print(self.messages[n*2 + 1])
            except Exception as e:
                print("Error in print_messages_pair():", e)


    def print_models(self):
        """
        Printout available model names
        """
        print("Available models:")
        for server in self.models:
            for short_name, full_name in self.models[server].items():
                print(f"{short_name:<10} {full_name:<}")
    

    def print_servers(self):
        """
        Printout available server names
        """
        print("Available servers:")
        for elem in self.servers:
            print(elem)
    

    def print_roles(self):
        """
        Printout available roles
        """
        print("Available roles:")
        for short_name, full_prompt in self.roles.items():
            print(short_name)
            print(full_prompt)
            print()


    def print_help(self):
        """
        Printout help instruction
        """
        print("Available commands:")
        print("\nPrintout help")
        for elem in (["h"], ["help"], ["-h"], ["-help"], ["/h"], ["/help"]):
            print(elem[0])
        print("\nPrintout list of available models")
        for elem in (["h", "m"], ["help", "m"], ["-h", "m"], ["-help", "m"], ["/h", "m"], ["/help", "m"], ["h", "-m"], ["help", "-m"], ["-h", "-m"], ["-help", "-m"], ["/h", "-m"], ["/help", "-m"], ["h", "models"], ["help", "models"], ["-h", "models"], ["-help", "models"], ["/h", "models"], ["/help", "models"], ["hm"], ["-hm"], ["-h-m"], ["/hm"], ["/h/m"], ["/h /m"], ["/help"], ["/help/models"], ["/help", "/models"]):
            print(*elem)
        print("\nPrintout list of available servers")
        for elem in (["h", "s"], ["help", "s"], ["-h", "s"], ["-help", "s"], ["/h", "s"], ["/help", "s"], ["h", "-s"], ["help", "-s"], ["-h", "-s"], ["-help", "-s"], ["/h", "-s"], ["/help", "-s"], ["h", "servers"], ["help", "servers"], ["-h", "servers"], ["-help", "servers"], ["/h", "servers"], ["/help", "servers"], ["hs"], ["-hs"], ["-h-s"], ["/hs"], ["/h/s"], ["/h /s"], ["/help/servers"], ["/help", "/servers"]):
            print(*elem)
        print("\nPrintout available roles")
        for elem in (["h", "r"], ["help", "r"], ["-h", "r"], ["-help", "r"], ["/h", "r"], ["/help", "r"], ["h", "-r"], ["help", "-r"], ["-h", "-r"], ["-help", "-r"], ["/h", "-r"], ["/help", "-r"], ["h", "roles"], ["help", "roles"], ["-h", "roles"], ["-help", "roles"], ["/h", "roles"], ["/help", "roles"], ["hr"], ["-hr"], ["-h-r"], ["/hr"], ["/h/r"], ["/h /r"], ["/help/roles"], ["/help", "/roles"]):
            print(*elem)
        print("\nPrintout current status")
        for elem in (["<just press enter>"], ["?"], ["status"], ["/?"], ["/status"], ["-?"], ["-status"]):
            print(elem[0])
        print("\nTurn on conversation mode")
        for elem in (["c+"], ["/c+"]):
            print(elem[0])
        print("\nTurn off conversation mode")
        for elem in (["c-"], ["/c-"]):
            print(elem[0])
        print("\nTurn on pronunciation mode")
        for elem in (["say+"], ["/say+"]):
            print(elem[0])
        print("\nTurn off pronunciation mode")
        for elem in (["say-"], ["/say-"]):
            print(elem[0])
        print("\nPrint messages history")
        for elem in (["print"], ["/print"]):
            print(elem[0])
        print("\nPrint selected pair of user input and model respond")
        for elem in ("print <number>", "print[<number>]"):
            print(elem)
        print("\nClear history")
        for elem in (["clear"], ["-clear"], ["/clear"]):
            print(elem[0])
        print("\nDelete selected pair of user input and model respond")
        for elem in ("del <number>", "del[<number>]"):
            print(elem)
        print("\nDelete the last pair of user input and model respond")
        for elem in ("del -1",):
            print(elem)
                
    
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
                
                # EXIT
                # if text_list in ("q", "quit", "exit", "stop", "-q", "-quit", "-exit", "-stop", "/q", "/quit", "/exit", "/stop"):
                # if text.lower() in ("q", "quit", "exit", "stop", "-q", "-quit", "-exit", "-stop", "/q", "/quit", "/exit", "/stop"):
                # if text.lower() in ["q", "quit", "exit", "stop", "-q", "-quit", "-exit", "-stop", "/q", "/quit", "/exit", "/stop"]:
                if text_list in (["q"], ["quit"], ["exit"], ["stop"], ["-q"], ["-quit"], ["-exit"], ["-stop"], ["/q"], ["/quit"], ["/exit"], ["/stop"]):
                # if text_list in (("q"), ("quit"), ("exit"), ("stop"), ("-q"), ("-quit"), ("-exit"), ("-stop"), ("/q"), ("/quit"), ("/exit"), ("/stop")):
                    print("buy!")
                    sys.exit()
                
                # PRINT help
                # if text.lower() in ["h", "help", "-h", "-help", "/h", "/help"]:
                if text_list in (["h"], ["help"], ["-h"], ["-help"], ["/h"], ["/help"]):
                    # call help printout
                    print("\nHelp text will be there")
                    self.print_help()
                    # self.print_models()
                    continue

                if text_list in (["h", "m"], ["help", "m"], ["-h", "m"], ["-help", "m"], ["/h", "m"], ["/help", "m"], ["h", "-m"], ["help", "-m"], ["-h", "-m"], ["-help", "-m"], ["/h", "-m"], ["/help", "-m"], ["h", "models"], ["help", "models"], ["-h", "models"], ["-help", "models"], ["/h", "models"], ["/help", "models"], ["hm"], ["-hm"], ["-h-m"], ["/hm"], ["/h/m"], ["/h", "/m"], ["/help/models"], ["/help", "/models"]):
                    # print available models
                    # print("\nHelp text will be there")
                    self.print_models()
                    continue
                
                if text_list in (["h", "s"], ["help", "s"], ["-h", "s"], ["-help", "s"], ["/h", "s"], ["/help", "s"], ["h", "-s"], ["help", "-s"], ["-h", "-s"], ["-help", "-s"], ["/h", "-s"], ["/help", "-s"], ["h", "servers"], ["help", "servers"], ["-h", "servers"], ["-help", "servers"], ["/h", "servers"], ["/help", "servers"], ["hs"], ["-hs"], ["-h-s"], ["/hs"], ["/h/s"], ["/h", "/s"], ["/help/servers"], ["/help", "/servers"]):
                    # print available servers
                    self.print_servers()
                    continue
                
                if text_list in (["h", "r"], ["help", "r"], ["-h", "r"], ["-help", "r"], ["/h", "r"], ["/help", "r"], ["h", "-r"], ["help", "-r"], ["-h", "-r"], ["-help", "-r"], ["/h", "-r"], ["/help", "-r"], ["h", "roles"], ["help", "roles"], ["-h", "roles"], ["-help", "roles"], ["/h", "roles"], ["/help", "roles"], ["hr"], ["-hr"], ["-h-r"], ["/hr"], ["/h/r"], ["/h", "/r"], ["/help/roles"], ["/help", "/roles"]):
                    # print available servers
                    self.print_roles()
                    continue

                # PRINT current settings
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
                # pass
                
                # DELETE chat history - del all dicts from messages but system. Same as "del all"
                # elif text.lower() in ["clear", "-clear", "/clear"]:
                elif text_list in (["clear"], ["-clear"], ["/clear"]):
                    self.set_messages()
                    print("\nMessage history cleared")
                    # print(self.messages)
                    # self.print_messages()
                    continue

                # SET conversation mod On or Off
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

                # SET pronunciation mode (say) On or Off
                elif text_list in (["say+"], ["/say+"]):
                    self.pronunciation = True
                    self.print_pronunciation_updated()
                    continue
                elif text_list in (["say-"], ["/say-"]):
                    self.pronunciation = False
                    self.print_pronunciation_updated()
                    continue

                # PRINT messages list of dictionaries 
                # elif text.lower() in ["print"]:
                elif text_list in (["print"], ["/print"]):
                    # print("\n", self.messages, sep="")
                    self.print_messages()
                    continue

                # PRINT selected pair of user and assistant messages
                elif text.startswith("print ") or text.startswith("print["):
                    # for pattern like: "print 123" or "print[123]"
                    if text[6].isdigit():
                        i = 0
                        for ch in text[6:]:
                            if ch.isdigit():
                                i += 1
                            else:
                                break
                        index = int(text[6:6+i])
                        self.print_messages_pair(index)
                    else:
                        print("\nWrong command:", text)
                    continue

                # DELETE last user prompt and last model answer
                # elif text == "del -1":
                elif text_list in (["del", "-1"],):
                    if len(self.messages) <= 0:
                        print("No messages")
                        # print("Current messages:")
                        # self.print_messages()
                        continue
                    else:
                        self.messages = self.messages[:-2]
                        print("\nLast message and response have been deleted")
                        if len(self.messages) > 0:
                            print("Current messages:")
                            self.print_messages()
                        else:
                            print("No messages")
                        continue
                
                # DELETE all messages - same as "clear"
                elif text_list in (["del", "all"],):
                    self.set_messages()
                    print("\nMessage history cleared")
                    continue

                # DELETE selected pair of user prompt and model answer
                elif text.startswith("del ") or text.startswith("del["):
                    # for pattern like: "del 123" or "del[123]"
                    if text[4].isdigit():
                        i = 0
                        for ch in text[4:]:
                            if ch.isdigit():
                                i += 1
                            else:
                                break
                        index = int(text[4:4+i])
                        if self.del_messages_pair(index) is True:
                            print(f"\nMessage pair {index} have been deleted")
                            print("Current messages:")
                            self.print_messages()
                            continue
                    else:
                        print("\nWrong command:", text)
                    continue
                
                # TURN OFF simple "del" command 
                elif text == "del":
                    print("\nWrong command:", text)
                    continue

                # SET server, openai, anthropic or ollama
                elif text in self.servers:
                    self.set_server(text)                              # change server first
                    self.set_model(list(self.models[self.server])[0])  # and model second
                    self.set_url()                                     # setup appropriate url
                    self.set_header()                                  # setup appropriate header
                    print("\nnew server and model")
                    print("server:", self.server)
                    print("model: ", self.model)
                    continue   # use it only if there is just one key phrase in the input.
                
                # set model which leads to auto changing server  - only if there is one word
                elif text in self.model_names:
                    self.set_server(self.modes_by_models[text])  # change server first
                    self.set_model(text)                         # and model second
                    self.set_url()                               # setup appropriate url
                    self.set_header()                            # setup appropriate header
                    self.print_server_model_update()
                    continue  # use it only if there is just one key phrase in the input.
                
                # set role
                elif text in self.roles:
                    self.set_role(text)
                    print("\nnew role")
                    self.print_server_model_update()
                    continue
            
            self.user_prompt = json.dumps(obj=text, ensure_ascii=False)  # convert string to json compatible format
            return self.user_prompt
    

    # pronounce given text
    # It uses now a simple "say" terminal app call on macbook and it's assumed that the given text is on English
    # potentially i could be improved to call a separate language model with auto language determination.
    def pronounce_text(self, text_queue):
        while True:
            text = text_queue.get()
            if text is None:
                break
            subprocess.run(["say", text])  # speak english
            text_queue.task_done() 
    
###
    # Depending on server, there would be different end-points to extract the content from the response
    # concurrent printout model response with pronunciation by Apple terminal cli app "say"
    def print_and_say(self, stream):
        text_queue = queue.Queue()
        pronunciation_thread = threading.Thread(target=self.pronounce_text, args=(text_queue,))
        pronunciation_thread.start()
        buffer = []
        response = []
        flag_code = True  # True: print chunks, False: skip chunks
        for chunk in stream:
            chunk_text = chunk.choices[0].delta.content
            if chunk_text:
                # manage code pronunciation
                buffer_text = chunk_text
                if chunk_text.startswith("``"):
                    if flag_code is True:  # it means that it's a start of the code snippet
                        flag_code = False
                        # buffer_text = [" The code snippet you may find in my text response. "]
                        buffer_text = [" "]*len(chunk_text)
                        buffer.extend(buffer_text)
                    else:
                        flag_code = True
                        buffer_text = [""]
                response.append(chunk_text)
                print(chunk_text, end="", flush=True)
                if flag_code is True:
                    # buffer.extend(buffer_text)
                    pass
                else:
                    buffer_text = [" "]*len(chunk_text)
                buffer.extend(buffer_text)
                # print(buffer, flush=True)
                if len(buffer) >= 100:
                    sentence = "".join(buffer)
                    text_queue.put(sentence)
                    buffer = []
        print()
        if buffer:
            sentence = "".join(buffer)
            text_queue.put(sentence)
        text_queue.put(None)
        pronunciation_thread.join()
        response = "".join(response)
        self.assistant_response = response

# ###
        
    # def print_stream(self, stream):
    #     response = []
    #     for chunk in stream:
    #         chunk_text = chunk.choices[0].delta.content
    #         if chunk_text:
    #             response.append(chunk_text)
    #             # print(chunk_text, end="", flush=True)
    #             sys.stdout.write(chunk_text)
    #             sys.stdout.flush()
    #     print()
    #     response = "".join(response)
    #     ta.assistant_response = response


    # Depending on server, there would be different end-points to extract the content from the response
    def print_stream(self, stream):
        response = []

        if self.server == "ollama":
            for chunk in stream.iter_lines():
                decoded_chunk = chunk.decode('utf-8')
                chunk_data = json.loads(decoded_chunk)
                chunk_text = chunk_data['message']['content']
                if chunk_text:
                    response.append(chunk_text)
                    print(chunk_text, end="", flush=True)
                # else:
                #     response.append("<nothing>")
            print()
            response = "".join(response)
            ta.assistant_response = response

        elif self.server == "openai":
            for chunk in stream.iter_lines():
                if chunk:
                    decoded_chunk = chunk.decode("utf-8")
                    if decoded_chunk == "data: [DONE]":
                        break
                    elif '"delta":{"role":"assistant"' in decoded_chunk:
                        continue
                    chunk_data = json.loads(decoded_chunk[6:])
                    if chunk_data["choices"][0]["delta"]:
                        chunk_text = chunk_data["choices"][0]["delta"]["content"]
                        print(chunk_text, end="", flush=True)
                        response.append(chunk_text)

        elif self.server == "anthropic":
            for chunk in stream.iter_lines():
                if chunk:
                    decoded_chunk = chunk.decode('utf-8')
                    if decoded_chunk.startswith('data'):
                        chunk_data = json.loads(decoded_chunk[6:])
                        if chunk_data['type'] == 'content_block_delta':
                            chunk_text = chunk_data['delta']['text']
                            print(chunk_text, end="", flush=True)
                            response.append(chunk_text)

        print()
        response = "".join(response)
        ta.assistant_response = response


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

        # # as it's possible to delete even system message, check that system message is exist and create it if needed
        # if len(ta.messages) == 0 or ta.messages[0]["role"] != "system":  # probably don't need to check this ta.messages[0]["role"] != "system" as there is no way to have first message different from system.

### probably need to delete this and the relative method set_messages()    
        if len(ta.messages) == 0:
            ta.set_messages()
        if ta.conversation is True:
            ta.add_user_message()  # add user message to the list
        else:
            ta.set_messages()  # reset messages
            ta.add_user_message()  # add user message to the list
        # prompt = ta.process_input()

        ta.set_data()   # initialise data


        # print llm answer header
        number_of_spaces = len(ta.model) + 1
        print("\n\n┌", "─" * number_of_spaces, "┐", sep='')
        print(f"│{ta.model}:│")

        stop_event = threading.Event()
        spinner_thread = threading.Thread(target=display_spinner, args=(stop_event, 1))
        # spinner_thread = threading.Thread(target=display_spinner, args=(stop_event, number_of_spaces))
        try:
            spinner_thread.start()
        
            # here we communicate to API
            stream = requests.post(ta.url, data=json.dumps(ta.data), headers=ta.header, stream=True)

            # stop spinner after receiving answer from ollama or ChatGPT 
            stop_event.set()
            spinner_thread.join()

###         simple text
            if stream.status_code == 200:
                ta.print_stream(stream)  # print response from the API

            else:
                print(json.dumps(json.loads(stream.text), indent=4))
                    # #### print and say or just print the response
                    # if ta.pronunciation is True:
                    #     ta.print_and_say(stream)
                    # else:
                    #     ta.print_stream(stream)

            # # a simple text answer 
            # response = []
            # for chunk in stream:
            #     if chunk.choices[0].delta.content:
            #         response.append(chunk.choices[0].delta.content)
            #         print(chunk.choices[0].delta.content, end="", flush=True)
            # print()
            # response = "".join(response)
            # ta.assistant_response = response



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