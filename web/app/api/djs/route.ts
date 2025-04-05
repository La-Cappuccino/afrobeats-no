import { NextRequest, NextResponse } from 'next/server';

// API configurations
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.API_KEY;

export async function GET(request: NextRequest) {
  try {
    // Get query parameters
    const searchParams = request.nextUrl.searchParams;
    const genres = searchParams.get('genres');
    const minRating = searchParams.get('minRating');
    const availability = searchParams.get('availability');

    // Build query string
    let queryString = '';
    if (genres) queryString += `genres=${encodeURIComponent(genres)}&`;
    if (minRating) queryString += `min_rating=${encodeURIComponent(minRating)}&`;
    if (availability) queryString += `availability=${encodeURIComponent(availability)}&`;

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
    const url = `${API_URL}/djs${queryString ? `?${queryString}` : ''}`;

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
        { error: errorData.error || 'Error fetching DJs' },
        { status: response.status }
      );
    }

    // Return the API response
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching DJs:', error);

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
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}