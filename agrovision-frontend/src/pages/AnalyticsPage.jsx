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
