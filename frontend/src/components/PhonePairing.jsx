/*
Q-IDE Phone Pairing Component
Handles QR code scanning, device pairing, and microphone access
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

  // Start phone pairing
  const startPairing = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/phone/start-pairing', {
        method: 'POST'
      });
      const data = await response.json();
      setPairingCode(data.pairing_code);
      setQrCode(data.qr_code_base64);
      setDeviceId(data.device_id);
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
      const response = await fetch('http://127.0.0.1:8000/api/phone/verify-pairing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pairing_code: manualPairingCode,
          device_name: deviceName
        })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('sessionToken', data.session_token);
        localStorage.setItem('deviceId', data.device_id);
        alert('Phone paired successfully!');
        setManualPairingCode('');
        setDeviceName('');
        setShowPairingDialog(false);
        refreshPairedDevices();
      } else {
        alert('Invalid pairing code');
      }
    } catch (error) {
      console.error('Pairing verification failed:', error);
    }
  };

  // Get paired devices
  const refreshPairedDevices = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/phone/paired-devices');
      const devices = await response.json();
      setPairedDevices(devices);

      const micsResponse = await fetch('http://127.0.0.1:8000/api/phone/active-mics');
      const micsData = await micsResponse.json();
      setActiveMics(micsData.active_devices);
    } catch (error) {
      console.error('Failed to get paired devices:', error);
    }
  };

  // Enable microphone for device
  const enableMicrophone = async (deviceId) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/phone/mic/enable/${deviceId}`, {
        method: 'POST'
      });

      if (response.ok) {
        // Start audio stream
        startAudioStream(deviceId);
        refreshPairedDevices();
      }
    } catch (error) {
      console.error('Failed to enable microphone:', error);
    }
  };

  // Disable microphone for device
  const disableMicrophone = async (deviceId) => {
    try {
      await fetch(`http://127.0.0.1:8000/api/phone/mic/disable/${deviceId}`, {
        method: 'POST'
      });
      refreshPairedDevices();
    } catch (error) {
      console.error('Failed to disable microphone:', error);
    }
  };

  // Start audio stream via WebSocket
  const startAudioStream = (deviceId) => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/api/phone/ws/audio/${deviceId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Audio received:', data);
      // Process audio data here
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  // Unpair device
  const unpairDevice = async (deviceId) => {
    if (window.confirm('Are you sure you want to unpair this device?')) {
      try {
        await fetch('http://127.0.0.1:8000/api/phone/unpair', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ device_id: deviceId })
        });
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
                    {new Date(device.paired_at).toLocaleString()}
                  </p>
                  <p>
                    <strong>Last Active:</strong>{' '}
                    {new Date(device.last_active).toLocaleString()}
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
