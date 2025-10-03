
'use client';

import { useEffect } from "react";

export default function SystemTestingControls() {

  const sendMockData = async () => {
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
    } catch (error: any) {
      showNotification('Connection error: ' + error.message, 'error');
    }
  };

  const startMockStream = async () => {
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
    } catch (error: any) {
      showNotification('Connection error: ' + error.message, 'error');
    }
  };

  const stopMockStream = async () => {
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
    } catch (error: any) {
      showNotification('Connection error: ' + error.message, 'error');
    }
  };

  const checkMockStatus = async () => {
    try {
      const response = await fetch('/api/test/mock-status');
      const result = await response.json();
      updateStreamStatus(result.mock_active);
    } catch (error) {
      console.error('Error checking mock status:', error);
    }
  };

  const updateStreamStatus = (isActive: boolean) => {
    const statusElement = document.getElementById('streamStatus');
    const statusDot = document.getElementById('streamStatusDot');
    const startBtn = document.getElementById('startStreamBtn') as HTMLButtonElement | null;
    const stopBtn = document.getElementById('stopStreamBtn') as HTMLButtonElement | null;
    if (isActive) {
      if (statusElement) { statusElement.textContent = 'Active'; statusElement.className = 'text-sm font-bold text-green-300'; }
      if (statusDot) statusDot.className = 'w-2 h-2 rounded-full bg-green-400 mr-2 animate-pulse';
      if (startBtn) { startBtn.disabled = true; startBtn.className = 'w-full bg-gray-400 text-gray-600 font-semibold px-4 py-2 rounded-lg cursor-not-allowed flex items-center justify-center opacity-50'; }
      if (stopBtn) { stopBtn.disabled = false; stopBtn.className = 'w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-500 text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center'; }
    } else {
      if (statusElement) { statusElement.textContent = 'Stopped'; statusElement.className = 'text-sm font-bold text-gray-300'; }
      if (statusDot) statusDot.className = 'w-2 h-2 rounded-full bg-gray-400 mr-2';
      if (startBtn) { startBtn.disabled = false; startBtn.className = 'w-full bg-gradient-to-r from-oasis-green to-green-600 hover:from-green-600 hover:to-oasis-green text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center'; }
      if (stopBtn) { stopBtn.disabled = true; stopBtn.className = 'w-full bg-gray-400 text-gray-600 font-semibold px-4 py-2 rounded-lg cursor-not-allowed flex items-center justify-center opacity-50'; }
    }
  };

  const showNotification = (message: string, type = 'info') => {
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-6 z-50 p-4 rounded-2xl shadow-2xl max-w-sm transition-all duration-500 transform translate-x-full`;
    const styles: { [key: string]: string } = {
      success: 'bg-gradient-to-r from-oasis-green to-green-600 text-white border border-green-300',
      error: 'bg-gradient-to-r from-red-500 to-red-600 text-white border border-red-300',
      warning: 'bg-gradient-to-r from-desert-sand to-yellow-500 text-deep-ocean border border-yellow-300',
      info: 'bg-gradient-to-r from-deep-ocean to-blue-600 text-white border border-blue-300'
    };
    const icons: { [key: string]: string } = {
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
    const lucide = require('lucide');
    lucide.createIcons();
    setTimeout(() => {
      notification.classList.remove('translate-x-full');
      notification.classList.add('animate-bounce');
      setTimeout(() => { notification.classList.remove('animate-bounce'); }, 600);
    }, 100);
    setTimeout(() => {
      notification.classList.add('translate-x-full', 'opacity-0');
      setTimeout(() => { if (notification.parentElement) { notification.remove(); } }, 500);
    }, 4000);
  };

  useEffect(() => {
    const sendMockBtn = document.getElementById('sendMockBtn');
    const startStreamBtn = document.getElementById('startStreamBtn');
    const stopStreamBtn = document.getElementById('stopStreamBtn');

    if (sendMockBtn) { sendMockBtn.addEventListener('click', sendMockData); }
    if (startStreamBtn) { startStreamBtn.addEventListener('click', startMockStream); }
    if (stopStreamBtn) { stopStreamBtn.addEventListener('click', stopMockStream); }

    checkMockStatus();
    const intervalId = setInterval(checkMockStatus, 10000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  return (
    <div className="card-3d rounded-2xl p-8 border border-gray-200 mb-8 animate-fade-in">
      <div className="flex items-center mb-6">
        <div className="bg-gradient-to-r from-deep-ocean to-oasis-green text-white rounded-full h-12 w-12 flex items-center justify-center mr-4">
          <i data-lucide="flask-conical" className="w-6 h-6"></i>
        </div>
        <div>
          <h3 className="text-2xl font-bold text-deep-ocean">System Testing Controls</h3>
          <p className="text-gray-600">Mock data generation and real-time testing</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg">
          <div className="flex items-center mb-4">
            <div className="bg-desert-sand text-deep-ocean rounded-full h-10 w-10 flex items-center justify-center mr-3">
              <i data-lucide="zap" className="w-5 h-5"></i>
            </div>
            <div>
              <h4 className="font-bold text-deep-ocean">Single Test</h4>
              <p className="text-sm text-gray-600">Send one data point</p>
            </div>
          </div>
          <button id="sendMockBtn" className="w-full bg-gradient-to-r from-desert-sand to-yellow-500 hover:from-yellow-500 hover:to-desert-sand text-deep-ocean font-semibold px-4 py-3 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center">
            <i data-lucide="send" className="w-4 h-4 mr-2"></i>
            Send Mock Data
          </button>
        </div>

        <div className="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-cloud-white to-gray-50 shadow-lg">
          <div className="flex items-center mb-4">
            <div className="bg-oasis-green text-cloud-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
              <i data-lucide="radio" className="w-5 h-5"></i>
            </div>
            <div>
              <h4 className="font-bold text-deep-ocean">Live Stream</h4>
              <p className="text-sm text-gray-600">Continuous data flow</p>
            </div>
          </div>
          <div className="space-y-3">
            <button id="startStreamBtn" className="w-full bg-gradient-to-r from-oasis-green to-green-600 hover:from-green-600 hover:to-oasis-green text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center">
              <i data-lucide="play" className="w-4 h-4 mr-2"></i>
              Start Stream
            </button>
            <button id="stopStreamBtn" className="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-500 text-white font-semibold px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center">
              <i data-lucide="stop-circle" className="w-4 h-4 mr-2"></i>
              Stop Stream
            </button>
          </div>
        </div>

        <div className="rounded-xl p-6 border border-gray-200 bg-gradient-to-br from-deep-ocean to-blue-900 shadow-lg text-white">
          <div className="flex items-center mb-4">
            <div className="bg-white/20 rounded-full h-10 w-10 flex items-center justify-center mr-3">
              <i data-lucide="activity" className="w-5 h-5"></i>
            </div>
            <div>
              <h4 className="font-bold">System Status</h4>
              <p className="text-sm opacity-90">Real-time monitoring</p>
            </div>
          </div>
          <div className="space-y-3">
            <div className="bg-white/10 rounded-lg p-3 border border-white/20">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium opacity-90">Mock Stream</span>
                <div className="flex items-center">
                  <div id="streamStatusDot" className="w-2 h-2 rounded-full bg-gray-400 mr-2"></div>
                  <span id="streamStatus" className="text-sm font-bold">Stopped</span>
                </div>
              </div>
            </div>
            <div className="bg-white/10 rounded-lg p-3 border border-gray-200">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium opacity-90">ESP32 Devices</span>
                <div className="flex items-center">
                  <div id="realDevicesDot" className="w-2 h-2 rounded-full bg-gray-400 mr-2"></div>
                  <span id="realDevicesCount" className="text-sm font-bold">0</span>
                </div>
              </div>
            </div>
            <div className="bg-white/10 rounded-lg p-3 border border-gray-200">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium opacity-90">Last Data</span>
                <span id="lastDataTime" className="text-xs font-medium opacity-75">Never</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-6 border border-gray-200">
        <div className="flex items-start">
          <div className="bg-blue-100 text-blue-600 rounded-full h-8 w-8 flex items-center justify-center mr-3 mt-1">
            <i data-lucide="info" className="w-4 h-4"></i>
          </div>
          <div className="flex-1">
            <h5 className="font-semibold text-deep-ocean mb-2">Testing Instructions</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
              <div>
                <p className="font-medium text-desert-sand mb-1">🧪 Single Test:</p>
                <p>Sends one realistic data point to test dashboard functionality and data flow.</p>
              </div>
              <div>
                <p className="font-medium text-oasis-green mb-1">📡 Live Stream:</p>
                <p>Generates continuous mock data every 1 second with realistic solar patterns.</p>
              </div>
              <div>
                <p className="font-medium text-deep-ocean mb-1">🌞 Solar Simulation:</p>
                <p>Mock data follows daily solar cycles (6 AM - 6 PM peak generation).</p>
              </div>
              <div>
                <p className="font-medium text-purple-600 mb-1">🔄 Real-time Updates:</p>
                <p>All test data appears instantly in charts, device cards, and database.</p>
              </div>
              <div>
                <p className="font-medium text-blue-600 mb-1">🔌 Real ESP32 Data:</p>
                <p>Send POST requests to <code className="bg-white px-1 rounded text-xs">/api/energy-data</code> from your ESP32.</p>
              </div>
              <div>
                <p className="font-medium text-green-600 mb-1">📡 Endpoint Ready:</p>
                <p>Your ESP32 can send data to <code className="bg-white px-1 rounded text-xs">http://YOUR_IP:5000/api/energy-data</code></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
