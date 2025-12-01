# Virtual-Triage-System

Team 5's project for the course CMSC 447.

# Installing

To install the dependencies, run:

```bash
pip install flask
pip install sqlalchemy
pip install markdown-it-py
pip install whoosh
pip install requests
pip install openai
pip install Flask-Bcrypt
pip install xdg-base-dirs
pip install irc
```

To use inside of a local venv with automatic dependency resolution,
run the following:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --editable .
```

# Setting up the configuration file with the AI api keys

Navigate to your XDG configuration directory. By default, this is the
`.config` directory under your home directory. Alternatively, you can
put it in any directory as long as you set the environment variable
`XDG_CONFIG_HOME` to that path.

Create the subdirectory `vts` and the file `config.toml`.

Add a `key` and `url` under `[agent]`, such as:

```toml
[agent]
key = "1A1B2C3D5E8F13G21H34I55J89K144L"
url = "https://example.com/"
```

The `config.example.toml` file shows what the file might look like.

You can test whether the connection to the agent api works by making a quick call to chatbot. To do so, type the following in terminal:

```
cd vts
python llm.py
```

# Local Testing

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

And then navigate your browser to the provided localhost URL.

Note that both pylint and pytest will not recognize imports from vts
in the tests folder without installing and running both pylint and
pytest *inside* of the venv.

Note that you also need the chatbot persisting on its own process, as
well as an IRC server.

The chatbot is:

```bash
python3 vts/chat_server.py
```

And the test IRC server is:

```bash
python3 -m irc.server
```

It can also connect to a real IRC server with the `[chat_server]`
configuration in the TOML, given a `domain` and a `key` (server
password).

# Setting Up Docker Compose and the Backend Environment
This sections assumes you are using a linux debian virtual machine. The corresponding setup instructions for other devices are the same or similar, and can be found elsewhere.

Step 0:
make sure your device is fully updated with latest updates.

Step 1:
set up docker compose and docker engine.

Step 2:
create and configure your .env file
 - rename '.env.example' to '.env'
 - replace the variable values with your own information

Step 3:
Access n8n through typing 'http://localhost:5678' into your browser
