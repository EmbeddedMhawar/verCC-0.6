
import Image from "next/image";

export default function Header() {
  return (
    <header className="bg-cloud-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Image src="/verifiedcc-logo.png" alt="VerifiedCC Logo" width={48} height={48} style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))', maxWidth: '150px' }} />
            <div>
              <h1 className="text-2xl font-bold text-deep-ocean">Guardian Dashboard</h1>
              <p className="text-sm text-gray-600">Verifiable Carbon Credit Management</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <div className="w-2 h-2 rounded-full bg-oasis-green animate-pulse"></div>
              <span>Connected</span>
            </div>
            <a href="/" className="text-gray-600 hover:text-oasis-green transition-colors">
              <i data-lucide="home" className="w-4 h-4 inline mr-1"></i>
              Home
            </a>
            <a href="/energy" className="text-gray-600 hover:text-oasis-green transition-colors">
              <i data-lucide="zap" className="w-4 h-4 inline mr-1"></i>
              Energy Dashboard
            </a>
            <form action="/logout" method="POST" className="inline">
              <button type="submit" className="text-gray-600 hover:text-red-600 transition-colors">
                <i data-lucide="log-out" className="w-4 h-4 inline mr-1"></i>
                Logout
              </button>
            </form>
          </div>
        </div>
      </div>
    </header>
  );
}
