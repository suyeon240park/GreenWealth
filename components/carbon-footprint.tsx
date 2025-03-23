"use client"

import { useEffect, useState } from "react"
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
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
  const [total, setTotal] = useState(0)
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
        const totalValue = carbonData.reduce((sum: number, item: CarbonData) => sum + item.value, 0)
        setTotal(totalValue)
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

  // Custom rendering for the pie chart labels to prevent overlap
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index, name }: any) => {
    const RADIAN = Math.PI / 180
    const radius = outerRadius * 1.1
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    // Only show label if segment is large enough
    if (percent < 0.05) return null

    return (
      <text
        x={x}
        y={y}
        fill={data[index].color}
        textAnchor={x > cx ? "start" : "end"}
        dominantBaseline="central"
        fontSize={12}
        fontWeight="500"
      >
        {name}
      </text>
    )
  }

  // Format the percentage for display
  const formatPercent = (percent: number) => {
    return `${(percent * 100).toFixed(0)}%`
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-center">
        <div className="text-center">
          <p className="text-sm text-muted-foreground">Total Carbon Footprint</p>
          <p className="text-3xl font-bold">{total.toFixed(1)} tons CO₂</p>
        </div>
      </div>

      <div className="h-[250px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomizedLabel}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number, name: string) => [
                `${name}: ${value.toFixed(1)} tons CO₂ (${((value / total) * 100).toFixed(0)}%)`
              ]}
              contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
