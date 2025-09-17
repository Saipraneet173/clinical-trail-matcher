import { NextResponse } from 'next/server';

// Rate limiting storage
const userRequests = new Map();
const MAX_REQUESTS_PER_IP = 10; // Allow 10 free searches per IP

export async function POST(request) {
  try {
    // Get user IP for rate limiting
    const ip = request.headers.get('x-forwarded-for') ||
               request.headers.get('x-real-ip') ||
               'unknown';

    // Check rate limit
    const userCount = userRequests.get(ip) || 0;
    if (userCount >= MAX_REQUESTS_PER_IP) {
      return NextResponse.json({
        message: "You've reached the free usage limit (10 searches). Please contact for unlimited access.",
        matches: []
      }, { status: 429 });
    }

    const patientData = await request.json();

    // Check if we have Groq API key
    const hasGroqKey = !!process.env.GROQ_API_KEY;

    if (!hasGroqKey) {
      // Demo mode without Groq
      return NextResponse.json({
        message: "Running in demo mode (no API key configured)",
        matches: [
          {
            nct_id: "NCT-DEMO-001",
            title: "Demo Trial for " + patientData.conditions,
            status: "NEEDS_REVIEW",
            explanation: "This is a demo result. Configure Groq API for real matching."
          }
        ]
      });
    }

    // Import Groq only if we have the key
    const { Groq } = await import('groq-sdk');
    const groq = new Groq({
      apiKey: process.env.GROQ_API_KEY
    });

    // Your existing trial data
    const SAMPLE_TRIALS = [
      {
        nct_id: "NCT04743505",
        title: "Study of Novel Therapy for Lung Cancer",
        conditions: "Non-Small Cell Lung Cancer",
        phase: "Phase 3"
      },
      {
        nct_id: "NCT05745350",
        title: "Diabetes Management Trial",
        conditions: "Type 2 Diabetes",
        phase: "Phase 2"
      }
    ];

    // Create analysis prompt
    const prompt = `Analyze if this patient is eligible for clinical trials:
    Patient: Age ${patientData.age}, ${patientData.gender},
    Conditions: ${patientData.conditions}
    Medications: ${patientData.medications || 'None'}
    Biomarkers: ${patientData.biomarkers || 'None'}

    Available trials: ${JSON.stringify(SAMPLE_TRIALS)}

    Return a JSON array with eligibility status for each trial.`;

    const completion = await groq.chat.completions.create({
      messages: [{
        role: 'user',
        content: prompt
      }],
      model: 'llama-3.2-3b-preview',
      max_tokens: 500,
      temperature: 0.3
    });

    // Increment usage counter after successful API call
    userRequests.set(ip, userCount + 1);

    return NextResponse.json({
      message: "Analysis complete",
      matches: [
        {
          nct_id: "NCT04743505",
          title: "Lung Cancer Study",
          status: "ELIGIBLE",
          explanation: completion.choices[0].message.content.slice(0, 200)
        }
      ]
    });

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}