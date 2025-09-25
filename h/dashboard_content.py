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
                        <h1 class="text-2xl font-bold text-deep-ocean">Carbon Credit Dashboard</h1>
                        <p class="text-sm text-gray-600">Real-time monitoring & verification</p>
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



            <!-- Devices Container -->
            <div id="devicesContainer" class="space-y-4 mb-6"></div>

            <!-- Guardian Integration Section -->
            <div class="card-3d rounded-2xl p-8 border border-gray-200 mb-8 animate-fade-in">
                <div class="flex items-center mb-6">
                    <div class="bg-deep-ocean text-white rounded-full h-12 w-12 flex items-center justify-center mr-4">
                        <i data-lucide="shield-check" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <h3 class="text-2xl font-bold text-deep-ocean">Guardian Integration</h3>
                        <p class="text-gray-600">Official carbon credit verification platform</p>
                    </div>
                </div>
                <div class="flex flex-wrap gap-4 mb-4">
                    <button onclick="sendToGuardian()" 
                            class="bg-desert-sand text-deep-ocean font-semibold px-6 py-3 rounded-lg hover:brightness-105 transition-transform hover:scale-105 shadow-lg">
                        <i data-lucide="send" class="w-4 h-4 inline mr-2"></i>
                        Send to Guardian
                    </button>
                    <button onclick="viewGuardianData()" 
                            class="bg-oasis-green text-white font-semibold px-6 py-3 rounded-lg hover:bg-green-700 transition-colors shadow-lg">
                        <i data-lucide="eye" class="w-4 h-4 inline mr-2"></i>
                        View Guardian Format
                    </button>
                </div>
                <div id="guardianStatus" class="mt-4"></div>
            </div>

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
            }

            // Update metrics
            updateDeviceMetrics(deviceCard, reading);
            
            // Update carbon credits
            updateCarbonCredits(reading);
            
            // Update timestamp
            lastUpdateElement.textContent = new Date(reading.timestamp).toLocaleString();
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

        function sendToGuardian() {
            // Get the first device's data
            const deviceIds = Object.keys(latest_readings);
            if (deviceIds.length === 0) {
                alert('No device data available');
                return;
            }

            const deviceId = deviceIds[0];
            fetch(`/api/carbon-credits/${deviceId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('guardianStatus').innerHTML = 
                        `<div class="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
                            <div class="flex items-center mb-2">
                                <i data-lucide="check-circle" class="w-5 h-5 text-oasis-green mr-2"></i>
                                <p class="text-oasis-green font-semibold">Guardian data prepared successfully!</p>
                            </div>
                            <pre class="bg-gray-800 text-green-400 p-4 rounded-lg text-xs overflow-x-auto font-mono">${JSON.stringify(data, null, 2)}</pre>
                         </div>`;
                    lucide.createIcons();
                })
                .catch(error => {
                    document.getElementById('guardianStatus').innerHTML = 
                        `<div class="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
                            <div class="flex items-center">
                                <i data-lucide="x-circle" class="w-5 h-5 text-red-500 mr-2"></i>
                                <p class="text-red-600 font-semibold">Error: ${error.message}</p>
                            </div>
                         </div>`;
                    lucide.createIcons();
                });
        }

        function viewGuardianData() {
            const deviceIds = Object.keys(latest_readings);
            if (deviceIds.length === 0) {
                alert('No device data available');
                return;
            }

            const deviceId = deviceIds[0];
            window.open(`/api/carbon-credits/${deviceId}`, '_blank');
        }

        // Store latest readings globally
        let latest_readings = {};

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