"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"

// Environment variable for client ID
const PLAID_CLIENT_ID = process.env.NEXT_PUBLIC_PLAID_CLIENT_ID || ""

interface PlaidContextType {
  isConnected: boolean
  setIsConnected: (connected: boolean) => void
  clientId: string
}

const PlaidContext = createContext<PlaidContextType>({
  isConnected: false,
  setIsConnected: () => {},
  clientId: PLAID_CLIENT_ID,
})

export const usePlaid = () => useContext(PlaidContext)

export function PlaidProvider({ children }: { children: ReactNode }) {
  const [isConnected, setIsConnected] = useState(false)
  const clientId = PLAID_CLIENT_ID

  // Check if user has already connected their account
  useEffect(() => {
    const checkConnection = async () => {
      try {
        // Try to fetch transactions as a way to check if connected
        const response = await fetch(`http://localhost:5000/api/transactions?client_id=${clientId}`)
        if (response.ok) {
          const data = await response.json()
          // If we get data back, user is connected
          setIsConnected(data && data.length > 0)
        }
      } catch (error) {
        // If error, user is not connected
        setIsConnected(false)
      }
    }

    checkConnection()
  }, [clientId])

  return <PlaidContext.Provider value={{ isConnected, setIsConnected, clientId }}>{children}</PlaidContext.Provider>
}

