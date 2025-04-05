import { NextRequest, NextResponse } from 'next/server';

// API configurations
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.API_KEY;

export async function GET(request: NextRequest) {
  try {
    // Get query parameters
    const searchParams = request.nextUrl.searchParams;
    const genres = searchParams.get('genres');
    const featured = searchParams.get('featured');

    // Build query string
    let queryString = '';
    if (genres) queryString += `genres=${encodeURIComponent(genres)}&`;
    if (featured) queryString += `featured=${encodeURIComponent(featured)}&`;

    // Remove trailing ampersand if it exists
    if (queryString.endsWith('&')) {
      queryString = queryString.slice(0, -1);
    }

    // Prepare headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // Add API key if available
    if (API_KEY) {
      headers['X-API-Key'] = API_KEY;
    }

    // Forward the request to the FastAPI backend
    const url = `${API_URL}/events${queryString ? `?${queryString}` : ''}`;

    const response = await fetch(url, {
      method: 'GET',
      headers,
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
        { error: errorData.error || 'Error fetching events' },
        { status: response.status }
      );
    }

    // Return the API response
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching events:', error);

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    // Parse the incoming request body
    const body = await request.json();

    // Validate required fields
    const requiredFields = ['title', 'date', 'time', 'venue', 'location', 'description', 'genres'];
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json(
          { error: `${field} is required` },
          { status: 400 }
        );
      }
    }

    // Prepare headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // Add API key if available
    if (API_KEY) {
      headers['X-API-Key'] = API_KEY;
    }

    // Forward the request to the FastAPI backend
    const response = await fetch(`${API_URL}/events`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
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
        { error: errorData.error || 'Error creating event' },
        { status: response.status }
      );
    }

    // Return the API response
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error creating event:', error);

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
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}