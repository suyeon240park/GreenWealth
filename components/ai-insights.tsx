"use client"

import { useEffect, useState } from "react"
import { Car, Utensils, ShoppingBag, Home, Plane, Wrench, Briefcase, LightbulbIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"

type Insight = {
  title: string
  description: string
  savingsAmount: string | null
  carbonReduction: string
  category: string
}

export function AiInsights() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/ai-insights');
        if (!response.ok) {
          throw new Error('Failed to fetch recommendations');
        }
        const data = await response.json();
        setInsights(data);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case "transportation":
        return <Car className="h-5 w-5 text-blue-500" />
      case "travel":
        return <Plane className="h-5 w-5 text-purple-500" />
      case "food and drinks":
        return <Utensils className="h-5 w-5 text-orange-500" />
      case "general merchandise":
        return <ShoppingBag className="h-5 w-5 text-pink-500" />
      case "home improvement":
        return <Wrench className="h-5 w-5 text-yellow-500" />
      case "rent and utilities":
        return <Home className="h-5 w-5 text-green-500" />
      case "general services":
        return <Briefcase className="h-5 w-5 text-indigo-500" />
      default:
        return <LightbulbIcon className="h-5 w-5 text-amber-500" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-4 space-x-1">
        <span>Generating AI insights</span>
        <span className="animate-bounce">.</span>
        <span className="animate-bounce delay-100">.</span>
        <span className="animate-bounce delay-200">.</span>
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {insights.length === 0 ? (
        <div className="col-span-3 text-center py-8">
          <p className="text-muted-foreground">Connect your bank account to get personalized insights.</p>
        </div>
      ) : (
        insights.map((insight, index) => (
          <div key={index} className="rounded-lg border bg-card p-5 shadow-sm">
            <div className="mb-3 flex items-center gap-2">
              {getCategoryIcon(insight.category)}
              <h3 className="font-semibold">{insight.title}</h3>
            </div>
            <p className="mb-4 text-sm text-muted-foreground">{insight.description}</p>
            <div className="flex flex-wrap gap-2">
              {insight.savingsAmount && (
                <Badge variant="outline" className="bg-green-50 text-green-700 hover:bg-green-100 hover:text-green-800">
                  Save {insight.savingsAmount}
                </Badge>
              )}
              <Badge variant="outline" className="bg-green-50 text-green-700 hover:bg-green-100 hover:text-green-800">
                Reduce CO<sub>2</sub> by {insight.carbonReduction}
              </Badge>
            </div>
          </div>
        ))
      )}
    </div>
  )
}

