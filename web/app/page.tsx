'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { FaMusic, FaCalendarAlt, FaStar, FaSearch, FaSpinner } from 'react-icons/fa'
import { MdPlaylistAdd } from 'react-icons/md'

export default function Home() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [response, setResponse] = useState('')
  const [error, setError] = useState('')
  const [agentsUsed, setAgentsUsed] = useState<string[]>([])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setResponse('')
    setError('')
    setAgentsUsed([])

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      })

      if (!res.ok) {
        throw new Error(`Error: ${res.status} ${res.statusText}`)
      }

      const data = await res.json()
      setResponse(data.response)
      setAgentsUsed(data.agents_used || [])
    } catch (error) {
      console.error('Error:', error)
      setError('Sorry, there was an error processing your request. Please try again later.')
    } finally {
      setIsLoading(false)
    }
  }

  // Example queries for quick selection
  const exampleQueries = [
    "Find me an Amapiano DJ for a party next weekend in Oslo",
    "What are the upcoming Afrobeats events in Oslo this month?",
    "Create a playlist of the top 10 Afrobeats songs of 2023",
    "Who are the highest rated DJs for Nigerian music in Oslo?"
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section with Parallax Effect */}
      <motion.div
        className="relative h-64 sm:h-80 md:h-96 mb-12 rounded-3xl overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-primary/90 to-primary/40 z-10"></div>
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3')"
          }}
        ></div>
        <div className="absolute inset-0 z-20 flex flex-col justify-center px-8 md:px-16">
          <h1 className="text-3xl md:text-5xl font-bold text-white mb-4">
            Discover Afrobeats &<br className="hidden md:block" />
            Amapiano in Oslo
          </h1>
          <p className="text-lg text-white/80 max-w-md mb-8">
            Find DJs, events, and curated playlists for the best African music experience
          </p>

          <form onSubmit={handleSubmit} className="relative max-w-2xl">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Find me an Amapiano DJ for a party next weekend in Oslo"
              className="input-field text-dark pr-14"
              aria-label="Search query"
            />
            <button
              type="submit"
              className="absolute right-2 top-2 bg-primary text-white p-2 rounded-full hover:bg-secondary hover:text-dark transition-colors"
              disabled={isLoading}
              aria-label="Submit search"
            >
              {isLoading ? (
                <FaSpinner className="w-6 h-6 animate-spin" />
              ) : (
                <FaSearch className="w-6 h-6" />
              )}
            </button>
          </form>
        </div>
      </motion.div>

      {/* Example Queries */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Try asking about:</h2>
        <div className="flex flex-wrap gap-2">
          {exampleQueries.map((exampleQuery, index) => (
            <button
              key={index}
              onClick={() => setQuery(exampleQuery)}
              className="bg-primary/10 hover:bg-primary/20 text-primary px-4 py-2 rounded-full text-sm transition-colors"
            >
              {exampleQuery}
            </button>
          ))}
        </div>
      </div>

      {/* Response Display */}
      {(response || error) && (
        <motion.div
          className="dashboard-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-xl font-semibold mb-4">
            {error ? 'Error' : 'Response'}
          </h2>

          {error ? (
            <p className="text-red-500">{error}</p>
          ) : (
            <>
              <p className="whitespace-pre-line mb-4">{response}</p>

              {agentsUsed.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white border-opacity-10">
                  <h3 className="text-sm font-medium mb-2">Powered by agents:</h3>
                  <div className="flex flex-wrap gap-2">
                    {agentsUsed.map((agent, index) => (
                      <span key={index} className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs">
                        {agent}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </motion.div>
      )}

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <motion.div
          className="dashboard-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="flex items-center mb-4">
            <div className="bg-secondary/10 p-3 rounded-full mr-4">
              <FaMusic className="text-secondary text-xl" />
            </div>
            <h2 className="text-xl font-semibold">DJ Booking</h2>
          </div>
          <p className="text-gray-600 mb-4">
            Book top Afrobeats and Amapiano DJs for your events in Oslo
          </p>
          <a href="/booking" className="text-primary font-semibold hover:text-secondary transition-colors">
            Explore DJs →
          </a>
        </motion.div>

        <motion.div
          className="dashboard-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="flex items-center mb-4">
            <div className="bg-secondary/10 p-3 rounded-full mr-4">
              <FaCalendarAlt className="text-secondary text-xl" />
            </div>
            <h2 className="text-xl font-semibold">Upcoming Events</h2>
          </div>
          <p className="text-gray-600 mb-4">
            Discover Afrobeats and Amapiano events happening in Oslo
          </p>
          <a href="/events" className="text-primary font-semibold hover:text-secondary transition-colors">
            View Events →
          </a>
        </motion.div>

        <motion.div
          className="dashboard-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="flex items-center mb-4">
            <div className="bg-secondary/10 p-3 rounded-full mr-4">
              <MdPlaylistAdd className="text-secondary text-xl" />
            </div>
            <h2 className="text-xl font-semibold">Playlists</h2>
          </div>
          <p className="text-gray-600 mb-4">
            Discover and create curated playlists of Afrobeats and Amapiano music
          </p>
          <a href="/playlists" className="text-primary font-semibold hover:text-secondary transition-colors">
            Explore Playlists →
          </a>
        </motion.div>
      </div>

      {/* Music Insights Section */}
      <motion.div
        className="dashboard-card mt-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <h2 className="text-xl font-semibold mb-4">Trending in Oslo</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gradient-to-r from-tertiary/20 to-tertiary/5 p-4 rounded-xl">
            <h3 className="font-medium mb-2">Top Genres This Month</h3>
            <ol className="list-decimal list-inside space-y-1">
              <li>Amapiano</li>
              <li>Afrobeats</li>
              <li>Afro House</li>
              <li>Afro Fusion</li>
              <li>Afro Pop</li>
            </ol>
          </div>
          <div className="bg-gradient-to-r from-secondary/20 to-secondary/5 p-4 rounded-xl">
            <h3 className="font-medium mb-2">Upcoming Notable Events</h3>
            <ul className="space-y-1">
              <li>• Oslo Afro Night - May 15</li>
              <li>• Piano Sundays - Every Sunday</li>
              <li>• African Vibes Festival - June 10-12</li>
              <li>• Afro House Sessions - Last Friday monthly</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  )
}