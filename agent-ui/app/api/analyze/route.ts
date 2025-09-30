import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { feedback } = await request.json();
    
    // Call the backend agent service
    const backendUrl = process.env.NEXT_PUBLIC_AGENT_SERVICE_URL || 'http://localhost:8000';
    
    const response = await fetch(`${backendUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        feedback
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`);
    }

    const data = await response.json();
    
    if (data.status === 'error') {
      throw new Error(data.error);
    }
    
    return NextResponse.json(data.result || data);

  } catch (error) {
    console.error('Analysis error:', error);
    return NextResponse.json(
      { error: 'Failed to analyze feedback' },
      { status: 500 }
    );
  }
}