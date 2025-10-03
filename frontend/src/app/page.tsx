'use client';

import { useEffect } from 'react';
import InteractiveElement from '../components/home/InteractiveElement';
import GradientBackground from '../components/home/GradientBackground';
import LoginForm from '../components/home/LoginForm';
import SignupForm from '../components/home/SignupForm';

export default function Home() {
  useEffect(() => {
    // Lucide Icons
    const lucide = require('lucide');
    lucide.createIcons();

    // Check for URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    const success = urlParams.get('success');

    // Handle error messages
    if (error === 'invalid') {
      alert('Invalid credentials. Please use password: verifiedcc');
    } else if (error === 'auth_required') {
      alert('Please sign in to access the dashboard.');
    } else if (error === 'email_exists') {
      alert('Email already registered. Please use a different email address.');
    } else if (error === 'signup_failed') {
      alert('Signup failed. Please try again.');
    } else if (error === 'db_unavailable') {
      alert('Database unavailable. Please try again later.');
    }

    // Handle success messages
    if (success === 'signup') {
      alert('Partnership application submitted successfully! We will contact you soon.');
    }
  }, []);

  return (
    <main>
      <InteractiveElement />
      <GradientBackground />
      <div className="max-w-md mx-auto">
        <LoginForm />
        <SignupForm />
      </div>
    </main>
  );
}