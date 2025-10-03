
'use client';

import { useEffect } from "react";

export default function SignupForm() {

  useEffect(() => {
    document.getElementById('cancelSignupBtn')?.addEventListener('click', function () {
      const signupForm = document.getElementById('signupForm');
      signupForm?.classList.add('hidden');
      // Reset form
      (signupForm?.querySelector('form') as HTMLFormElement)?.reset();
    });
  }, []);

  return (
    <div id="signupForm" className="hidden mt-6 border-t border-gray-200 pt-6">
      <h4 className="text-lg font-bold text-deep-ocean mb-4 text-center">Partner Signup</h4>
      <form action="/signup" method="POST" className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="company_name" className="block text-sm font-medium text-deep-ocean mb-1">Company Name *</label>
            <input type="text" id="company_name" name="company_name" required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm bg-white/50" />
          </div>
          <div>
            <label htmlFor="contact_person" className="block text-sm font-medium text-deep-ocean mb-1">Contact Person *</label>
            <input type="text" id="contact_person" name="contact_person" required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm bg-white/50" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="signup_email" className="block text-sm font-medium text-deep-ocean mb-1">Email Address *</label>
            <input type="email" id="signup_email" name="email" required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm bg-white/50" />
          </div>
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-deep-ocean mb-1">Phone</label>
            <input type="tel" id="phone" name="phone"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm bg-white/50" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="country" className="block text-sm font-medium text-deep-ocean mb-1">Country</label>
            <input type="text" id="country" name="country"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm bg-white/50" />
          </div>
          <div>
            <label htmlFor="project_type" className="block text-sm font-medium text-deep-ocean mb-1">Project Type</label>
            <select id="project_type" name="project_type"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm bg-white/50">
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
          <label htmlFor="expected_emission_reductions" className="block text-sm font-medium text-deep-ocean mb-1">Expected Emission Reductions (tCO2/year)</label>
          <input type="number" id="expected_emission_reductions" name="expected_emission_reductions" step="0.01"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm bg-white/50" />
        </div>

        <div>
          <label htmlFor="project_description" className="block text-sm font-medium text-deep-ocean mb-1">Project Description</label>
          <textarea id="project_description" name="project_description" rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors text-sm bg-white/50"
            placeholder="Brief description of your renewable energy project..."></textarea>
        </div>

        <div className="flex gap-3">
          <button type="submit"
            className="flex-1 bg-oasis-green hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg text-sm">
            <i data-lucide="user-plus" className="w-4 h-4 inline mr-2"></i>
            Submit Application
          </button>
          <button type="button" id="cancelSignupBtn"
            className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition-all duration-300 text-sm">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
