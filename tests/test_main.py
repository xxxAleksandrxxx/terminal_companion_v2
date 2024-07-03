from terminal_companion_v2.main import AssistantLLM
import unittest
from unittest.mock import patch  #, Mock
import os
# import requests
# import json
# import queue

# Set up test API keys - these are fake keys
os.environ["OPENAI_API_KEY"] = "sk-test-fake-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "test-fake-anthropic-api-key"

class TestAssistantLLM(unittest.TestCase):

    def setUp(self):
        """Setup method to create an instance of the class before each test."""
        self.assistant = AssistantLLM()

    # -- Test initialisation and settings --
    def test_init(self):
        """Test if the __init__ method initializes the attributes correctly."""
        self.assertEqual(self.assistant.server, "ollama")
        self.assertEqual(self.assistant.model, "llama3")
        self.assertEqual(self.assistant.temperature, 0.3)
        self.assertEqual(self.assistant.max_tokens, 1024)
        self.assertEqual(self.assistant.conversation, False)
        self.assertEqual(self.assistant.pronunciation, False)

    def test_set_server(self):
        """Test if the set_server method sets the server correctly."""
        self.assistant.set_server("openai")
        self.assertEqual(self.assistant.server, "openai")
        self.assistant.set_server("anthropic")
        self.assertEqual(self.assistant.server, "anthropic")

    def test_set_servers_by_models(self):
        """Test if the set_servers_by_models method sets the correct server based on the model."""
        self.assistant.set_servers_by_models()
        self.assertEqual(self.assistant.modes_by_models['gpt3'], "openai")
        self.assertEqual(self.assistant.modes_by_models['llama3'], "ollama")
        self.assertEqual(self.assistant.modes_by_models['ha3'], "anthropic")

    def test_set_model(self):
        """Test if the set_model method sets the model correctly."""
        self.assistant.set_server("openai")
        self.assistant.set_model("gpt3")
        self.assertEqual(self.assistant.model, "gpt-3.5-turbo")
        self.assistant.set_server("ollama")
        self.assistant.set_model("llama3")
        self.assertEqual(self.assistant.model, "llama3")
        self.assistant.set_server("anthropic")
        self.assistant.set_model("ha3")
        self.assertEqual(self.assistant.model, "claude-3-haiku-20240307")

    def test_set_model_names(self):
        """Test if the set_model_names method correctly sets the list of model names."""
        self.assistant.set_model_names()
        self.assertIn("gpt3", self.assistant.model_names)
        self.assertIn("gpt4o", self.assistant.model_names)
        self.assertIn("gpt4", self.assistant.model_names)
        self.assertIn("llama3", self.assistant.model_names)
        self.assertIn("ha3", self.assistant.model_names)
        self.assertIn("sn35", self.assistant.model_names)
        self.assertIn("op3", self.assistant.model_names)

    def test_set_role(self):
        """Test if the set_role method sets the role correctly."""
        self.assistant.set_role("coder")
        self.assertEqual(self.assistant.role_name, "coder")
        self.assertEqual(self.assistant.role, self.assistant.roles["coder"])

    def test_set_messages(self):
        """Test if the set_messages method initializes the messages attribute as an empty list."""
        self.assistant.set_messages()
        self.assertEqual(self.assistant.messages, [])

    def test_set_url(self):
        """Test if the set_url method sets the correct URL based on the server."""
        self.assistant.set_server("openai")
        self.assistant.set_url()
        self.assertEqual(self.assistant.url, "https://api.openai.com/v1/chat/completions")
        self.assistant.set_server("ollama")
        self.assistant.set_url()
        self.assertEqual(self.assistant.url, "http://localhost:11434/api/chat")
        self.assistant.set_server("anthropic")
        self.assistant.set_url()
        self.assertEqual(self.assistant.url, "https://api.anthropic.com/v1/messages")

    def test_set_header(self):
        """Test if the set_header method sets the correct header based on the server."""
        self.assistant.set_server("openai")
        self.assistant.set_header()
        self.assertEqual(self.assistant.header['Authorization'], "Bearer " + os.environ["OPENAI_API_KEY"])
        self.assistant.set_server("ollama")
        self.assistant.set_header()
        self.assertEqual(self.assistant.header['Content-Type'], "application/json")
        self.assistant.set_server("anthropic")
        self.assistant.set_header()
        self.assertEqual(self.assistant.header['x-api-key'], os.environ["ANTHROPIC_API_KEY"])

    def test_set_data(self):
        """Test if the set_data method sets the data field correctly for different servers."""
        # Test for ollama
        self.assistant.set_server("ollama")
        self.assistant.set_data()
        self.assertEqual(self.assistant.data['model'], "llama3")
        self.assertEqual(self.assistant.data['temperature'], 0.3)
        self.assertEqual(self.assistant.data['max_tokens'], 1024)
        self.assertEqual(self.assistant.data['stream'], True)
        self.assertEqual(self.assistant.data['messages'][0]['role'], 'system')
        # Test for openai
        self.assistant.set_server("openai")
        self.assistant.set_model("gpt3")
        self.assistant.set_data()
        self.assertEqual(self.assistant.data['model'], "gpt-3.5-turbo")
        self.assertEqual(self.assistant.data['temperature'], 0.3)
        self.assertEqual(self.assistant.data['max_tokens'], 1024)
        self.assertEqual(self.assistant.data['stream'], True)
        self.assertEqual(self.assistant.data['messages'][0]['role'], 'system')
        # Test for anthropic
        self.assistant.set_server("anthropic")
        self.assistant.set_model("ha3")
        self.assistant.set_data()
        self.assertEqual(self.assistant.data['model'], "claude-3-haiku-20240307")
        self.assertEqual(self.assistant.data['temperature'], 0.3)
        self.assertEqual(self.assistant.data['max_tokens'], 1024)
        self.assertEqual(self.assistant.data['stream'], True)
        self.assertEqual(self.assistant.data['system'], self.assistant.role)

    def test_add_user_message(self):
        """Test if the add_user_message method adds the user message to the messages list."""
        self.assistant.user_prompt = "Hello"
        self.assistant.add_user_message()
        self.assertEqual(self.assistant.messages[0]['role'], 'user')
        self.assertEqual(self.assistant.messages[0]['content'], 'Hello')

    def test_del_messages_pair(self):
        """Test if the del_messages_pair method correctly deletes a pair of messages."""
        # Add two pairs of messages
        self.assistant.messages.append({'role': 'user', 'content': 'Hello'})
        self.assistant.messages.append({'role': 'assistant', 'content': 'Hi there!'})
        self.assistant.messages.append({'role': 'user', 'content': 'How are you?'})
        self.assistant.messages.append({'role': 'assistant', 'content': 'I am doing well, thank you.'})
        # Delete the first pair
        self.assistant.del_messages_pair(0)
        # Check if the first pair is deleted and the second pair remains
        self.assertEqual(len(self.assistant.messages), 2)
        self.assertEqual(self.assistant.messages[0]['content'], 'How are you?')
        self.assertEqual(self.assistant.messages[1]['content'], 'I am doing well, thank you.')

    # # -- Test print methods --
    # # ... (Tests for print methods - these are already covered by other tests)

    # -- Test input and processing methods --
    @patch('builtins.input', return_value='Hello')
    def test_input_multi_single_line(self, mock_input):
        """Test input_multi method with a single line input."""
        text = self.assistant.input_multi()
        self.assertEqual(text, "Hello")

    @patch('builtins.input', side_effect=[':::', 'Hello', 'world', ':::'])
    def test_input_multi_multi_line(self, mock_input):
        """Test input_multi method with a multi-line input."""
        text = self.assistant.input_multi()
        self.assertEqual(text, "Hello\nworld")

    @patch('builtins.input', side_effect=['/quit', 'Hello'])
    def test_process_input_quit(self, mock_input):
        """Test process_input method with the quit command."""
        with self.assertRaises(SystemExit):
            self.assistant.process_input()

    @patch('builtins.input', side_effect=['/help', 'Hello'])
    def test_process_input_help(self, mock_input):
        """Test process_input method with the help command."""
        with patch('builtins.print') as mock_print:
            self.assistant.process_input()
            mock_print.assert_called()

    @patch('builtins.input', side_effect=['/clear', 'Hello'])
    def test_process_input_clear(self, mock_input):
        """Test process_input method with the clear command."""
        self.assistant.messages = [{'role': 'user', 'content': 'Test message'}]
        self.assistant.process_input()
        self.assertEqual(self.assistant.messages, [])

    @patch('builtins.input', side_effect=['/c+', 'Hello'])
    def test_process_input_conversation_on(self, mock_input):
        """Test process_input method with the conversation on command."""
        self.assistant.process_input()
        self.assertTrue(self.assistant.conversation)

    @patch('builtins.input', side_effect=['/c-', 'Hello'])
    def test_process_input_conversation_off(self, mock_input):
        """Test process_input method with the conversation off command."""
        self.assistant.process_input()
        self.assertFalse(self.assistant.conversation)

    @patch('builtins.input', side_effect=['/say+', 'Hello'])
    def test_process_input_pronunciation_on(self, mock_input):
        """Test process_input method with the pronunciation on command."""
        self.assistant.process_input()
        self.assertTrue(self.assistant.pronunciation)

    @patch('builtins.input', side_effect=['/say-', 'Hello'])
    def test_process_input_pronunciation_off(self, mock_input):
        """Test process_input method with the pronunciation off command."""
        self.assistant.process_input()
        self.assertFalse(self.assistant.pronunciation)

    @patch('builtins.input', side_effect=['print', 'Hello'])
    def test_process_input_print(self, mock_input):
        """Test process_input method with the print command."""
        with patch('builtins.print') as mock_print:
            self.assistant.messages = [{'role': 'user', 'content': 'Test message'}]
            self.assistant.process_input()
            mock_print.assert_called()

    @patch('builtins.input', side_effect=['print 0', 'Hello'])
    def test_process_input_print_index(self, mock_input):
        """Test process_input method with the print command and index."""
        with patch('builtins.print') as mock_print:
            self.assistant.messages = [{'role': 'user', 'content': 'Test message 1'}, {'role': 'assistant', 'content': 'Test message 2'}]
            self.assistant.process_input()
            mock_print.assert_called()

    @patch('builtins.input', side_effect=['del -1', 'Hello'])
    def test_process_input_del_last(self, mock_input):
        """Test process_input method with the delete last message command."""
        self.assistant.messages = [{'role': 'user', 'content': 'Test message 1'}, {'role': 'assistant', 'content': 'Test message 2'}]
        self.assistant.process_input()
        self.assertEqual(len(self.assistant.messages), 0)

    @patch('builtins.input', side_effect=['del all', 'Hello'])
    def test_process_input_del_all(self, mock_input):
        """Test process_input method with the delete all messages command."""
        self.assistant.messages = [{'role': 'user', 'content': 'Test message 1'}, {'role': 'assistant', 'content': 'Test message 2'}]
        self.assistant.process_input()
        self.assertEqual(self.assistant.messages, [])

    @patch('builtins.input', side_effect=['del 0', 'Hello'])
    def test_process_input_del_index(self, mock_input):
        """Test process_input method with the delete message by index command."""
        self.assistant.messages = [{'role': 'user', 'content': 'Test message 1'}, {'role': 'assistant', 'content': 'Test message 2'}, {'role': 'user', 'content': 'Test message 3'}, {'role': 'assistant', 'content': 'Test message 4'}]
        self.assistant.process_input()
        self.assertEqual(len(self.assistant.messages), 2)
        self.assertEqual(self.assistant.messages[0]['content'], 'Test message 3')
        self.assertEqual(self.assistant.messages[1]['content'], 'Test message 4')

    @patch('builtins.input', side_effect=['openai', 'Hello'])
    def test_process_input_set_server(self, mock_input):
        """Test process_input method with setting a server."""
        self.assistant.process_input()
        self.assertEqual(self.assistant.server, "openai")

    @patch('builtins.input', side_effect=['gpt3', 'Hello'])
    def test_process_input_set_model(self, mock_input):
        """Test process_input method with setting a model."""
        self.assistant.process_input()
        self.assertEqual(self.assistant.model, "gpt-3.5-turbo")

    @patch('builtins.input', side_effect=['coder', 'Hello'])
    def test_process_input_set_role(self, mock_input):
        """Test process_input method with setting a role."""
        self.assistant.process_input()
        self.assertEqual(self.assistant.role_name, "coder")

    # # -- Test pronounce_text method --
    # @patch('subprocess.run')
    # def test_pronounce_text(self, mock_subprocess):
    #     """Test pronounce_text method."""
    #     text_queue = queue.Queue()
    #     text_queue.put("Hello")
    #     text_queue.put(None)  # Signal the end of the queue
    #     self.assistant.pronounce_text(text_queue)
    #     mock_subprocess.assert_called_with(["say", "Hello"])

    # # -- Test print_and_say method --
    # # ... (This method is difficult to test due to threading and requires a more complex setup)

    # -- Test print_stream method --
    def test_print_stream_ollama(self):
        """Test print_stream method with Ollama response."""
        class MockResponse:
            def __init__(self, status_code):
                self.status_code = status_code

            def iter_lines(self):
                yield b'{"message": {"content": "Hello"}}'
                yield b'{"message": {"content": " world!"}}'

        with patch('requests.post', return_value=MockResponse(200)) as mock_post:
            self.assistant.set_server("ollama")
            self.assistant.print_stream(mock_post.return_value)
            self.assertEqual(self.assistant.assistant_response, "Hello world!")

    def test_print_stream_openai(self):
        """Test print_stream method with OpenAI response."""
        class MockResponse:
            def __init__(self, status_code):
                self.status_code = status_code

            def iter_lines(self):
                yield b'data: {"choices": [{"delta": {"content": "Hello"}}]}'
                yield b'data: {"choices": [{"delta": {"content": " world!"}}]}'
                yield b'data: [DONE]'

        with patch('requests.post', return_value=MockResponse(200)) as mock_post:
            self.assistant.set_server("openai")
            self.assistant.print_stream(mock_post.return_value)
            self.assertEqual(self.assistant.assistant_response, "Hello world!")

    def test_print_stream_anthropic(self):
        """Test print_stream method with Anthropic response."""
        class MockResponse:
            def __init__(self, status_code):
                self.status_code = status_code

            def iter_lines(self):
                yield b'data: {"type": "content_block_delta", "delta": {"text": "Hello"}}'
                yield b'data: {"type": "content_block_delta", "delta": {"text": " world!"}}'

        with patch('requests.post', return_value=MockResponse(200)) as mock_post:
            self.assistant.set_server("anthropic")
            self.assistant.print_stream(mock_post.return_value)
            self.assertEqual(self.assistant.assistant_response, "Hello world!")


if __name__ == '__main__':
    unittest.main()