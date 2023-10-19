from flask import Flask, jsonify, request
from flask_limiter import Limiter
from vpoker_analyzer import HandAnalyzer
import re

app = Flask(__name__)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Use the client's IP address as the key for rate limiting
    default_limits=["1 per second"]  # Set the default rate limit
)

@limiter.request_filter
def exempt_users():
    return False  # No one is exempt from the rate limit

@limiter.error_message
def ratelimit_error():
    return jsonify({"error": "ratelimit exceeded"}), 429

def is_valid_card_string(card_str):
    return bool(re.match('^[a-jc-t0-9]{10}$', card_str))

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

if __name__ == "__main__":
    app.run()