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
                        <p class="text-sm text-gray-600">ESP32 Monitoring + Guardian Tools Architecture</p>
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

            <!-- AMS-I.D Integration Section -->
            <div class="card-3d rounded-2xl p-8 border border-gray-200 mb-8 animate-fade-in">
                <div class="flex items-center mb-6">
                    <div class="bg-gradient-to-r from-oasis-green to-desert-sand text-white rounded-full h-12 w-12 flex items-center justify-center mr-4">
                        <i data-lucide="leaf" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <h3 class="text-2xl font-bold text-deep-ocean">AMS-I.D Carbon Credit System</h3>
                        <p class="text-gray-600">Automatic aggregation and Guardian submission</p>
                    </div>
                </div>

                <!-- AMS-I.D Status Grid -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                    <!-- Status -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg">
                        <div class="flex items-center mb-4">
                            <div class="bg-oasis-green text-cloud-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="activity" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-deep-ocean">System Status</h4>
                                <p class="text-sm text-gray-600">AMS-I.D Integration</p>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Status</span>
                                    <span class="text-sm font-semibold" id="ams-status">
                                        <span class="inline-block w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                                        Initializing...
                                    </span>
                                </div>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Guardian</span>
                                    <span class="text-sm font-semibold" id="ams-guardian-status">
                                        <span class="inline-block w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                                        Connecting...
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Measurements -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg">
                        <div class="flex items-center mb-4">
                            <div class="bg-desert-sand text-deep-ocean rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="database" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-deep-ocean">Data Processing</h4>
                                <p class="text-sm text-gray-600">Measurements & Buffer</p>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Processed</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="ams-measurements">0</span>
                                </div>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Buffer</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="ams-buffer">0</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Submissions -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg">
                        <div class="flex items-center mb-4">
                            <div class="bg-deep-ocean text-cloud-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="send" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-deep-ocean">Guardian Submissions</h4>
                                <p class="text-sm text-gray-600">Projects & Reports</p>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Projects</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="ams-projects">0</span>
                                </div>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Reports</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="ams-reports">0</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Carbon Credits -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-oasis-green to-desert-sand shadow-lg text-white">
                        <div class="flex items-center mb-4">
                            <div class="bg-white/20 rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="leaf" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold">Carbon Credits</h4>
                                <p class="text-sm opacity-90">AMS-I.D Generated</p>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <div class="bg-white/10 rounded-lg p-3 border border-white/20">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm font-medium opacity-90">Total</span>
                                    <span class="text-lg font-bold" id="ams-carbon-credits">0.000</span>
                                </div>
                            </div>
                            <div class="bg-white/10 rounded-lg p-3 border border-white/20">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm font-medium opacity-90">Energy</span>
                                    <span class="text-lg font-bold" id="ams-energy">0.000 MWh</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AMS-I.D Controls -->
                <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg mb-6">
                    <div class="flex items-center mb-6">
                        <div class="bg-deep-ocean text-cloud-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                            <i data-lucide="settings" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h4 class="text-xl font-bold text-deep-ocean">AMS-I.D Workflow Controls</h4>
                            <p class="text-gray-600 text-sm">Manual triggers and system management</p>
                        </div>
                    </div>
                    
                    <!-- Device Selection -->
                    <div class="bg-gray-50 rounded-lg p-4 border border-gray-100 mb-4">
                        <label for="ams-device-select" class="block text-sm font-medium text-deep-ocean mb-2">Select Device for AMS-I.D Processing:</label>
                        <select id="ams-device-select" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-desert-sand focus:border-transparent bg-white">
                            <option value="">All devices</option>
                        </select>
                    </div>

                    <!-- Control Buttons -->
                    <div class="flex flex-wrap gap-3 justify-center mb-4">
                        <button onclick="initializeAMSID()" 
                                class="bg-oasis-green text-cloud-white font-semibold px-6 py-3 rounded-lg hover:brightness-105 transition-transform hover:scale-105 shadow-lg text-sm flex items-center">
                            <i data-lucide="power" class="w-4 h-4 mr-2"></i>
                            Initialize AMS-I.D
                        </button>
                        <button onclick="triggerAMSAggregation()" 
                                class="bg-desert-sand text-deep-ocean font-semibold px-6 py-3 rounded-lg hover:brightness-105 transition-transform hover:scale-105 shadow-lg text-sm flex items-center">
                            <i data-lucide="layers" class="w-4 h-4 mr-2"></i>
                            Trigger Aggregation
                        </button>
                        <button onclick="runAMSWorkflow()" 
                                class="bg-gradient-to-r from-oasis-green to-desert-sand text-cloud-white font-semibold px-6 py-3 rounded-lg hover:brightness-105 transition-transform hover:scale-105 shadow-lg text-sm flex items-center">
                            <i data-lucide="play-circle" class="w-4 h-4 mr-2"></i>
                            Run Complete Workflow
                        </button>
                        <button onclick="refreshAMSStatus()" 
                                class="bg-deep-ocean text-cloud-white font-semibold px-6 py-3 rounded-lg hover:brightness-105 transition-colors shadow-lg text-sm flex items-center">
                            <i data-lucide="refresh-cw" class="w-4 h-4 mr-2"></i>
                            Refresh Status
                        </button>
                    </div>

                    <!-- AMS-I.D Activity Log -->
                    <div class="bg-cloud-white rounded-lg border border-gray-200 p-4 shadow-inner">
                        <div class="flex items-center mb-3">
                            <div class="bg-gray-100 text-deep-ocean rounded-full h-8 w-8 flex items-center justify-center mr-3">
                                <i data-lucide="file-text" class="w-4 h-4"></i>
                            </div>
                            <h5 class="font-semibold text-deep-ocean">AMS-I.D Activity Log</h5>
                        </div>
                        <div id="ams-activity-log" class="space-y-2 max-h-32 overflow-y-auto text-sm">
                            <div class="text-gray-500 italic flex items-center">
                                <span class="inline-block w-2 h-2 bg-desert-sand rounded-full mr-2 animate-pulse"></span>
                                AMS-I.D system ready for initialization...
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Guardian Tools Architecture Section -->
            <div class="card-3d rounded-2xl p-8 border border-gray-200 mb-8 animate-fade-in">
                <div class="flex items-center mb-6">
                    <div class="bg-deep-ocean text-white rounded-full h-12 w-12 flex items-center justify-center mr-4">
                        <i data-lucide="shield-check" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <h3 class="text-2xl font-bold text-deep-ocean">Guardian Tools Architecture</h3>
                        <p class="text-gray-600">Real-time MRV processing pipeline</p>
                    </div>
                </div>

                <!-- Guardian Tools Status Grid -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <!-- Tool 10: Data Source -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg hover:shadow-xl transition-shadow duration-300">
                        <div class="flex items-center mb-4">
                            <div class="bg-oasis-green text-cloud-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="database" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-deep-ocean">Tool 10 - Data Source</h4>
                                <p class="text-sm text-gray-600">ESP32 IoT Sensors</p>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Data Points</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="tool10-data-points">0</span>
                                </div>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Active Devices</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="tool10-devices">0</span>
                                </div>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Status</span>
                                    <span class="text-sm font-semibold text-oasis-green" id="tool10-status">
                                        <span class="inline-block w-2 h-2 bg-oasis-green rounded-full mr-2 animate-pulse"></span>
                                        Online
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tool 07: Aggregation -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg hover:shadow-xl transition-shadow duration-300">
                        <div class="flex items-center mb-4">
                            <div class="bg-desert-sand text-deep-ocean rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="settings" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-deep-ocean">Tool 07 - Aggregation</h4>
                                <p class="text-sm text-gray-600">Data Processing</p>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Reports</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="tool07-reports">0</span>
                                </div>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Energy</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="tool07-energy">0 kWh</span>
                                </div>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Emissions</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="tool07-emissions">0 tCO2</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tool 03: Hedera -->
                    <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg hover:shadow-xl transition-shadow duration-300">
                        <div class="flex items-center mb-4">
                            <div class="bg-deep-ocean text-cloud-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                                <i data-lucide="link" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-deep-ocean">Tool 03 - Hedera</h4>
                                <p class="text-sm text-gray-600">Verification</p>
                            </div>
                        </div>
                        <div class="space-y-3">
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Records</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="tool03-records">0</span>
                                </div>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Verified</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="tool03-verified">0</span>
                                </div>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-600 text-sm font-medium">Reductions</span>
                                    <span class="text-lg font-bold text-deep-ocean" id="tool03-reductions">0 tCO2</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Guardian Workflow Controls -->
                <div class="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg">
                    <div class="flex items-center mb-6">
                        <div class="bg-deep-ocean text-cloud-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                            <i data-lucide="workflow" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h4 class="text-xl font-bold text-deep-ocean">Guardian Tools Workflow</h4>
                            <p class="text-gray-600 text-sm">Complete MRV processing pipeline</p>
                        </div>
                    </div>
                    
                    <!-- Workflow Flow Diagram -->
                    <div class="bg-gray-50 rounded-lg p-4 border border-gray-100 mb-6">
                        <div class="flex items-center justify-center overflow-x-auto">
                            <div class="flex items-center space-x-2 min-w-max">
                                <div class="bg-oasis-green text-cloud-white px-3 py-2 rounded-lg text-xs font-semibold text-center shadow-lg min-w-[80px]">
                                    <div class="font-bold">Tool 10</div>
                                    <div class="text-xs opacity-90">Data Source</div>
                                </div>
                                <i data-lucide="arrow-right" class="w-4 h-4 text-gray-400 flex-shrink-0"></i>
                                <div class="bg-desert-sand text-deep-ocean px-3 py-2 rounded-lg text-xs font-semibold text-center shadow-lg min-w-[80px]">
                                    <div class="font-bold">Tool 07</div>
                                    <div class="text-xs opacity-90">Aggregation</div>
                                </div>
                                <i data-lucide="arrow-right" class="w-4 h-4 text-gray-400 flex-shrink-0"></i>
                                <div class="bg-deep-ocean text-cloud-white px-3 py-2 rounded-lg text-xs font-semibold text-center shadow-lg min-w-[80px]">
                                    <div class="font-bold">Tool 03</div>
                                    <div class="text-xs opacity-90">Hedera</div>
                                </div>
                                <i data-lucide="arrow-right" class="w-4 h-4 text-gray-400 flex-shrink-0"></i>
                                <div class="bg-gradient-to-r from-oasis-green to-desert-sand text-cloud-white px-3 py-2 rounded-lg text-xs font-semibold text-center shadow-lg min-w-[80px]">
                                    <div class="font-bold">Guardian</div>
                                    <div class="text-xs opacity-90">MRV Report</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Device Selection and Controls -->
                    <div class="space-y-4 mb-6">
                        <div class="bg-gray-50 rounded-lg p-4 border border-gray-100">
                            <label for="guardian-device-select" class="block text-sm font-medium text-deep-ocean mb-2">Select Device:</label>
                            <select id="guardian-device-select" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-desert-sand focus:border-transparent bg-white">
                                <option value="">Choose ESP32 device...</option>
                            </select>
                        </div>
                        <div class="flex flex-wrap gap-3 justify-center">
                            <button onclick="triggerAggregation()" 
                                    class="bg-desert-sand text-deep-ocean font-semibold px-6 py-3 rounded-lg hover:brightness-105 transition-transform hover:scale-105 shadow-lg text-sm flex items-center">
                                <i data-lucide="settings" class="w-4 h-4 mr-2"></i>
                                Trigger Aggregation
                            </button>
                            <button onclick="runCompleteWorkflow()" 
                                    class="bg-oasis-green text-cloud-white font-semibold px-6 py-3 rounded-lg hover:brightness-105 transition-transform hover:scale-105 shadow-lg text-sm flex items-center">
                                <i data-lucide="play" class="w-4 h-4 mr-2"></i>
                                Run Complete Workflow
                            </button>
                            <button onclick="refreshGuardianStatus()" 
                                    class="bg-deep-ocean text-cloud-white font-semibold px-6 py-3 rounded-lg hover:brightness-105 transition-colors shadow-lg text-sm flex items-center">
                                <i data-lucide="refresh-cw" class="w-4 h-4 mr-2"></i>
                                Refresh Status
                            </button>
                        </div>
                    </div>

                    <!-- Activity Log -->
                    <div class="bg-cloud-white rounded-lg border border-gray-200 p-4 shadow-inner">
                        <div class="flex items-center mb-3">
                            <div class="bg-gray-100 text-deep-ocean rounded-full h-8 w-8 flex items-center justify-center mr-3">
                                <i data-lucide="activity" class="w-4 h-4"></i>
                            </div>
                            <h5 class="font-semibold text-deep-ocean">Activity Log</h5>
                        </div>
                        <div id="guardian-activity-log" class="space-y-2 max-h-32 overflow-y-auto text-sm">
                            <div class="text-gray-500 italic flex items-center">
                                <span class="inline-block w-2 h-2 bg-oasis-green rounded-full mr-2 animate-pulse"></span>
                                Guardian Tools initialized and ready...
                            </div>
                        </div>
                    </div>
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
                
                // Update Guardian device selector when new device appears
                updateGuardianDeviceSelect();
                updateAMSDeviceSelect();
                addGuardianLog(`📱 New device detected: ${reading.device_id}`);
            }

            // Update metrics
            updateDeviceMetrics(deviceCard, reading);
            
            // Update carbon credits
            updateCarbonCredits(reading);
            
            // Update timestamp
            lastUpdateElement.textContent = new Date(reading.timestamp).toLocaleString();
            
            // Store reading globally for Guardian functions
            latest_readings[reading.device_id] = reading;
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

        // Guardian Tools Functions
        function refreshGuardianStatus() {
            addGuardianLog('Refreshing Guardian Tools status...');
            
            fetch('/api/guardian/status')
                .then(response => response.json())
                .then(status => {
                    updateGuardianToolsStatus(status);
                    addGuardianLog('✅ Status refreshed successfully');
                })
                .catch(error => {
                    addGuardianLog('❌ Error refreshing status: ' + error.message);
                });
        }

        function updateGuardianToolsStatus(status) {
            // Tool 10 - Data Source
            document.getElementById('tool10-data-points').textContent = status.tool_10_data_source.raw_data_points;
            document.getElementById('tool10-devices').textContent = status.tool_10_data_source.devices_active;
            
            // Tool 07 - Aggregation
            document.getElementById('tool07-reports').textContent = status.tool_07_aggregation.aggregated_reports;
            document.getElementById('tool07-energy').textContent = status.tool_07_aggregation.total_energy_processed.toFixed(3) + ' kWh';
            document.getElementById('tool07-emissions').textContent = status.tool_07_aggregation.total_emission_reductions.toFixed(6) + ' tCO2';
            
            // Tool 03 - Hedera
            document.getElementById('tool03-records').textContent = status.tool_03_hedera.hedera_records;
            document.getElementById('tool03-verified').textContent = status.tool_03_hedera.verified_records;
            document.getElementById('tool03-reductions').textContent = status.tool_03_hedera.total_verified_reductions.toFixed(6) + ' tCO2';
        }

        // AMS-I.D Functions
        async function initializeAMSID() {
            addAMSActivity('🔧 Initializing AMS-I.D system...');
            
            try {
                const response = await fetch('/api/ams-id/initialize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addAMSActivity('✅ AMS-I.D system initialized successfully');
                    refreshAMSStatus();
                } else {
                    addAMSActivity(`❌ Initialization failed: ${result.message}`);
                }
            } catch (error) {
                addAMSActivity(`❌ Error: ${error.message}`);
            }
        }

        async function triggerAMSAggregation() {
            const deviceSelect = document.getElementById('ams-device-select');
            const selectedDevice = deviceSelect.value || 'all';
            
            addAMSActivity(`🔄 Triggering AMS-I.D aggregation for ${selectedDevice}...`);
            
            try {
                const endpoint = selectedDevice === 'all' ? 
                    '/api/ams-id/aggregate/ESP32_001?hours=24' : 
                    `/api/ams-id/aggregate/${selectedDevice}?hours=24`;
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const report = result.report;
                    addAMSActivity(`✅ Aggregation successful: ${report.total_energy_mwh.toFixed(3)} MWh, ${report.emission_reductions_tco2.toFixed(6)} tCO2e`);
                    refreshAMSStatus();
                } else {
                    addAMSActivity(`❌ Aggregation failed: ${result.message}`);
                }
            } catch (error) {
                addAMSActivity(`❌ Error: ${error.message}`);
            }
        }

        async function runAMSWorkflow() {
            const deviceSelect = document.getElementById('ams-device-select');
            const selectedDevice = deviceSelect.value;
            
            addAMSActivity(`🚀 Starting complete AMS-I.D workflow...`);
            
            try {
                const endpoint = selectedDevice ? 
                    `/api/ams-id/workflow/${selectedDevice}` : 
                    '/api/ams-id/workflow/all';
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    addAMSActivity('✅ Complete AMS-I.D workflow successful!');
                    addAMSActivity('📤 Data submitted to Guardian via AMS-I.D policy');
                    refreshAMSStatus();
                    updateTotalCredits(); // Update main carbon credits display
                } else {
                    addAMSActivity(`❌ Workflow failed: ${result.message}`);
                }
            } catch (error) {
                addAMSActivity(`❌ Error: ${error.message}`);
            }
        }

        async function refreshAMSStatus() {
            try {
                const response = await fetch('/api/ams-id/metrics');
                const metrics = await response.json();
                
                // Update status indicators
                const statusElement = document.getElementById('ams-status');
                const guardianStatusElement = document.getElementById('ams-guardian-status');
                
                if (metrics.ams_id_status === 'online') {
                    statusElement.innerHTML = '<span class="inline-block w-2 h-2 bg-oasis-green rounded-full mr-2 animate-pulse"></span><span class="text-oasis-green">Online</span>';
                } else {
                    statusElement.innerHTML = '<span class="inline-block w-2 h-2 bg-red-500 rounded-full mr-2"></span><span class="text-red-500">Offline</span>';
                }
                
                if (metrics.guardian_status === 'authenticated') {
                    guardianStatusElement.innerHTML = '<span class="inline-block w-2 h-2 bg-oasis-green rounded-full mr-2 animate-pulse"></span><span class="text-oasis-green">Connected</span>';
                } else {
                    guardianStatusElement.innerHTML = '<span class="inline-block w-2 h-2 bg-red-500 rounded-full mr-2"></span><span class="text-red-500">Disconnected</span>';
                }
                
                // Update metrics
                document.getElementById('ams-measurements').textContent = metrics.measurements_processed;
                document.getElementById('ams-buffer').textContent = metrics.buffer_count;
                document.getElementById('ams-projects').textContent = metrics.projects_submitted;
                document.getElementById('ams-reports').textContent = metrics.reports_submitted;
                document.getElementById('ams-carbon-credits').textContent = metrics.total_carbon_credits.toFixed(6);
                document.getElementById('ams-energy').textContent = `${metrics.total_energy_mwh.toFixed(3)} MWh`;
                
                // Update main carbon credits display
                const mainCreditsElement = document.getElementById('totalCredits');
                if (mainCreditsElement) {
                    const currentCredits = parseFloat(mainCreditsElement.textContent) || 0;
                    const newTotal = currentCredits + metrics.total_carbon_credits;
                    mainCreditsElement.textContent = newTotal.toFixed(6);
                }
                
            } catch (error) {
                console.error('Error refreshing AMS status:', error);
            }
        }

        function addAMSActivity(message) {
            const logContainer = document.getElementById('ams-activity-log');
            const timestamp = new Date().toLocaleTimeString();
            
            const logEntry = document.createElement('div');
            logEntry.className = 'flex items-start text-sm';
            logEntry.innerHTML = `
                <span class="text-gray-400 text-xs mr-2 mt-0.5 font-mono">${timestamp}</span>
                <span class="flex-1">${message}</span>
            `;
            
            logContainer.appendChild(logEntry);
            
            // Keep only last 10 entries
            while (logContainer.children.length > 10) {
                logContainer.removeChild(logContainer.firstChild);
            }
            
            // Scroll to bottom
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        // Guardian Tools Functions
        function triggerAggregation() {
            const deviceSelect = document.getElementById('guardian-device-select');
            const selectedDevice = deviceSelect.value;
            
            if (!selectedDevice) {
                alert('Please select a device first');
                return;
            }
            
            addGuardianLog(`🔄 Triggering aggregation for ${selectedDevice}...`);
            
            fetch(`/api/guardian/aggregate/${selectedDevice}`, {
                method: 'POST'
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        addGuardianLog(`✅ Aggregation completed for ${selectedDevice}`);
                        addGuardianLog(`📊 Energy: ${result.data.total_energy_kwh.toFixed(3)} kWh, Emissions: ${result.data.emission_reductions_tco2.toFixed(6)} tCO2`);
                        refreshGuardianStatus();
                    } else {
                        addGuardianLog(`❌ Aggregation failed: ${result.message}`);
                    }
                })
                .catch(error => {
                    addGuardianLog('❌ Error triggering aggregation: ' + error.message);
                });
        }

        function runCompleteWorkflow() {
            const deviceSelect = document.getElementById('guardian-device-select');
            const selectedDevice = deviceSelect.value;
            
            if (!selectedDevice) {
                alert('Please select a device first');
                return;
            }
            
            addGuardianLog(`🚀 Starting complete workflow for ${selectedDevice}...`);
            
            fetch(`/api/guardian/workflow/${selectedDevice}`, {
                method: 'POST'
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        addGuardianLog(`✅ Complete workflow finished for ${selectedDevice}`);
                        addGuardianLog(`📊 Emission reductions: ${result.aggregated_data.emission_reductions_tco2.toFixed(6)} tCO2`);
                        addGuardianLog(`🔗 Hedera TX: ${result.hedera_record.hedera_transaction_id}`);
                        addGuardianLog(`🛡️ Guardian submitted: ${result.guardian_submitted ? 'Yes' : 'No'}`);
                        refreshGuardianStatus();
                        
                        // Show success notification
                        document.getElementById('guardianStatus').innerHTML = 
                            `<div class="bg-green-50 border border-green-200 rounded-lg p-4 mt-4">
                                <div class="flex items-center mb-2">
                                    <i data-lucide="check-circle" class="w-5 h-5 text-oasis-green mr-2"></i>
                                    <p class="text-oasis-green font-semibold">Guardian workflow completed successfully!</p>
                                </div>
                                <div class="text-sm text-green-700">
                                    <p>• Emission reductions: ${result.aggregated_data.emission_reductions_tco2.toFixed(6)} tCO2</p>
                                    <p>• Hedera transaction: ${result.hedera_record.hedera_transaction_id}</p>
                                    <p>• Data hash: ${result.hedera_record.data_hash.substring(0, 16)}...</p>
                                </div>
                             </div>`;
                        lucide.createIcons();
                    } else {
                        addGuardianLog(`❌ Workflow failed: ${result.error}`);
                    }
                })
                .catch(error => {
                    addGuardianLog('❌ Error running workflow: ' + error.message);
                });
        }

        function addGuardianLog(message) {
            const logContainer = document.getElementById('guardian-activity-log');
            const timestamp = new Date().toLocaleTimeString();
            
            const logEntry = document.createElement('div');
            logEntry.className = 'text-xs text-gray-600 border-l-2 border-gray-300 pl-2';
            logEntry.innerHTML = `<span class="text-gray-400">[${timestamp}]</span> ${message}`;
            
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // Keep only last 20 log entries
            while (logContainer.children.length > 20) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }

        function updateGuardianDeviceSelect() {
            const deviceSelect = document.getElementById('guardian-device-select');
            const currentDevices = Object.keys(latest_readings);
            
            // Clear existing options except the first one
            deviceSelect.innerHTML = '<option value="">Select device...</option>';
            
            // Add current devices
            currentDevices.forEach(deviceId => {
                const option = document.createElement('option');
                option.value = deviceId;
                option.textContent = deviceId;
                deviceSelect.appendChild(option);
            });
        }

        function updateAMSDeviceSelect() {
            const deviceSelect = document.getElementById('ams-device-select');
            const currentDevices = Object.keys(latest_readings);
            
            // Clear existing options except the first one
            deviceSelect.innerHTML = '<option value="">All devices</option>';
            
            // Add current devices
            currentDevices.forEach(deviceId => {
                const option = document.createElement('option');
                option.value = deviceId;
                option.textContent = deviceId;
                deviceSelect.appendChild(option);
            });
        }

        function sendToGuardian() {
            // Legacy function - now redirects to complete workflow
            const deviceIds = Object.keys(latest_readings);
            if (deviceIds.length === 0) {
                alert('No device data available');
                return;
            }

            const deviceId = deviceIds[0];
            document.getElementById('guardian-device-select').value = deviceId;
            runCompleteWorkflow();
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

        // Initialize Guardian Tools on page load
        document.addEventListener('DOMContentLoaded', function() {
            // Initial Guardian status refresh
            setTimeout(() => {
                refreshGuardianStatus();
                addGuardianLog('🛡️ Guardian Tools Dashboard initialized');
            }, 2000);
            
            // Auto-refresh Guardian status every 30 seconds
            setInterval(refreshGuardianStatus, 30000);
            
            // Auto-refresh AMS-I.D status every 30 seconds
            setInterval(refreshAMSStatus, 30000);
            
            // Initialize AMS-I.D status on page load
            setTimeout(refreshAMSStatus, 2000);
            
            // Initialize Lucide icons
            lucide.createIcons();
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