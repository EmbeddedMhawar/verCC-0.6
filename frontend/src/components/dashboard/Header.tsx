
import Image from "next/image";

export default function Header() {
  return (
    <header className="bg-cloud-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Image src="/verifiedcc-logo.png" alt="VerifiedCC Logo" width={48} height={48} style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))', maxWidth: '150px' }} />
            <div>
              <h1 className="text-2xl font-bold text-deep-ocean">VerifiedCC Dashboard</h1>
              <p className="text-sm text-gray-600">ESP32 Real-time Monitoring Dashboard</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <a href="/" className="text-gray-600 hover:text-oasis-green transition-colors">
              <i data-lucide="home" className="w-4 h-4 inline mr-1"></i>
              Home
            </a>
            <div className="status-indicator inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold" id="connectionStatus">
              <div className="w-2 h-2 rounded-full mr-2" id="statusDot"></div>
              <span id="statusText">Connecting...</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
