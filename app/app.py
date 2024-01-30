from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

def get_user_id(username):
    hd = {
        "Cookie": "YOUR_COOKIE"
    }
    get = requests.get(f"https://www.facebook.com/{username}", headers=hd).text
    id_acc = get.split('"userID":"')[1].split('"')[0]
    return id_acc

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        try:
            user_id = get_user_id(username)
            return jsonify({'uid': user_id})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'User information not found.'}), 404

    return render_template('index.html', uid=None)

@app.route('/user-details/<user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        access_token = "YOUR_ACCESS_TOKEN"
        graph_api_url = f"https://graph.facebook.com/{user_id}?fields=id,is_verified,cover,created_time,link,name,locale,gender,first_name,subscribers.limit(0)&access_token={access_token}"
        response = requests.get(graph_api_url)
        response.raise_for_status()
        user_details = response.json()

        user_details['created_time'] = datetime.strptime(user_details['created_time'], '%Y-%m-%dT%H:%M:%S+0000').strftime('%H:%M:%S %d/%m/%Y UTC')
        user_details['followers'] = user_details['subscribers']['summary']['total_count']
        del user_details['subscribers']

        return jsonify(user_details)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to fetch user details.'}), 500

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
