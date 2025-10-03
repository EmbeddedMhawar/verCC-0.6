
'use client';

import { useEffect } from 'react';
import * as lucide from 'lucide';

export default function Notifications() {

  const showNotification = (message: string, type = 'info') => {
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-6 z-50 p-4 rounded-2xl shadow-2xl max-w-sm transition-all duration-500 transform translate-x-full`;
    const styles: { [key: string]: string } = {
      success: 'bg-gradient-to-r from-oasis-green to-green-600 text-white border border-green-300',
      error: 'bg-gradient-to-r from-red-500 to-red-600 text-white border border-red-300',
      warning: 'bg-gradient-to-r from-desert-sand to-yellow-500 text-deep-ocean border border-yellow-300',
      info: 'bg-gradient-to-r from-deep-ocean to-blue-600 text-white border border-blue-300'
    };
    const icons: { [key: string]: string } = {
      success: 'check-circle',
      error: 'alert-circle',
      warning: 'alert-triangle',
      info: 'info'
    };
    notification.className += ` ${styles[type] || styles.info}`;
    notification.innerHTML = `
        <div class="flex items-center">
            <div class="bg-white/20 rounded-full h-8 w-8 flex items-center justify-center mr-3">
                <i data-lucide="${icons[type] || icons.info}" class="w-4 h-4"></i>
            </div>
            <span class="flex-1 font-medium">${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-3 bg-white/20 hover:bg-white/30 rounded-full h-6 w-6 flex items-center justify-center transition-colors">
                <i data-lucide="x" class="w-3 h-3"></i>
            </button>
        </div>
    `;
    document.body.appendChild(notification);
    lucide.createIcons();
    setTimeout(() => {
      notification.classList.remove('translate-x-full');
      notification.classList.add('animate-bounce');
      setTimeout(() => { notification.classList.remove('animate-bounce'); }, 600);
    }, 100);
    setTimeout(() => {
      notification.classList.add('translate-x-full', 'opacity-0');
      setTimeout(() => { if (notification.parentElement) { notification.remove(); } }, 500);
    }, 4000);
  };

  useEffect(() => {
    // @ts-ignore
    window.showNotification = showNotification;
  }, []);

  return null;
}
