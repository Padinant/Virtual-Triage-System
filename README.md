# Virtual-Triage-System

Team 5's project for the course CMSC 447.

# Local testing
For some set up, run:
```bash
pip install flask
pip install sqlalchemy
pip install markdown
```

To use inside of a local venv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --editable .
```

To test locally on your machine, navigate to the `vts` directory and
then run:

```bash
flask --app website run
```

And then navigate your browser to the provided localhost URL.

## Viewing the interactive chat page
For the interactive chatpage, add "/chat.html" to the end of the URL obtained earlier.
