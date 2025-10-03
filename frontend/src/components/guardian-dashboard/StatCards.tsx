
export default function StatCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div className="card-3d rounded-2xl p-6 border border-gray-200 text-center">
        <div className="bg-desert-sand text-white rounded-full h-12 w-12 mx-auto flex items-center justify-center mb-4">
          <i data-lucide="shield-check" className="w-6 h-6"></i>
        </div>
        <h3 className="text-2xl font-bold text-deep-ocean" id="totalCredentials">0</h3>
        <p className="text-gray-600">Total Credentials</p>
      </div>

      <div className="card-3d rounded-2xl p-6 border border-gray-200 text-center">
        <div className="bg-oasis-green text-white rounded-full h-12 w-12 mx-auto flex items-center justify-center mb-4">
          <i data-lucide="leaf" className="w-6 h-6"></i>
        </div>
        <h3 className="text-2xl font-bold text-deep-ocean" id="totalEmissions">0</h3>
        <p className="text-gray-600">tCO2 Reduced</p>
      </div>

      <div className="card-3d rounded-2xl p-6 border border-gray-200 text-center">
        <div className="bg-deep-ocean text-white rounded-full h-12 w-12 mx-auto flex items-center justify-center mb-4">
          <i data-lucide="building" className="w-6 h-6"></i>
        </div>
        <h3 className="text-2xl font-bold text-deep-ocean" id="totalProjects">0</h3>
        <p className="text-gray-600">Active Projects</p>
      </div>

      <div className="card-3d rounded-2xl p-6 border border-gray-200 text-center">
        <div className="bg-purple-600 text-white rounded-full h-12 w-12 mx-auto flex items-center justify-center mb-4">
          <i data-lucide="globe" className="w-6 h-6"></i>
        </div>
        <h3 className="text-2xl font-bold text-deep-ocean" id="totalCountries">0</h3>
        <p className="text-gray-600">Countries</p>
      </div>
    </div>
  );
}
