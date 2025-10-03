
'use client';

import { useEffect } from "react";

export default function AddCredential({ addTestCredential }: { addTestCredential: () => void }) {

  useEffect(() => {
    const testCredentialBtn = document.getElementById('testCredentialBtn');
    if (testCredentialBtn) { testCredentialBtn.addEventListener('click', addTestCredential); }
  }, [addTestCredential]);

  return (
    <div className="card-3d rounded-2xl p-6 border border-gray-200">
      <div className="flex items-center mb-6">
        <div className="bg-gradient-to-r from-desert-sand to-oasis-green text-white rounded-full h-10 w-10 flex items-center justify-center mr-3">
          <i data-lucide="plus" className="w-5 h-5"></i>
        </div>
        <h3 className="text-xl font-bold text-deep-ocean">Add New Credential</h3>
      </div>

      <div className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-6 border border-gray-200">
        <div className="flex items-start">
          <div className="bg-blue-100 text-blue-600 rounded-full h-8 w-8 flex items-center justify-center mr-3 mt-1">
            <i data-lucide="info" className="w-4 h-4"></i>
          </div>
          <div className="flex-1">
            <h5 className="font-semibold text-deep-ocean mb-2">Guardian Integration</h5>
            <p className="text-sm text-gray-700 mb-4">
              Credentials are automatically synchronized from the Guardian platform.
              New verifiable credentials will appear here once processed by the Guardian network.
            </p>
            <button id="testCredentialBtn"
              className="bg-gradient-to-r from-desert-sand to-yellow-500 text-deep-ocean font-semibold px-6 py-2 rounded-lg hover:from-yellow-500 hover:to-desert-sand transition-all duration-300 transform hover:scale-105">
              <i data-lucide="flask-conical" className="w-4 h-4 inline mr-2"></i>
              Add Test Credential
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
