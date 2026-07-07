// src/pages/ProfilePage.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const [lang, setLang] = useState('en');
  const [wifiOnly, setWifiOnly] = useState(true);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 space-y-6 max-w-lg mx-auto">
      <div className="flex items-center space-x-4">
        <div className="w-16 h-16 rounded-full bg-slate-700 flex items-center justify-center text-xl font-bold text-emerald-400 border-2 border-emerald-500">
          {user?.name?.[0] || 'F'}
        </div>
        <div>
          <h1 className="text-xl font-bold">{user?.name || 'Farmer Suresh'}</h1>
          <p className="text-sm text-slate-400">{user?.phone || '+91 9999999999'}</p>
        </div>
      </div>

      {/* Language Switcher Setting */}
      <div className="glass-surface p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-base font-semibold text-slate-200">System Preferences</h3>
        
        <div className="flex justify-between items-center">
          <label className="text-sm text-slate-300">App Language</label>
          <select 
            value={lang} 
            onChange={(e) => setLang(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="en">English (US)</option>
            <option value="kn">Kannada (ಕನ್ನಡ)</option>
            <option value="es">Español (ES)</option>
          </select>
        </div>

        {/* WiFi Sync Toggle */}
        <div className="flex justify-between items-center">
          <div>
            <label className="text-sm text-slate-300 block">Wi-Fi Only Sync</label>
            <span className="text-[10px] text-slate-400">Save cellular data on image uploads</span>
          </div>
          <input 
            type="checkbox" 
            checked={wifiOnly}
            onChange={() => setWifiOnly(!wifiOnly)}
            className="w-5 h-5 rounded accent-emerald-500"
          />
        </div>
      </div>

      {/* Cache Control */}
      <div className="glass-surface p-6 rounded-2xl border border-slate-800 space-y-3">
        <h3 className="text-base font-semibold text-slate-200">Data & Storage</h3>
        <div className="flex justify-between items-center text-sm">
          <span>Local Image Cache (45.2 MB)</span>
          <button className="text-xs font-semibold text-red-400 hover:underline">Clear Cache</button>
        </div>
      </div>

      {/* Logout Action Button */}
      <button 
        onClick={logout}
        className="w-full py-3 bg-red-600/10 hover:bg-red-600/20 active:scale-[0.99] text-red-400 font-semibold rounded-xl border border-red-500/20 transition-all text-center"
      >
        Sign Out Account
      </button>
    </div>
  );
}
