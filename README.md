# Virtual-Triage-System

Team 5's project for the course CMSC 447.

# Installing

To install the dependencies, run:

```bash
pip install flask
pip install sqlalchemy
pip install markdown
```

To use inside of a local venv with automatic dependency resolution,
run the following:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --editable .
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
