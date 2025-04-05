'use client'

import { useState, useEffect } from 'react'
import { FiFilter, FiCalendar, FiMapPin, FiMusic, FiStar } from 'react-icons/fi'
import { motion } from 'framer-motion'
import { format, parseISO } from 'date-fns'
import { useEvents } from '../components/api-connector'

export default function EventsPage() {
  // State for filters
  const [selectedGenre, setSelectedGenre] = useState<string>('')
  const [showFeaturedOnly, setShowFeaturedOnly] = useState<boolean>(false)
  const [favoriteEvents, setFavoriteEvents] = useState<number[]>([])

  // Get events from API
  const { events, loading, error } = useEvents({
    genres: selectedGenre || undefined,
    featured: showFeaturedOnly || undefined
  })

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      const date = parseISO(dateString)
      return format(date, 'EEEE, MMMM d, yyyy')
    } catch (e) {
      return dateString
    }
  }

  // Toggle favorite status
  const toggleFavorite = (eventId: number) => {
    if (favoriteEvents.includes(eventId)) {
      setFavoriteEvents(favoriteEvents.filter(id => id !== eventId))
    } else {
      setFavoriteEvents([...favoriteEvents, eventId])
    }
  }

  // Get all unique genres
  const allGenres = Array.from(
    new Set(events.flatMap(event => event.genres))
  ).sort()

  // Reset filters
  const resetFilters = () => {
    setSelectedGenre('')
    setShowFeaturedOnly(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-3">Afrobeats & Amapiano Events</h1>
          <p className="text-xl opacity-80 max-w-3xl mx-auto">
            Discover the best Afrobeats and Amapiano events happening in Oslo
          </p>
        </div>

        {/* Filters section */}
        <div className="bg-black/30 backdrop-blur-md rounded-xl p-6 mb-8">
          <div className="flex items-center mb-4">
            <FiFilter className="mr-2" />
            <h2 className="text-xl font-semibold">Filters</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Genre filter */}
            <div>
              <h3 className="text-lg mb-2">Genres</h3>
              <select
                value={selectedGenre}
                onChange={(e) => setSelectedGenre(e.target.value)}
                className="w-full bg-gray-800 text-white rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All Genres</option>
                {allGenres.map(genre => (
                  <option key={genre} value={genre}>{genre}</option>
                ))}
              </select>
            </div>

            {/* Featured filter */}
            <div className="flex items-center">
              <label className="flex items-center cursor-pointer">
                <div className="relative">
                  <input
                    type="checkbox"
                    className="sr-only"
                    checked={showFeaturedOnly}
                    onChange={() => setShowFeaturedOnly(!showFeaturedOnly)}
                  />
                  <div className="block bg-gray-800 w-14 h-8 rounded-full"></div>
                  <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition ${
                    showFeaturedOnly ? 'transform translate-x-6' : ''
                  }`}></div>
                </div>
                <div className="ml-3 text-white font-medium">
                  Featured Events Only
                </div>
              </label>
            </div>

            {/* Reset button */}
            <div className="flex items-center">
              <button
                onClick={resetFilters}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm"
              >
                Reset Filters
              </button>
            </div>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-600/80 text-white p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Loading indicator */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
          </div>
        ) : (
          <>
            {/* Featured Events */}
            {events.some(event => event.featured) && (
              <div className="mb-12">
                <h2 className="text-2xl font-bold mb-6 flex items-center">
                  <FiStar className="mr-2 text-yellow-400" />
                  Featured Events
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {events
                    .filter(event => event.featured)
                    .map(event => (
                      <motion.div
                        key={event.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="bg-gradient-to-br from-purple-800 to-indigo-900 rounded-xl overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-300"
                      >
                        <div
                          className="h-64 bg-cover bg-center relative"
                          style={{ backgroundImage: `url(${event.image || '/images/event-placeholder.jpg'})` }}
                        >
                          <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
                            <h3 className="text-2xl font-bold text-white">{event.title}</h3>
                            <div className="flex items-center mt-2">
                              <FiCalendar className="mr-2 text-purple-300" />
                              <span>{formatDate(event.date)}</span>
                            </div>
                          </div>

                          <button
                            onClick={() => toggleFavorite(event.id)}
                            className="absolute top-4 right-4 h-10 w-10 rounded-full bg-black/50 flex items-center justify-center hover:bg-black/80 transition-colors"
                          >
                            {favoriteEvents.includes(event.id) ? (
                              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#ff4081" stroke="#ff4081" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                              </svg>
                            ) : (
                              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                              </svg>
                            )}
                          </button>
                        </div>

                        <div className="p-6">
                          <div className="flex flex-wrap gap-2 mb-4">
                            {event.genres.map(genre => (
                              <span key={genre} className="bg-purple-700/50 text-white px-3 py-1 rounded-full text-sm">
                                {genre}
                              </span>
                            ))}
                          </div>

                          <p className="text-gray-300 mb-4 line-clamp-3">{event.description}</p>

                          <div className="flex justify-between items-center">
                            <div className="flex items-center">
                              <FiMapPin className="mr-2 text-purple-300" />
                              <span>{event.venue}, {event.location}</span>
                            </div>
                            <div>
                              <a
                                href={event.ticket_link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md inline-block transition-colors"
                              >
                                Get Tickets
                              </a>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                </div>
              </div>
            )}

            {/* All Events */}
            <div>
              <h2 className="text-2xl font-bold mb-6">All Events</h2>

              {events.length === 0 ? (
                <div className="bg-black/30 backdrop-blur-md rounded-xl p-8 text-center">
                  <p>No events found matching your filters. Try adjusting your criteria.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {events.map(event => (
                    <motion.div
                      key={event.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: event.id * 0.1 }}
                      className="bg-black/30 backdrop-blur-md rounded-xl overflow-hidden hover:shadow-xl transition-all"
                    >
                      <div
                        className="h-48 bg-cover bg-center"
                        style={{ backgroundImage: `url(${event.image || '/images/event-placeholder.jpg'})` }}
                      >
                        <button
                          onClick={() => toggleFavorite(event.id)}
                          className="m-3 h-8 w-8 rounded-full bg-black/50 flex items-center justify-center hover:bg-black/80 transition-colors"
                        >
                          {favoriteEvents.includes(event.id) ? (
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="#ff4081" stroke="#ff4081" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                            </svg>
                          ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                            </svg>
                          )}
                        </button>
                      </div>
                      <div className="p-4">
                        <h3 className="text-xl font-bold mb-2">{event.title}</h3>

                        <div className="flex flex-wrap gap-1 mb-2">
                          {event.genres.map(genre => (
                            <span key={genre} className="bg-gray-800 text-xs px-2 py-1 rounded">
                              {genre}
                            </span>
                          ))}
                        </div>

                        <div className="text-sm space-y-1 mb-3">
                          <div className="flex items-center">
                            <FiCalendar className="mr-2 opacity-70" />
                            <span>{formatDate(event.date)} at {event.time}</span>
                          </div>
                          <div className="flex items-center">
                            <FiMapPin className="mr-2 opacity-70" />
                            <span>{event.venue}, {event.location}</span>
                          </div>
                        </div>

                        <div className="flex justify-between items-center">
                          <div className="text-sm">
                            {event.ticket_price ? (
                              <span>From ${event.ticket_price}</span>
                            ) : (
                              <span>Free entry</span>
                            )}
                          </div>
                          <a
                            href={event.ticket_link || '#'}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded transition-colors"
                          >
                            Tickets
                          </a>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}