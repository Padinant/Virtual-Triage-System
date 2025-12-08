"""
Creates a server to persist the chat state.
"""

import re

from typing import Optional

from irc.bot import SingleServerIRCBot
from irc.bot import ServerSpec

from vts.config import load_config

from vts.llm import chat_with_agent

# Our bot likes to send multiple lines, so let's send the line "End
# Msg" backwards, which is extremely unlikely to be a valid output
# line.
END_MSG = 'gsM dnE'

def split_whitespace(line: str, too_long: int) -> tuple[str, Optional[str], bool]:
    """
    Attempts to split at the first whitespace of the midpoint of a
    string. If that fails, then it attempts to split on the first
    whitespace on a string from the start. If that fails, it cannot be
    reduced.

    The second result is either a string or None depending on if a
    split is done.
    """
    # No need to split
    if len(line) < too_long:
        return (line, None, True)
    # Split from the midpoint
    midpoint = len(line) // 2
    replace = re.split(r'(\s+)', line[midpoint:], maxsplit=1)
    if len(replace) > 1:
        return (line[:midpoint] + replace[0], replace[2], True)
    # Split from the midpoint, in reverse
    replace = re.split(r'(\s+)', line[:midpoint][::-1], maxsplit=1)
    if len(replace) > 1:
        left = replace[2][::-1]
        right = replace[0][::-1] + line[midpoint:]
        return (left, right, True)
    # Failure to split
    return (line, None, False)

def split_long_line(line: str, too_long: int) -> list[str]:
    "Attempts to split a line that's too long into lists."
    left, right, is_reduced = split_whitespace(line, too_long)
    # The attempt to split failed or the attempt is unncessary.
    if not is_reduced or not right:
        # Short line.
        if is_reduced:
            return [line]
        # Truncate long line.
        return [line[:min(len(line), too_long - 1)]]
    return split_long_line(left, too_long) + split_long_line(right, too_long)

def send_split_message(response: str, connection):
    "Splits the message into multiple lines and sends it."
    lines = response.splitlines()
    for line in lines:
        if len(line) > 450:
            more_lines = split_long_line(line, 450)
            for split_line in more_lines:
                # If the splitting didn't work, truncate
                if len(split_line) > 475:
                    connection.privmsg("#test", split_line[:475])
                else:
                    connection.privmsg("#test", split_line)
        else:
            connection.privmsg("#test", line)

class LlmBot(SingleServerIRCBot):
    "A bot representing the LLM"
    def __init__(self, server_list, nickname, realname):
        self.message_list = []
        super().__init__(server_list, nickname, realname)

    # pylint:disable-next=unused-argument
    def on_welcome(self, c, e):
        "Autojoin a channel; ignore e"
        c.join("#test")

    def on_pubmsg(self, c, e):
        "Take any responses in the channel and reply with the chatbot."
        # nick = e.source.nick
        message = e.arguments[0]
        print(message)
        response, message_list = chat_with_agent(message, self.message_list)
        self.message_list = message_list
        print(response)
        send_split_message(response, c)
        c.privmsg('#test', END_MSG)

class GuestBot(SingleServerIRCBot):
    "A bot representing the LLM"
    def __init__(self, server_list, nickname, realname):
        self.outgoing_message = ''
        self.incoming_messages = []
        self.final_message = ''
        self.done = False
        super().__init__(server_list, nickname, realname)

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
        if message is None:
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

def create_guest_bot(message: str) -> Optional[str]:
    "Creates the guest bot."
    config = load_config()
    if "chat_server" in config:
        config = config["chat_server"]
        server = ServerSpec(config["domain"], 6667, config["key"])
    else:
        server = ServerSpec("127.0.0.1", 6667)
    # Note that any error at all in the try/except block means return
    # None, which will tell the caller to use the fallback instead.
    try:
        bot = GuestBot([server], 'notbot', 'notbot')
        bot.outgoing_message = message
        bot.connect(server.host, 6667, 'notbot')
        while not bot.done:
            bot.reactor.process_once()
        return bot.final_message
    # Note: The point of this is to fallback on ANY exception state so
    # that another way to use the API can be attempted so the bare
    # exception is desirable here.
    #
    # pylint:disable-next=bare-except
    except:
        return None

# The bot connects to a server such as the one from `python3 -m irc.server`
#
# That means the bot, the server, and Flask are all running as processes.
if __name__ == "__main__":
    create_bot()
