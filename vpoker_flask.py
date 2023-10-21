import logging
from logging import StreamHandler
from flask import Flask, jsonify, request, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from vpoker_analyzer import HandAnalyzer
import re

# Set up logging
logger = logging.getLogger('vpoker_flask')
logger.setLevel(logging.DEBUG)  # Set logging level

# StreamHandler logs to console (STDOUT)
stream_handler = StreamHandler()
stream_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)

app = Flask(__name__)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Use the client's IP address as the key for rate limiting
    default_limits=["1 per second"]  # Set the default rate limit
)

@app.before_request
def log_request_info():
    logger.info('Request: %s %s %s %s', request.method, request.url, request.data, request.headers)

@app.after_request
def log_response_info(response):
    logger.info('Response: %s %s %s', response.status, response.data, response.headers)
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error('Exception occurred: %s', str(e), exc_info=True)
    return jsonify(error=str(e)), 500

@limiter.request_filter
def exempt_users():
    return False 

@app.errorhandler(429)
def ratelimit_error(e):
    return make_response(jsonify(error="ratelimit exceeded"), 429)

def is_valid_card_string(card_str):
    return bool(re.match('^[a-jc-t0-9]{10}$', card_str))

def get_remote_address():
    return request.remote_addr

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error="404 Not Found: The requested URL was not found on the server."), 404

@app.route('/', methods=['GET'])
def root():
    return '', 200

@app.route('/analyze-hand', methods=['POST'])
@limiter.limit("1 per second")  # Apply rate limiting to this endpoint
def analyze_hand():
    data = request.json
    
    # Ensure the hand data is provided
    if not data or 'hand' not in data:
        return jsonify({"error": "Hand not provided."}), 400
    
    hand = data['hand']
    
    # Validate the hand value based on the criteria
    if not is_valid_card_string(hand):
        return jsonify({"error": "Invalid card string."}), 400
    
    # Create an instance of HandAnalyzer
    analyzer = HandAnalyzer(hand)
    
    # Call analyze method with specific parameters
    result = analyzer.analyze(return_full_analysis=False, return_bestdisc_cnts=True)
    
    return jsonify(result)