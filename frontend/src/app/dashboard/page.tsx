
'use client';

import { useEffect, useRef, useState } from 'react';
import * as lucide from 'lucide';
import Header from '../components/dashboard/Header';
import CarbonCredits from '../components/dashboard/CarbonCredits';
import SystemTestingControls from '../components/dashboard/SystemTestingControls';
import DeviceCard from '../components/dashboard/DeviceCard';
import PowerChart from '../components/dashboard/PowerChart';
import EnergyChart from '../components/dashboard/EnergyChart';
import EnvironmentChart from '../components/dashboard/EnvironmentChart';
import Notifications from '../components/dashboard/Notifications';

export default function Dashboard() {
  const ws = useRef<WebSocket | null>(null);
  const [devices, setDevices] = useState<string[]>([]);
  const latestReadings = useRef<{ [key: string]: any }>({});

  const updateDeviceMetrics = (reading: any) => {
    const deviceId = reading.device_id;
    (document.getElementById(`${deviceId}-power`) as HTMLElement).textContent = `${reading.power.toFixed(1)} W`;
    (document.getElementById(`${deviceId}-current`) as HTMLElement).textContent = `${reading.current.toFixed(3)} A`;
    (document.getElementById(`${deviceId}-energy`) as HTMLElement).textContent = `${reading.total_energy_kwh.toFixed(4)} kWh`;
    (document.getElementById(`${deviceId}-efficiency`) as HTMLElement).textContent = `${(reading.efficiency * 100).toFixed(1)}%`;
    (document.getElementById(`${deviceId}-temp`) as HTMLElement).textContent = `${reading.ambient_temp_c.toFixed(1)}°C`;
    (document.getElementById(`${deviceId}-irradiance`) as HTMLElement).textContent = `${reading.irradiance_w_m2.toFixed(0)} W/m²`;
    (document.getElementById(`${deviceId}-voltage`) as HTMLElement).textContent = `${reading.voltage.toFixed(0)} V`;
    (document.getElementById(`${deviceId}-pf`) as HTMLElement).textContent = `${reading.power_factor.toFixed(3)}`;
  };

  const updateCharts = (reading: any) => {
    const time = new Date(reading.timestamp).toLocaleTimeString();

    // @ts-ignore
    const powerChart = window.powerChart;
    if (powerChart) {
      powerChart.data.labels.push(time);
      powerChart.data.datasets[0].data.push(reading.power);
      if (powerChart.data.labels.length > 20) {
        powerChart.data.labels.shift();
        powerChart.data.datasets[0].data.shift();
      }
      powerChart.update('none');
    }

    // @ts-ignore
    const energyChart = window.energyChart;
    if (energyChart) {
      energyChart.data.labels.push(time);
      energyChart.data.datasets[0].data.push(reading.total_energy_kwh);
      if (energyChart.data.labels.length > 20) {
        energyChart.data.labels.shift();
        energyChart.data.datasets[0].data.shift();
      }
      energyChart.update('none');
    }

    // @ts-ignore
    const environmentChart = window.environmentChart;
    if (environmentChart) {
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
  };

  const updateCarbonCredits = (reading: any) => {
    const morocco_ef = 0.81;
    const export_mwh = reading.total_energy_kwh / 1000.0 * 0.98;
    const carbon_credits = export_mwh * morocco_ef;
    const totalCreditsElement = document.getElementById('totalCredits');
    if (totalCreditsElement) totalCreditsElement.textContent = carbon_credits.toFixed(6);
  };

  const updateRealDeviceStatus = () => {
    const realDevices = Object.keys(latestReadings.current).filter(deviceId => !deviceId.includes('MOCK'));
    const realDevicesCount = document.getElementById('realDevicesCount');
    const realDevicesDot = document.getElementById('realDevicesDot');
    const lastDataTime = document.getElementById('lastDataTime');
    if (realDevicesCount) realDevicesCount.textContent = realDevices.length.toString();
    if (realDevices.length > 0) {
      if (realDevicesDot) realDevicesDot.className = 'w-2 h-2 rounded-full bg-green-400 mr-2 animate-pulse';
      let mostRecentTime: Date | null = null;
      realDevices.forEach(deviceId => {
        const reading = latestReadings.current[deviceId];
        const readingTime = new Date(reading.timestamp);
        if (!mostRecentTime || readingTime > mostRecentTime) { mostRecentTime = readingTime; }
      });
      if (mostRecentTime && lastDataTime) { lastDataTime.textContent = mostRecentTime.toLocaleTimeString(); }
    } else {
      if (realDevicesDot) realDevicesDot.className = 'w-2 h-2 rounded-full bg-gray-400 mr-2';
      if (lastDataTime) lastDataTime.textContent = 'Never';
    }
  };

  const updateDashboard = (reading: any) => {
    if (!devices.includes(reading.device_id)) {
      setDevices(prevDevices => [...prevDevices, reading.device_id]);
      if (!reading.device_id.includes('MOCK')) { 
        // @ts-ignore
        window.showNotification(`New ESP32 device connected: ${reading.device_id}`, 'success'); 
      }
    }
    updateDeviceMetrics(reading);
    updateCarbonCredits(reading);
    const lastUpdateElement = document.getElementById('lastUpdate');
    if (lastUpdateElement) lastUpdateElement.textContent = new Date(reading.timestamp).toLocaleString();
    latestReadings.current[reading.device_id] = reading;
    updateRealDeviceStatus();
  };

  useEffect(() => {
    lucide.createIcons();

    ws.current = new WebSocket(`ws://${window.location.host}/ws`);

    ws.current.onopen = () => {
      const statusText = document.getElementById('statusText');
      const statusDot = document.getElementById('statusDot');
      const connectionStatus = document.getElementById('connectionStatus');
      if (statusText) statusText.textContent = 'Connected';
      if (statusDot) statusDot.className = 'w-2 h-2 rounded-full mr-2 bg-oasis-green animate-pulse';
      if (connectionStatus) connectionStatus.className = 'status-indicator online inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-green-100 text-oasis-green';
    };

    ws.current.onclose = () => {
      const statusText = document.getElementById('statusText');
      const statusDot = document.getElementById('statusDot');
      const connectionStatus = document.getElementById('connectionStatus');
      if (statusText) statusText.textContent = 'Disconnected';
      if (statusDot) statusDot.className = 'w-2 h-2 rounded-full mr-2 bg-red-500';
      if (connectionStatus) connectionStatus.className = 'status-indicator offline inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-red-100 text-red-600';
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'energy_reading') {
        updateDashboard(message.data);
        updateCharts(message.data);
      } else if (message.type === 'latest_readings') {
        Object.values(message.data).forEach((reading: any) => {
          updateDashboard(reading);
        });
      }
    };

    fetch('/api/latest-readings')
      .then(response => response.json())
      .then(data => {
        latestReadings.current = data;
        Object.values(data).forEach((reading: any) => {
          updateDashboard(reading);
        });
      })
      .catch(error => console.error('Error fetching initial data:', error));

    return () => {
      ws.current?.close();
    };
  }, []);

  return (
    <>
      <Notifications />
      <Header />

      <main className="relative z-10">
        <div className="container mx-auto px-6 py-8">
          <CarbonCredits />
          <SystemTestingControls />

          <div id="devicesContainer" className="space-y-4 mb-6">
            {devices.map(deviceId => (
              <DeviceCard key={deviceId} deviceId={deviceId} />
            ))}
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
            <PowerChart />
            <EnergyChart />
          </div>

          <EnvironmentChart />

          <div className="text-center text-gray-500 text-sm">
            <p>Last updated: <span id="lastUpdate" className="font-medium">Never</span></p>
            <p className="mt-2">Powered by VerifiedCC - Automating Carbon Credits with AI and Hedera</p>
          </div>
        </div>
      </main>
    </>
  );
}
