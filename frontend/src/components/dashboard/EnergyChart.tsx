
'use client';

import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export default function EnergyChart() {
  const energyChartRef = useRef<any>(null);

  useEffect(() => {
    const energyCtx = (document.getElementById('energyChart') as HTMLCanvasElement)?.getContext('2d');

    if (energyCtx) {
      energyChartRef.current = new Chart(energyCtx, {
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
    }

    return () => {
      energyChartRef.current?.destroy();
    };
  }, []);

  return (
    <div className="card-3d rounded-2xl p-6 border border-gray-200 animate-fade-in" style={{ animationDelay: '0.2s' }}>
      <div className="flex items-center mb-4">
        <div className="bg-oasis-green text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
          <i data-lucide="battery" className="w-5 h-5"></i>
        </div>
        <h3 className="text-xl font-bold text-deep-ocean">Energy Accumulation</h3>
      </div>
      <div className="relative h-80">
        <canvas id="energyChart"></canvas>
      </div>
    </div>
  );
}
