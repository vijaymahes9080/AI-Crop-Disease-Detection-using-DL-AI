// src/features/diagnostics/components/HeatmapViewer.jsx
import React, { useState } from 'react';

export default function HeatmapViewer({ originalImage, heatmapImage, diseaseName, confidence }) {
  const [opacity, setOpacity] = useState(0.5); // Default blend factor
  const [showOverlay, setShowOverlay] = useState(true);

  return (
    <div className="glass-surface p-6 rounded-2xl max-w-md mx-auto shadow-2xl">
      <h3 className="text-lg font-semibold text-slate-50 mb-2">Model Focus Area</h3>
      <p className="text-sm text-slate-400 mb-4">
        Below is the activation map highlighting the leaf spots that informed the classification.
      </p>

      {/* Layer Stack Frame */}
      <div className="relative aspect-square w-full rounded-xl overflow-hidden bg-slate-900 border border-slate-700">
        {/* Underlay: Original Leaf Photo */}
        <img 
          src={originalImage} 
          alt="Original leaf capture" 
          className="absolute inset-0 w-full h-full object-cover"
        />

        {/* Overlay: Heatmap */}
        {showOverlay && (
          <img 
            src={heatmapImage} 
            alt="Grad-CAM activation heatmap overlay" 
            className="absolute inset-0 w-full h-full object-cover transition-opacity duration-150"
            style={{ opacity: opacity }}
          />
        )}
      </div>

      {/* Opacity Control Slider */}
      <div className="mt-6 space-y-4">
        <div className="flex items-center justify-between">
          <label htmlFor="opacity-slider" className="text-sm font-medium text-slate-200">
            Heatmap Intensity
          </label>
          <button 
            onClick={() => setShowOverlay(!showOverlay)}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-colors ${
              showOverlay ? 'bg-emerald-500 text-slate-950' : 'bg-slate-700 text-slate-300'
            }`}
          >
            {showOverlay ? 'Hide Overlay' : 'Show Overlay'}
          </button>
        </div>

        <input 
          id="opacity-slider"
          type="range" 
          min="0" 
          max="1" 
          step="0.05"
          value={opacity}
          disabled={!showOverlay}
          onChange={(e) => setOpacity(parseFloat(e.target.value))}
          className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500 disabled:opacity-50"
        />

        {/* Diagnostic Metadata Footer */}
        <div className="border-t border-slate-700 pt-4 flex justify-between items-center">
          <div>
            <span className="text-xs text-slate-400 block uppercase tracking-wider">Prediction</span>
            <span className="text-base font-bold text-slate-100">{diseaseName}</span>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400 block uppercase tracking-wider">Confidence</span>
            <span className="text-base font-bold text-emerald-400">{(confidence * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
