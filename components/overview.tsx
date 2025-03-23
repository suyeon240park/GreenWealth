"use client"

import { useEffect, useState } from "react"
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { fetchFinancialOverview } from "@/lib/plaid"
import { Skeleton } from "@/components/ui/skeleton"
import { usePlaid } from "@/lib/plaid-context"
import { BarChart3 } from "lucide-react"

interface OverviewData {
  name: string
  Spending: number
  Saving: number
  Income: number
}

export function Overview() {
  const [mounted, setMounted] = useState(false)
  const [data, setData] = useState<OverviewData[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { isConnected, clientId } = usePlaid()

  useEffect(() => {
    setMounted(true)

    const getOverviewData = async () => {
      if (!isConnected) return

      try {
        setLoading(true)
        const overviewData = await fetchFinancialOverview(clientId)
        setData(overviewData)
        setError(null)
      } catch (err) {
        console.error("Error fetching financial overview data:", err)
        setError("Failed to load financial overview data")
      } finally {
        setLoading(false)
      }
    }

    if (mounted && isConnected) {
      getOverviewData()
    }
  }, [mounted, isConnected, clientId])

  if (!mounted) return null

  if (!isConnected) {
    return (
      <div className="flex h-[350px] w-full flex-col items-center justify-center text-center">
        <BarChart3 className="mb-4 h-12 w-12 text-muted-foreground" />
        <h3 className="mb-2 text-lg font-medium">No Financial Data Available</h3>
        <p className="text-sm text-muted-foreground">Connect your bank account to see your financial overview.</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="h-[350px] w-full flex items-center justify-center">
        <Skeleton className="h-[300px] w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[350px] w-full flex items-center justify-center">
        <p className="text-muted-foreground">{error}</p>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="h-[350px] w-full flex items-center justify-center">
        <p className="text-muted-foreground">No financial overview data available yet.</p>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip 
          formatter={(value: number) => [`$${value.toLocaleString()}`]}
          contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
        />
        <Legend />
        <Bar dataKey="Income" fill="#10b981" />
        <Bar dataKey="Spending" fill="#f43f5e" />
        <Bar dataKey="Saving" fill="#3b82f6" />
      </BarChart>
    </ResponsiveContainer>
  )
}

