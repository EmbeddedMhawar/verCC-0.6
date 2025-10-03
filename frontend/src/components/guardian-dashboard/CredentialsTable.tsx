
'use client';

import { useEffect } from "react";
import * as lucide from 'lucide';

export default function CredentialsTable({ loadDashboardData }: { loadDashboardData: () => void }) {

  useEffect(() => {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) { refreshBtn.addEventListener('click', loadDashboardData); }
  }, [loadDashboardData]);

  return (
    <div className="card-3d rounded-2xl p-6 border border-gray-200 mb-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="bg-deep-ocean text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
            <i data-lucide="database" className="w-5 h-5"></i>
          </div>
          <h3 className="text-xl font-bold text-deep-ocean">Recent Credentials</h3>
        </div>
        <button id="refreshBtn" className="bg-oasis-green text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
          <i data-lucide="refresh-cw" className="w-4 h-4 inline mr-2"></i>
          Refresh
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-deep-ocean">Organization</th>
              <th className="text-left py-3 px-4 font-semibold text-deep-ocean">Project Type</th>
              <th className="text-left py-3 px-4 font-semibold text-deep-ocean">Country</th>
              <th className="text-left py-3 px-4 font-semibold text-deep-ocean">Emissions (tCO2)</th>
              <th className="text-left py-3 px-4 font-semibold text-deep-ocean">Date</th>
              <th className="text-left py-3 px-4 font-semibold text-deep-ocean">Status</th>
            </tr>
          </thead>
          <tbody id="credentialsTable">
            <tr>
              <td colSpan={6} className="text-center py-8 text-gray-500">
                <i data-lucide="loader" className="w-6 h-6 animate-spin mx-auto mb-2"></i>
                Loading credentials...
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
