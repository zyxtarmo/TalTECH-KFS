from flask import Flask, jsonify

app = Flask(__name__)

# Function to validate API key
def validate_api_key(api_key, api_user):
    return api_key == API_KEY 
    
@app.route('/')
def index():
    return "Welcome to the API server!"

@app.route('/api/data', methods=['GET'])
def get_data():
	
	api_key = request.headers.get('X-API-Key')
	api_user = request.headers.get('X-API-User')
    if not (api_key or api_user):
        abort(401, 'Missing API key or user')

    # Validate the API key
    if not validate_api_key(api_key, api_user):
        abort(401, 'Invalid API key')

    # Sample data to return
    data = {'name': 'John', 'age': 30, 'city': 'New York'}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
