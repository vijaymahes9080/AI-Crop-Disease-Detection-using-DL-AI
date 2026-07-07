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
