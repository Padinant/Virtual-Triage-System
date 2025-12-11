You should have been given a `config.toml` with one entry, the
`[agent]` with a `key` and a `url`. You can use this to talk to the
chatbot agent server. The other configuration options (for the remote
chat server and for a PostgreSQL database username and password) are
not necessary and including those options will override the local
testing version of the application.

When you run with just Flask, you have a direct chat session with no
chat history memory for the agent. Assuming you are in a virtual
environment configured as described in [INSTALL.md](INSTALL.md), you
can use `flask --app vts/website run` from this current directory.

Running tests from this current directory can be done with `pylint vts
tests`, `pytest tests`, and `mypy vts tests --ignore-missing-imports`.
This is similar to what GitHub does automatically on every push and
every pull request.

If you want to have a persistent session, you have to first run the
test chatroom server with `python3 -m irc.server` and then run the
chatbot server with `python3 -m vts/chat_server`, keeping all three
processes running. You exit these processes with the Ctrl+C keyboard
interrupt and seeing a stack trace after a keyboard interrupt is
normal. We did not have time to implement multiple sessions with
stored history in the chatbot server so the history is shared until
the script is stopped and then restarted.

Sample questions to ask the chatbot are
[here](sample_chatbot_questions/sample_questions.md).
