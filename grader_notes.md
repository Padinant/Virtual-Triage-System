## Note on the git repository's branches

Note that there was an issue with a commit in the git repository in
the second sprint where an entire `venv` directory was committed and
made it into `main`. The fix was to rewrite history to redact the
`venv` from the commit, but that rewrote *all* history and made the
other branches inconsistent with the `main` branch. It was easier to
rename the fixed, but inconsistent `main` branch to `old_main` and do
it over again, with `main` skipping rather than editing the
problematic commit. This, however, means that [Dua's corrected
commit](https://github.com/Padinant/Virtual-Triage-System/commit/ba1573d54227afb73bb9fe41d61256bc992be475)
from Sprint 2 no longer shows up in the `main` branch because it lives
in `old_main`. The authorship of those lines of code thus do not show
up as Dua's in the third `main` branch (it's the third after the
mistaken `main` that is no longer available and the `old_main` that
became inconsistent with the other branches).

At the time of this writing, there are 6 branches in addition to the
`main` branch:

* the `old_main` with an entirely distinct history due to the commit
  redaction
* `frontend` which was originally intended to be shared by Jia and
  Dua, but wound up becoming Jia's branch
* `web_frontend`, which was Jia's old branch before moving all work to
  the `frontend` branch.
* `chatbot_frontend`, which was Dua's branch
* `chatbot_backend`, which was Padina's branch
* `data_backend`, which was Michael's branch

Despite the names of the branches, these branches were used for other
purposes as well. For instance, Jia implemented the search on the
`frontend` branch and Michael did non-database features on the
`data_backend` branch. Having exactly one branch per person in Sprint
2 was done to avoid the complexity in Sprint 2 that lead to the
inconsistent `main`.

## Running this project

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

## Recreating this project from scratch

The cloud-based parts of this project can be recreated fairly easily.
We used Digital Ocean's Agent Platform. The `knowledge_files_markdown`
folder was what we gave to the AI agent. The prompt is
`instructions_v4.md`, while the `contacts.md` and `knowledge.md` were
uploaded via the web interface to the Knowledge Base. We used the
cheapest and smallest model on the platform, which we found to be
satisfactory for our use case. It is called "OpenAI GPT-oss-20b". The
agent requires a knowledge base to be generated to upload the two
files and then endpoint access keys can be generated to access the
private access point URL.
