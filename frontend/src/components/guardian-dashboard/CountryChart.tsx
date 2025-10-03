
'use client';

import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export default function CountryChart() {
  const countryChartRef = useRef<any>(null);

  useEffect(() => {
    const countryCtx = (document.getElementById('countryChart') as HTMLCanvasElement)?.getContext('2d');

    if (countryCtx) {
      countryChartRef.current = new Chart(countryCtx, {
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
              ticks: {
                color: '#003F5C',
                font: { family: 'Inter' }
              }
            },
            x: {
              grid: { color: 'rgba(0, 63, 92, 0.1)' },
              ticks: {
                color: '#003F5C',
                font: { family: 'Inter' }
              }
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
      // @ts-ignore
      window.countryChart = countryChartRef.current;
    }

    return () => {
      countryChartRef.current?.destroy();
    };
  }, []);

  return (
    <div className="card-3d rounded-2xl p-6 border border-gray-200">
      <div className="flex items-center mb-4">
        <div className="bg-oasis-green text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
          <i data-lucide="map" className="w-5 h-5"></i>
        </div>
        <h3 className="text-xl font-bold text-deep-ocean">Emissions by Country</h3>
      </div>
      <div className="relative h-80">
        <canvas id="countryChart"></canvas>
      </div>
    </div>
  );
}
