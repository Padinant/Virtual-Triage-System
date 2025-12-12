# Installing

To set our project up inside of a Python `venv`, navigate to the root
directory (where this file is located) and run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --editable .
```

This sets up a venv, switches your shell to it, and locally installs
this project to the venv's pip.

If you are already in a sandbox, container, or virtual machine and do
not wish to use `venv`, then an alternative option is available: just
run the shell command `pip install --editable .` directly.

This command installs our project as if it was a pip package on PyPi,
reading the dependencies from `pyproject.toml`. This allows you to run
the application without issues.

Note that we have several external dependencies:

- PostgreSQL (production) or SQLite (testing) for the database.
- An external web server for Flask (see Flask's ["Deploying to
  Production"](https://flask.palletsprojects.com/en/stable/deploying/)
  page) when run in a non-testing environment. In development, Flask
  can run itself directly.
- A way to persist the chatbot message state (such as an IRC server,
  known as an "IRCd") when run in a non-testing environment. Porting
  this to another, more robust setup may be ideal, but the older IRC
  protocol for chat was one that was suitable for running a local test
  environment on everyone's diverse development machines for the short
  three month scope of this project.

Note that our project only uses PostgreSQL if there is a `database`
entry in the configuration file. To disable this, comment it out with
`#` at the start of the relevant database config lines.

## Configuration file

We have a TOML file located in the XDG config directory. By default,
it will be `$HOME/.config/vts/config.toml`. In other words, it's in
the `.config` directory under your home directory. Alternatively, you
can put it in any directory as long as you set the environment
variable `XDG_CONFIG_HOME` to that path.

In that `.config` directory, you can create the `vts` subdirectory and
the file `config.toml` in that subdirectory.

For the chatbot to function, it needs an API key and an endpoint
URL. This configuration can look like this:

```toml
[agent]
key = "1A1B2C3D5E8F13G21H34I55J89K144L"
url = "https://example.com/"
```

Alternatively, the chatbot can be running on a remote server. This
means that you don't need the `[agent]` entry, but you do need to
specify where that server is. If that is the case, then the server has
its own key and domain. For instance:

```toml
[chat_server]
domain = "127.0.0.1"
key = "0Z1Y1X2W3V5U8T13S21R34Q55P89O144N"
```

If this entry is not present, then it's assumed to be an
unauthenticated local server.

Finally, if you are using PostgreSQL, you need a `[database]` entry
which will tell the program to use that database instead of
SQLite. This looks something like this:

```toml
[database]
username = "username"
password = "password"
host = "example.com"
```

An example configuration file is located in this repository with the
name `config.example.toml`, using the same example values. Note that
these example values are nonsense and the sample keys are just the
Fibonacci sequence mixed with letters.

# Running Locally

If you're using a venv, you need to activate it before running. If you
followed our instructions, it's in `.venv`, which means you can run it
with `source .venv/bin/activate`. Otherwise, you need the provide
proper path to `activate`.

For the chatbot to run, there either needs to be an API key for the
chatbot or a server key for accessing an external chat server if the
chatbot's persistent chat is already running on a remote server. If
running locally, the chatbot process and the chat server process need
to run.

You can test whether the connection to the agent api works by making a
quick call to chatbot. To do so, type either of the following in
terminal:

```bash
cd vts
python llm.py
```

or

```bash
python vts/llm.py
```

To test locally on your machine, either navigate to the `vts`
directory and then run:

```bash
flask --app website run
```

Alternatively, from the top-level directory (where this file is
located) run:

```bash
flask --app vts/website run
```

After that, navigate your browser to the Flask-provided localhost URL.

Note that both pylint and pytest will not recognize imports from vts
in the tests folder without installing and running both pylint and
pytest *inside* of the venv if you are using virtual environments.

## Running the chatbot with the application

If only Flask is running, then the agent will run without any
persistent history because Flask relies on either files or on cookies
or on other processes such as servers and databases to persist
history. Running the agent directly from inside of Flask requires an
`[agent]` key in your configuration.

If you want chat history to persist between requests, then you need
the chatbot persisting on its own process (where it keeps track of its
state), as well as an IRC server (to connect to).

The test IRC server is:

```bash
python3 -m irc.server
```

And then the chatbot is:

```bash
python3 vts/chat_server.py
```

Note: Make sure to run in this order: flask, IRC, chatbot. If the
chatbot can't see an already-started IRC server, then it won't connect
when started.

