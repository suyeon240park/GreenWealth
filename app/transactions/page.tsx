"use client"

import { useEffect, useState } from "react"
import { Avatar } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Car, Home, ShoppingBag, Utensils, CreditCard, Briefcase, Plane, BanknoteIcon } from "lucide-react"
import { fetchTransactions } from "@/lib/plaid"
import { Skeleton } from "@/components/ui/skeleton"
import { usePlaid } from "@/lib/plaid-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface Transaction {
  id: string
  name: string
  amount: string
  date: string
  category: string
  carbon: string
  impact: string
}

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { isConnected, clientId } = usePlaid()

  useEffect(() => {
    const getTransactions = async () => {
      if (!isConnected) return

      try {
        setLoading(true)
        const data = await fetchTransactions(clientId)
        setTransactions(data)
        setError(null)
      } catch (err) {
        console.error("Error fetching transactions:", err)
        setError("Failed to load transactions. Please try again later.")
      } finally {
        setLoading(false)
      }
    }

    if (isConnected) {
      getTransactions()
    }
  }, [isConnected, clientId])

  // Get icon based on transaction category
  const getIcon = (category: string) => {
    switch (category) {
      case "FOOD_AND_DRINK":
        return <Utensils className="h-4 w-4" />
      case "TRANSPORTATION":
        return <Car className="h-4 w-4" />
      case "GENERAL_MERCHANDISE":
        return <ShoppingBag className="h-4 w-4" />
      case "RENT_AND_UTILITIES":
        return <Home className="h-4 w-4" />
      case "GENERAL_SERVICES":
        return <Briefcase className="h-4 w-4" />
      case "TRAVEL":
        return <Plane className="h-4 w-4" />
      default:
        return <CreditCard className="h-4 w-4" />
    }
  }

  if (!isConnected) {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-center">
        <BanknoteIcon className="mb-4 h-12 w-12 text-muted-foreground" />
        <h3 className="mb-2 text-lg font-medium">No Bank Account Connected</h3>
        <p className="mb-4 text-sm text-muted-foreground">
          Connect your bank account to see your transaction history and carbon impact.
        </p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Skeleton className="h-9 w-9 rounded-full" />
              <div>
                <Skeleton className="h-4 w-32" />
                <Skeleton className="mt-1 h-3 w-24" />
              </div>
            </div>
            <div className="flex flex-col items-end">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="mt-1 h-3 w-20" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="py-4 text-center text-muted-foreground">
        <p>{error}</p>
        <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </div>
    )
  }

  if (transactions.length === 0) {
    return (
      <div className="py-4 text-center text-muted-foreground">
        No transactions found. Recent transactions will appear here.
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6">
      <Card>
        <CardHeader>
          <CardTitle>All Transactions</CardTitle>
          <CardDescription>View your complete transaction history and carbon impact</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {transactions.map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Avatar className="flex h-9 w-9 items-center justify-center rounded-full border bg-muted">
                    <div>{getIcon(transaction.category)}</div>
                  </Avatar>
                  <div>
                    <div className="font-medium">{transaction.name}</div>
                    <div className="text-sm text-muted-foreground">{transaction.date}</div>
                  </div>
                </div>
                <div className="flex flex-col items-end">
                  <div className="font-medium">{transaction.amount}</div>
                  <div className="flex items-center gap-1">
                    <span className="text-xs text-muted-foreground">{transaction.carbon}</span>
                    <Badge
                      variant={
                        transaction.impact === "low"
                          ? "outline"
                          : transaction.impact === "medium"
                            ? "secondary"
                            : "destructive"
                      }
                      className="text-xs"
                    >
                      {transaction.impact}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 