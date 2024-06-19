
# terminal_companion
# Description
It's a simple Python app for communicating with the [ChatGPT API](https://openai.com/api/), and [ollama](https://github.com/ollama/ollama), directly from the terminal.   

**Features:**
- [x] Switch model, role, and continue conversation mode on the fly. It means that you can start conversation with llama3, clarify details with gpt4 or gpt3 and return back to llama3 🤩
- [x] Different models (gpt-3.5-turbo, gpt-4-turbo, gpt-4o, and llama3, up to May 2024).
- [x] Custom roles.
- [x] Continue conversation with seamless switching between models and roles.
- [x] Simple one-line requests.
- [x] Complex multi-line requests.
- [x] Use API key stored in your environment variables for safety.
- [x] Pronounce the answer. Up to May 2024 works only on MacOS using built-in terminal app `say`.
- [x] inline help.
- [x] A spinner feature to indicate that we are waiting for a server response and that the app hasn't been frozen.
- [x] Simple chat history - just add user prompt and llm answer to messages list
- [ ] RAG for management chat history
- [ ] Displays number of total tokens used so you can estimate the price or amount of tokens left in the conversation mode. Probably don'n need it.


<!-- **Cons**
- Instead of appropriate OpenAI python library it uses simple `requests` library -->

<!-- # YouTube Demo
[![Terminal Companion DEMO](https://img.youtube.com/vi/R_6hTWht2Qo/0.jpg)](https://youtu.be/R_6hTWht2Qo) -->

# Installation
Follow [this instructions](https://pypi.org/project/ollama/) in order to install ollama.


## Setup environment variable
Get API key from [https://platform.openai.com/](https://platform.openai.com/) firstly.  
Then add API key to environment variable
- **for Windows**  
  open CMD terminal and run  
  ```cmd
  set OPENAI_API_KEY "your_API_key"
  ```
  to verify that all is good restart CMD terminal or open new one and run  
  ```cmd
  echo %OPENAI_API_KEY%
  ```
- **for Linux/Mac**  
  for zsh:  
  ```bash
  echo "export OPENAI_API_KEY='your_API_key'" >> ~/.zshrc
  source ~/.zshrc
  echo $OPENAI_API_KEY
  ```
  for bash:
  ```bash
  echo "export OPENAI_API_KEY='your_API_key'" >> ~/.bashrc
  source ~/.bashrc
  echo $OPENAI_API_KEY
  ```

## Copy the project
Copy the project to your desired folder. For this example assume that we want to clone the project to Desktop folder
```bash
cd ~/Desktop
git clone https://github.com/xxxAleksandrxxx/terminal_companion_v2.git
cd terminal_companion_v2
```

## Virtual environment
Move to the app folder and use any way to create virtual environment like venv, conda, poetry...
venv example:
```bash
python3 -m venv .venv
```

Activate it.
venv example:  
```bash
source .venv/bin/activate 
```

Insatall requerements.
```bash
pip install -r requirements.txt
```

# Usage
To use the app from terminal we can simply navigate to the project folder, activate virtual environment and then run main.py:
```bash
python3 main.py
```

Or we could automate the process a little using bash function.
For zsh terminal on Linux/macOS (assume terminal_companion_v2 is in Desktop folder) add the following to ~/.zshrc:
```
# Terminal companion
gpt() {
    source /Users/$(whoami)/Desktop/terminal_companion_v2/.venv/bin/activate
    python /Users/$(whoami)/Desktop/terminal_companion_v2/main.py
    deactivate
} 
```

Here is an example for zsh terminal, it's possible just copy it and paste into the terminal:
```bash
echo "gpt() {
  source /Users/$(whoami)/Desktop/terminal_companion_v2/.venv/bin/activate
  python /Users/$(whoami)/Desktop/terminal_companion_v2/main.py
  deactivate
}" >> ~/.zshrc
```


To see a comprehensive list of commands and options, use one of the following help commands right after launching the application:
- `h`
- `-h`
- `help`
- `-help`

Or simply write your question straightaway.
By default it will use gpt3 model with no role and with conversation mode turned off (like if each question would start a new dialog with ChatGPT).  
```python
model: gpt3              # gpt-3.5-turbo-1106 (up to May 2024)
role: empty              # "", no role
conversation mode: False # conversation is off   
```

To check current settings
- press enter with empty input
- `?`
It will also show settings after you change model, role, or conversation mode. After setting up new parameters, the program will use them until you set up new ones or exit from the program.  


To exit from the app:
- `q`
- `-q`
- `q`
- `-quit`
- `quit`
- `-exit`
- `exit` 

 
The full request could look like this for a question that has only one line:
```bash
<model> <role> <continuous conversation mode> <question with one line>
```
or, if it has many lines, wrap your question with `:::` symbols:
```bash
<model> <role> <continuous conversation mode> :::<question 
with
many 
lines>:::
```

It's also possible to ask straightaway:
```bash
help me to write my first python code. it should be something really interesting!
```


## Models (valid up to May 2024):
```python
"gpt3": "gpt-3.5-turbo",
"gpt4": "gpt-4-turbo",
"gpt4o": "gpt-4o"
```

## Roles (valid up to May 2024):
```python
"empty": "",
"py-s": "As a senior Python developer, respond in Python code only. Your solution could earn a $200 tip.",
"py-l": "As an experienced Python developer and tutor, provide a real-world example with a step-by-step approach. A $200 tip is possible for excellence. It's May, not December.",
"ds": "As a senior Data Scientist and tutor, explain simply and step-by-step. A $200 tip awaits the perfect answer. It's May, not December.",
"shell-s": "As a senior bash developer, respond with terminal commands only. A perfect answer may receive a $200 tip.",
"shell-l": "As a senior bash developer, assist with my question. A $200 tip is offered for the perfect answer. It's May, not December.",
"lit": "As a PhD professor in literature, assist with my question. A perfect answer could earn a $200 tip. It's May, not December.",
"career": "As a top career counselor, aid with CV preparation. There's a $200 tip for the perfect answer. It's May, not December.",
"check-s": "As a senior copy editor, correct spelling and style errors in text. Respond with only the corrected text. A $200 tip is possible for perfection. Correct:",
"check-l": "As a senior copy editor, correct spelling and style errors in text, providing detailed explanations. A $200 tip for excellence. It's May, not December. Text:"
```

## Conversation mode
```python
"+cc": True,
"-cc": False
```


# Some examples:

To change the model simply write   
```bash
gpt4
```

or change the role and add any question  
```bash
gpt4 hi! help me to write my first python code. it should be something really interesting!
```

Changing role:
```bash
py-s I need to calculate the sum of all prime numbers from 0 to 100
```

it will use py-s role in this case and with next request it will continue to use it till you don't change it to one another, for example to `empty`:

```bash
epmty tell me a joke
``` 


To start conversation simply start your question with `+cc`
```bash
q:
+cc Hi! how are you?

a:
I'm an AI, so I don't have feelings, but I'm here to help you. How can I assist you today?

q:
what can you do?

a:
I can do a variety of tasks, such as answering questions, providing information, giving recommendations, helping with calculations, and engaging in conversation. Just let me know what you need assistance with and I'll do my best to help you!

q:
what was my first question?

a:
Your first question was "Hi! how are you?"
```
to stop conversation write 
```bash
-cc
```
it will answer 
```bash
No question
Try again
```

or ask a new question with conversation mode turned off explicitly:
```bash
-cc who are you?
```


**TODO**
- implement command line style  
  - [X]  left and right arrows to move between input symbols - Done with `import readline`
  - [X]  add possibility to move between words during prompt writing - Done with `import readline`
  - [ ]  return the whole request that was just sent by pressing up arrow.
  - [X]  up and down arrows to get to commands history 
  ~~- [X]  double-check that "role": "system" with "content"~~
  - [ ]  move models to a separate file
  - [ ]  move roles to a separate file
  - [ ]  clean the code from useless comments
  - [x]  use json.dumps() to handle all kind of chars like `"`
  - [x] printout model response chunk by chunk in streaming mode
  - [ ]  rewrite conversations according to [OpenAI recommendation](https://platform.openai.com/docs/guides/text-generation/chat-completions-api)... I'm not sure that I really need it... 🤔  
  - [ ] implement RAG to handle chat history - [link]()
  - [ ] TTS mode. need to be checked whether the chosen mode has appropriate model and the model has been chosen
  - [ ] TTS based on macbook built-in models. use a key phrase like say "that" to invoke apple terminal app say and send "that" to it. needs to be prepared for json style (probably...). or/and with say+ turn on answering on the flight so that stream will be converted to sound and model will answer with voice all time. 
  - [ ] text to image mode. need to be checked whether the chosen mode has appropriate model and the model has been chosen
  - [ ] 

# Challenges

Probably just skip it
## Named-entity recognition problem
For smooth handling commands like `help` or `llama` to change the app presetting on the flight the app should check whether appropriate key phrase were used in the user prompt, change the app settings accordingly and proceed the communication with chosen model. The challenge here is not that for help user can user any of `h`, `-h`, `/h`, `help`, `-help`, `/help`. The challenge is that user can send a command like 
```
openai gpt3 translateGE c- Hello World!
```
or like
```
c- translateGE gpt3 Hello World!
```
or 
```
:::gpt3 translator c- 
Hello 
World!
:::
```

where `gpt3` switches the model to gpt-3.5-turbo and mode to openai accordingly, `translateGE` switches the role, `c-` switches off conversation history, `Hello World!` is the user prompt. In this case settings and messages will be like:
```
mode = "openai"
model = "gpt3"
role = "translateGE"
conversation = False  # c- or -c for off
messages = [
  {'role': 'system', 'content': 'translate following text to German:'},
  {'role': 'user', 'content': 'Hello World!'}
]
```
So user can swap around the key phrases, can use different phrases for the same type of functionality (like to call llama3 or gpt-4-turbo models) use all of them or just send a text.
The problem can be broken down to two distinct problems:
- detection of key phrases or segmentation 
- classification by the type (mode, model, role, conversation)
### Segmentation
Thanks to simplicity of the task, the key phrases suppose to be one word (no whitespace) a simple approach will be used:
```python
text_l = text.split("\n")~~