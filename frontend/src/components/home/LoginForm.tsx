
'use client';

import Image from "next/image";
import { useEffect } from "react";

export default function LoginForm() {

  useEffect(() => {
    // Demo button handler
    document.getElementById('demoBtn')?.addEventListener('click', function () {
      // Auto-fill demo credentials
      (document.getElementById('email') as HTMLInputElement).value = 'demo@verifiedcc.com';
      (document.getElementById('password') as HTMLInputElement).value = 'verifiedcc';

      // Submit the form
      (document.querySelector('form[action="/auth"]') as HTMLFormElement)?.submit();
    });

    // Signup form toggle
    document.getElementById('signupBtn')?.addEventListener('click', function () {
      const signupForm = document.getElementById('signupForm');
      signupForm?.classList.remove('hidden');
      signupForm?.scrollIntoView({ behavior: 'smooth' });
    });
  }, []);

  return (
    <div className="bg-white/80 backdrop-blur-lg rounded-2xl p-8 border border-gray-200/50 shadow-2xl">
      <div className="text-center mb-6">
        <Image src="/verifiedcc-logo.png" alt="VerifiedCC Logo" width={64} height={64} className="h-16 w-auto mx-auto mb-4" />
        <h3 className="text-2xl font-bold text-deep-ocean">Become Our Partner</h3>
        <p className="text-gray-600 mt-2">Access Guardian Verifiable Credentials Portal</p>
      </div>

      <form action="/auth" method="POST" className="space-y-6">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-deep-ocean mb-2">Email Address</label>
          <input type="email" id="email" name="email" required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors bg-white/50"
            placeholder="partner@company.com" />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-deep-ocean mb-2">Password</label>
          <input type="password" id="password" name="password" required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oasis-green focus:border-transparent transition-colors bg-white/50"
            placeholder="••••••••" />
          <p className="text-xs text-gray-500 mt-1">Demo password: <code className="bg-gray-100 px-1 rounded">verifiedcc</code></p>
        </div>

        <button type="submit"
          className="w-full bg-gradient-to-r from-oasis-green to-desert-sand text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg">
          <i data-lucide="log-in" className="w-5 h-5 inline mr-2"></i>
          Access Dashboard
        </button>
      </form>

      <div className="mt-4">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white/80 text-gray-500">Or</span>
          </div>
        </div>

        <button id="demoBtn" type="button"
          className="w-full mt-4 bg-gray-500 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg">
          <i data-lucide="play-circle" className="w-5 h-5 inline mr-2"></i>
          Try Demo Account
        </button>
      </div>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          New partner?
          <button id="signupBtn" type="button" className="text-oasis-green hover:text-green-700 font-medium underline">
            Sign up for partnership
          </button>
        </p>
      </div>
    </div>
  );
}
