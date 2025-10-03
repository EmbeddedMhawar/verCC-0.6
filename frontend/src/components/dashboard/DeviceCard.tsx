
'use client';

import { useEffect } from 'react';
import * as lucide from 'lucide';

export default function DeviceCard({ deviceId }: { deviceId: string }) {

  useEffect(() => {
    lucide.createIcons();
  }, []);

  return (
    <div className="card-3d rounded-xl p-4 border border-gray-200 animate-fade-in bg-white" id={`device-${deviceId}`}>
      <div className="flex items-center mb-4">
        <div className="bg-desert-sand text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
          <i data-lucide="cpu" className="w-5 h-5"></i>
        </div>
        <div>
          <h3 className="text-xl font-bold text-deep-ocean">Device: {deviceId}</h3>
          <p className="text-gray-600 text-sm">ESP32 Solar Monitor</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-gray-600 text-sm font-medium">Power</span>
            <i data-lucide="zap" className="w-4 h-4 text-desert-sand"></i>
          </div>
          <span className="text-lg font-bold text-deep-ocean" id={`${deviceId}-power`}>0 W</span>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-gray-600 text-sm font-medium">Current</span>
            <i data-lucide="activity" className="w-4 h-4 text-oasis-green"></i>
          </div>
          <span className="text-lg font-bold text-deep-ocean" id={`${deviceId}-current`}>0 A</span>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-gray-600 text-sm font-medium">Energy</span>
            <i data-lucide="battery" className="w-4 h-4 text-desert-sand"></i>
          </div>
          <span className="text-lg font-bold text-deep-ocean" id={`${deviceId}-energy`}>0 kWh</span>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-gray-600 text-sm font-medium">Efficiency</span>
            <i data-lucide="trending-up" className="w-4 h-4 text-oasis-green"></i>
          </div>
          <span className="text-lg font-bold text-deep-ocean" id={`${deviceId}-efficiency`}>0%</span>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-gray-600 text-sm font-medium">Temperature</span>
            <i data-lucide="thermometer" className="w-4 h-4 text-red-500"></i>
          </div>
          <span className="text-lg font-bold text-deep-ocean" id={`${deviceId}-temp`}>0°C</span>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-gray-600 text-sm font-medium">Irradiance</span>
            <i data-lucide="sun" className="w-4 h-4 text-yellow-500"></i>
          </div>
          <span className="text-lg font-bold text-deep-ocean" id={`${deviceId}-irradiance`}>0 W/m²</span>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-gray-600 text-sm font-medium">Voltage</span>
            <i data-lucide="plug" className="w-4 h-4 text-blue-500"></i>
          </div>
          <span className="text-lg font-bold text-deep-ocean" id={`${deviceId}-voltage`}>0 V</span>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-gray-600 text-sm font-medium">Power Factor</span>
            <i data-lucide="gauge" className="w-4 h-4 text-purple-500"></i>
          </div>
          <span className="text-lg font-bold text-deep-ocean" id={`${deviceId}-pf`}>0</span>
        </div>
      </div>
    </div>
  );
}
