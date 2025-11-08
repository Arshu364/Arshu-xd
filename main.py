import React, { useState, useRef, useEffect } from 'react';
import { Send, StopCircle, Upload, Play } from 'lucide-react';

export default function FBMessenger() {
  const [tokenMode, setTokenMode] = useState('single');
  const [singleToken, setSingleToken] = useState('');
  const [tokenFile, setTokenFile] = useState(null);
  const [convoId, setConvoId] = useState('');
  const [kidsName, setKidsName] = useState('');
  const [apnaName, setApnaName] = useState('');
  const [msgFile, setMsgFile] = useState(null);
  const [delay, setDelay] = useState(30);
  const [isRunning, setIsRunning] = useState(false);
  const [status, setStatus] = useState('Ready');
  const [taskKey, setTaskKey] = useState('');
  const [stats, setStats] = useState({ sent: 0, cycles: 0, errors: 0 });
  const [logs, setLogs] = useState([]);
  
  const stopRef = useRef(false);
  const messagesRef = useRef([]);
  const tokensRef = useRef([]);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-50), { time: timestamp, msg: message, type }]);
  };

  const generateKey = () => {
    return 'KEY-' + Math.random().toString(36).substr(2, 9).toUpperCase();
  };

  const handleTokenFileUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const text = await file.text();
      const tokens = text.split('\n').filter(t => t.trim());
      tokensRef.current = tokens;
      setTokenFile(file.name);
      addLog(`Loaded ${tokens.length} tokens from file`, 'success');
    }
  };

  const handleMsgFileUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const text = await file.text();
      const messages = text.split('\n').filter(m => m.trim());
      messagesRef.current = messages;
      setMsgFile(file.name);
      addLog(`Loaded ${messages.length} messages from file`, 'success');
    }
  };

  const sendMessage = async (token, message, retries = 3) => {
    const formattedMsg = `${kidsName} ${message} ${apnaName}`;
    const url = `https://graph.facebook.com/v17.0/t_${convoId}`;
    
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
      'Referer': 'https://www.facebook.com/',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': '*/*',
      'Accept-Language': 'en-US,en;q=0.9',
      'Origin': 'https://www.facebook.com',
      'X-Requested-With': 'XMLHttpRequest'
    };

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers,
          body: new URLSearchParams({
            access_token: token,
            message: formattedMsg
          })
        });

        if (response.ok) {
          return { success: true, data: await response.json() };
        } else if (response.status === 429) {
          addLog('Rate limit hit, waiting 60s...', 'warning');
          await new Promise(resolve => setTimeout(resolve, 60000));
          continue;
        } else {
          const error = await response.text();
          if (attempt === retries) {
            return { success: false, error };
          }
          await new Promise(resolve => setTimeout(resolve, 5000 * attempt));
        }
      } catch (error) {
        if (attempt === retries) {
          return { success: false, error: error.message };
        }
        await new Promise(resolve => setTimeout(resolve, 5000 * attempt));
      }
    }
    return { success: false, error: 'Max retries exceeded' };
  };

  const startTask = async () => {
    if (!convoId || !kidsName || !apnaName || messagesRef.current.length === 0) {
      addLog('Please fill all required fields', 'error');
      return;
    }

    if (tokenMode === 'single' && !singleToken) {
      addLog('Please enter access token', 'error');
      return;
    }

    if (tokenMode === 'file' && tokensRef.current.length === 0) {
      addLog('Please upload token file', 'error');
      return;
    }

    const key = generateKey();
    setTaskKey(key);
    setIsRunning(true);
    stopRef.current = false;
    setStats({ sent: 0, cycles: 0, errors: 0 });
    addLog(`Task started with key: ${key}`, 'success');

    const tokens = tokenMode === 'single' ? [singleToken] : tokensRef.current;
    let cycle = 0;

    while (!stopRef.current) {
      cycle++;
      setStats(prev => ({ ...prev, cycles: cycle }));
      setStatus(`Running Cycle ${cycle}`);
      addLog(`Starting Cycle ${cycle}`, 'info');

      let tokenIndex = 0;
      
      for (let msgIndex = 0; msgIndex < messagesRef.current.length; msgIndex++) {
        if (stopRef.current) break;

        const currentToken = tokens[tokenIndex % tokens.length];
        const currentMsg = messagesRef.current[msgIndex];

        setStatus(`Cycle ${cycle} - Msg ${msgIndex + 1}/${messagesRef.current.length}`);
        
        const result = await sendMessage(currentToken, currentMsg);
        
        if (result.success) {
          setStats(prev => ({ ...prev, sent: prev.sent + 1 }));
          addLog(`✓ Message ${msgIndex + 1} sent successfully`, 'success');
        } else {
          setStats(prev => ({ ...prev, errors: prev.errors + 1 }));
          addLog(`✗ Failed to send message ${msgIndex + 1}: ${result.error}`, 'error');
        }

        if (tokenMode === 'file') {
          tokenIndex++;
        }

        await new Promise(resolve => setTimeout(resolve, delay * 1000));
      }

      addLog(`Cycle ${cycle} completed. Resting for 30 seconds...`, 'info');
      setStatus(`Resting after Cycle ${cycle}`);
      await new Promise(resolve => setTimeout(resolve, 30000));
    }

    setIsRunning(false);
    setStatus('Stopped');
    addLog('Task stopped', 'warning');
  };

  const stopTask = () => {
    stopRef.current = true;
    setIsRunning(false);
    addLog('Stop signal sent', 'warning');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-pink-50 to-pink-100 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-8 rounded-2xl shadow-2xl mb-6 text-center">
          <h1 className="text-4xl font-black tracking-wider mb-2 drop-shadow-lg">
            EAGLES  RUL3X
          </h1>
          <p className="text-xl font-bold tracking-wide">
            OWN3R:  ARNAV SINGH
          </p>
        </div>

        {/* Control Panel */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6 border-4 border-pink-300">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Token Mode */}
            <div>
              <label className="block text-lg font-bold text-gray-800 mb-3">
                TOKEN MODE
              </label>
              <div className="flex gap-4 mb-4">
                <button
                  onClick={() => setTokenMode('single')}
                  className={`flex-1 py-3 px-4 rounded-lg font-bold transition-all ${
                    tokenMode === 'single'
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  SINGLE TOKEN
                </button>
                <button
                  onClick={() => setTokenMode('file')}
                  className={`flex-1 py-3 px-4 rounded-lg font-bold transition-all ${
                    tokenMode === 'file'
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  TOKEN FILE
                </button>
              </div>

              {tokenMode === 'single' ? (
                <input
                  type="text"
                  value={singleToken}
                  onChange={(e) => setSingleToken(e.target.value)}
                  placeholder="Enter Access Token"
                  className="w-full p-3 border-2 border-pink-300 rounded-lg font-bold focus:border-purple-500 focus:outline-none"
                  disabled={isRunning}
                />
              ) : (
                <label className="block cursor-pointer">
                  <div className="border-2 border-dashed border-pink-300 rounded-lg p-6 text-center hover:bg-pink-50 transition-all">
                    <Upload className="mx-auto mb-2 text-purple-600" size={32} />
                    <span className="font-bold text-gray-700">
                      {tokenFile || 'UPLOAD TOKEN FILE'}
                    </span>
                  </div>
                  <input
                    type="file"
                    onChange={handleTokenFileUpload}
                    className="hidden"
                    accept=".txt"
                    disabled={isRunning}
                  />
                </label>
              )}
            </div>

            {/* Message File */}
            <div>
              <label className="block text-lg font-bold text-gray-800 mb-3">
                MESSAGE FILE
              </label>
              <label className="block cursor-pointer">
                <div className="border-2 border-dashed border-pink-300 rounded-lg p-6 text-center hover:bg-pink-50 transition-all">
                  <Upload className="mx-auto mb-2 text-purple-600" size={32} />
                  <span className="font-bold text-gray-700">
                    {msgFile || 'UPLOAD MESSAGE FILE'}
                  </span>
                </div>
                <input
                  type="file"
                  onChange={handleMsgFileUpload}
                  className="hidden"
                  accept=".txt"
                  disabled={isRunning}
                />
              </label>
            </div>

            {/* Convo ID */}
            <div>
              <label className="block text-lg font-bold text-gray-800 mb-3">
                CONVO ID
              </label>
              <input
                type="text"
                value={convoId}
                onChange={(e) => setConvoId(e.target.value)}
                placeholder="Enter Conversation ID"
                className="w-full p-3 border-2 border-pink-300 rounded-lg font-bold focus:border-purple-500 focus:outline-none"
                disabled={isRunning}
              />
            </div>

            {/* Kids Name */}
            <div>
              <label className="block text-lg font-bold text-gray-800 mb-3">
                KIDS NAME
              </label>
              <input
                type="text"
                value={kidsName}
                onChange={(e) => setKidsName(e.target.value)}
                placeholder="Enter Kids Name"
                className="w-full p-3 border-2 border-pink-300 rounded-lg font-bold focus:border-purple-500 focus:outline-none"
                disabled={isRunning}
              />
            </div>

            {/* Apna Name */}
            <div>
              <label className="block text-lg font-bold text-gray-800 mb-3">
                APNA NAAM
              </label>
              <input
                type="text"
                value={apnaName}
                onChange={(e) => setApnaName(e.target.value)}
                placeholder="Enter Your Name"
                className="w-full p-3 border-2 border-pink-300 rounded-lg font-bold focus:border-purple-500 focus:outline-none"
                disabled={isRunning}
              />
            </div>

            {/* Delay */}
            <div>
              <label className="block text-lg font-bold text-gray-800 mb-3">
                TIME (SECONDS)
              </label>
              <input
                type="number"
                value={delay}
                onChange={(e) => setDelay(Number(e.target.value))}
                min="10"
                className="w-full p-3 border-2 border-pink-300 rounded-lg font-bold focus:border-purple-500 focus:outline-none"
                disabled={isRunning}
              />
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex gap-4 mt-6">
            <button
              onClick={startTask}
              disabled={isRunning}
              className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white py-4 rounded-xl font-black text-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Play size={24} />
              START TASK
            </button>
            <button
              onClick={stopTask}
              disabled={!isRunning}
              className="flex-1 bg-gradient-to-r from-red-500 to-red-600 text-white py-4 rounded-xl font-black text-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <StopCircle size={24} />
              STOP TASK
            </button>
          </div>

          {/* Task Key */}
          {taskKey && (
            <div className="mt-6 bg-gradient-to-r from-yellow-100 to-yellow-200 p-4 rounded-lg border-2 border-yellow-400">
              <p className="text-center font-black text-gray-800">
                TASK KEY: <span className="text-purple-600">{taskKey}</span>
              </p>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-pink-300 text-center">
            <p className="text-sm font-bold text-gray-600 mb-1">STATUS</p>
            <p className="text-xl font-black text-purple-600">{status}</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-pink-300 text-center">
            <p className="text-sm font-bold text-gray-600 mb-1">SENT</p>
            <p className="text-xl font-black text-green-600">{stats.sent}</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-pink-300 text-center">
            <p className="text-sm font-bold text-gray-600 mb-1">CYCLES</p>
            <p className="text-xl font-black text-blue-600">{stats.cycles}</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg border-2 border-pink-300 text-center">
            <p className="text-sm font-bold text-gray-600 mb-1">ERRORS</p>
            <p className="text-xl font-black text-red-600">{stats.errors}</p>
          </div>
        </div>

        {/* Logs */}
        <div className="bg-white rounded-2xl shadow-xl p-6 border-4 border-pink-300">
          <h2 className="text-2xl font-black text-gray-800 mb-4">ACTIVITY LOGS</h2>
          <div className="bg-gray-900 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
            {logs.map((log, i) => (
              <div
                key={i}
                className={`mb-1 ${
                  log.type === 'error'
                    ? 'text-red-400'
                    : log.type === 'success'
                    ? 'text-green-400'
                    : log.type === 'warning'
                    ? 'text-yellow-400'
                    : 'text-gray-300'
                }`}
              >
                <span className="text-gray-500">[{log.time}]</span> {log.msg}
              </div>
            ))}
            {logs.length === 0 && (
              <p className="text-gray-500 text-center mt-20">No logs yet...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
