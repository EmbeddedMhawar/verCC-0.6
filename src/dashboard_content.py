dashboard_html = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <title>VerifiedCC - Carbon Credit Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/png" href="/static/verifiedcc-logo.png" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        "desert-sand": "#FDB813",
                        "oasis-green": "#2E8540",
                        "deep-ocean": "#003F5C",
                        "cloud-white": "#FFFFFF",
                    },
                    animation: {
                        float: "float 6s ease-in-out infinite",
                        glow: "glow 2s ease-in-out infinite alternate",
                        "slide-up": "slideUp 0.8s ease-out",
                        "fade-in": "fadeIn 1s ease-out",
                        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                    },
                },
            },
        };
    </script>
    <style>
        body {
            font-family: "Inter", sans-serif;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(1deg); }
        }
        
        @keyframes glow {
            from { box-shadow: 0 0 20px rgba(253, 184, 19, 0.3); }
            to { box-shadow: 0 0 40px rgba(253, 184, 19, 0.6), 0 0 60px rgba(46, 133, 64, 0.3); }
        }
        
        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .card-3d {
            transform-style: preserve-3d;
            transition: transform 0.3s ease;
            background: #ffffff;
            box-shadow: 20px 20px 60px #d1d5db, -20px -20px 60px #ffffff;
        }
        
        .card-3d:hover {
            transform: translateY(-5px) rotateX(2deg) rotateY(2deg);
        }
        
        .hero-bg {
            background: #f8fafc;
            position: relative;
            overflow: hidden;
        }
        
        .hero-bg::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 30%, rgba(253, 184, 19, 0.1), transparent 50%),
                        radial-gradient(circle at 80% 70%, rgba(46, 133, 64, 0.1), transparent 50%),
                        radial-gradient(circle at 40% 80%, rgba(0, 63, 92, 0.05), transparent 50%);
            animation: float 8s ease-in-out infinite;
        }
        
        .status-indicator {
            position: relative;
            overflow: hidden;
        }
        
        .status-indicator::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .status-indicator.online::before {
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
    </style>
</head>
<body class="bg-gray-50 text-deep-ocean min-h-screen">
    <!-- Header -->
    <header class="bg-cloud-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-50">
        <div class="container mx-auto px-6 py-4">
            <div class="flex justify-between items-center">
                <div class="flex items-center space-x-4">
                    <img src="/static/verifiedcc-logo.png" alt="VerifiedCC Logo" class="h-12 w-auto" 
                         style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); max-width:150px;"
                         onerror="this.onerror=null; this.src='/static/verifiedcc-logo.png';"/>
                    <div>
                        <h1 class="text-2xl font-bold text-deep-ocean">VerifiedCC Dashboard</h1>
                        <p class="text-sm text-gray-600">ESP32 Real-time Monitoring Dashboard</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="status-indicator inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold" id="connectionStatus">
                        <div class="w-2 h-2 rounded-full mr-2" id="statusDot"></div>
                        <span id="statusText">Connecting...</span>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main class="hero-bg relative z-10">
        <div class="container mx-auto px-6 py-8">
            <!-- Carbon Credits Hero Section -->
            <div class="bg-gradient-to-r from-oasis-green to-desert-sand rounded-2xl p-8 md:p-12 text-cloud-white text-center shadow-2xl mb-8 animate-slide-up">
                <div class="flex items-center justify-center mb-4">
                    <i data-lucide="leaf" class="w-12 h-12 mr-4 animate-float"></i>
                    <h2 class="text-4xl md:text-6xl font-extrabold" id="totalCredits">0.000</h2>
                </div>
                <p class="text-xl md:text-2xl font-medium opacity-90">Total Carbon Credits Generated (tCO2)</p>
                <p class="text-sm opacity-75 mt-2">Verified through VerifiedCC's AI-powered platform</p>
            </div>



            <!-- Test Control Panel -->
            <div class="card-3d rounded-2xl p-8 border border-gray-200 mb-8 animate-fade-in">
                <div class="flex items-center mb-6">
                    <div class="bg-gradient-to-r from-deep-ocean to-oasis-green text-white rounded-full h-12 w-12 flex items-center justify-center mr-4">
                        <i data-lucide="flask-conical" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <h3 class="text-2xl font-bold text-deep-ocean">System Testing Controls</h3>
                        <p class="text-gray-600">Mock data generation and real-time testing</p>
                    </div>
                </div>

                <!-- Control Buttons Grid -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <!-- Send Mock Data -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg">
                        <div class="flex items-center mb-4">
                            <div class="bg-desert-sand text-deep-ocean rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="zap" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-deep-ocean">Single Test</h4>
                                <p class="text-sm text-gray-600">Send one data point</p>
                            </div>
                        </div>
                        <button id="sendMockBtn" class="w-full bg-gradient-to-r from-desert-sand to-yellow-500 hover:from-yellow-500 hover:to-desert-sand text-deep-ocean font-semibold px-4 py-3 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center">
                            <i data-lucide="send" class="w-4 h-4 mr-2"></i>
                            Send Mock Data
                        </button>
                    </div>

                    <!-- Stream Controls -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg">
                        <div class="flex items-center mb-4">
                            <div class="bg-oasis-green text-cloud-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="radio" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-deep-ocean">Live Stream</h4>
                                <p class="text-sm text-gray-600">Continuous data flow</p>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <button id="startStreamBtn" class="w-full bg-gradient-to-r from-oasis-green to-green-600 hover:from-green-600 hover:to-oasis-green text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center">
                                <i data-lucide="play" class="w-4 h-4 mr-2"></i>
                                Start Stream
                            </button>
                            <button id="stopStreamBtn" class="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-500 text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center">
                                <i data-lucide="stop-circle" class="w-4 h-4 mr-2"></i>
                                Stop Stream
                            </button>
                        </div>
                    </div>

                    <!-- Status Display -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-deep-ocean to-blue-900 shadow-lg text-white">
                        <div class="flex items-center mb-4">
                            <div class="bg-white/20 rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="activity" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold">System Status</h4>
                                <p class="text-sm opacity-90">Real-time monitoring</p>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <div class="bg-white/10 rounded-lg p-3 border border-white/20">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm font-medium opacity-90">Mock Stream</span>
                                    <div class="flex items-center">
                                        <div id="streamStatusDot" class="w-2 h-2 rounded-full bg-gray-400 mr-2"></div>
                                        <span id="streamStatus" class="text-sm font-bold">Stopped</span>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white/10 rounded-lg p-3 border border-white/20">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm font-medium opacity-90">ESP32 Devices</span>
                                    <div class="flex items-center">
                                        <div id="realDevicesDot" class="w-2 h-2 rounded-full bg-gray-400 mr-2"></div>
                                        <span id="realDevicesCount" class="text-sm font-bold">0</span>
                                    </div>
                                </div>
                            </div>
                            <div class="bg-white/10 rounded-lg p-3 border border-white/20">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm font-medium opacity-90">Last Data</span>
                                    <span id="lastDataTime" class="text-xs font-medium opacity-75">Never</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Information Panel -->
                <div class="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-6 border border-gray-200">
                    <div class="flex items-start">
                        <div class="bg-blue-100 text-blue-600 rounded-full h-8 w-8 flex items-center justify-center mr-3 mt-1">
                            <i data-lucide="info" class="w-4 h-4"></i>
                        </div>
                        <div class="flex-1">
                            <h5 class="font-semibold text-deep-ocean mb-2">Testing Instructions</h5>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
                                <div>
                                    <p class="font-medium text-desert-sand mb-1">🧪 Single Test:</p>
                                    <p>Sends one realistic data point to test dashboard functionality and data flow.</p>
                                </div>
                                <div>
                                    <p class="font-medium text-oasis-green mb-1">📡 Live Stream:</p>
                                    <p>Generates continuous mock data every 1 second with realistic solar patterns.</p>
                                </div>
                                <div>
                                    <p class="font-medium text-deep-ocean mb-1">🌞 Solar Simulation:</p>
                                    <p>Mock data follows daily solar cycles (6 AM - 6 PM peak generation).</p>
                                </div>
                                <div>
                                    <p class="font-medium text-purple-600 mb-1">🔄 Real-time Updates:</p>
                                    <p>All test data appears instantly in charts, device cards, and database.</p>
                                </div>
                                <div>
                                    <p class="font-medium text-blue-600 mb-1">🔌 Real ESP32 Data:</p>
                                    <p>Send POST requests to <code class="bg-white px-1 rounded text-xs">/api/energy-data</code> from your ESP32.</p>
                                </div>
                                <div>
                                    <p class="font-medium text-green-600 mb-1">📡 Endpoint Ready:</p>
                                    <p>Your ESP32 can send data to <code class="bg-white px-1 rounded text-xs">http://YOUR_IP:5000/api/energy-data</code></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Devices Container -->
            <div id="devicesContainer" class="space-y-4 mb-6"></div>





            <!-- Charts Grid -->
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
                <!-- Power Chart -->
                <div class="card-3d rounded-2xl p-6 border border-gray-200 animate-fade-in">
                    <div class="flex items-center mb-4">
                        <div class="bg-desert-sand text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                            <i data-lucide="zap" class="w-5 h-5"></i>
                        </div>
                        <h3 class="text-xl font-bold text-deep-ocean">Real-time Power Generation</h3>
                    </div>
                    <div class="relative h-80">
                        <canvas id="powerChart"></canvas>
                    </div>
                </div>

                <!-- Energy Chart -->
                <div class="card-3d rounded-2xl p-6 border border-gray-200 animate-fade-in" style="animation-delay: 0.2s">
                    <div class="flex items-center mb-4">
                        <div class="bg-oasis-green text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                            <i data-lucide="battery" class="w-5 h-5"></i>
                        </div>
                        <h3 class="text-xl font-bold text-deep-ocean">Energy Accumulation</h3>
                    </div>
                    <div class="relative h-80">
                        <canvas id="energyChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Environmental Chart -->
            <div class="card-3d rounded-2xl p-6 border border-gray-200 animate-fade-in mb-8" style="animation-delay: 0.4s">
                <div class="flex items-center mb-4">
                    <div class="bg-deep-ocean text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                        <i data-lucide="thermometer" class="w-5 h-5"></i>
                    </div>
                    <h3 class="text-xl font-bold text-deep-ocean">Environmental Conditions</h3>
                </div>
                <div class="relative h-80">
                    <canvas id="environmentChart"></canvas>
                </div>
            </div>

            <!-- Footer -->
            <div class="text-center text-gray-500 text-sm">
                <p>Last updated: <span id="lastUpdate" class="font-medium">Never</span></p>
                <p class="mt-2">Powered by VerifiedCC - Automating Carbon Credits with AI and Hedera</p>
            </div>
        </div>
    </main>    
