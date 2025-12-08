# Virtual-Triage-System

Team 5's project for the UMBC course CMSC 447 in the Fall 2025
semester.

## Installing, configuring, and running

For instructions on installing, configuring, and running our
application, please see our [INSTALL.md](INSTALL.md) file.

## Local testing (the short, quickstart version)

The full instructions are in INSTALL.md, but if you're impatient, then
inside of this current directory run:

```bash
flask --app vts/website run
```

Assuming every library is detected, such as being installed through a
venv, the application should provide a localhost URL that you can load
in web browsers.

If you don't have an `[agent]` key, then the chatbot will only respond
with an error message. The chatbot will not preserve chat history
inside of the chat conversation without running several other
processes in the background, which is described in the INSTALL.md
instructions.
