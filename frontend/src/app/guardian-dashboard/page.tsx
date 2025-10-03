
'use client';

import { useEffect } from 'react';
import * as lucide from 'lucide';
import Header from '../components/guardian-dashboard/Header';
import StatCards from '../components/guardian-dashboard/StatCards';
import ProjectTypeChart from '../components/guardian-dashboard/ProjectTypeChart';
import CountryChart from '../components/guardian-dashboard/CountryChart';
import CredentialsTable from '../components/guardian-dashboard/CredentialsTable';
import AddCredential from '../components/guardian-dashboard/AddCredential';

export default function GuardianDashboard() {

  const updateCredentialsTable = (credentials: any[]) => {
    const tbody = document.getElementById('credentialsTable');
    if (!tbody) return;

    if (credentials.length === 0) {
      tbody.innerHTML = `
        <tr>
            <td colSpan={6} className="text-center py-8 text-gray-500">
                <i data-lucide="database" className="w-6 h-6 mx-auto mb-2"></i>
                No credentials found. Add your first credential to get started.
            </td>
        </tr>
      `;
    } else {
      tbody.innerHTML = credentials.map(credential => `
        <tr className="border-b border-gray-100 hover:bg-gray-50">
            <td className="py-3 px-4">
                <div className="font-medium text-deep-ocean">${credential.organization_name || 'Unknown'}</div>
            </td>
            <td className="py-3 px-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-oasis-green/10 text-oasis-green">
                    ${credential.project_type || 'Unknown'}
                </span>
            </td>
            <td className="py-3 px-4 text-gray-600">${credential.country || 'Unknown'}</td>
            <td className="py-3 px-4 font-medium text-deep-ocean">${(credential.emission_reductions || 0).toLocaleString()}</td>
            <td className="py-3 px-4 text-gray-600">${new Date(credential.created_at).toLocaleDateString()}</td>
            <td className="py-3 px-4">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-400 mr-1"></div>
                    Verified
                </span>
            </td>
        </tr>
      `).join('');
    }
    lucide.createIcons();
  };

  const loadDashboardData = async () => {
    try {
      const summaryResponse = await fetch('/api/guardian/summary');
      const summaryData = await summaryResponse.json();
      if (summaryData.success) {
        const summary = summaryData.data;
        const totalCredentials = document.getElementById('totalCredentials');
        if (totalCredentials) totalCredentials.textContent = summary.total_projects || 0;
        const totalEmissions = document.getElementById('totalEmissions');
        if (totalEmissions) totalEmissions.textContent = (summary.total_emission_reductions || 0).toLocaleString();
        const totalProjects = document.getElementById('totalProjects');
        if (totalProjects) totalProjects.textContent = summary.total_projects || 0;
        const totalCountries = document.getElementById('totalCountries');
        if (totalCountries) totalCountries.textContent = Object.keys(summary.by_country || {}).length;

        // @ts-ignore
        const projectTypeChart = window.projectTypeChart;
        if (summary.by_project_type && projectTypeChart) {
          projectTypeChart.data.labels = Object.keys(summary.by_project_type);
          projectTypeChart.data.datasets[0].data = Object.values(summary.by_project_type);
          projectTypeChart.update();
        }
        // @ts-ignore
        const countryChart = window.countryChart;
        if (summary.by_country && countryChart) {
          countryChart.data.labels = Object.keys(summary.by_country);
          countryChart.data.datasets[0].data = Object.values(summary.by_country);
          countryChart.update();
        }
      }

      const credentialsResponse = await fetch('/api/guardian/credentials?limit=10');
      const credentialsData = await credentialsResponse.json();
      if (credentialsData.success) {
        updateCredentialsTable(credentialsData.data);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      const credentialsTable = document.getElementById('credentialsTable');
      if (credentialsTable) {
        credentialsTable.innerHTML = `
          <tr>
              <td colSpan={6} className="text-center py-8 text-red-500">
                  <i data-lucide="alert-circle" className="w-6 h-6 mx-auto mb-2"></i>
                  Error loading data. Please refresh the page.
              </td>
          </tr>
        `;
      }
      lucide.createIcons();
    }
  };

  const addTestCredential = async () => {
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
        loadDashboardData();
      } else {
        alert('Error adding test credential');
      }
    } catch (error) {
      console.error('Error adding test credential:', error);
      alert('Error adding test credential');
    }
  };

  useEffect(() => {
    lucide.createIcons();
    loadDashboardData();
  }, []);

  return (
    <>
      <Header />

      <main className="relative z-10">
        <div className="container mx-auto px-6 py-8">
          <StatCards />

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
            <ProjectTypeChart />
            <CountryChart />
          </div>

          <CredentialsTable loadDashboardData={loadDashboardData} />

          <AddCredential addTestCredential={addTestCredential} />
        </div>
      </main>
    </>
  );
}
