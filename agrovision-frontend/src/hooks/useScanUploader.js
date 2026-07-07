// src/hooks/useScanUploader.js
import { useState } from 'react';
import { apiClient, fetchWithRetry } from '../services/apiClient';

export const SCAN_STATES = {
  IDLE: 'IDLE',
  UPLOADING: 'UPLOADING',
  PREPROCESSING: 'PREPROCESSING',
  INFERENCING: 'INFERENCING',
  SUCCESS: 'SUCCESS',
  ERROR: 'ERROR'
};

export function useScanUploader() {
  const [scanState, setScanState] = useState(SCAN_STATES.IDLE);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const uploadAndAnalyzeScan = async (imageBlob, cropId, coords) => {
    setError(null);
    setScanState(SCAN_STATES.UPLOADING);

    const formData = new FormData();
    formData.append('image', imageBlob);
    formData.append('crop_category_id', cropId.toString());
    formData.append('latitude', coords.latitude?.toString() || '0');
    formData.append('longitude', coords.longitude?.toString() || '0');

    const apiCall = () => apiClient.post('/scans/analyze', formData, {
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        if (percentCompleted === 100) {
          setScanState(SCAN_STATES.PREPROCESSING);
        }
      }
    });

    try {
      // Execute request with backoff retry
      const response = await fetchWithRetry(apiCall, 3, 1000);
      
      setScanState(SCAN_STATES.INFERENCING);
      // Wait briefly to smooth out UX transitions between API stages
      await new Promise(r => setTimeout(r, 600));
      
      setResult(response.data);
      setScanState(SCAN_STATES.SUCCESS);
      return response.data;
      
    } catch (err) {
      console.warn("[!] Upload failed. Initiating offline recovery...", err);
      
      // Error Recovery: Write scan payload locally
      const localQueue = JSON.parse(localStorage.getItem('sync_queue') || '[]');
      const offlineId = `offline_${Date.now()}`;
      
      // Save base64 image data locally for subsequent uploads
      const reader = new FileReader();
      reader.readAsDataURL(imageBlob);
      reader.onloadend = () => {
        const base64data = reader.result;
        localQueue.push({
          id: offlineId,
          cropId: cropId,
          coords: coords,
          imageBytes: base64data,
          timestamp: new Date().toISOString()
        });
        localStorage.setItem('sync_queue', JSON.stringify(localQueue));
      };

      setError("Offline mode active: Scan saved locally in queue.");
      setScanState(SCAN_STATES.ERROR);
    }
  };

  return { uploadAndAnalyzeScan, scanState, result, error };
}
