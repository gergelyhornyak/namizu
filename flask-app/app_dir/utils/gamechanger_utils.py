import json

def load_page_values():
    try:
        with open('player_score.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'apple': 0, 'banana': 0, 'coconut': 0, 'dates': 0}

def save_page_values(values):
    with open('player_score.json', 'w') as f:
        json.dump(values, f)
