import { useState, useEffect, useRef } from 'react';
import { Network, Users, Activity, PlayCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../../api';

export default function AdminDashboard() {
  const [isServerRunning, setIsServerRunning] = useState(false);
  const [metrics, setMetrics] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [showAddHospital, setShowAddHospital] = useState(false);
  const [newHospital, setNewHospital] = useState({ name: '', contactEmail: '', username: '', password: '' });
  const prevHospitalsRef = useRef();

  // Mock data for initial render or if API fails
  const mockMetrics = [
    { round: 1, accuracy: 0.50, loss: 0.71 },
    { round: 2, accuracy: 0.66, loss: 0.60 },
    { round: 3, accuracy: 0.76, loss: 0.53 },
    { round: 4, accuracy: 0.79, loss: 0.48 },
    { round: 5, accuracy: 0.82, loss: 0.44 },
  ];

  useEffect(() => {
    // Fetch historical metrics
    setMetrics(mockMetrics);
    
    // Poll hospitals every 3 seconds
    fetchHospitals();
    const interval = setInterval(fetchHospitals, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Check if we transitioned from having WEIGHTS_SENT to not having it (simulating aggregation complete)
    if (isServerRunning && prevHospitalsRef.current) {
      const previouslyAggregating = prevHospitalsRef.current.some(h => h.status === 'WEIGHTS_SENT');
      const currentlyAggregating = hospitals.some(h => h.status === 'WEIGHTS_SENT');
      const isOnline = hospitals.some(h => h.status === 'ONLINE');
      
      if (previouslyAggregating && !currentlyAggregating && isOnline) {
        setIsServerRunning(false); // Reset the button
      }
    }
    prevHospitalsRef.current = hospitals;
  }, [hospitals, isServerRunning]);

  const fetchHospitals = async () => {
    try {
      const res = await api.get('/hospitals');
      setHospitals(res.data);
    } catch (err) {
      console.error('Failed to fetch hospitals', err);
    }
  };

  const getGlobalStatus = () => {
    if (!isServerRunning) return { text: 'Offline', color: 'text-gray-600' };
    const hasSentWeights = hospitals.some(h => h.status === 'WEIGHTS_SENT');
    const isTraining = hospitals.some(h => h.status === 'TRAINING');
    
    if (hasSentWeights) return { text: 'Weights Received & Aggregating...', color: 'text-green-600' };
    if (isTraining) return { text: 'Active (Clients are training)', color: 'text-blue-600' };
    
    return { text: 'Active (Waiting for clients)', color: 'text-green-600' };
  };

  const globalStatus = getGlobalStatus();

  const handleInputChange = (e) => {
    setNewHospital({ ...newHospital, [e.target.name]: e.target.value });
  };

  const handleAddHospital = async (e) => {
    e.preventDefault();
    try {
      await api.post('/hospitals', newHospital);
      setShowAddHospital(false);
      setNewHospital({ name: '', contactEmail: '', username: '', password: '' });
      fetchHospitals(); // refresh list
    } catch (err) {
      alert('Failed to add hospital');
    }
  };

  const handleStartServer = async () => {
    setIsServerRunning(true);
    try {
      await api.post('/training/start?totalRounds=5');
      // In a real app, we would start polling /training/status or /metrics/global here
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Super Admin Dashboard</h1>
          <p className="text-gray-500">Monitor and control global federated learning</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Controls */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 lg:col-span-1">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Network className="text-blue-600" /> Control Panel
            </h2>
            <button
              onClick={handleStartServer}
              disabled={isServerRunning}
              className={`w-full py-3 rounded-lg font-medium text-white flex items-center justify-center gap-2 ${
                isServerRunning ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              <PlayCircle className="w-5 h-5" />
              {isServerRunning ? 'Global Server Running...' : 'Start Global Model Server'}
            </button>
            <div className="mt-6 space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">Status</span>
                <span className={`font-medium ${globalStatus.color}`}>
                  {globalStatus.text}
                </span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">Algorithm</span>
                <span className="font-medium">FedProx (μ=1.0)</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">Base Model</span>
                <span className="font-medium">Neural Network (MLP)</span>
              </div>
            </div>
          </div>

          {/* Metrics Chart */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 lg:col-span-2">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Activity className="text-green-600" /> Training Metrics
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="round" />
                  <YAxis yAxisId="left" domain={[0, 1]} />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="accuracy" stroke="#2563eb" name="Global Accuracy" strokeWidth={2} />
                  <Line yAxisId="right" type="monotone" dataKey="loss" stroke="#ef4444" name="Global Loss" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Connected Clients */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Users className="text-purple-600" /> Participating Hospitals
            </h2>
            <button
              onClick={() => setShowAddHospital(true)}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-purple-700 font-medium"
            >
              + Add Hospital
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-500">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3">Hospital ID</th>
                  <th className="px-6 py-3">Name</th>
                  <th className="px-6 py-3">Contact</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {hospitals.map(h => (
                  <tr key={h.id} className="border-b">
                    <td className="px-6 py-4 font-medium text-gray-900">HOSP-{h.id}</td>
                    <td className="px-6 py-4">{h.name}</td>
                    <td className="px-6 py-4">{h.contactEmail}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        h.status === 'ONLINE' ? 'bg-green-100 text-green-800' :
                        h.status === 'TRAINING' ? 'bg-blue-100 text-blue-800' :
                        h.status === 'WEIGHTS_SENT' ? 'bg-purple-100 text-purple-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {h.status || 'REGISTERED'}
                      </span>
                    </td>
                  </tr>
                ))}
                {hospitals.length === 0 && (
                  <tr>
                    <td colSpan="4" className="px-6 py-4 text-center text-gray-500">No hospitals registered yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {showAddHospital && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
            <h3 className="text-2xl font-bold mb-6">Register New Hospital</h3>
            <form onSubmit={handleAddHospital} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Hospital Name</label>
                <input required type="text" name="name" onChange={handleInputChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Contact Email</label>
                <input required type="email" name="contactEmail" onChange={handleInputChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Login Username</label>
                <input required type="text" name="username" onChange={handleInputChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Login Password</label>
                <input required type="password" name="password" onChange={handleInputChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2 focus:ring-blue-500 focus:border-blue-500" />
              </div>
              <div className="flex gap-4 mt-8">
                <button type="button" onClick={() => setShowAddHospital(false)} className="w-full py-2 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300">Cancel</button>
                <button type="submit" className="w-full py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700">Register</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
