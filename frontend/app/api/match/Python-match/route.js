import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const patientData = await request.json();
    
    // Call your Python backend (assuming it's running on port 8000)
    const pythonResponse = await fetch('http://localhost:8000/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientData)
    });
    
    if (!pythonResponse.ok) {
      throw new Error('Python backend error');
    }
    
    const results = await pythonResponse.json();
    return NextResponse.json(results);
    
  } catch (error) {
    console.error('Backend connection error:', error);
    
    // Fallback to Groq-only approach if Python backend is down
    const { Groq } = await import('groq-sdk');
    const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
    
    // Your existing Groq logic here...
    return NextResponse.json({
      message: "Using fallback matching",
      matches: []
    });
  }
}