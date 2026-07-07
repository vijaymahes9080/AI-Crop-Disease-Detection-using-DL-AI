// src/pages/AnalyticsDashboard.jsx
import React, { useState, useEffect } from 'react';

export default function AnalyticsDashboard() {
  const [cropFilter, setCropFilter] = useState('all');
  const [dateRange, setDateRange] = useState('30');
  const [data, setData] = useState(null);

  // Mock loading data
  useEffect(() => {
    // Mimics api fetching logic
    setData({
      avgConfidence: 0.942,
      avgSeverity: 24.5,
      usage: [12, 18, 22, 15, 30, 24, 45], // Scan rates
      distribution: [
        { disease: 'Late Blight', count: 45 },
        { disease: 'Leaf Rust', count: 28 },
        { disease: 'Healthy', count: 68 }
      ]
    });
  }, [cropFilter, dateRange]);

  const handleExportCSV = () => {
    window.open(`http://localhost:8000/api/v1/analytics/export?crop_id=${cropFilter}`);
  };

  if (!data) return <div className="text-center text-slate-400 p-8">Loading data metrics...</div>;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">Diagnostics Intelligence</h1>
          <p className="text-sm text-slate-400">Outbreak statistics and model accuracy logs</p>
        </div>
        <button 
          onClick={handleExportCSV}
          className="bg-emerald-500 hover:bg-emerald-600 active:scale-95 text-slate-950 font-bold px-4 py-2 rounded-xl transition-all flex items-center space-x-2 text-sm shadow-md"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span>Export CSV Report</span>
        </button>
      </div>

      {/* Filters Area */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-800/40 p-4 rounded-xl border border-slate-800">
        <div className="flex flex-col">
          <label htmlFor="crop-select" className="text-xs text-slate-400 font-semibold mb-1.5">Crop Filter</label>
          <select 
            id="crop-select"
            value={cropFilter}
            onChange={(e) => setCropFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg p-2 text-sm text-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
          >
            <option value="all">All Crops Combined</option>
            <option value="1">Tomato Category</option>
            <option value="2">Potato Category</option>
            <option value="3">Coffee Category</option>
          </select>
        </div>

        <div className="flex flex-col">
          <label htmlFor="date-select" className="text-xs text-slate-400 font-semibold mb-1.5">Time Interval</label>
          <select 
            id="date-select"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg p-2 text-sm text-slate-200 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
          >
            <option value="7">Last 7 Days</option>
            <option value="30">Last 30 Days</option>
            <option value="90">Last Quarter</option>
          </select>
        </div>
      </div>

      {/* Grid Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* 1. Bar Chart: Disease Distribution (SVG based to avoid NPM packages delays) */}
        <div className="glass-surface p-6 rounded-2xl border border-slate-800">
          <h3 className="text-base font-semibold text-slate-200 mb-6">Pathogen Distribution</h3>
          <div className="space-y-4">
            {data.distribution.map((item, idx) => {
              const maxCount = Math.max(...data.distribution.map(d => d.count));
              const pct = (item.count / maxCount) * 100;
              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-slate-300">{item.disease}</span>
                    <span className="text-emerald-400">{item.count} Scans</span>
                  </div>
                  <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800">
                    <div 
                      className="bg-emerald-500 h-full rounded-full transition-all duration-500" 
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 2. Model Performance stats card */}
        <div className="glass-surface p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <h3 className="text-base font-semibold text-slate-200 mb-4">Diagnostics Performance</h3>
          <div className="grid grid-cols-2 gap-4 my-auto">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
              <span className="text-slate-400 text-xs uppercase font-semibold">Classification Match</span>
              <h4 className="text-3xl font-extrabold text-emerald-400 mt-2">{(data.avgConfidence * 100).toFixed(1)}%</h4>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
              <span className="text-slate-400 text-xs uppercase font-semibold">Avg Spot Severity</span>
              <h4 className="text-3xl font-extrabold text-slate-100 mt-2">{data.avgSeverity.toFixed(1)}%</h4>
            </div>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed mt-4">
            * Metric data represents weighted validation parameters collected from verified geolocated farm scans.
          </p>
        </div>
      </div>
    </div>
  );
}
