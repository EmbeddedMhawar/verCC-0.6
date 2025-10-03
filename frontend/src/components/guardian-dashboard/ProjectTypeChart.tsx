
'use client';

import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export default function ProjectTypeChart() {
  const projectTypeChartRef = useRef<any>(null);

  useEffect(() => {
    const projectTypeCtx = (document.getElementById('projectTypeChart') as HTMLCanvasElement)?.getContext('2d');

    if (projectTypeCtx) {
      projectTypeChartRef.current = new Chart(projectTypeCtx, {
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
      // @ts-ignore
      window.projectTypeChart = projectTypeChartRef.current;
    }

    return () => {
      projectTypeChartRef.current?.destroy();
    };
  }, []);

  return (
    <div className="card-3d rounded-2xl p-6 border border-gray-200">
      <div className="flex items-center mb-4">
        <div className="bg-desert-sand text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
          <i data-lucide="pie-chart" className="w-5 h-5"></i>
        </div>
        <h3 className="text-xl font-bold text-deep-ocean">Emissions by Project Type</h3>
      </div>
      <div className="relative h-80">
        <canvas id="projectTypeChart"></canvas>
      </div>
    </div>
  );
}