<script>
        // WebSocket connection
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const connectionStatus = document.getElementById('connectionStatus');
        const devicesContainer = document.getElementById('devicesContainer');
        const totalCreditsElement = document.getElementById('totalCredits');
        const lastUpdateElement = document.getElementById('lastUpdate');

        // Chart setup
        const powerCtx = document.getElementById('powerChart').getContext('2d');
        const energyCtx = document.getElementById('energyChart').getContext('2d');
        const environmentCtx = document.getElementById('environmentChart').getContext('2d');

        const powerChart = new Chart(powerCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Power (W)',
                    data: [],
                    borderColor: '#FDB813',
                    backgroundColor: 'rgba(253, 184, 19, 0.1)',
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#FDB813',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 63, 92, 0.1)' },
                        ticks: { color: '#003F5C', font: { family: 'Inter' } }
                    },
                    x: {
                        grid: { color: 'rgba(0, 63, 92, 0.1)' },
                        ticks: { color: '#003F5C', font: { family: 'Inter' } }
                    }
                },
                plugins: {
                    legend: { 
                        labels: { 
                            color: '#003F5C',
                            font: { family: 'Inter', weight: '600' }
                        } 
                    }
                }
            }
        });

        const energyChart = new Chart(energyCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Energy (kWh)',
                    data: [],
                    borderColor: '#2E8540',
                    backgroundColor: 'rgba(46, 133, 64, 0.1)',
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#2E8540',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 63, 92, 0.1)' },
                        ticks: { color: '#003F5C', font: { family: 'Inter' } }
                    },
                    x: {
                        grid: { color: 'rgba(0, 63, 92, 0.1)' },
                        ticks: { color: '#003F5C', font: { family: 'Inter' } }
                    }
                },
                plugins: {
                    legend: { 
                        labels: { 
                            color: '#003F5C',
                            font: { family: 'Inter', weight: '600' }
                        } 
                    }
                }
            }
        });

        const environmentChart = new Chart(environmentCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Temperature (°C)',
                        data: [],
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y',
                        borderWidth: 3,
                        pointBackgroundColor: '#ef4444',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    },
                    {
                        label: 'Irradiance (W/m²)',
                        data: [],
                        borderColor: '#eab308',
                        backgroundColor: 'rgba(234, 179, 8, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1',
                        borderWidth: 3,
                        pointBackgroundColor: '#eab308',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: { color: 'rgba(0, 63, 92, 0.1)' },
                        ticks: { color: '#003F5C', font: { family: 'Inter' } }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        ticks: { color: '#003F5C', font: { family: 'Inter' } }
                    },
                    x: {
                        grid: { color: 'rgba(0, 63, 92, 0.1)' },
                        ticks: { color: '#003F5C', font: { family: 'Inter' } }
                    }
                },
                plugins: {
                    legend: { 
                        labels: { 
                            color: '#003F5C',
                            font: { family: 'Inter', weight: '600' }
                        } 
                    }
                }
            }
        });

        ws.onopen = function(event) {
            const statusText = document.getElementById('statusText');
            const statusDot = document.getElementById('statusDot');
            const connectionStatus = document.getElementById('connectionStatus');
            
            statusText.textContent = 'Connected';
            statusDot.className = 'w-2 h-2 rounded-full mr-2 bg-oasis-green animate-pulse';
            connectionStatus.className = 'status-indicator online inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-green-100 text-oasis-green';
        };

        ws.onclose = function(event) {
            const statusText = document.getElementById('statusText');
            const statusDot = document.getElementById('statusDot');
            const connectionStatus = document.getElementById('connectionStatus');
            
            statusText.textContent = 'Disconnected';
            statusDot.className = 'w-2 h-2 rounded-full mr-2 bg-red-500';
            connectionStatus.className = 'status-indicator offline inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-red-100 text-red-600';
        };

        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            
            if (message.type === 'energy_reading') {
                updateDashboard(message.data);
                updateCharts(message.data);
            } else if (message.type === 'latest_readings') {
                Object.values(message.data).forEach(reading => {
                    updateDashboard(reading);
                });
            }
        };

        function updateDashboard(reading) {
            // Update device cards
            let deviceCard = document.getElementById(`device-${reading.device_id}`);
            if (!deviceCard) {
                deviceCard = createDeviceCard(reading.device_id);
                devicesContainer.appendChild(deviceCard);
                
                // New device detected - show notification for real ESP32 devices
                if (!reading.device_id.includes('MOCK')) {
                    showNotification(`New ESP32 device connected: ${reading.device_id}`, 'success');
                }
            }

            // Update metrics
            updateDeviceMetrics(deviceCard, reading);
            
            // Update carbon credits
            updateCarbonCredits(reading);
            
            // Update timestamp
            lastUpdateElement.textContent = new Date(reading.timestamp).toLocaleString();
            
            // Store reading globally
            latest_readings[reading.device_id] = reading;
            
            // Update real device status
            updateRealDeviceStatus();
        }





        function createDeviceCard(deviceId) {
            const card = document.createElement('div');
            card.className = 'card-3d rounded-xl p-4 border border-gray-200 animate-fade-in bg-white';
            card.id = `device-${deviceId}`;
            card.innerHTML = `
                <div class="flex items-center mb-4">
                    <div class="bg-desert-sand text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                        <i data-lucide="cpu" class="w-5 h-5"></i>
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-deep-ocean">Device: ${deviceId}</h3>
                        <p class="text-gray-600 text-sm">ESP32 Solar Monitor</p>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-gray-600 text-sm font-medium">Power</span>
                            <i data-lucide="zap" class="w-4 h-4 text-desert-sand"></i>
                        </div>
                        <span class="text-lg font-bold text-deep-ocean" id="${deviceId}-power">0 W</span>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-gray-600 text-sm font-medium">Current</span>
                            <i data-lucide="activity" class="w-4 h-4 text-oasis-green"></i>
                        </div>
                        <span class="text-lg font-bold text-deep-ocean" id="${deviceId}-current">0 A</span>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-gray-600 text-sm font-medium">Energy</span>
                            <i data-lucide="battery" class="w-4 h-4 text-desert-sand"></i>
                        </div>
                        <span class="text-lg font-bold text-deep-ocean" id="${deviceId}-energy">0 kWh</span>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-gray-600 text-sm font-medium">Efficiency</span>
                            <i data-lucide="trending-up" class="w-4 h-4 text-oasis-green"></i>
                        </div>
                        <span class="text-lg font-bold text-deep-ocean" id="${deviceId}-efficiency">0%</span>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-gray-600 text-sm font-medium">Temperature</span>
                            <i data-lucide="thermometer" class="w-4 h-4 text-red-500"></i>
                        </div>
                        <span class="text-lg font-bold text-deep-ocean" id="${deviceId}-temp">0°C</span>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-gray-600 text-sm font-medium">Irradiance</span>
                            <i data-lucide="sun" class="w-4 h-4 text-yellow-500"></i>
                        </div>
                        <span class="text-lg font-bold text-deep-ocean" id="${deviceId}-irradiance">0 W/m²</span>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-gray-600 text-sm font-medium">Voltage</span>
                            <i data-lucide="plug" class="w-4 h-4 text-blue-500"></i>
                        </div>
                        <span class="text-lg font-bold text-deep-ocean" id="${deviceId}-voltage">0 V</span>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-gray-600 text-sm font-medium">Power Factor</span>
                            <i data-lucide="gauge" class="w-4 h-4 text-purple-500"></i>
                        </div>
                        <span class="text-lg font-bold text-deep-ocean" id="${deviceId}-pf">0</span>
                    </div>
                </div>
            `;
            
            // Initialize Lucide icons for the new card
            setTimeout(() => {
                lucide.createIcons();
            }, 100);
            
            return card;
        }

        function updateDeviceMetrics(card, reading) {
            const deviceId = reading.device_id;
            document.getElementById(`${deviceId}-power`).textContent = `${reading.power.toFixed(1)} W`;
            document.getElementById(`${deviceId}-current`).textContent = `${reading.current.toFixed(3)} A`;
            document.getElementById(`${deviceId}-energy`).textContent = `${reading.total_energy_kwh.toFixed(4)} kWh`;
            document.getElementById(`${deviceId}-efficiency`).textContent = `${(reading.efficiency * 100).toFixed(1)}%`;
            document.getElementById(`${deviceId}-temp`).textContent = `${reading.ambient_temp_c.toFixed(1)}°C`;
            document.getElementById(`${deviceId}-irradiance`).textContent = `${reading.irradiance_w_m2.toFixed(0)} W/m²`;
            document.getElementById(`${deviceId}-voltage`).textContent = `${reading.voltage.toFixed(0)} V`;
            document.getElementById(`${deviceId}-pf`).textContent = `${reading.power_factor.toFixed(3)}`;
        }

        function updateCharts(reading) {
            const time = new Date(reading.timestamp).toLocaleTimeString();
            
            // Update power chart
            powerChart.data.labels.push(time);
            powerChart.data.datasets[0].data.push(reading.power);
            
            // Keep only last 20 points
            if (powerChart.data.labels.length > 20) {
                powerChart.data.labels.shift();
                powerChart.data.datasets[0].data.shift();
            }
            
            powerChart.update('none');
            
            // Update energy chart
            energyChart.data.labels.push(time);
            energyChart.data.datasets[0].data.push(reading.total_energy_kwh);
            
            if (energyChart.data.labels.length > 20) {
                energyChart.data.labels.shift();
                energyChart.data.datasets[0].data.shift();
            }
            
            energyChart.update('none');

            // Update environment chart
            environmentChart.data.labels.push(time);
            environmentChart.data.datasets[0].data.push(reading.ambient_temp_c);
            environmentChart.data.datasets[1].data.push(reading.irradiance_w_m2);
            
            if (environmentChart.data.labels.length > 20) {
                environmentChart.data.labels.shift();
                environmentChart.data.datasets[0].data.shift();
                environmentChart.data.datasets[1].data.shift();
            }
            
            environmentChart.update('none');
        }

        function updateCarbonCredits(reading) {
            // Calculate carbon credits (Morocco emission factor: 0.81 tCO2/MWh)
            const morocco_ef = 0.81;
            const export_mwh = reading.total_energy_kwh / 1000.0 * 0.98;
            const carbon_credits = export_mwh * morocco_ef;
            
            totalCreditsElement.textContent = carbon_credits.toFixed(6);
        }

        // Store latest readings globally
        let latest_readings = {};

        // Test control functions
        async function sendMockData() {
            try {
                const response = await fetch('/api/test/send-mock-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    showNotification('Test data sent successfully! Check your dashboard for updates.', 'success');
                } else {
                    showNotification('Failed to send test data. Please try again.', 'error');
                }
            } catch (error) {
                showNotification('Connection error: ' + error.message, 'error');
            }
        }

        async function startMockStream() {
            try {
                const response = await fetch('/api/test/start-mock-stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    showNotification('Live data stream started! Generating realistic solar data every 1 second.', 'success');
                    updateStreamStatus(true);
                } else if (result.status === 'already_running') {
                    showNotification('Data stream is already active and running.', 'warning');
                    updateStreamStatus(true);
                } else {
                    showNotification('Failed to start data stream. Please try again.', 'error');
                }
            } catch (error) {
                showNotification('Connection error: ' + error.message, 'error');
            }
        }

        async function stopMockStream() {
            try {
                const response = await fetch('/api/test/stop-mock-stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    showNotification('Data stream stopped successfully.', 'info');
                    updateStreamStatus(false);
                } else if (result.status === 'not_running') {
                    showNotification('Data stream was not active.', 'warning');
                    updateStreamStatus(false);
                } else {
                    showNotification('Failed to stop data stream. Please try again.', 'error');
                }
            } catch (error) {
                showNotification('Connection error: ' + error.message, 'error');
            }
        }

        async function checkMockStatus() {
            try {
                const response = await fetch('/api/test/mock-status');
                const result = await response.json();
                updateStreamStatus(result.mock_active);
            } catch (error) {
                console.error('Error checking mock status:', error);
            }
        }

        function updateRealDeviceStatus() {
            const realDevices = Object.keys(latest_readings).filter(deviceId => !deviceId.includes('MOCK'));
            const realDevicesCount = document.getElementById('realDevicesCount');
            const realDevicesDot = document.getElementById('realDevicesDot');
            const lastDataTime = document.getElementById('lastDataTime');
            
            // Update device count
            realDevicesCount.textContent = realDevices.length;
            
            // Update status dot
            if (realDevices.length > 0) {
                realDevicesDot.className = 'w-2 h-2 rounded-full bg-green-400 mr-2 animate-pulse';
                
                // Find most recent real device data
                let mostRecentTime = null;
                realDevices.forEach(deviceId => {
                    const reading = latest_readings[deviceId];
                    const readingTime = new Date(reading.timestamp);
                    if (!mostRecentTime || readingTime > mostRecentTime) {
                        mostRecentTime = readingTime;
                    }
                });
                
                if (mostRecentTime) {
                    lastDataTime.textContent = mostRecentTime.toLocaleTimeString();
                }
            } else {
                realDevicesDot.className = 'w-2 h-2 rounded-full bg-gray-400 mr-2';
                lastDataTime.textContent = 'Never';
            }
        }

        function updateStreamStatus(isActive) {
            const statusElement = document.getElementById('streamStatus');
            const statusDot = document.getElementById('streamStatusDot');
            const startBtn = document.getElementById('startStreamBtn');
            const stopBtn = document.getElementById('stopStreamBtn');
            
            if (isActive) {
                statusElement.textContent = 'Active';
                statusElement.className = 'text-sm font-bold text-green-300';
                statusDot.className = 'w-2 h-2 rounded-full bg-green-400 mr-2 animate-pulse';
                
                startBtn.disabled = true;
                startBtn.className = 'w-full bg-gray-400 text-gray-600 font-semibold px-4 py-2 rounded-lg cursor-not-allowed flex items-center justify-center opacity-50';
                
                stopBtn.disabled = false;
                stopBtn.className = 'w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-500 text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center';
            } else {
                statusElement.textContent = 'Stopped';
                statusElement.className = 'text-sm font-bold text-gray-300';
                statusDot.className = 'w-2 h-2 rounded-full bg-gray-400 mr-2';
                
                startBtn.disabled = false;
                startBtn.className = 'w-full bg-gradient-to-r from-oasis-green to-green-600 hover:from-green-600 hover:to-oasis-green text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center';
                
                stopBtn.disabled = true;
                stopBtn.className = 'w-full bg-gray-400 text-gray-600 font-semibold px-4 py-2 rounded-lg cursor-not-allowed flex items-center justify-center opacity-50';
            }
        }

        function showNotification(message, type = 'info') {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `fixed top-20 right-6 z-50 p-4 rounded-2xl shadow-2xl max-w-sm transition-all duration-500 transform translate-x-full`;
            
            // Set colors and styles based on type using dashboard color scheme
            const styles = {
                success: 'bg-gradient-to-r from-oasis-green to-green-600 text-white border border-green-300',
                error: 'bg-gradient-to-r from-red-500 to-red-600 text-white border border-red-300',
                warning: 'bg-gradient-to-r from-desert-sand to-yellow-500 text-deep-ocean border border-yellow-300',
                info: 'bg-gradient-to-r from-deep-ocean to-blue-600 text-white border border-blue-300'
            };
            
            const icons = {
                success: 'check-circle',
                error: 'alert-circle',
                warning: 'alert-triangle',
                info: 'info'
            };
            
            notification.className += ` ${styles[type] || styles.info}`;
            notification.innerHTML = `
                <div class="flex items-center">
                    <div class="bg-white/20 rounded-full h-8 w-8 flex items-center justify-center mr-3">
                        <i data-lucide="${icons[type] || icons.info}" class="w-4 h-4"></i>
                    </div>
                    <span class="flex-1 font-medium">${message}</span>
                    <button onclick="this.parentElement.parentElement.remove()" class="ml-3 bg-white/20 hover:bg-white/30 rounded-full h-6 w-6 flex items-center justify-center transition-colors">
                        <i data-lucide="x" class="w-3 h-3"></i>
                    </button>
                </div>
            `;
            
            document.body.appendChild(notification);
            
            // Initialize icons for the notification
            lucide.createIcons();
            
            // Animate in with bounce effect
            setTimeout(() => {
                notification.classList.remove('translate-x-full');
                notification.classList.add('animate-bounce');
                setTimeout(() => {
                    notification.classList.remove('animate-bounce');
                }, 600);
            }, 100);
            
            // Auto remove after 4 seconds
            setTimeout(() => {
                notification.classList.add('translate-x-full', 'opacity-0');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 500);
            }, 4000);
        }

        // Initialize dashboard on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize Lucide icons
            lucide.createIcons();
            
            // Set up test button event listeners
            document.getElementById('sendMockBtn').addEventListener('click', sendMockData);
            document.getElementById('startStreamBtn').addEventListener('click', startMockStream);
            document.getElementById('stopStreamBtn').addEventListener('click', stopMockStream);
            
            // Check initial mock status
            checkMockStatus();
            
            // Check mock status every 10 seconds
            setInterval(checkMockStatus, 10000);
        });



        // Fetch initial data
        fetch('/api/latest-readings')
            .then(response => response.json())
            .then(data => {
                latest_readings = data;
                Object.values(data).forEach(reading => {
                    updateDashboard(reading);
                });
            })
            .catch(error => console.error('Error fetching initial data:', error));

        // Initialize Lucide icons
        lucide.createIcons();
    </script>
</body>
</html>"""