# Frontend Implementation Specification (React + Tailwind)
## Project: AgroVision AI — Crop Disease Detection Platform

---

## 1. Global State Management (`context/AuthContext.jsx`)

Provides authenticated contexts, storing user identities and JWT access tokens in browser memory.

```javascript
// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      // Decode JWT token payload to extract user info (simplified)
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser({ phone: payload.sub, role: payload.role || 'farmer' });
      } catch (e) {
        logout();
      }
    } else {
      localStorage.removeItem('token');
      setUser(null);
    }
    setLoading(false);
  }, [token]);

  const login = (jwtToken) => {
    setToken(jwtToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

---

## 2. Custom Device Hooks (`hooks/`)

### 2.1 Browser GPS Geolocation Hook
Accesses device GPS coordinates with accuracy margins.

```javascript
// src/hooks/useGeoLocation.js
import { useState, useEffect } from 'react';

export function useGeoLocation() {
  const [location, setLocation] = useState({ latitude: null, longitude: null });
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser");
      return;
    }

    const success = (position) => {
      setLocation({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      });
    };

    const fail = (err) => {
      setError(`Unable to retrieve location: ${err.message}`);
    };

    navigator.geolocation.getCurrentPosition(success, fail, {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    });
  }, []);

  return { location, error };
}
```

---

### 2.2 Device Camera Handler Hook
Manages the hardware camera stream life cycles.

```javascript
// src/hooks/useCamera.js
import { useState, useEffect, useRef } from 'react';

export function useCamera() {
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1024 }, height: { ideal: 1024 } }
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      setError(`Camera access rejected: ${err.message}`);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  useEffect(() => {
    return () => stopCamera();
  }, [stream]);

  return { videoRef, startCamera, stopCamera, error };
}
```

---

## 3. Core Scan Interface Component (`components/CameraUpload.jsx`)

An interactive scanning layout utilizing alignment grids and responsive shutter actions.

```javascript
// src/features/diagnostics/components/CameraUpload.jsx
import React, { useState } from 'react';
import { useCamera } from '../../../hooks/useCamera';

export default function CameraUpload({ onCapture }) {
  const { videoRef, startCamera, stopCamera, error } = useCamera();
  const [isActive, setIsActive] = useState(false);

  const handleStart = () => {
    setIsActive(true);
    startCamera();
  };

  const handleCapture = () => {
    const video = videoRef.current;
    if (!video) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob((blob) => {
      onCapture(blob);
      stopCamera();
      setIsActive(false);
    }, 'image/jpeg', 0.95);
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 glass-surface rounded-2xl max-w-lg mx-auto border border-slate-700">
      {!isActive ? (
        <button 
          onClick={handleStart}
          className="w-24 h-24 rounded-full bg-emerald-500 hover:bg-emerald-600 active:scale-95 flex items-center justify-center transition-all duration-200 shadow-lg group"
        >
          <svg className="w-10 h-10 text-slate-950 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      ) : (
        <div className="relative w-full aspect-square rounded-xl overflow-hidden bg-slate-950 border border-slate-700 shadow-inner">
          {error && <div className="absolute inset-0 flex items-center justify-center text-red-400 p-4 text-center">{error}</div>}
          
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            className="w-full h-full object-cover"
          />

          {/* Leaf Overlay Guides */}
          <div className="absolute inset-0 border-4 border-dashed border-emerald-500/30 m-8 rounded-xl pointer-events-none flex items-center justify-center">
            <span className="text-xs font-semibold text-emerald-400/80 bg-slate-900/80 px-3 py-1 rounded-full uppercase tracking-wider">
              Align leaf inside grid
            </span>
          </div>

          {/* Capture Shutter Button */}
          <div className="absolute bottom-4 inset-x-0 flex justify-center">
            <button 
              onClick={handleCapture}
              className="w-16 h-16 rounded-full border-4 border-slate-100 bg-emerald-500 hover:bg-emerald-600 active:scale-90 transition-transform shadow-2xl"
            />
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 4. Primary UI View Pages (`pages/`)

### 4.1 Dashboard Page (`pages/DashboardPage.jsx`)
Features interactive metric cards and recent logs of diagnostic lists.

```javascript
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
```

---

### 4.2 Analytics & Spatial Dashboard (`pages/AnalyticsPage.jsx`)
Features css charts representing regional epidemics logs.

```javascript
// src/pages/AnalyticsPage.jsx
import React from 'react';

export default function AnalyticsPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Spatial Outbreak Analytics</h1>
        <p className="text-sm text-slate-400">Real-time localized disease outbreak monitoring</p>
      </div>

      {/* Outbreak Heatmap Grid Card */}
      <div className="glass-surface p-6 rounded-2xl border border-slate-800">
        <h3 className="text-lg font-semibold mb-4">PostGIS Epidemic Density Map</h3>
        <div className="aspect-video w-full rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center text-slate-500">
          {/* Mapping wrapper (e.g. Mapbox / React-Leaflet integration placeholder) */}
          <div className="text-center">
            <svg className="w-12 h-12 mx-auto mb-2 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <span className="text-xs uppercase tracking-wider font-semibold">Map View Integration Placeholder</span>
          </div>
        </div>
      </div>

      {/* Outbreak Metrics Listings */}
      <div className="glass-surface p-6 rounded-2xl border border-slate-800">
        <h3 className="text-lg font-semibold mb-4">Outbreaks Reported by District</h3>
        <div className="space-y-4">
          {[
            { district: 'Bangalore North', pathogen: 'Late Blight', count: 18, risk: 'HIGH' },
            { district: 'Kolar Gold Fields', pathogen: 'Leaf Rust', count: 9, risk: 'MEDIUM' },
            { district: 'Mandya rural', pathogen: 'Healthy', count: 42, risk: 'LOW' }
          ].map((item, idx) => (
            <div key={idx} className="flex justify-between items-center p-4 bg-slate-800/50 rounded-xl border border-slate-700/50">
              <div>
                <span className="text-sm font-semibold block">{item.district}</span>
                <span className="text-xs text-slate-400">Pathogen: {item.pathogen}</span>
              </div>
              <div className="text-right">
                <span className="text-sm font-bold block">{item.count} Scans</span>
                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                  item.risk === 'HIGH' ? 'bg-red-500/10 text-red-400' :
                  item.risk === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400' : 'bg-green-500/10 text-green-400'
                }`}>{item.risk} RISK</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

### 4.3 Profile & Settings Control Page (`pages/ProfilePage.jsx`)
Features settings toggles (multilingual selectors, offline cache management).

```javascript
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
```

---

*This React implementation codebase maps out responsive structures, settings selectors, and custom sensor hooks for the AgroVision platform.*
