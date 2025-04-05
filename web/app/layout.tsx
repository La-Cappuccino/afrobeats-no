import '../styles/globals.css'
import type { Metadata } from 'next'
import { Sidebar } from '../components/Sidebar'

export const metadata: Metadata = {
  title: 'Afrobeats.no | DJ Booking & Events',
  description: 'Afrobeats and Amapiano DJ booking, event marketing, playlist curation, and DJ ratings in Oslo, Norway',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 p-6 md:p-10">{children}</main>
        </div>
      </body>
    </html>
  )
}