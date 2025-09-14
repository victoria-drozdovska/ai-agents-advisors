import os
import sys
import asyncio
import time # Added this line
from flask import Flask, request, jsonify, send_from_directory

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(__file__))
from advisor_logic import ooda_run, METRICS # Import ooda_run and METRICS

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Disable database for this project as it's not used
# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)
# with app.app_context():
#     db.create_all()

@app.route('/api/analyze', methods=['POST'])
def analyze_question():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    # Reset metrics for each new question
    METRICS.llm_tokens_in = 0
    METRICS.llm_tokens_out = 0
    METRICS.tool_calls = {"search": 0, "fetch": 0, "vector": 0}
    METRICS.cache_hits = {"search": 0, "fetch": 0}
    METRICS.events = []
    METRICS.error_count = 0
    METRICS.start_time = time.time() # Reset start time

    # Run the OODA loop asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(ooda_run(question))
    loop.close()

    return jsonify({
        'analysis': result,
        'metrics': METRICS.summary(),
        'log': METRICS.events
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


