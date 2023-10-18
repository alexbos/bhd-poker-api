from flask import Flask, jsonify, request
from vpoker_analyzer import HandAnalyzer

app = Flask(__name__)

# Import the HandAnalyzer class from the provided code
# exec(vp_analyzer_code)

@app.route('/analyze-hand', methods=['POST'])
def analyze_hand():
    data = request.json
    
    # Ensure the hand data is provided
    if not data or 'hand' not in data:
        return jsonify({"error": "Poker hand not provided."}), 400
    
    hand = data['hand']
    
    # Create an instance of HandAnalyzer
    analyzer = HandAnalyzer(hand)
    
    # Call analyze method with specific parameters
    result = analyzer.analyze(return_full_analysis=False, return_bestdisc_cnts=True)
    
    return jsonify(result)


# For demonstration purposes in this environment, we won't run the app
# In a real environment, you would run the app using app.run()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
