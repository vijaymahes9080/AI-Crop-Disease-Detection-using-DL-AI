// src/features/diagnostics/components/TreatmentGuide.jsx
import React, { useState } from 'react';

export default function TreatmentGuide({ remedyData, riskLevel }) {
  const [activeTab, setActiveTab] = useState('organic'); // Tabs: 'organic' or 'chemical'
  const remedies = remedyData.treatments[activeTab];

  return (
    <div className="glass-surface p-6 rounded-2xl max-w-lg mx-auto border border-slate-700 space-y-6">
      {/* Header Info */}
      <div className="flex justify-between items-start">
        <div>
          <h4 className="text-xs text-slate-400 uppercase tracking-wider">Agronomic Remedy Guide</h4>
          <h3 className="text-lg font-bold text-slate-100">Pathogen Treatment Protocols</h3>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wide ${
          riskLevel === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
          riskLevel === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
          'bg-green-500/10 text-green-400 border border-green-500/20'
        }`}>
          {riskLevel} Risk
        </span>
      </div>

      <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-800 text-sm">
        <strong className="text-slate-200 block mb-1">Biological Cause:</strong>
        <p className="text-slate-400 leading-relaxed">{remedyData.cause}</p>
      </div>

      {/* Selector Tabs Toggle */}
      <div className="grid grid-cols-2 gap-2 bg-slate-950 p-1 rounded-xl border border-slate-800">
        <button
          onClick={() => setActiveTab('organic')}
          className={`py-2 text-sm font-semibold rounded-lg transition-all ${
            activeTab === 'organic' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Organic Options
        </button>
        <button
          onClick={() => setActiveTab('chemical')}
          className={`py-2 text-sm font-semibold rounded-lg transition-all ${
            activeTab === 'chemical' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Chemical Inputs
        </button>
      </div>

      {/* Remedies Action List */}
      <div className="space-y-4">
        <div>
          <span className="text-xs text-slate-400 uppercase font-semibold">Recommended Steps</span>
          <ul className="list-disc pl-5 mt-2 space-y-2 text-sm text-slate-300">
            {remedies.steps.map((step, idx) => (
              <li key={idx} className="leading-relaxed">{step}</li>
            ))}
          </ul>
        </div>

        <div className="border-t border-slate-700/60 pt-4">
          <span className="text-xs text-slate-400 uppercase font-semibold block">Dosage Details</span>
          <p className="text-sm font-medium text-emerald-400 mt-1">{remedies.dosage}</p>
        </div>
      </div>

      {/* Prevention Section */}
      <div className="border-t border-slate-700/60 pt-4 space-y-2">
        <span className="text-xs text-slate-400 uppercase font-semibold block">Preventative Farm Guidelines</span>
        <ul className="list-decimal pl-5 space-y-1.5 text-xs text-slate-400 leading-relaxed">
          {remedyData.prevention.map((prev, idx) => (
            <li key={idx}>{prev}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
