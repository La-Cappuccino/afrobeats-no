import React from 'react'
import { FaMusic, FaCalendarAlt, FaStar, FaNewspaper, FaInstagram, FaChartLine, FaUserAlt } from 'react-icons/fa'

export function Sidebar() {
  return (
    <aside className="w-64 bg-primary bg-opacity-95 text-neutral p-6 hidden md:block">
      <div className="mb-10">
        <h1 className="text-2xl font-bold">Afrobeats.no</h1>
        <p className="text-neutral text-opacity-70 mt-[-5px]">Agent System</p>
      </div>
      
      <nav className="mb-8">
        <ul className="space-y-4">
          <li className="flex items-center space-x-3 p-2 rounded hover:bg-white hover:bg-opacity-10">
            <FaMusic className="text-secondary" />
            <span>DJ Booking</span>
          </li>
          <li className="flex items-center space-x-3 p-2 rounded hover:bg-white hover:bg-opacity-10">
            <FaCalendarAlt className="text-secondary" />
            <span>Events</span>
          </li>
          <li className="flex items-center space-x-3 p-2 rounded hover:bg-white hover:bg-opacity-10">
            <FaStar className="text-secondary" />
            <span>DJ Ratings</span>
          </li>
          <li className="flex items-center space-x-3 p-2 rounded hover:bg-white hover:bg-opacity-10">
            <FaNewspaper className="text-secondary" />
            <span>Content</span>
          </li>
          <li className="flex items-center space-x-3 p-2 rounded hover:bg-white hover:bg-opacity-10">
            <FaInstagram className="text-secondary" />
            <span>Social Media</span>
          </li>
          <li className="flex items-center space-x-3 p-2 rounded hover:bg-white hover:bg-opacity-10">
            <FaChartLine className="text-secondary" />
            <span>Analytics</span>
          </li>
          <li className="flex items-center space-x-3 p-2 rounded hover:bg-white hover:bg-opacity-10">
            <FaUserAlt className="text-secondary" />
            <span>Artists</span>
          </li>
        </ul>
      </nav>
      
      <div className="pt-6 border-t border-white border-opacity-10">
        <h3 className="text-lg font-semibold mb-2">Model Settings</h3>
        <div className="mb-4">
          <label className="block text-sm mb-1">AI Model</label>
          <select className="w-full bg-primary border border-white border-opacity-20 rounded p-2">
            <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
            <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
          </select>
        </div>
        
        <div className="mb-6">
          <label className="block text-sm mb-1">Creativity Level</label>
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.1" 
            defaultValue="0.7"
            className="w-full accent-secondary" 
          />
        </div>
      </div>
      
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-2">Security Status</h3>
        <div className="p-3 bg-green-900 bg-opacity-20 rounded-lg border border-green-500 border-opacity-30">
          <p className="font-medium">🔒 Secure Mode Enabled</p>
          <ul className="text-sm mt-1 space-y-1 text-neutral text-opacity-90">
            <li>• Input validation</li>
            <li>• API key protection</li>
            <li>• Error isolation</li>
          </ul>
        </div>
      </div>
      
      <div className="mt-12 text-center text-neutral text-opacity-50 text-xs">
        <p>© 2025 Afrobeats.no</p>
        <p>Oslo, Norway</p>
      </div>
    </aside>
  )
}