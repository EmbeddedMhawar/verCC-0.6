
export default function CarbonCredits() {
  return (
    <div className="bg-gradient-to-r from-oasis-green to-desert-sand rounded-2xl p-8 md:p-12 text-cloud-white text-center shadow-2xl mb-8 animate-slide-up">
      <div className="flex items-center justify-center mb-4">
        <i data-lucide="leaf" className="w-12 h-12 mr-4 animate-float"></i>
        <h2 className="text-4xl md:text-6xl font-extrabold" id="totalCredits">0.000</h2>
      </div>
      <p className="text-xl md:text-2xl font-medium opacity-90">Total Carbon Credits Generated (tCO2)</p>
      <p className="text-sm opacity-75 mt-2">Verified through VerifiedCC's AI-powered platform</p>
    </div>
  );
}
