"use client"

import { useEffect, useState } from "react"
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
import { fetchCarbonFootprint } from "@/lib/plaid"
import { Skeleton } from "@/components/ui/skeleton"
import { usePlaid } from "@/lib/plaid-context"
import { Leaf } from "lucide-react"

interface CarbonData {
  name: string
  value: number
  color: string
}

export function CarbonFootprint() {
  const [mounted, setMounted] = useState(false)
  const [data, setData] = useState<CarbonData[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { isConnected, clientId } = usePlaid()

  useEffect(() => {
    setMounted(true)

    const getCarbonData = async () => {
      if (!isConnected) return

      try {
        setLoading(true)
        const carbonData = await fetchCarbonFootprint(clientId)
        setData(carbonData)
        setError(null)
      } catch (err) {
        console.error("Error fetching carbon footprint data:", err)
        setError("Failed to load carbon footprint data")
      } finally {
        setLoading(false)
      }
    }

    if (mounted && isConnected) {
      getCarbonData()
    }
  }, [mounted, isConnected, clientId])

  if (!mounted) return null

  if (!isConnected) {
    return (
      <div className="flex h-[300px] w-full flex-col items-center justify-center text-center">
        <Leaf className="mb-4 h-12 w-12 text-muted-foreground" />
        <h3 className="mb-2 text-lg font-medium">No Carbon Data Available</h3>
        <p className="text-sm text-muted-foreground">
          Connect your bank account to see your carbon footprint analysis.
        </p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="h-[300px] w-full flex items-center justify-center">
        <Skeleton className="h-[200px] w-[200px] rounded-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[300px] w-full flex items-center justify-center">
        <p className="text-muted-foreground">{error}</p>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="h-[300px] w-full flex items-center justify-center">
        <p className="text-muted-foreground">No carbon footprint data available yet.</p>
      </div>
    )
  }

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => [`${value} tons CO₂`, "Carbon Footprint"]} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

