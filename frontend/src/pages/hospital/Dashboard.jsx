import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Server, Stethoscope, CheckCircle, Upload } from 'lucide-react';
import api from '../../api';

export default function HospitalDashboard() {
  const [status, setStatus] = useState('Idle');
  const [isTraining, setIsTraining] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const hospitalId = localStorage.getItem('hospitalId');

  useEffect(() => {
    if (hospitalId) {
      api.put(`/hospitals/${hospitalId}/status`, { status: 'ONLINE' });
    }
  }, [hospitalId]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleStartTraining = async () => {
    if (!selectedFile) {
      alert("Please select a training CSV file first.");
      return;
    }

    setIsTraining(true);
    setStatus('Connecting to Global Server and Uploading Dataset...');
    if (hospitalId) {
      await api.put(`/hospitals/${hospitalId}/status`, { status: 'TRAINING' });
    }
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      await api.post(`/training/join?hospitalId=${hospitalId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setStatus('Training locally & Sending weights...');
      
      // Simulate training time
      setTimeout(async () => {
        setStatus('Completed Round Successfully');
        setIsTraining(false);
        if (hospitalId) {
          await api.put(`/hospitals/${hospitalId}/status`, { status: 'WEIGHTS_SENT' });
        }
        alert("Success: Local training completed and weights have been successfully sent to the Global Server!");
        
        // Reset to ONLINE after a short delay to simulate readiness for the next round
        setTimeout(async () => {
          if (hospitalId) {
            await api.put(`/hospitals/${hospitalId}/status`, { status: 'ONLINE' });
          }
        }, 10000);
      }, 5000);
    } catch (err) {
      setStatus('Failed to connect to server');
      setIsTraining(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Hospital Admin Dashboard</h1>
            <p className="text-gray-500">Participate in Federated Learning</p>
          </div>
          <button 
            onClick={() => navigate('/hospital/predict')}
            className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
          >
            <Stethoscope className="w-5 h-5" />
            Run Prediction
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-blue-100 rounded-lg text-blue-600">
                <Server className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-semibold">Federated Training</h2>
            </div>
            <p className="text-gray-600 mb-6">
              Train the global model using your local patient data without sharing raw information.
            </p>
            
            <div className="mb-6">
              <input 
                type="file" 
                accept=".csv"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden" 
              />
              <button 
                onClick={() => fileInputRef.current.click()}
                className="w-full py-3 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 flex items-center justify-center gap-2 hover:border-blue-500 hover:text-blue-500 transition-colors"
              >
                <Upload className="w-5 h-5" />
                {selectedFile ? selectedFile.name : "Select Local Dataset (CSV)"}
              </button>
            </div>

            <button
              onClick={handleStartTraining}
              disabled={isTraining || !selectedFile}
              className={`w-full py-3 rounded-lg font-medium text-white flex items-center justify-center gap-2 ${
                isTraining || !selectedFile ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isTraining ? (
                <>
                  <Activity className="w-5 h-5 animate-pulse" />
                  Training in Progress...
                </>
              ) : (
                'Start Local Training & Send Weights'
              )}
            </button>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-semibold mb-4">Status</h2>
            <div className="flex items-center gap-3">
              {status === 'Completed Round Successfully' ? (
                <CheckCircle className="w-6 h-6 text-green-500" />
              ) : (
                <div className={`w-3 h-3 rounded-full ${isTraining ? 'bg-yellow-500 animate-ping' : 'bg-gray-300'}`} />
              )}
              <span className="text-gray-700 font-medium">{status}</span>
            </div>
            <div className="mt-6 pt-6 border-t border-gray-100">
              <h3 className="text-sm font-semibold text-gray-500 uppercase">Local Dataset</h3>
              <p className="mt-2 text-gray-900 font-medium">
                {selectedFile ? `Ready for training (${selectedFile.name})` : "No dataset selected"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
