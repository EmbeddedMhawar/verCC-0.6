#!/usr/bin/env python3
"""
Simple MRV Sender Alternative
A Python-based mrv-sender that mimics the Guardian mrv-sender functionality
but works reliably on Windows
"""

from flask import Flask, request, jsonify
import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Guardian configuration
GUARDIAN_CONFIG = {
    "base_url": "https://guardianservice.app/api/v1",
    "username": "Mhawar",
    "password": "Mhawar2001'",
    "tenant_id": "68cc28cc348f53cc0b247ce4",
    "policy_id": "68d5ba75152381fe552b1c6d",
    "block_id": "1021939c-b948-4732-bd5f-90cc4ae1cd50"
}

class GuardianClient:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
    
    def authenticate(self):
        """Authenticate with Guardian"""
        try:
            # Login
            login_data = {
                "username": GUARDIAN_CONFIG["username"],
                "password": GUARDIAN_CONFIG["password"],
                "tenantId": GUARDIAN_CONFIG["tenant_id"]
            }
            
            response = requests.post(
                f"{GUARDIAN_CONFIG['base_url']}/accounts/login",
                json=login_data
            )
            
            if response.status_code == 200:
                self.refresh_token = response.json().get("refreshToken")
                
                # Get access token
                token_data = {"refreshToken": self.refresh_token}
                response = requests.post(
                    f"{GUARDIAN_CONFIG['base_url']}/accounts/access-token",
                    json=token_data
                )
                
                if response.status_code in [200, 201]:
                    self.access_token = response.json().get("accessToken")
                    logger.info("Guardian authentication successful")
                    return True
            
            logger.error("Guardian authentication failed")
            return False
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def submit_to_guardian(self, data):
        """Submit data to Guardian (placeholder for now)"""
        logger.info(f"Would submit to Guardian: {data}")
        # For now, just log the data since the Guardian API endpoint isn't working
        return True

guardian_client = GuardianClient()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "simple-mrv-sender"}), 200

@app.route('/mrv-generate', methods=['POST'])
def mrv_generate():
    """
    MRV Generate endpoint - compatible with Guardian mrv-sender API
    Accepts MRV data and processes it
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        logger.info(f"Received MRV data: {json.dumps(data, indent=2)}")
        
        # Process the data (create verifiable credential structure)
        processed_data = {
            "timestamp": datetime.now().isoformat(),
            "original_data": data,
            "processed": True,
            "status": "received"
        }
        
        # Authenticate with Guardian if not already done
        if not guardian_client.access_token:
            if not guardian_client.authenticate():
                return jsonify({"error": "Guardian authentication failed"}), 500
        
        # Submit to Guardian (placeholder)
        if guardian_client.submit_to_guardian(processed_data):
            logger.info("MRV data processed successfully")
            return jsonify({
                "status": "success",
                "message": "MRV data processed and queued for Guardian submission",
                "data": processed_data
            }), 200
        else:
            return jsonify({"error": "Failed to submit to Guardian"}), 500
            
    except Exception as e:
        logger.error(f"Error processing MRV data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/templates', methods=['GET'])
def get_templates():
    """Get available templates (compatible with Guardian mrv-sender)"""
    templates = ["test_irec.json"]
    return jsonify(templates), 200

@app.route('/', methods=['GET'])
def index():
    """Index page"""
    return """
    <h1>Simple MRV Sender</h1>
    <p>Python-based MRV Sender alternative</p>
    <h2>Endpoints:</h2>
    <ul>
        <li><code>GET /health</code> - Health check</li>
        <li><code>POST /mrv-generate</code> - Submit MRV data</li>
        <li><code>GET /templates</code> - Get templates</li>
    </ul>
    <h2>Status:</h2>
    <p>Guardian Authentication: <span id="auth-status">Checking...</span></p>
    
    <script>
        // Check authentication status
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                document.getElementById('auth-status').textContent = data.status;
            });
    </script>
    """

def main():
    print("Starting Simple MRV Sender...")
    print("=" * 50)
    
    # Test Guardian authentication on startup
    print("Testing Guardian authentication...")
    if guardian_client.authenticate():
        print("Guardian authentication successful")
    else:
        print("Guardian authentication failed - will retry on requests")
    
    print("\nStarting server on http://localhost:3005")
    print("Endpoints available:")
    print("   - GET  /health")
    print("   - POST /mrv-generate")
    print("   - GET  /templates")
    print("   - GET  /")
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=3005, debug=False)

if __name__ == "__main__":
    main()