
'use client';

import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export default function EnvironmentChart() {
  const environmentChartRef = useRef<any>(null);

  useEffect(() => {
    const environmentCtx = (document.getElementById('environmentChart') as HTMLCanvasElement)?.getContext('2d');

    if (environmentCtx) {
      environmentChartRef.current = new Chart(environmentCtx, {
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
    }

    return () => {
      environmentChartRef.current?.destroy();
    };
  }, []);

  return (
    <div className="card-3d rounded-2xl p-6 border border-gray-200 animate-fade-in mb-8" style={{ animationDelay: '0.4s' }}>
      <div className="flex items-center mb-4">
        <div className="bg-deep-ocean text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
          <i data-lucide="thermometer" className="w-5 h-5"></i>
        </div>
        <h3 className="text-xl font-bold text-deep-ocean">Environmental Conditions</h3>
      </div>
      <div className="relative h-80">
        <canvas id="environmentChart"></canvas>
      </div>
    </div>
  );
}
