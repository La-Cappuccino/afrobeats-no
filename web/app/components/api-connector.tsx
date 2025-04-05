'use client';

import { useState, useEffect } from 'react';

// Function to fetch DJs with optional filtering
export const useDJs = (filters?: {
  genres?: string;
  minRating?: number;
  availability?: string;
}) => {
  const [djs, setDJs] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDJs = async () => {
      setLoading(true);
      setError(null);

      try {
        // Build query string
        let queryString = '';
        if (filters?.genres) queryString += `genres=${encodeURIComponent(filters.genres)}&`;
        if (filters?.minRating) queryString += `minRating=${encodeURIComponent(filters.minRating)}&`;
        if (filters?.availability) queryString += `availability=${encodeURIComponent(filters.availability)}&`;

        // Remove trailing ampersand if it exists
        if (queryString.endsWith('&')) {
          queryString = queryString.slice(0, -1);
        }

        // Fetch DJs
        const response = await fetch(`/api/djs${queryString ? `?${queryString}` : ''}`);

        if (!response.ok) {
          throw new Error('Failed to fetch DJs');
        }

        const data = await response.json();
        setDJs(data.djs || []);
      } catch (error) {
        console.error('Error fetching DJs:', error);
        setError('Failed to load DJs. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDJs();
  }, [filters?.genres, filters?.minRating, filters?.availability]);

  return { djs, loading, error };
};

// Function to fetch events with optional filtering
export const useEvents = (filters?: {
  genres?: string;
  featured?: boolean;
}) => {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      setLoading(true);
      setError(null);

      try {
        // Build query string
        let queryString = '';
        if (filters?.genres) queryString += `genres=${encodeURIComponent(filters.genres)}&`;
        if (filters?.featured !== undefined) queryString += `featured=${filters.featured}&`;

        // Remove trailing ampersand if it exists
        if (queryString.endsWith('&')) {
          queryString = queryString.slice(0, -1);
        }

        // Fetch events
        const response = await fetch(`/api/events${queryString ? `?${queryString}` : ''}`);

        if (!response.ok) {
          throw new Error('Failed to fetch events');
        }

        const data = await response.json();
        setEvents(data.events || []);
      } catch (error) {
        console.error('Error fetching events:', error);
        setError('Failed to load events. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [filters?.genres, filters?.featured]);

  return { events, loading, error };
};

// Function to submit a booking
export const useBooking = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<any | null>(null);

  const submitBooking = async (bookingData: {
    dj_name: string;
    date: string;
    time: string;
    hours: number;
    venue: string;
    details?: string;
  }) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/bookings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bookingData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to submit booking');
      }

      const data = await response.json();
      setSuccess(data);
      return data;
    } catch (error: any) {
      console.error('Error submitting booking:', error);
      setError(error.message || 'Failed to submit booking. Please try again later.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { submitBooking, loading, error, success };
};

// Function to submit a query to the agent system
export const useAgent = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<string | null>(null);

  const submitQuery = async (query: string, context?: any) => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, context }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process query');
      }

      const data = await response.json();
      setResponse(data.response || '');
      return data.response;
    } catch (error: any) {
      console.error('Error processing query:', error);
      setError(error.message || 'Failed to process query. Please try again later.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { submitQuery, loading, error, response };
};