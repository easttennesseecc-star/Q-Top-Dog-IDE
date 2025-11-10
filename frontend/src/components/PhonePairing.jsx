/*
 Q-IDE Phone Pairing Component
 Handles QR code scanning, device pairing, and microphone access
 TypeScript interop: provide a minimal JSDoc typedef for editor hints.
 @typedef {Object} PairingSession
 @property {string} id
 @property {string} state
*/

import React, { useState, useEffect, useRef } from 'react';
import './PhonePairing.css';

const PhonePairing = () => {
  const [pairingCode, setPairingCode] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [deviceId, setDeviceId] = useState('');
  const [pairedDevices, setPairedDevices] = useState([]);
  const [activeMics, setActiveMics] = useState([]);
  const [showPairingDialog, setShowPairingDialog] = useState(false);
  const [manualPairingCode, setManualPairingCode] = useState('');
  const [deviceName, setDeviceName] = useState('');
  const mediaStreamRef = useRef(null);

  // Resolve backend base URL (match App.tsx logic)
  const backendBase = (
    window.__VITE_BACKEND_URL ||
    (import.meta?.env?.VITE_BACKEND_URL) ||
    (import.meta?.env?.VITE_API_URL) ||
    ''
  );
  const toApi = (path) => `${String(backendBase).replace(/\/$/, '')}${path.startsWith('/') ? path : '/' + path}`;

  // Stable local device id
  useEffect(() => {
    try {
      let did = localStorage.getItem('td.deviceId');
      if (!did) {
        // simple uuid v4
        did = ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
          (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
        localStorage.setItem('td.deviceId', did);
      }
      setDeviceId(did);
    } catch (_) {}
  }, []);

  // Start phone pairing
  const startPairing = async () => {
    try {
      const response = await fetch(toApi('/phone/pairing/generate-qr'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'test-pro' })
      });
      if (!response.ok) throw new Error('Failed to generate QR');
      const data = await response.json();
      setPairingCode(data.pairing_token);
      setQrCode(data.qr_code_base64);
      setShowPairingDialog(true);
    } catch (error) {
      console.error('Failed to start pairing:', error);
    }
  };

  // Verify pairing code (called from phone)
  const verifyPairing = async () => {
    if (!manualPairingCode || !deviceName) {
      alert('Please enter pairing code and device name');
      return;
    }

    try {
      const response = await fetch(toApi('/phone/pairing/pair'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pairing_token: manualPairingCode,
          device_id: deviceId || 'web-device',
          device_name: deviceName,
          device_type: 'web',
          os_version: navigator.userAgent,
          app_version: 'web'
        })
      });

      if (!response.ok) throw new Error('Invalid or expired pairing token');
      const data = await response.json();
      localStorage.setItem('td.jwt', data.jwt_token);
      localStorage.setItem('td.deviceId', data.device_id);
      alert('Phone paired successfully!');
      setManualPairingCode('');
      setDeviceName('');
      setShowPairingDialog(false);
      refreshPairedDevices();
    } catch (error) {
      console.error('Pairing verification failed:', error);
      alert('Pairing failed. Ensure the code is correct and not expired.');
    }
  };

  // Get paired devices
  const refreshPairedDevices = async () => {
    try {
      const url = new URL(toApi('/phone/devices'));
      url.searchParams.set('user_id', 'test-pro');
      const response = await fetch(url.toString());
      if (!response.ok) throw new Error('failed to fetch devices');
      const devices = await response.json();
      setPairedDevices(devices);
      setActiveMics([]); // feature not wired yet
    } catch (error) {
      console.error('Failed to get paired devices:', error);
    }
  };

  // Enable microphone for device
  const enableMicrophone = async (_deviceId) => {
    alert('Live mic streaming is not enabled in this build.');
  };

  // Disable microphone for device
  const disableMicrophone = async (_deviceId) => {
    alert('Live mic streaming is not enabled in this build.');
  };

  // Start audio stream via WebSocket
  const startAudioStream = (_deviceId) => {};

  // Unpair device
  const unpairDevice = async (deviceId) => {
    if (window.confirm('Are you sure you want to unpair this device?')) {
      try {
        const url = toApi(`/phone/devices/${encodeURIComponent(deviceId)}?user_id=test-pro`);
        await fetch(url, { method: 'DELETE' });
        refreshPairedDevices();
      } catch (error) {
        console.error('Failed to unpair device:', error);
      }
    }
  };

  // Load paired devices on mount
  useEffect(() => {
    refreshPairedDevices();
    const interval = setInterval(refreshPairedDevices, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="phone-pairing">
      <div className="pairing-header">
        <h2>📱 Phone Pairing</h2>
        <button className="btn-primary" onClick={startPairing}>
          + Pair New Phone
        </button>
      </div>

      {/* Pairing Dialog */}
      {showPairingDialog && (
        <div className="pairing-dialog">
          <div className="dialog-content">
            <h3>Pair Your Phone with Q-IDE</h3>

            {/* QR Code */}
            {qrCode && (
              <div className="qr-section">
                <p>Scan this QR code with your phone:</p>
                <img src={`data:image/png;base64,${qrCode}`} alt="Pairing QR Code" />
              </div>
            )}

            {/* Manual Code */}
            <div className="manual-pairing">
              <p>Or enter this code on your phone:</p>
              <div className="pairing-code">{pairingCode}</div>

              <h4>Phone Setup Instructions:</h4>
              <ol>
                <li>Open Q-IDE on your phone</li>
                <li>Tap "Pair with Desktop"</li>
                <li>Scan the QR code OR enter the code above</li>
                <li>Enter your phone name (e.g., "iPhone 15")</li>
                <li>Tap "Pair"</li>
              </ol>

              <div className="form-group">
                <input
                  type="text"
                  placeholder="Pairing Code"
                  value={manualPairingCode}
                  onChange={(e) => setManualPairingCode(e.target.value.toUpperCase())}
                  maxLength="6"
                />
              </div>

              <div className="form-group">
                <input
                  type="text"
                  placeholder="Device Name (e.g., iPhone 15)"
                  value={deviceName}
                  onChange={(e) => setDeviceName(e.target.value)}
                />
              </div>

              <button className="btn-primary" onClick={verifyPairing}>
                ✓ Verify Pairing
              </button>
              <button className="btn-secondary" onClick={() => setShowPairingDialog(false)}>
                ✕ Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Paired Devices List */}
      <div className="devices-section">
        <h3>Paired Devices ({pairedDevices.length})</h3>

        {pairedDevices.length === 0 ? (
          <div className="no-devices">
            <p>No phones paired yet</p>
            <p>Click "Pair New Phone" to get started</p>
          </div>
        ) : (
          <div className="devices-list">
            {pairedDevices.map((device) => (
              <div key={device.device_id} className="device-card">
                <div className="device-header">
                  <span className="device-name">📱 {device.name}</span>
                  <span className={`mic-status ${device.mic_enabled ? 'active' : 'inactive'}`}>
                    {device.mic_enabled ? '🎤 Mic On' : '🎤 Mic Off'}
                  </span>
                </div>

                <div className="device-info">
                  <p>
                    <strong>Paired:</strong>{' '}
                    {new Date(device.paired_at || device.pairedAt || Date.now()).toLocaleString()}
                  </p>
                  <p>
                    <strong>Last Active:</strong>{' '}
                    {new Date(device.last_seen || device.lastSeen || Date.now()).toLocaleString()}
                  </p>
                </div>

                <div className="device-actions">
                  {device.mic_enabled ? (
                    <button
                      className="btn-danger"
                      onClick={() => disableMicrophone(device.device_id)}
                    >
                      🛑 Turn Off Mic
                    </button>
                  ) : (
                    <button
                      className="btn-success"
                      onClick={() => enableMicrophone(device.device_id)}
                    >
                      🎤 Turn On Mic
                    </button>
                  )}
                  <button
                    className="btn-secondary"
                    onClick={() => unpairDevice(device.device_id)}
                  >
                    ✕ Unpair
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Active Microphones */}
      {activeMics.length > 0 && (
        <div className="active-mics">
          <h3>🎙️ Active Microphones ({activeMics.length})</h3>
          <p>The following devices are transmitting audio:</p>
          <ul>
            {activeMics.map((deviceId) => {
              const device = pairedDevices.find((d) => d.device_id === deviceId);
              return <li key={deviceId}>{device?.name || deviceId}</li>;
            })}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PhonePairing;
// TypeScript compatibility shim
// eslint-disable-next-line no-undef
export const __esModule = true;
