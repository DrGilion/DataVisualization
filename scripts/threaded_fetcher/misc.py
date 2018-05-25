import json

def set_json_file(name, data):
    file = 'data/%s.json' % name
    with open(file, 'w') as f:
        f.write(json.dumps(data))