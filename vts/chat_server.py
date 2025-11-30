"""
Creates a server to persist the chat state.
"""

import time

from irc.bot import SingleServerIRCBot
from irc.bot import ServerSpec

from vts.config import load_config

from vts.llm import create_agent_client
from vts.llm import get_agent_response

# Our bot likes to send multiple lines, so let's send the line "End
# Msg" backwards, which is extremely unlikely to be a valid output
# line.
END_MSG = 'gsM dnE'

class LlmBot(SingleServerIRCBot):
    "A bot representing the LLM"
    # pylint:disable-next=unused-argument
    def on_welcome(self, c, e):
        "Autojoin a channel; ignore e"
        c.join("#test")

    def on_pubmsg(self, c, e):
        "Take any responses in the channel and reply with the chatbot."
        # nick = e.source.nick
        message = e.arguments[0]
        agent = create_agent_client()
        print(message)
        response = get_agent_response(agent, message)
        print(response)
        lines = response.split('\n')
        for line in lines:
            c.privmsg("#test", line)
        c.privmsg('#test', END_MSG)

class GuestBot(SingleServerIRCBot):
    "A bot representing the LLM"
    def __init__(self, server_list, nickname, realname):
        self.outgoing_message = ''
        self.incoming_messages = []
        self.final_message = ''
        self.done = False
        super(GuestBot, self).__init__(server_list, nickname, realname)

    # pylint:disable-next=unused-argument
    def on_welcome(self, c, e):
        "Autojoin a channel; ignore e"
        c.join("#test")
        self.send_message()

    # pylint:disable-next=unused-argument
    def on_pubmsg(self, c, e):
        "Log messages."
        nick = e.source.nick
        message = e.arguments[0]
        if nick == 'bot':
            if message == END_MSG:
                self.final_message = '\n'.join(self.incoming_messages)
                self.done = True
                print(self.final_message)
                self.disconnect()
            else:
                self.incoming_messages.append(message)

    def send_message(self, message=None):
        "Send a message"
        c = self.connection
        if message == None:
            message = self.outgoing_message
        print(message)
        c.privmsg('#test', message)

def create_bot():
    "Creates the bot."
    config = load_config()
    if "chat_server" in config:
        config = config["chat_server"]
        server = ServerSpec(config["domain"], 6667, config["key"])
    # Run a local server with `python3 -m irc.server`
    #
    # This can then connect to that.
    else:
        server = ServerSpec("127.0.0.1", 6667)
    bot = LlmBot([server], 'bot', 'bot')
    bot.start()

def create_guest_bot(message):
    "Creates the guest bot."
    config = load_config()
    if "chat_server" in config:
        config = config["chat_server"]
        server = ServerSpec(config["domain"], 6667, config["key"])
    else:
        server = ServerSpec("127.0.0.1", 6667)
    bot = GuestBot([server], 'notbot', 'notbot')
    bot.outgoing_message = message
    bot.connect(server.host, 6667, 'notbot')
    while not bot.done:
        bot.reactor.process_once()
    return bot.final_message

# The bot connects to a server such as the one from `python3 -m irc.server`
#
# That means the bot, the server, and Flask are all running as processes.
if __name__ == "__main__":
    create_bot()
