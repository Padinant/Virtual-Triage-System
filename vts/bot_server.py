"""
A server for the LLM client.
"""

from vts.chat_server import get_session
from vts.llm import create_agent_client
from vts.llm import get_agent_response

def bot_session():
    "Starts a bot session infinite loop."
    user_queue, bot_queue = get_session()
    client = create_agent_client()
    while True:
        user_message = user_queue.get()
        response = get_agent_response(client, user_message)
        bot_queue.put(response)

if __name__ == "__main__":
    bot_session()
