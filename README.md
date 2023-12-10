# tzeract
A simple webserver for calling external commands and returning the result.

## How the program works:

A webserver is started, and can receive commands that will be run in a shell. The body of the POST request should use JSON to
specify the command to be run, with optional arguments. For example, to run:
```
ls -l test/*
```

give:
```
{"command":"ls", "args":["-l", "test/*"]}
```

An artificial delay is introduced by calling sleep(5) to sleep for 5 seconds.

Several commands can be processed in parallel. If the server is stopped with ctrl-c when running, it will
send replies back for outstanding requests before terminating.

## Setting up and running the program:

Check out the code from GitHub:

```
git@github.com:henrikw/tzeract.git
cd tzeract
```

Create and activate a virtual environment:
```
python3 -m venv env
. env/bin/activate
```

Install dependencies (requests and pytest):
```
pip install -r requirements.txt
```

### To run tests:

```    
pytest test_tzeract_server.py
```

### To run the program:

```
# Start the web server by running:
uvicorn tzeract_server:app --port 8080

# Examples of usage by calling it using curl:

# List files in the directory:
curl -X POST http://localhost:8080/execute-command -H "Content-Type: application/json" -d '{"command":"ls"}'

# List files in the directory (with the -l flag):
curl -X POST http://localhost:8080/execute-command -H "Content-Type: application/json" -d '{"command":"ls", "args":["-l"]}'

# Create a directory called test:
curl -X POST http://localhost:8080/execute-command -H "Content-Type: application/json" -d '{"command":"mkdir", "args":["test"]}'

# Create a file in the directory using touch:
curl -X POST http://localhost:8080/execute-command -H "Content-Type: application/json" -d '{"command":"touch", "args":["test/file3.txt"]}'

# List files in the directory using wildcard:
curl -X POST http://localhost:8080/execute-command -H "Content-Type: application/json" -d '{"command":"ls", "args":["-l", "test/*3.txt"]}'

# External command that doesn't exits (lsx):
curl -X POST http://localhost:8080/execute-command -H "Content-Type: application/json" -d '{"command":"lsx", "args":["-l", "test/*3.txt"]}'

# Faulty URL:
curl -X POST http://localhost:8080/execute-commandXXX -H "Content-Type: application/json" -d '{"command":"ls"}'
```

## Future improvements

The examples given above can be turned into automatic tests.
