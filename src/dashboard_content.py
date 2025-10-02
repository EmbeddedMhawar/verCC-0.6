# Guardian Landing Page HTML
guardian_landing_html = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <title>VerifiedCC - Become Our Partner</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" type="image/png" href="/static/verifiedcc-logo.png" />
    <script src="https://cdn.tailwindcss.com"></script>
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
                    },
                },
            },
        };
    </script>
    <style>
        body {
          min-height: 100vh;
          margin: 0;
          /* Create a mixed gradient background */
          background: linear-gradient(120deg, #FDB813 0%, #2E8540 100%);
          background-size: 200% 200%;
          animation: gradientFlow 8s linear infinite;
        }

         @keyframes gradientFlow {
          0% {
            background-position: 0% 50%;
          }
          100% {
            background-position: 100% 50%;
          }
        }
        body { font-family: "Inter", sans-serif; }
        
        @keyframes glow {
            from { box-shadow: 0 0 20px rgba(253, 184, 19, 0.3); }
            to { box-shadow: 0 0 40px rgba(253, 184, 19, 0.6), 0 0 60px rgba(46, 133, 64, 0.3); }
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
    </style>
    <style>
        /* GLOBAL OVERRIDE: Fix button clicking issues across ALL pages */
        .card-3d,
        .card-3d:hover,
        .card-3d:focus,
        .card-3d:active {
            transform-style: initial !important;
            perspective: none !important;
        }
        
        .card-3d {
            position: relative !important;
            transition: all 0.3s ease !important;
            background: #ffffff !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        }
        
        .card-3d:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
        }
        
        /* Ensure all interactive elements are clickable */
        .card-3d button,
        .card-3d a,
        .card-3d input,
        .card-3d select,
        .card-3d textarea {
            pointer-events: auto !important;
            position: relative;
            z-index: 10;
        }
        
        .card-3d form {
            position: relative;
            z-index: 5;
        }
        
        /* COMPREHENSIVE BUTTON FIX for all pages */
        button,
        input[type="submit"],
        input[type="button"],
        a.button,
        .btn {
            pointer-events: auto !important;
            cursor: pointer !important;
            position: relative !important;
            z-index: 999 !important;
        }
        
        button:hover,
        input[type="submit"]:hover,
        input[type="button"]:hover,
        a.button:hover,
        .btn:hover {
            cursor: pointer !important;
        }
        
        /* Specific fixes for problematic buttons */
        #demoBtn,
        #testCredentialBtn,
        #refreshBtn,
        #sendMockBtn,
        #startStreamBtn,
        #stopStreamBtn,
        button[type="submit"] {
            pointer-events: auto !important;
            cursor: pointer !important;
            z-index: 1000 !important;
        }
    </style>
</head>
<body class="bg-gray-50 text-deep-ocean min-h-screen">
    <main class="relative z-10">
        <div class="container mx-auto px-6 py-8">


            <!-- Authentication Section -->
            <div class="max-w-md mx-auto mt-20">
                <div class="card-3d rounded-2xl p-8 border border-gray-200">
                    <div class="text-center mb-6">
                        <img src="/static/verifiedcc-logo.png" alt="VerifiedCC Logo" class="h-16 w-auto mx-auto mb-4">
                        <h3 class="text-2xl font-bold text-deep-ocean">Become Our Partner</h3>
                        <p class="text-gray-600 mt-2">Access Guardian Verifiable Credentials Portal</p>
                    </div>

                    <form action="/auth" method="POST" class="space-y-6">
                        <div>
                            <label for="email" class="block text-sm font-medium text-deep-ocean mb-2">Email Address</label>
                            <input type="email" id="email" name="email" required
                                   class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors"
                                   placeholder="partner@company.com">
                        </div>

                        <div>
                            <label for="password" class="block text-sm font-medium text-deep-ocean mb-2">Password</label>
                            <input type="password" id="password" name="password" required
                                   class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors"
                                   placeholder="••••••••">
                            <p class="text-xs text-gray-500 mt-1">Demo password: <code class="bg-gray-100 px-1 rounded">verifiedcc</code></p>
                        </div>

                        <button type="submit" 
                                class="w-full bg-gradient-to-r from-oasis-green to-desert-sand text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg">
                            <i data-lucide="log-in" class="w-5 h-5 inline mr-2"></i>
                            Access Dashboard
                        </button>
                    </form>

                    <div class="mt-4">
                        <div class="relative">
                            <div class="absolute inset-0 flex items-center">
                                <div class="w-full border-t border-gray-300"></div>
                            </div>
                            <div class="relative flex justify-center text-sm">
                                <span class="px-2 bg-white text-gray-500">Or</span>
                            </div>
                        </div>
                        
                        <button id="demoBtn" type="button" 
                                class="w-full mt-4 bg-gray-500 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg">
                            <i data-lucide="play-circle" class="w-5 h-5 inline mr-2"></i>
                            Try Demo Account
                        </button>
                    </div>

                    <div class="mt-6 text-center">
                        <p class="text-sm text-gray-600">
                            New partner? 
                            <button id="signupBtn" type="button" class="text-oasis-green hover:text-green-700 font-medium underline">
                                Sign up for partnership
                            </button>
                        </p>
                    </div>

                    <!-- Signup Form (initially hidden) -->
                    <div id="signupForm" class="hidden mt-6 border-t border-gray-200 pt-6">
                        <h4 class="text-lg font-bold text-deep-ocean mb-4 text-center">Partner Signup</h4>
                        <form action="/signup" method="POST" class="space-y-4">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label for="company_name" class="block text-sm font-medium text-deep-ocean mb-1">Company Name *</label>
                                    <input type="text" id="company_name" name="company_name" required
                                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm">
                                </div>
                                <div>
                                    <label for="contact_person" class="block text-sm font-medium text-deep-ocean mb-1">Contact Person *</label>
                                    <input type="text" id="contact_person" name="contact_person" required
                                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm">
                                </div>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label for="signup_email" class="block text-sm font-medium text-deep-ocean mb-1">Email Address *</label>
                                    <input type="email" id="signup_email" name="email" required
                                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm">
                                </div>
                                <div>
                                    <label for="phone" class="block text-sm font-medium text-deep-ocean mb-1">Phone</label>
                                    <input type="tel" id="phone" name="phone"
                                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm">
                                </div>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label for="country" class="block text-sm font-medium text-deep-ocean mb-1">Country</label>
                                    <input type="text" id="country" name="country"
                                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm">
                                </div>
                                <div>
                                    <label for="project_type" class="block text-sm font-medium text-deep-ocean mb-1">Project Type</label>
                                    <select id="project_type" name="project_type"
                                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm">
                                        <option value="">Select type</option>
                                        <option value="Solar">Solar</option>
                                        <option value="Wind">Wind</option>
                                        <option value="Hydro">Hydro</option>
                                        <option value="Biomass">Biomass</option>
                                        <option value="Geothermal">Geothermal</option>
                                        <option value="Other">Other</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div>
                                <label for="expected_emission_reductions" class="block text-sm font-medium text-deep-ocean mb-1">Expected Emission Reductions (tCO2/year)</label>
                                <input type="number" id="expected_emission_reductions" name="expected_emission_reductions" step="0.01"
                                       class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm">
                            </div>
                            
                            <div>
                                <label for="project_description" class="block text-sm font-medium text-deep-ocean mb-1">Project Description</label>
                                <textarea id="project_description" name="project_description" rows="3"
                                          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm"
                                          placeholder="Brief description of your renewable energy project..."></textarea>
                            </div>
                            
                            <div class="flex gap-3">
                                <button type="submit" 
                                        class="flex-1 bg-oasis-green hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg text-sm">
                                    <i data-lucide="user-plus" class="w-4 h-4 inline mr-2"></i>
                                    Submit Application
                                </button>
                                <button type="button" id="cancelSignupBtn"
                                        class="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition-all duration-300 text-sm">
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>


        </div>
    </main>

    <script>
        lucide.createIcons();
        
        // Check for URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const error = urlParams.get('error');
        const success = urlParams.get('success');
        
        // Handle error messages
        if (error === 'invalid') {
            alert('Invalid credentials. Please use password: verifiedcc');
        } else if (error === 'auth_required') {
            alert('Please sign in to access the dashboard.');
        } else if (error === 'email_exists') {
            alert('Email already registered. Please use a different email address.');
        } else if (error === 'signup_failed') {
            alert('Signup failed. Please try again.');
        } else if (error === 'db_unavailable') {
            alert('Database unavailable. Please try again later.');
        }
        
        // Handle success messages
        if (success === 'signup') {
            alert('Partnership application submitted successfully! We will contact you soon.');
        }

        // Demo button handler
        document.getElementById('demoBtn').addEventListener('click', function() {
            // Auto-fill demo credentials
            document.getElementById('email').value = 'demo@verifiedcc.com';
            document.getElementById('password').value = 'verifiedcc';
            
            // Submit the form
            document.querySelector('form').submit();
        });

        // Signup form toggle
        document.getElementById('signupBtn').addEventListener('click', function() {
            const signupForm = document.getElementById('signupForm');
            signupForm.classList.remove('hidden');
            signupForm.scrollIntoView({ behavior: 'smooth' });
        });

        document.getElementById('cancelSignupBtn').addEventListener('click', function() {
            const signupForm = document.getElementById('signupForm');
            signupForm.classList.add('hidden');
            // Reset form
            signupForm.querySelector('form').reset();
        });
    </script>
</body>
</html>
"""

# Guardian Dashboard HTML
guardian_dashboard_html = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <title>VerifiedCC - Guardian Dashboard</title>
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
        body { font-family: "Inter", sans-serif; }
        
        
        @keyframes glow {
            from { box-shadow: 0 0 20px rgba(253, 184, 19, 0.3); }
            to { box-shadow: 0 0 40px rgba(253, 184, 19, 0.6), 0 0 60px rgba(46, 133, 64, 0.3); }
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
                        <h1 class="text-2xl font-bold text-deep-ocean">Guardian Dashboard</h1>
                        <p class="text-sm text-gray-600">Verifiable Carbon Credit Management</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="flex items-center space-x-2 text-sm text-gray-600">
                        <div class="w-2 h-2 rounded-full bg-oasis-green animate-pulse"></div>
                        <span>Connected</span>
                    </div>
                    <a href="/" class="text-gray-600 hover:text-oasis-green transition-colors">
                        <i data-lucide="home" class="w-4 h-4 inline mr-1"></i>
                        Home
                    </a>
                    <a href="/energy" class="text-gray-600 hover:text-oasis-green transition-colors">
                        <i data-lucide="zap" class="w-4 h-4 inline mr-1"></i>
                        Energy Dashboard
                    </a>
                    <form action="/logout" method="POST" class="inline">
                        <button type="submit" class="text-gray-600 hover:text-red-600 transition-colors">
                            <i data-lucide="log-out" class="w-4 h-4 inline mr-1"></i>
                            Logout
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </header>

    <main class="relative z-10">
        <div class="container mx-auto px-6 py-8">
            <!-- Summary Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="card-3d rounded-2xl p-6 border border-gray-200 text-center">
                    <div class="bg-desert-sand text-white rounded-full h-12 w-12 mx-auto flex items-center justify-center mb-4">
                        <i data-lucide="shield-check" class="w-6 h-6"></i>
                    </div>
                    <h3 class="text-2xl font-bold text-deep-ocean" id="totalCredentials">0</h3>
                    <p class="text-gray-600">Total Credentials</p>
                </div>

                <div class="card-3d rounded-2xl p-6 border border-gray-200 text-center">
                    <div class="bg-oasis-green text-white rounded-full h-12 w-12 mx-auto flex items-center justify-center mb-4">
                        <i data-lucide="leaf" class="w-6 h-6"></i>
                    </div>
                    <h3 class="text-2xl font-bold text-deep-ocean" id="totalEmissions">0</h3>
                    <p class="text-gray-600">tCO2 Reduced</p>
                </div>

                <div class="card-3d rounded-2xl p-6 border border-gray-200 text-center">
                    <div class="bg-deep-ocean text-white rounded-full h-12 w-12 mx-auto flex items-center justify-center mb-4">
                        <i data-lucide="building" class="w-6 h-6"></i>
                    </div>
                    <h3 class="text-2xl font-bold text-deep-ocean" id="totalProjects">0</h3>
                    <p class="text-gray-600">Active Projects</p>
                </div>

                <div class="card-3d rounded-2xl p-6 border border-gray-200 text-center">
                    <div class="bg-purple-600 text-white rounded-full h-12 w-12 mx-auto flex items-center justify-center mb-4">
                        <i data-lucide="globe" class="w-6 h-6"></i>
                    </div>
                    <h3 class="text-2xl font-bold text-deep-ocean" id="totalCountries">0</h3>
                    <p class="text-gray-600">Countries</p>
                </div>
            </div>

            <!-- Charts Section -->
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
                <!-- Emissions by Project Type -->
                <div class="card-3d rounded-2xl p-6 border border-gray-200">
                    <div class="flex items-center mb-4">
                        <div class="bg-desert-sand text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                            <i data-lucide="pie-chart" class="w-5 h-5"></i>
                        </div>
                        <h3 class="text-xl font-bold text-deep-ocean">Emissions by Project Type</h3>
                    </div>
                    <div class="relative h-80">
                        <canvas id="projectTypeChart"></canvas>
                    </div>
                </div>

                <!-- Emissions by Country -->
                <div class="card-3d rounded-2xl p-6 border border-gray-200">
                    <div class="flex items-center mb-4">
                        <div class="bg-oasis-green text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                            <i data-lucide="map" class="w-5 h-5"></i>
                        </div>
                        <h3 class="text-xl font-bold text-deep-ocean">Emissions by Country</h3>
                    </div>
                    <div class="relative h-80">
                        <canvas id="countryChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Credentials Table -->
            <div class="card-3d rounded-2xl p-6 border border-gray-200 mb-8">
                <div class="flex items-center justify-between mb-6">
                    <div class="flex items-center">
                        <div class="bg-deep-ocean text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                            <i data-lucide="database" class="w-5 h-5"></i>
                        </div>
                        <h3 class="text-xl font-bold text-deep-ocean">Recent Credentials</h3>
                    </div>
                    <button id="refreshBtn" class="bg-oasis-green text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
                        <i data-lucide="refresh-cw" class="w-4 h-4 inline mr-2"></i>
                        Refresh
                    </button>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead>
                            <tr class="border-b border-gray-200">
                                <th class="text-left py-3 px-4 font-semibold text-deep-ocean">Organization</th>
                                <th class="text-left py-3 px-4 font-semibold text-deep-ocean">Project Type</th>
                                <th class="text-left py-3 px-4 font-semibold text-deep-ocean">Country</th>
                                <th class="text-left py-3 px-4 font-semibold text-deep-ocean">Emissions (tCO2)</th>
                                <th class="text-left py-3 px-4 font-semibold text-deep-ocean">Date</th>
                                <th class="text-left py-3 px-4 font-semibold text-deep-ocean">Status</th>
                            </tr>
                        </thead>
                        <tbody id="credentialsTable">
                            <tr>
                                <td colspan="6" class="text-center py-8 text-gray-500">
                                    <i data-lucide="loader" class="w-6 h-6 animate-spin mx-auto mb-2"></i>
                                    Loading credentials...
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Add New Credential -->
            <div class="card-3d rounded-2xl p-6 border border-gray-200">
                <div class="flex items-center mb-6">
                    <div class="bg-gradient-to-r from-desert-sand to-oasis-green text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
                        <i data-lucide="plus" class="w-5 h-5"></i>
                    </div>
                    <h3 class="text-xl font-bold text-deep-ocean">Add New Credential</h3>
                </div>

                <div class="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-6 border border-gray-200">
                    <div class="flex items-start">
                        <div class="bg-blue-100 text-blue-600 rounded-full h-8 w-8 flex items-center justify-center mr-3 mt-1">
                            <i data-lucide="info" class="w-4 h-4"></i>
                        </div>
                        <div class="flex-1">
                            <h5 class="font-semibold text-deep-ocean mb-2">Guardian Integration</h5>
                            <p class="text-sm text-gray-700 mb-4">
                                Credentials are automatically synchronized from the Guardian platform. 
                                New verifiable credentials will appear here once processed by the Guardian network.
                            </p>
                            <button id="testCredentialBtn" onclick="window.addTestCredential()"
                                    class="bg-gradient-to-r from-desert-sand to-yellow-500 text-deep-ocean font-semibold px-6 py-2 rounded-lg hover:from-yellow-500 hover:to-desert-sand transition-all duration-300 transform hover:scale-105">
                                <i data-lucide="flask-conical" class="w-4 h-4 inline mr-2"></i>
                                Add Test Credential
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();

        // Chart setup
        const projectTypeCtx = document.getElementById('projectTypeChart').getContext('2d');
        const countryCtx = document.getElementById('countryChart').getContext('2d');

        let projectTypeChart = new Chart(projectTypeCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: ['#FDB813', '#2E8540', '#003F5C', '#ef4444', '#8b5cf6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#003F5C',
                            font: { family: 'Inter', weight: '600' }
                        }
                    }
                }
            }
        });

        let countryChart = new Chart(countryCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Emissions Reduced (tCO2)',
                    data: [],
                    backgroundColor: '#2E8540',
                    borderColor: '#1a5928',
                    borderWidth: 1
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

        // Load data
        async function loadDashboardData() {
            try {
                // Load summary
                const summaryResponse = await fetch('/api/guardian/summary');
                const summaryData = await summaryResponse.json();
                
                if (summaryData.success) {
                    const summary = summaryData.data;
                    document.getElementById('totalCredentials').textContent = summary.total_projects || 0;
                    document.getElementById('totalEmissions').textContent = (summary.total_emission_reductions || 0).toLocaleString();
                    document.getElementById('totalProjects').textContent = summary.total_projects || 0;
                    document.getElementById('totalCountries').textContent = Object.keys(summary.by_country || {}).length;

                    // Update charts
                    if (summary.by_project_type) {
                        projectTypeChart.data.labels = Object.keys(summary.by_project_type);
                        projectTypeChart.data.datasets[0].data = Object.values(summary.by_project_type);
                        projectTypeChart.update();
                    }

                    if (summary.by_country) {
                        countryChart.data.labels = Object.keys(summary.by_country);
                        countryChart.data.datasets[0].data = Object.values(summary.by_country);
                        countryChart.update();
                    }
                }

                // Load credentials
                const credentialsResponse = await fetch('/api/guardian/credentials?limit=10');
                const credentialsData = await credentialsResponse.json();
                
                if (credentialsData.success) {
                    updateCredentialsTable(credentialsData.data);
                }

            } catch (error) {
                console.error('Error loading dashboard data:', error);
                document.getElementById('credentialsTable').innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center py-8 text-red-500">
                            <i data-lucide="alert-circle" class="w-6 h-6 mx-auto mb-2"></i>
                            Error loading data. Please refresh the page.
                        </td>
                    </tr>
                `;
                lucide.createIcons();
            }
        }

        function updateCredentialsTable(credentials) {
            const tbody = document.getElementById('credentialsTable');
            
            if (credentials.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center py-8 text-gray-500">
                            <i data-lucide="database" class="w-6 h-6 mx-auto mb-2"></i>
                            No credentials found. Add your first credential to get started.
                        </td>
                    </tr>
                `;
            } else {
                tbody.innerHTML = credentials.map(credential => `
                    <tr class="border-b border-gray-100 hover:bg-gray-50">
                        <td class="py-3 px-4">
                            <div class="font-medium text-deep-ocean">${credential.organization_name || 'Unknown'}</div>
                        </td>
                        <td class="py-3 px-4">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-oasis-green/10 text-oasis-green">
                                ${credential.project_type || 'Unknown'}
                            </span>
                        </td>
                        <td class="py-3 px-4 text-gray-600">${credential.country || 'Unknown'}</td>
                        <td class="py-3 px-4 font-medium text-deep-ocean">${(credential.emission_reductions || 0).toLocaleString()}</td>
                        <td class="py-3 px-4 text-gray-600">${new Date(credential.created_at).toLocaleDateString()}</td>
                        <td class="py-3 px-4">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                <div class="w-1.5 h-1.5 rounded-full bg-green-400 mr-1"></div>
                                Verified
                            </span>
                        </td>
                    </tr>
                `).join('');
            }
            
            lucide.createIcons();
        }

        // Event listeners
        document.getElementById('refreshBtn').addEventListener('click', loadDashboardData);

        // Fix testCredentialBtn event handler
        const testCredentialBtn = document.getElementById('testCredentialBtn');
        if (testCredentialBtn) {
            testCredentialBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/guardian/credentials', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        "id": `urn:uuid:test-${Date.now()}`,
                        "type": ["VerifiableCredential"],
                        "issuer": "did:hedera:testnet:verifiedcc-issuer",
                        "issuanceDate": new Date().toISOString(),
                        "@context": ["https://www.w3.org/2018/credentials/v1", "schema:guardian-policy-v1"],
                        "credentialSubject": [{
                            "participant_profile": {
                                "summaryDescription": "Test renewable energy project",
                                "sectoralScope": "Energy",
                                "projectType": "Solar",
                                "typeOfActivity": "Installation",
                                "projectScale": "Medium",
                                "locationLatitude": 31.7917,
                                "locationLongitude": -7.0926,
                                "organizationName": "VerifiedCC Test Company",
                                "country": "Morocco",
                                "emissionReductions": Math.floor(Math.random() * 10000) + 1000,
                                "startDate": "2025-01-01",
                                "creditingPeriods": [{"start": "2025-01-01", "end": "2027-12-31"}],
                                "monitoringPeriods": [{"start": "2025-01-01", "end": "2025-12-31"}],
                                "policyId": "test-policy-id",
                                "guardianVersion": "3.3.0-test"
                            }
                        }],
                        "proof": {
                            "type": "Ed25519Signature2018",
                            "created": new Date().toISOString(),
                            "verificationMethod": "did:hedera:testnet:verifiedcc-issuer#did-root-key",
                            "proofPurpose": "assertionMethod",
                            "jws": "test-signature"
                        }
                    })
                });

                if (response.ok) {
                    alert('Test credential added successfully!');
                    loadDashboardData();
                } else {
                    alert('Error adding test credential');
                }
            } catch (error) {
                console.error('Error adding test credential:', error);
                alert('Error adding test credential');
            }
            });
        } else {
            console.error('testCredentialBtn not found');
        }

        // Load initial data
        loadDashboardData();
    </script>
</body>
</html>
"""

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
                    <a href="/" class="text-gray-600 hover:text-oasis-green transition-colors">
                        <i data-lucide="home" class="w-4 h-4 inline mr-1"></i>
                        Home
                    </a>
                    <div class="status-indicator inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold" id="connectionStatus">
                        <div class="w-2 h-2 rounded-full mr-2" id="statusDot"></div>
                        <span id="statusText">Connecting...</span>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main class="relative z-10">
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
                        <button id="sendMockBtn" onclick="window.sendMockData()" class="w-full bg-gradient-to-r from-desert-sand to-yellow-500 hover:from-yellow-500 hover:to-desert-sand text-deep-ocean font-semibold px-4 py-3 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center">
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
                            <button id="startStreamBtn" onclick="window.startMockStream()" class="w-full bg-gradient-to-r from-oasis-green to-green-600 hover:from-green-600 hover:to-oasis-green text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center">
                                <i data-lucide="play" class="w-4 h-4 mr-2"></i>
                                Start Stream
                            </button>
                            <button id="stopStreamBtn" onclick="window.stopMockStream()" class="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-500 text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center">
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

        // Test control functions - Explicitly assign to window for global access
        window.addTestCredential = async function() {
            console.log('addTestCredential function called');
            try {
                const response = await fetch('/api/guardian/credentials', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        "id": `urn:uuid:test-${Date.now()}`,
                        "type": ["VerifiableCredential"],
                        "issuer": "did:hedera:testnet:verifiedcc-issuer",
                        "issuanceDate": new Date().toISOString(),
                        "@context": ["https://www.w3.org/2018/credentials/v1", "schema:guardian-policy-v1"],
                        "credentialSubject": [{
                            "participant_profile": {
                                "summaryDescription": "Test renewable energy project",
                                "sectoralScope": "Energy",
                                "projectType": "Solar",
                                "typeOfActivity": "Installation",
                                "projectScale": "Medium",
                                "locationLatitude": 31.7917,
                                "locationLongitude": -7.0926,
                                "organizationName": "VerifiedCC Test Company",
                                "country": "Morocco",
                                "emissionReductions": Math.floor(Math.random() * 10000) + 1000,
                                "startDate": "2025-01-01",
                                "creditingPeriods": [{"start": "2025-01-01", "end": "2027-12-31"}],
                                "monitoringPeriods": [{"start": "2025-01-01", "end": "2025-12-31"}],
                                "policyId": "test-policy-id",
                                "guardianVersion": "3.3.0-test"
                            }
                        }],
                        "proof": {
                            "type": "Ed25519Signature2018",
                            "created": new Date().toISOString(),
                            "verificationMethod": "did:hedera:testnet:verifiedcc-issuer#did-root-key",
                            "proofPurpose": "assertionMethod",
                            "jws": "test-signature"
                        }
                    })
                });

                if (response.ok) {
                    alert('Test credential added successfully!');
                    if (typeof loadDashboardData === 'function') {
                        loadDashboardData();
                    }
                } else {
                    alert('Error adding test credential');
                }
            } catch (error) {
                console.error('Error adding test credential:', error);
                alert('Error adding test credential');
            }
        }
        
        window.sendMockData = async function() {
            console.log('sendMockData function called');
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

        window.startMockStream = async function() {
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

        window.stopMockStream = async function() {
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
            
            // Set up test button event listeners with null checks
            const sendMockBtn = document.getElementById('sendMockBtn');
            const startStreamBtn = document.getElementById('startStreamBtn');
            const stopStreamBtn = document.getElementById('stopStreamBtn');
            
            if (sendMockBtn) {
                sendMockBtn.addEventListener('click', sendMockData);
                console.log('sendMockBtn event listener attached');
            } else {
                console.error('sendMockBtn not found');
            }
            
            if (startStreamBtn) {
                startStreamBtn.addEventListener('click', startMockStream);
            } else {
                console.error('startStreamBtn not found');
            }
            
            if (stopStreamBtn) {
                stopStreamBtn.addEventListener('click', stopStreamBtn);
            } else {
                console.error('stopStreamBtn not found');
            }
            
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
</html>
"""