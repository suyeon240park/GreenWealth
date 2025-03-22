"use client"

import { useState, useCallback } from "react"
import { usePlaidLink } from "react-plaid-link"
import { Button } from "@/components/ui/button"
import { createLinkToken, exchangePublicToken } from "@/lib/plaid"
import { useToast } from "@/hooks/use-toast"
import { usePlaid } from "@/lib/plaid-context"

interface PlaidLinkButtonProps {
  onSuccess?: () => void
}

export function PlaidLinkButton({ onSuccess }: PlaidLinkButtonProps) {
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()
  const { clientId, setIsConnected } = usePlaid()

  // Get a link token when the component mounts
  const getToken = useCallback(async () => {
    setLoading(true)
    try {
      const linkToken = await createLinkToken(clientId)
      setToken(linkToken)
    } catch (error) {
      console.error("Error getting link token:", error)
      toast({
        title: "Error",
        description: "Failed to initialize Plaid Link",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }, [clientId, toast])

  // Handle the Plaid Link success
  const onPlaidSuccess = useCallback(
    async (publicToken: string, metadata: any) => {
      try {
        await exchangePublicToken(publicToken, clientId)
        toast({
          title: "Success",
          description: "Your account was successfully connected!",
        })
        // Update global state to indicate user is connected
        setIsConnected(true)
        if (onSuccess) {
          onSuccess()
        }
      } catch (error) {
        console.error("Error exchanging public token:", error)
        toast({
          title: "Error",
          description: "Failed to connect your account",
          variant: "destructive",
        })
      }
    },
    [clientId, onSuccess, toast, setIsConnected],
  )

  // Configure the Plaid Link
  const { open, ready } = usePlaidLink({
    token,
    onSuccess: (public_token, metadata) => {
      onPlaidSuccess(public_token, metadata)
    },
    onExit: (err, metadata) => {
      console.log("Plaid Link exit:", err, metadata)
    },
  })

  // Handle the button click
  const handleClick = useCallback(() => {
    if (token) {
      open()
    } else {
      getToken()
    }
  }, [token, open, getToken])

  return (
    <Button onClick={handleClick} disabled={loading || (token && !ready)}>
      {loading ? "Loading..." : "Connect Bank Account"}
    </Button>
  )
}

