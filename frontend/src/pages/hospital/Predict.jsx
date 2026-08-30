import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Stethoscope } from 'lucide-react';
import api from '../../api';

export default function Predict() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    age: 60, sex: 1, cp: 3, trestbps: 140, chol: 250, fbs: 0,
    restecg: 0, thalach: 150, exang: 0, oldpeak: 1.5, slope: 1, ca: 0, thal: 2
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) });
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Simulate API call for prediction
      // For demo, the Spring backend expects JSON string in a specific structure or directly
      const payload = JSON.stringify(formData);
      const res = await api.post('/predict', payload, {
        headers: { 'Content-Type': 'application/json' }
      });
      // Mock result if backend returns standard response
      setResult(res.data.prediction || "High Risk");
    } catch (err) {
      console.error(err);
      setResult("Error evaluating model");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <button 
          onClick={() => navigate('/hospital/dashboard')}
          className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </button>
        
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center gap-4 mb-8">
            <div className="p-3 bg-indigo-100 rounded-lg text-indigo-600">
              <Stethoscope className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold">Patient Risk Prediction</h1>
          </div>

          <form onSubmit={handlePredict} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.keys(formData).map((key) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">
                    {key}
                  </label>
                  <input
                    type="number"
                    step="any"
                    name={key}
                    value={formData[key]}
                    onChange={handleChange}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
              ))}
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full md:w-auto px-8 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              {loading ? 'Analyzing...' : 'Run Global Model Prediction'}
            </button>
          </form>

          {result && (
            <div className={`mt-8 p-6 rounded-lg border ${
              result.includes('High') ? 'bg-red-50 border-red-100' : 'bg-green-50 border-green-100'
            }`}>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Prediction Result</h3>
              <p className={`text-2xl font-bold ${
                result.includes('High') ? 'text-red-700' : 'text-green-700'
              }`}>
                {result}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
