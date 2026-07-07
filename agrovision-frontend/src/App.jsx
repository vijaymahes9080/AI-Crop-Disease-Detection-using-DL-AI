import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import DashboardPage from './pages/DashboardPage';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import ProfilePage from './pages/ProfilePage';

function AppContent() {
  const [currentPage, setCurrentPage] = useState('dashboard'); // 'dashboard', 'analytics', 'profile'
  const { token, login } = useAuth();
  
  // Quick Mock authentication bypass for preview
  const handleMockLogin = () => {
    // Generate a simple mock JWT containing farmer role
    const mockHeader = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
    const mockPayload = btoa(JSON.stringify({ sub: "+91 9999999999", role: "farmer", name: "Farmer Suresh" }));
    const mockToken = `${mockHeader}.${mockPayload}.signature`;
    login(mockToken);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex justify-between items-center shadow-lg sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-500 flex items-center justify-center font-black text-slate-950 text-lg shadow-emerald-500/20 shadow-md">
            AV
          </div>
          <div>
            <span className="font-extrabold text-slate-50 text-lg tracking-tight block">AgroVision AI</span>
            <span className="text-[10px] font-semibold text-emerald-500 tracking-wider uppercase">Production Serving</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        {token && (
          <nav className="flex space-x-1 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${
                currentPage === 'dashboard' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('analytics')}
              className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${
                currentPage === 'analytics' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Analytics
            </button>
            <button 
              onClick={() => setCurrentPage('profile')}
              className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${
                currentPage === 'profile' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Profile
            </button>
          </nav>
        )}
      </header>

      {/* Main Container */}
      <main className="flex-grow pb-16">
        {!token ? (
          <div className="max-w-md mx-auto my-24 p-8 glass-surface rounded-2xl border border-slate-800 shadow-2xl text-center space-y-6">
            <div className="w-16 h-16 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center justify-center mx-auto text-emerald-400">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-50">Welcome to AgroVision</h2>
              <p className="text-sm text-slate-400 mt-1">Please authenticate to inspect crop scans and telemetry guides.</p>
            </div>
            <button 
              onClick={handleMockLogin}
              className="w-full py-3 bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-slate-950 font-bold rounded-xl transition-all shadow-lg"
            >
              Authenticate Account (Farmer)
            </button>
          </div>
        ) : (
          <div>
            {currentPage === 'dashboard' && <DashboardPage />}
            {currentPage === 'analytics' && <AnalyticsDashboard />}
            {currentPage === 'profile' && <ProfilePage />}
          </div>
        )}
      </main>

      {/* Persistent Status Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 text-[11px] text-slate-500 py-3 text-center px-4 flex justify-between items-center fixed bottom-0 left-0 right-0 z-40">
        <span>License: MIT (AgroVision AI Platform)</span>
        <div className="flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-semibold text-slate-400">Edge Inference Status: OK</span>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
