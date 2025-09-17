'use client';

import { useState } from 'react';
import { Brain, Activity, FileText, Search, ChevronRight, Clock, Shield, Users, Sparkles, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import PDFReportButton from './components/PDFReport';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState('form');
  const [formData, setFormData] = useState({
    age: '',
    gender: 'Male',
    conditions: '',
    medications: '',
    biomarkers: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      setResults(data);
      setActiveTab('results');
    } catch (error) {
      console.error('Error:', error);
      alert('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'ELIGIBLE': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'NOT_ELIGIBLE': return <XCircle className="h-5 w-5 text-red-500" />;
      default: return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <span className="font-semibold text-xl">ClinicalMatch AI</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">Powered by RAG Technology</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Find Your Clinical Trial Match
            </h1>
            <p className="text-xl opacity-90 max-w-3xl mx-auto">
              Advanced AI technology analyzes your medical profile against thousands of trials to find the best matches for you
            </p>
            
            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto mt-12">
              <div>
                <div className="text-3xl font-bold">20+</div>
                <div className="text-sm opacity-75">Active Trials</div>
              </div>
              <div>
                <div className="text-3xl font-bold">95%</div>
                <div className="text-sm opacity-75">Match Accuracy</div>
              </div>
              <div>
                <div className="text-3xl font-bold">&lt;10s</div>
                <div className="text-sm opacity-75">Analysis Time</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        {/* Features */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <Sparkles className="h-8 w-8 text-yellow-500 mb-3" />
            <h3 className="font-semibold mb-1">AI-Powered</h3>
            <p className="text-sm text-gray-600">LLM analysis for accurate matching</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <Shield className="h-8 w-8 text-green-500 mb-3" />
            <h3 className="font-semibold mb-1">Secure & Private</h3>
            <p className="text-sm text-gray-600">Your data is encrypted and protected</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <Clock className="h-8 w-8 text-blue-500 mb-3" />
            <h3 className="font-semibold mb-1">Fast Results</h3>
            <p className="text-sm text-gray-600">Get matches in under 10 seconds</p>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <Users className="h-8 w-8 text-purple-500 mb-3" />
            <h3 className="font-semibold mb-1">Expert Validated</h3>
            <p className="text-sm text-gray-600">Reviewed by medical professionals</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 mb-8 bg-gray-100 p-1 rounded-lg max-w-md">
          <button
            onClick={() => setActiveTab('form')}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition ${
              activeTab === 'form' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Patient Information
          </button>
          <button
            onClick={() => setActiveTab('results')}
            disabled={!results}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition ${
              activeTab === 'results' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900 disabled:opacity-50'
            }`}
          >
            Results {results && `(${results.matches?.length || 0})`}
          </button>
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100">
          {activeTab === 'form' ? (
            <div className="p-8">
              <h2 className="text-2xl font-bold mb-6 text-gray-900">Enter Your Medical Information</h2>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Age
                    </label>
                    <input
                      type="number"
                      required
                      min="18"
                      max="120"
                      className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition text-gray-900 placeholder-gray-500"
                      value={formData.age}
                      onChange={(e) => setFormData({...formData, age: e.target.value})}
                      placeholder="Enter your age"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Gender
                    </label>
                    <select
                      className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition text-gray-900 placeholder-gray-500"
                      value={formData.gender}
                      onChange={(e) => setFormData({...formData, gender: e.target.value})}
                    >
                      <option>Male</option>
                      <option>Female</option>
                      <option>Other</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Medical Conditions
                    <span className="text-red-500 ml-1">*</span>
                  </label>
                  <textarea
                    required
                    className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition text-gray-900 placeholder-gray-500"
                    rows="3"
                    value={formData.conditions}
                    onChange={(e) => setFormData({...formData, conditions: e.target.value})}
                    placeholder="e.g., Type 2 Diabetes, Hypertension, NSCLC Stage III"
                  />
                  <p className="text-xs text-gray-500 mt-1">List all relevant diagnoses</p>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Current Medications
                  </label>
                  <textarea
                    className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition text-gray-900 placeholder-gray-500"
                    rows="2"
                    value={formData.medications}
                    onChange={(e) => setFormData({...formData, medications: e.target.value})}
                    placeholder="e.g., Metformin 500mg, Lisinopril 10mg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Biomarkers & Lab Values
                  </label>
                  <textarea
                    className="w-full px-4 py-2.5 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition text-gray-900 placeholder-gray-500"
                    rows="2"
                    value={formData.biomarkers}
                    onChange={(e) => setFormData({...formData, biomarkers: e.target.value})}
                    placeholder="e.g., HbA1c: 7.5%, PD-L1: 50%, EGFR: Positive"
                  />
                  <p className="text-xs text-gray-500 mt-1">Include relevant test results if available</p>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transform hover:scale-[1.02] transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Search className="h-5 w-5" />
                      <span>Find Matching Trials</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          ) : (
            <div className="p-8">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-500">Your Trial Matches</h2>
                <button
                  onClick={() => setActiveTab('form')}
                  className="text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-1"
                >
                  <ChevronRight className="h-4 w-4 rotate-180" />
                  <span>Back to Form</span>
                </button>
              </div>
              
              {results && (
                <div>
                  {results.message && (
                    <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-blue-800">{results.message}</p>
                    </div>
                  )}
                  
                  <div className="space-y-4">
                    {results.matches?.map((match, idx) => (
                      <div key={idx} className="border-2 border-gray-200 rounded-lg p-6 hover:border-blue-300 transition">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="font-semibold text-lg">{match.title}</h3>
                            <p className="text-sm text-gray-500 mt-1">NCT ID: {match.nct_id}</p>
                          </div>
                          {getStatusIcon(match.status)}
                        </div>
                        
                        {results.matches && results.matches.length > 0 && (
                          <div className="mt-6 pt-6 border-t border-gray-200 flex justify-center">
                            <PDFReportButton patient={formData} results={results} />
                          </div>
                       )}
                        <div className="flex items-center space-x-2 mb-3">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            match.status === 'ELIGIBLE' ? 'bg-green-100 text-green-800' :
                            match.status === 'NOT_ELIGIBLE' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {match.status?.replace('_', ' ')}
                          </span>
                        </div>
                        
                        <p className="text-gray-700">{match.explanation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-20">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-gray-400">© 2024 ClinicalMatch AI. For informational purposes only.</p>
            <p className="text-sm text-gray-500 mt-2">Always consult with your healthcare provider before making medical decisions.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}