It can also connect to a real IRC server with the `[chat_server]`
configuration in the TOML, given a `domain` and a `key` (server
password). Note that if it connects to a real IRC server, then only
the machine running the chatbot needs the `[agent]` key!

Also note that the file `vts/llm.py` can be run directly as its own
script so that you can test a chat session with the `[agent]` key from
the configuration file without having to integrate with the rest of
the web application.

# Dependencies Explained

Our direct dependencies are as follows:

## flask

One of the two major Python web frameworks, Flask is the lightweight
and minimalist one. This allows us to write the website backend to
serve requests.

## sqlalchemy

This library is both an abstraction over SQL and an Object Relational
Mapper (ORM). Because our database needs are very modest, we mostly
use the high-level ORM for the sake of conciseness. Either way, an
abstraction layer library is needed because we need to support SQLite
for testing and PostgreSQL for production.

This project should be able to be modified to support other SQL
databases as well. The main point of extension is in the `Engine` enum
in `database.py`, which currently has `SQLITE_MEMORY`, `SQLITE_FILE`,
and `POSTGRES` values. These affect the behavior of the `AppDatabase`
constructor, which is where new behavior would need to be added for
other SQL databases. The `AppDatabase` object, in turn, abstracts over
most of the calls to SQLAlchemy via its exposed methods.

## whoosh

We used a pure-Python search solution for several reasons:

- We didn't want to have to deal with another, JavaScript, package
  manager this late in the design and development of the project. Many
  search solutions are based in JavaScript to provide Google-style
  real-time results as the user types.
- We wanted to be able to run it locally on all of our machines
  without having it be too complicated because two of us develop on
  Windows, one on macOS, and one directly on Linux. This also means
  that any of us could run the demo in the presentation.

## openai

We don't use OpenAI directly, but its API has become the standard way
to interact with remote LLMs. Using this library means that the
chatbot host can be switched to another service. The primary concerns
for our class project were low price and avoiding vendor lock-in, but
if the stakeholder selects our project, the stakeholder's deployment
situation may differ.

## markdown-it-py

*Trivial API; substitution would be simple.*

We originally used the library called `markdown`, but that wasn't
enough for the Markdown dialect that the LLM-based chatbot generates
so we had to switch to a more modern library. Additionally, the
library needed Markdown table support even though it is not officially
part of either Markdown standard (neither the original nor
Commonmark). This library solves all of our problems.

## Flask-Bcrypt

*Trivial API; substitution would be simple.*

This library integrates a password hashing algorithm (bcrypt) with
Flask. It's relatively trivial and direct use of `bcrypt` would be a
viable alternative.

## xdg-base-dirs

*Trivial API; substitution would be simple.*

This lets us store configuration files in the proper location using
the XDG standard, which is probably `$HOME/.config/vts/` unless
overridden by an environment variable or other configuration. Until
that point, only files in the git directory (perhaps ignored) had any
affect on our program's behavior, but it is safer to have the various
API keys entirely outside of the git repository instead of merely
`.gitignore`d.

## irc (optional)

*Easy API; substitution is extremely feasible.*

This is an optional dependency. If the IRC bots and server are not
running (i.e. the connection fails either locally or to the server
specified by `[chat_server]`), then the application attempts to
directly connect to the chatbot agent specified under `[agent]` in the
config. If even that is not provided, then the chat does not function.

Flask only has four ways to persist state: an external database, files
on disk, client-side browser storage, or talking to another
process. Because of this, one has to serialize the chat over either an
existing chat protocol or via passing messages in a persistent message
queue (likely two queues, a send and a receive). This is just a
serialization so it can be substituted with anything else that can
persist chat and send/receive messages.

We went with a chat protocol serialization because it is higher
level. We chose an IRC library because the clients and test server can
be hosted entirely locally on modest hardware without running an
external service. This was important for local testing and for doing
the presentation demo. The disadvantage is that older versions of the
IRC protocol (including the one that the library used) are
line-oriented and have a line length limit so messages need to be
split before serializing.

An advantage of using a high-level chat protocol serialization instead
of a low-level message queue based implementation is that we can
handle multiple chat sessions as conversations in multiple chat rooms
(called "channels" in IRC terminology) between the same two bots (one
representing the chatbot and one representing the user).

## psycopg2-binary (optional)

This is how SQLAlchemy communicates with PostgreSQL. If you are using
SQLite, this dependency is not used.
