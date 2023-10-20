#Based on https://gist.github.com/iMilnb/bf27da3f38272a76c801

from flask import Flask, request
import requests
import json
import jsonschema

app = Flask(__name__)

msgs = {}
valid_msgs_needed = 3 # Number of valid messages needed to consider the task done

def msg_process(msg, tstamp):
    try:
        js = json.loads(msg)
    except:
        print("Invalid JSON received: {}".format(msg), file='error.log')
        return

    # Receive message with the following format:
    # {
    #    "name": "<Full name>",
    #    "id": "<ID number>",
    #    "temp_f": "<Temperature in Fahrenheit>",
    #    "light_level": "<Light level string>"
    # }

    # Validate the message by checking against the schema in schema.json
    with open('schema.json', 'r') as f:
        schema = json.load(f)
    try:
        jsonschema.validate(js, schema)
    except jsonschema.exceptions.ValidationError as e:
        if 'id' in js and js['id'] in msgs:
            msgs[js['id']].append({'json':js, 'timestamp':tstamp, 'valid':False})
        else:
            print("Invalid message received: {}".format(e), file='error.log')
        return

    # Store the message in a dictionary by ID number and name
    # If the ID number already exists, append the new message to the list
    # Save the dictionary to a file

    msg_dict = {'json':js, 'timestamp':tstamp, 'valid':True}
    if js['id'] in msgs:
        msgs[js['id']].append(msg_dict)
    else:
        msgs[js['id']] = [msg_dict]

    with open('msgs.json', 'w') as f:
        json.dump(msgs, f)

    # Check if the task is done
    if len(msgs[js['id']]) == valid_msgs_needed:
        print("Task done for {}, ID: {}".format(js['name'], js['id']))

@app.route('/', methods = ['GET', 'POST', 'PUT'])
def sns():
    # AWS sends JSON with text/plain mimetype
    try:
        js = json.loads(request.data)
    except:
        pass

    hdr = request.headers.get('X-Amz-Sns-Message-Type')
    # subscribe to the SNS topic
    if hdr == 'SubscriptionConfirmation' and 'SubscribeURL' in js:
        r = requests.get(js['SubscribeURL'])

    if hdr == 'Notification':
        msg_process(js['Message'], js['Timestamp'])

    return 'OK\n'

@app.route('/results', methods = ['GET'])
def results():
    # Return the results in html rendered format
    # If the task is not done, return a message saying so
    # If the task is done, return the results in a table

    # Check arguments for student ID if provided
    id = request.args.get('id')
    if id is not None:
        if id in msgs:
            return json.dumps(msgs[id], indent=4)
        else:
            return "No results yet"

    if len(msgs) == 0:
        return "No results yet"
    
    # Return table of students who have submitted valid messages with their name, ID, number of valid messages and if the task is done, with the name being a link to the results for that student
    html = "<table><tr><th>Name</th><th>ID</th><th>Number of Valid Messages</th><th>Task Done</th></tr>"
    for id in msgs:
        html += "<tr><td><a href='/results?id={}'>{}</a></td><td>{}</td><td>{}</td><td>{}</td></tr>".format(id, msgs[id][0]['json']['name'], id, len(msgs[id]), len(msgs[id]) >= valid_msgs_needed)
    html += "</table>"
    return html

if __name__ == '__main__':
    app.run(
        host = "0.0.0.0",
        port = 5000,
        debug = True
    )