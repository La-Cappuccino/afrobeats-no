'use client'

import { useState, useEffect } from 'react'
import { FiFilter, FiStar, FiClock, FiCalendar, FiMapPin, FiMessageSquare } from 'react-icons/fi'
import { useDJs, useBooking } from '../components/api-connector'

export default function DJBooking() {
  // State for filters
  const [selectedGenres, setSelectedGenres] = useState<string[]>([])
  const [selectedDay, setSelectedDay] = useState<string>('')
  const [minRating, setMinRating] = useState<number>(0)
  const [selectedDJ, setSelectedDJ] = useState<any | null>(null)

  // State for booking form
  const [bookingForm, setBookingForm] = useState({
    date: '',
    time: '',
    hours: 2,
    venue: '',
    details: ''
  })

  // State for UI
  const [showBookingModal, setShowBookingModal] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  // Get DJs from API
  const { djs, loading, error } = useDJs({
    genres: selectedGenres.length > 0 ? selectedGenres.join(',') : undefined,
    minRating: minRating > 0 ? minRating : undefined,
    availability: selectedDay || undefined
  })

  // Use booking hook
  const {
    submitBooking,
    loading: bookingLoading,
    error: bookingError,
    success: bookingSuccess
  } = useBooking()

  // Set success message when booking is successful
  useEffect(() => {
    if (bookingSuccess) {
      setSuccessMessage(`Your booking with ${selectedDJ?.name} has been submitted! Booking ID: ${bookingSuccess.booking_id}`)
      setShowBookingModal(false)
      setSelectedDJ(null)
      setBookingForm({
        date: '',
        time: '',
        hours: 2,
        venue: '',
        details: ''
      })
    }
  }, [bookingSuccess, selectedDJ])

  // Helper function to toggle genre selection
  const toggleGenre = (genre: string) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter(g => g !== genre))
    } else {
      setSelectedGenres([...selectedGenres, genre])
    }
  }

  // Helper function to reset filters
  const resetFilters = () => {
    setSelectedGenres([])
    setSelectedDay('')
    setMinRating(0)
  }

  // Handle booking form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setBookingForm(prev => ({
      ...prev,
      [name]: name === 'hours' ? parseInt(value) : value
    }))
  }

  // Handle booking submission
  const handleBookingSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedDJ) return

    const bookingData = {
      dj_name: selectedDJ.name,
      date: bookingForm.date,
      time: bookingForm.time,
      hours: bookingForm.hours,
      venue: bookingForm.venue,
      details: bookingForm.details
    }

    await submitBooking(bookingData)
  }

  // Extract all available genres from DJs
  const allGenres = Array.from(new Set(djs.flatMap(dj => dj.genres))).sort()

  // Extract all available days
  const allDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">Book a DJ</h1>
        <p className="text-xl mb-8 opacity-80">Find and book the perfect DJ for your event</p>

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
              <div className="flex flex-wrap gap-2">
                {allGenres.map(genre => (
                  <button
                    key={genre}
                    onClick={() => toggleGenre(genre)}
                    className={`px-3 py-1 rounded-full text-sm ${
                      selectedGenres.includes(genre)
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {genre}
                  </button>
                ))}
              </div>
            </div>

            {/* Day filter */}
            <div>
              <h3 className="text-lg mb-2">Availability</h3>
              <select
                value={selectedDay}
                onChange={(e) => setSelectedDay(e.target.value)}
                className="w-full bg-gray-800 text-white rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Any day</option>
                {allDays.map(day => (
                  <option key={day} value={day}>{day}</option>
                ))}
              </select>
            </div>

            {/* Rating filter */}
            <div>
              <h3 className="text-lg mb-2">Minimum Rating</h3>
              <div className="flex items-center">
                <input
                  type="range"
                  min="0"
                  max="5"
                  step="0.1"
                  value={minRating}
                  onChange={(e) => setMinRating(parseFloat(e.target.value))}
                  className="w-full"
                />
                <span className="ml-2 min-w-[3rem] flex">
                  {minRating > 0 ? (
                    <>
                      {minRating.toFixed(1)}
                      <FiStar className="ml-1" />
                    </>
                  ) : 'Any'}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={resetFilters}
            className="mt-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm"
          >
            Reset Filters
          </button>
        </div>

        {/* Success message */}
        {successMessage && (
          <div className="bg-green-600/80 text-white p-4 rounded-lg mb-6">
            {successMessage}
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-600/80 text-white p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* DJ Listings */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Available DJs</h2>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
            </div>
          ) : djs.length === 0 ? (
            <div className="bg-black/30 backdrop-blur-md rounded-xl p-8 text-center">
              <p>No DJs found matching your filters. Try adjusting your criteria.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {djs.map((dj) => (
                <div
                  key={dj.id}
                  className="bg-black/30 backdrop-blur-md rounded-xl overflow-hidden hover:shadow-xl transition-all"
                >
                  <div
                    className="h-48 bg-cover bg-center"
                    style={{ backgroundImage: `url(${dj.image || '/images/dj-placeholder.jpg'})` }}
                  ></div>
                  <div className="p-4">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-xl font-bold">{dj.name}</h3>
                      <div className="flex items-center bg-purple-700 px-2 py-1 rounded text-sm">
                        {dj.rating}
                        <FiStar className="ml-1" />
                      </div>
                    </div>

                    <div className="mb-2 flex flex-wrap gap-1">
                      {dj.genres.map((genre: string) => (
                        <span key={genre} className="bg-gray-800 text-xs px-2 py-1 rounded">
                          {genre}
                        </span>
                      ))}
                    </div>

                    <p className="text-gray-300 text-sm mb-3">{dj.bio}</p>

                    <div className="flex justify-between items-center text-sm mb-4">
                      <div>
                        <strong>${dj.hourly_rate}</strong>/hour
                      </div>
                      <div>
                        Available: {dj.availability.join(', ')}
                      </div>
                    </div>

                    <button
                      onClick={() => {
                        setSelectedDJ(dj)
                        setShowBookingModal(true)
                      }}
                      className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-md transition-colors"
                    >
                      Book Now
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Booking Modal */}
      {showBookingModal && selectedDJ && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-xl max-w-md w-full p-6 relative">
            <button
              onClick={() => setShowBookingModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              ✕
            </button>

            <h2 className="text-2xl font-bold mb-4">Book {selectedDJ.name}</h2>

            {bookingError && (
              <div className="bg-red-600/80 text-white p-3 rounded-lg mb-4">
                {bookingError}
              </div>
            )}

            <form onSubmit={handleBookingSubmit}>
              <div className="mb-4">
                <label className="block text-gray-300 mb-1">
                  <FiCalendar className="inline mr-2" />
                  Date
                </label>
                <input
                  type="date"
                  name="date"
                  value={bookingForm.date}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-gray-800 text-white rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div className="mb-4">
                <label className="block text-gray-300 mb-1">
                  <FiClock className="inline mr-2" />
                  Start Time
                </label>
                <input
                  type="time"
                  name="time"
                  value={bookingForm.time}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-gray-800 text-white rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div className="mb-4">
                <label className="block text-gray-300 mb-1">
                  <FiClock className="inline mr-2" />
                  Hours
                </label>
                <select
                  name="hours"
                  value={bookingForm.hours}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-gray-800 text-white rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {[1, 2, 3, 4, 5, 6].map(h => (
                    <option key={h} value={h}>{h} hour{h > 1 ? 's' : ''}</option>
                  ))}
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-gray-300 mb-1">
                  <FiMapPin className="inline mr-2" />
                  Venue
                </label>
                <input
                  type="text"
                  name="venue"
                  value={bookingForm.venue}
                  onChange={handleInputChange}
                  required
                  placeholder="Venue name and address"
                  className="w-full bg-gray-800 text-white rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div className="mb-4">
                <label className="block text-gray-300 mb-1">
                  <FiMessageSquare className="inline mr-2" />
                  Additional Details
                </label>
                <textarea
                  name="details"
                  value={bookingForm.details}
                  onChange={handleInputChange}
                  placeholder="Type of event, expected attendance, etc."
                  rows={3}
                  className="w-full bg-gray-800 text-white rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                ></textarea>
              </div>

              <div className="mb-4 bg-gray-800/50 p-3 rounded-md text-sm">
                <p className="font-bold">Estimated Total: ${selectedDJ.hourly_rate * bookingForm.hours}</p>
                <p className="text-gray-400">Final pricing may vary based on specific requirements</p>
              </div>

              <button
                type="submit"
                disabled={bookingLoading}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-md transition-colors disabled:bg-purple-900 disabled:cursor-not-allowed"
              >
                {bookingLoading ? 'Submitting...' : 'Submit Booking Request'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}