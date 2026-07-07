// src/pages/DashboardPage.jsx
import React, { useState } from 'react';
import CameraUpload from '../features/diagnostics/components/CameraUpload';
import { useGeoLocation } from '../hooks/useGeoLocation';

export default function DashboardPage() {
  const [isScanning, setIsScanning] = useState(false);
  const { location } = useGeoLocation();

  const handleCaptureImage = async (blob) => {
    const formData = new FormData();
    formData.append('image', blob);
    formData.append('crop_category_id', '1');
    formData.append('latitude', location.latitude?.toString() || '0');
    formData.append('longitude', location.longitude?.toString() || '0');

    console.log("[*] Dispatching analysis payload to FastAPI backend...");
    // Fetch API logic triggers here...
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 space-y-6">
      {/* Dashboard Top Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">AgroVision AI</h1>
          <p className="text-sm text-slate-400">Integrated crop diagnostics workspace</p>
        </div>
        <div className="flex items-center space-x-2 bg-slate-800 px-3 py-1 rounded-full text-xs border border-slate-700">
          <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" />
          <span className="text-slate-300 font-medium">GPS Linked</span>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-surface p-6 rounded-2xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Total Scans</span>
          <h2 className="text-3xl font-extrabold mt-2">142</h2>
        </div>
        <div className="glass-surface p-6 rounded-2xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Offline Logs</span>
          <h2 className="text-3xl font-extrabold mt-2 text-amber-400">3 Pending</h2>
        </div>
        <div className="glass-surface p-6 rounded-2xl border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Active Health Score</span>
          <h2 className="text-3xl font-extrabold mt-2 text-emerald-400">94.5%</h2>
        </div>
      </div>

      {/* Main scanning launcher area */}
      <div className="glass-surface p-8 rounded-2xl border border-slate-800 text-center space-y-4">
        <h3 className="text-xl font-bold">Perform Crop Scan</h3>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Capture high-fidelity photos of leaves to identify crop disease pathogens.
        </p>
        <CameraUpload onCapture={handleCaptureImage} />
      </div>
    </div>
  );
}
