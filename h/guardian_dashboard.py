"""
Guardian Tools Dashboard Content
Enhanced dashboard showing the complete Guardian Tools Architecture
"""

guardian_dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VerifiedCC - Guardian Tools Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .tool-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .tool-card:hover {
            transform: translateY(-5px);
        }
        
        .tool-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .tool-icon {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-right: 15px;
            color: white;
        }
        
        .tool-10 { background: #4CAF50; }
        .tool-07 { background: #2196F3; }
        .tool-03 { background: #FF9800; }
        .guardian { background: #9C27B0; }
        
        .tool-title {
            font-size: 1.4rem;
            font-weight: bold;
            color: #333;
        }
        
        .tool-subtitle {
            color: #666;
            font-size: 0.9rem;
        }
        
        .tool-content {
            margin-bottom: 20px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #666;
        }
        
        .metric-value {
            font-weight: bold;
            color: #333;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online { background: #4CAF50; }
        .status-offline { background: #f44336; }
        .status-processing { background: #FF9800; }
        
        .workflow-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .workflow-title {
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: #333;
        }
        
        .workflow-flow {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .flow-step {
            background: #f5f5f5;
            padding: 15px 20px;
            border-radius: 10px;
            text-align: center;
            min-width: 150px;
            margin: 5px;
        }
        
        .flow-arrow {
            font-size: 24px;
            color: #666;
            margin: 0 10px;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s ease;
        }
        
        .btn-primary {
            background: #2196F3;
            color: white;
        }
        
        .btn-primary:hover {
            background: #1976D2;
        }
        
        .btn-success {
            background: #4CAF50;
            color: white;
        }
        
        .btn-success:hover {
            background: #45a049;
        }
        
        .device-selector {
            margin-bottom: 15px;
        }
        
        .device-selector select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .log-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .log-entry {
            padding: 5px 0;
            border-bottom: 1px solid #eee;
            font-family: monospace;
            font-size: 12px;
        }
        
        .log-timestamp {
            color: #666;
            margin-right: 10px;
        }
        
        .log-message {
            color: #333;
        }
        
        @media (max-width: 768px) {
            .tools-grid {
                grid-template-columns: 1fr;
            }
            
            .workflow-flow {
                flex-direction: column;
            }
            
            .flow-arrow {
                transform: rotate(90deg);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Guardian Tools Dashboard</h1>
            <p>Real-time monitoring of Guardian Tools Architecture for MRV Processing</p>
        </div>
        
        <!-- Guardian Tools Status -->
        <div class="tools-grid">
            <!-- Tool 10: Data Source -->
            <div class="tool-card">
                <div class="tool-header">
                    <div class="tool-icon tool-10">📊</div>
                    <div>
                        <div class="tool-title">Tool 10 - Data Source</div>
                        <div class="tool-subtitle">ESP32 IoT Sensors</div>
                    </div>
                </div>
                <div class="tool-content">
                    <div class="metric">
                        <span class="metric-label">Raw Data Points:</span>
                        <span class="metric-value" id="tool10-data-points">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Active Devices:</span>
                        <span class="metric-value" id="tool10-devices">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Latest Reading:</span>
                        <span class="metric-value" id="tool10-latest">Never</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Status:</span>
                        <span class="metric-value">
                            <span class="status-indicator status-online"></span>
                            <span id="tool10-status">Online</span>
                        </span>
                    </div>
                </div>
            </div>
            
            <!-- Tool 07: Aggregation -->
            <div class="tool-card">
                <div class="tool-header">
                    <div class="tool-icon tool-07">⚙️</div>
                    <div>
                        <div class="tool-title">Tool 07 - Aggregation</div>
                        <div class="tool-subtitle">Data Processing & Reporting</div>
                    </div>
                </div>
                <div class="tool-content">
                    <div class="metric">
                        <span class="metric-label">Aggregated Reports:</span>
                        <span class="metric-value" id="tool07-reports">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Energy Processed:</span>
                        <span class="metric-value" id="tool07-energy">0 kWh</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Emission Reductions:</span>
                        <span class="metric-value" id="tool07-emissions">0 tCO2</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Status:</span>
                        <span class="metric-value">
                            <span class="status-indicator status-processing"></span>
                            <span id="tool07-status">Processing</span>
                        </span>
                    </div>
                </div>
            </div>
            
            <!-- Tool 03: Hedera -->
            <div class="tool-card">
                <div class="tool-header">
                    <div class="tool-icon tool-03">🔗</div>
                    <div>
                        <div class="tool-title">Tool 03 - Hedera Hashgraph</div>
                        <div class="tool-subtitle">Immutable Verification</div>
                    </div>
                </div>
                <div class="tool-content">
                    <div class="metric">
                        <span class="metric-label">Hedera Records:</span>
                        <span class="metric-value" id="tool03-records">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Verified Records:</span>
                        <span class="metric-value" id="tool03-verified">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Verified Reductions:</span>
                        <span class="metric-value" id="tool03-reductions">0 tCO2</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Status:</span>
                        <span class="metric-value">
                            <span class="status-indicator status-online"></span>
                            <span id="tool03-status">Ready</span>
                        </span>
                    </div>
                </div>
            </div>
            
            <!-- Guardian Integration -->
            <div class="tool-card">
                <div class="tool-header">
                    <div class="tool-icon guardian">🛡️</div>
                    <div>
                        <div class="tool-title">Guardian Integration</div>
                        <div class="tool-subtitle">MRV Reporting & Token Minting</div>
                    </div>
                </div>
                <div class="tool-content">
                    <div class="metric">
                        <span class="metric-label">Authentication:</span>
                        <span class="metric-value" id="guardian-auth">Checking...</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">MRV Sender:</span>
                        <span class="metric-value" id="guardian-mrv">Checking...</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Reports Submitted:</span>
                        <span class="metric-value" id="guardian-submitted">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Status:</span>
                        <span class="metric-value">
                            <span class="status-indicator status-processing"></span>
                            <span id="guardian-status">Connecting...</span>
                        </span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Workflow Control -->
        <div class="workflow-section">
            <div class="workflow-title">Guardian Tools Workflow Control</div>
            
            <div class="workflow-flow">
                <div class="flow-step">
                    <strong>Tool 10</strong><br>
                    Data Source<br>
                    <small>ESP32 Sensors</small>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <strong>Tool 07</strong><br>
                    Aggregation<br>
                    <small>5s → 1h → 1 day</small>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <strong>Tool 03</strong><br>
                    Hedera Hash<br>
                    <small>Immutable Record</small>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <strong>Guardian</strong><br>
                    MRV Report<br>
                    <small>Token Minting</small>
                </div>
            </div>
            
            <div class="device-selector">
                <label for="device-select">Select Device:</label>
                <select id="device-select">
                    <option value="">Select a device...</option>
                </select>
            </div>
            
            <div class="controls">
                <button class="btn btn-primary" onclick="triggerAggregation()">
                    🔄 Trigger Aggregation (Tool 07)
                </button>
                <button class="btn btn-success" onclick="triggerCompleteWorkflow()">
                    🚀 Run Complete Workflow
                </button>
                <button class="btn btn-primary" onclick="refreshStatus()">
                    📊 Refresh Status
                </button>
            </div>
        </div>
        
        <!-- Activity Log -->
        <div class="workflow-section">
            <div class="workflow-title">Activity Log</div>
            <div class="log-section" id="activity-log">
                <div class="log-entry">
                    <span class="log-timestamp">[System]</span>
                    <span class="log-message">Guardian Tools Dashboard initialized</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedDevice = '';
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshStatus();
            loadDevices();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshStatus, 30000);
        });
        
        async function refreshStatus() {
            try {
                // Get Guardian status
                const response = await fetch('/api/guardian/status');
                const status = await response.json();
                
                updateToolStatus(status);
                addLogEntry('Status refreshed successfully');
                
            } catch (error) {
                console.error('Error refreshing status:', error);
                addLogEntry('Error refreshing status: ' + error.message, 'error');
            }
        }
        
        function updateToolStatus(status) {
            // Tool 10 - Data Source
            document.getElementById('tool10-data-points').textContent = status.tool_10_data_source.raw_data_points;
            document.getElementById('tool10-devices').textContent = status.tool_10_data_source.devices_active;
            document.getElementById('tool10-latest').textContent = status.tool_10_data_source.latest_timestamp || 'Never';
            
            // Tool 07 - Aggregation
            document.getElementById('tool07-reports').textContent = status.tool_07_aggregation.aggregated_reports;
            document.getElementById('tool07-energy').textContent = status.tool_07_aggregation.total_energy_processed.toFixed(3) + ' kWh';
            document.getElementById('tool07-emissions').textContent = status.tool_07_aggregation.total_emission_reductions.toFixed(6) + ' tCO2';
            
            // Tool 03 - Hedera
            document.getElementById('tool03-records').textContent = status.tool_03_hedera.hedera_records;
            document.getElementById('tool03-verified').textContent = status.tool_03_hedera.verified_records;
            document.getElementById('tool03-reductions').textContent = status.tool_03_hedera.total_verified_reductions.toFixed(6) + ' tCO2';
        }
        
        async function loadDevices() {
            try {
                const response = await fetch('/api/latest-readings');
                const readings = await response.json();
                
                const deviceSelect = document.getElementById('device-select');
                deviceSelect.innerHTML = '<option value="">Select a device...</option>';
                
                Object.keys(readings).forEach(deviceId => {
                    const option = document.createElement('option');
                    option.value = deviceId;
                    option.textContent = deviceId;
                    deviceSelect.appendChild(option);
                });
                
                deviceSelect.addEventListener('change', function() {
                    selectedDevice = this.value;
                });
                
            } catch (error) {
                console.error('Error loading devices:', error);
                addLogEntry('Error loading devices: ' + error.message, 'error');
            }
        }
        
        async function triggerAggregation() {
            if (!selectedDevice) {
                alert('Please select a device first');
                return;
            }
            
            try {
                addLogEntry(`Triggering aggregation for ${selectedDevice}...`);
                
                const response = await fetch(`/api/guardian/aggregate/${selectedDevice}`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addLogEntry(`✅ Aggregation completed for ${selectedDevice}`);
                    refreshStatus();
                } else {
                    addLogEntry(`❌ Aggregation failed: ${result.message}`, 'error');
                }
                
            } catch (error) {
                console.error('Error triggering aggregation:', error);
                addLogEntry('Error triggering aggregation: ' + error.message, 'error');
            }
        }
        
        async function triggerCompleteWorkflow() {
            if (!selectedDevice) {
                alert('Please select a device first');
                return;
            }
            
            try {
                addLogEntry(`🚀 Starting complete workflow for ${selectedDevice}...`);
                
                const response = await fetch(`/api/guardian/workflow/${selectedDevice}`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addLogEntry(`✅ Complete workflow finished for ${selectedDevice}`);
                    addLogEntry(`📊 Emission reductions: ${result.aggregated_data.emission_reductions_tco2.toFixed(6)} tCO2`);
                    addLogEntry(`🔗 Hedera TX: ${result.hedera_record.hedera_transaction_id}`);
                    addLogEntry(`🛡️ Guardian submitted: ${result.guardian_submitted ? 'Yes' : 'No'}`);
                    refreshStatus();
                } else {
                    addLogEntry(`❌ Workflow failed: ${result.error}`, 'error');
                }
                
            } catch (error) {
                console.error('Error triggering workflow:', error);
                addLogEntry('Error triggering workflow: ' + error.message, 'error');
            }
        }
        
        function addLogEntry(message, type = 'info') {
            const logSection = document.getElementById('activity-log');
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            
            const timestamp = new Date().toLocaleTimeString();
            const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
            
            logEntry.innerHTML = `
                <span class="log-timestamp">[${timestamp}]</span>
                <span class="log-message">${icon} ${message}</span>
            `;
            
            logSection.appendChild(logEntry);
            logSection.scrollTop = logSection.scrollHeight;
            
            // Keep only last 50 log entries
            while (logSection.children.length > 50) {
                logSection.removeChild(logSection.firstChild);
            }
        }
        
        // Check Guardian services on load
        async function checkGuardianServices() {
            try {
                // Check MRV Sender
                const mrvResponse = await fetch('http://localhost:3005/health');
                if (mrvResponse.ok) {
                    document.getElementById('guardian-mrv').textContent = '✅ Online';
                } else {
                    document.getElementById('guardian-mrv').textContent = '❌ Offline';
                }
            } catch (error) {
                document.getElementById('guardian-mrv').textContent = '❌ Offline';
            }
        }
        
        // Check services on load
        setTimeout(checkGuardianServices, 1000);
    </script>
</body>
</html>
"""