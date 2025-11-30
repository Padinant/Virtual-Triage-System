"""
Creates a server to persist the chat state.
"""

import atexit
from multiprocessing import Lock
from multiprocessing.managers import BaseManager
from queue import Queue

sessions = {}
lock = Lock()
user_queue = Queue()
bot_queue = Queue()

def get_llm_session(session_id):
    "Store an LLM session."
    with lock:
        if session_id not in sessions:
            sessions[session_id] = "Test"

        return sessions[session_id]

def start_server():
    "Start the chat server."
    manager = BaseManager(address=('', 55331), authkey=b'test')
    # manager.register('get_llm_session', get_llm_session)
    manager.register('get_user_queue', callable=lambda:user_queue)
    manager.register('get_bot_queue', callable=lambda:bot_queue)
    server = manager.get_server()
    server.serve_forever()

@atexit.register
def close_server():
    "Cleanup and notification of closing the server."
    print("\nClosing chat server!")

def get_session():
    "Return the two queues."
    manager = BaseManager(address=('', 55331), authkey=b'test')
    # manager.register('get_llm_session')
    manager.register('get_user_queue')
    manager.register('get_bot_queue')
    manager.connect()
    # Note: Again, here's some Python magic that pylint can't figure out.
    # pylint:disable-next=no-member
    return manager.get_user_queue(), manager.get_bot_queue()

if __name__ == "__main__":
    print("Hello!")
    start_server()
