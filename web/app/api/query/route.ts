import { NextRequest, NextResponse } from 'next/server';

// API configurations
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.API_KEY;

export async function POST(request: NextRequest) {
  try {
    // Parse the incoming request body
    const body = await request.json();

    if (!body.query) {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      );
    }

    // Prepare headers for the API request
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // Add API key if available
    if (API_KEY) {
      headers['X-API-Key'] = API_KEY;
    }

    // Forward the request to the FastAPI backend
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        query: body.query,
        context: body.context || {},
      }),
      cache: 'no-store',
    });

    // Check if the request was successful
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));

      console.error('API error:', {
        status: response.status,
        statusText: response.statusText,
        data: errorData,
      });

      return NextResponse.json(
        { error: errorData.error || 'Error processing query' },
        { status: response.status }
      );
    }

    // Return the API response
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error processing query:', error);

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}