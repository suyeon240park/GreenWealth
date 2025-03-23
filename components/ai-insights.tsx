"use client"

import { useEffect, useState, useRef } from "react"
import { LightbulbIcon, Leaf, ShoppingCart, ChevronLeft, ChevronRight } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Home } from "lucide-react"

type Insight = {
  title: string
  description: string
  savingsAmount: string | null
  carbonReduction: string
  icon: string
}

export function AiInsights() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const getInsights = async () => {
      setIsLoading(true)
      /*
      try {
        const data = await fetchInsights()

        // If we have less than 6 insights, duplicate some to reach 6
        let extendedData = [...data]
        if (data.length < 6) {
          // Create additional insights by modifying existing ones
          const additionalInsights = data.map((insight, index) => ({
            ...insight,
            title: `Alternative ${insight.title}`,
            id: `extended-${index}`,
          }))
          extendedData = [...data, ...additionalInsights].slice(0, 6)
        }

        setInsights(extendedData)
      } catch (error) {
        console.error("Error fetching insights:", error)
        */
        // Fallback mock data with 6 insights
        setInsights([
          {
            title: "Reduce Transportation Emissions",
            description:
              "Switching to public transport twice a week could save you $120/month and reduce your carbon footprint by 30%.",
            savingsAmount: "$120/month",
            carbonReduction: "30%",
            icon: "transportation",
          },
          {
            title: "Grocery Shopping Tip",
            description:
              "Buying seasonal produce from local farmers markets can reduce your grocery carbon footprint by 25% and save approximately $15 per week.",
            savingsAmount: "$60/month",
            carbonReduction: "25%",
            icon: "grocery",
          },
          {
            title: "Online Shopping Consolidation",
            description:
              "Consolidating your Amazon orders to once per week instead of multiple orders can reduce packaging waste and delivery emissions by 40%.",
            savingsAmount: null,
            carbonReduction: "40%",
            icon: "shopping",
          },
          {
            title: "Reduce Home Energy Usage",
            description:
              "Lowering your thermostat by 2 degrees in winter can save you $45/month on heating costs and reduce your carbon footprint.",
            savingsAmount: "$45/month",
            carbonReduction: "15%",
            icon: "home",
          },
          {
            title: "Switch to LED Lighting",
            description:
              "Replacing your home's light bulbs with LED alternatives can save $10/month on electricity and reduce energy consumption.",
            savingsAmount: "$10/month",
            carbonReduction: "8%",
            icon: "home",
          },
          {
            title: "Reduce Food Waste",
            description:
              "Planning meals and properly storing food can save a family of four up to $150/month while reducing methane emissions from landfills.",
            savingsAmount: "$150/month",
            carbonReduction: "20%",
            icon: "grocery",
          },
        ])
      } /*finally {
        setIsLoading(false)
      }
    }

    getInsights()
  }, [])
*/
  }, [])

  // Change them
  const getIcon = (iconType: string) => {
    switch (iconType) {
      case "transportation":
        return <LightbulbIcon className="h-5 w-5 text-amber-500" />
      case "grocery":
        return <LightbulbIcon className="h-5 w-5 text-amber-500" />
      case "shopping":
        return <ShoppingCart className="h-5 w-5 text-green-500" />
      case "home":
        return <Home className="h-5 w-5 text-blue-500" />
      default:
        return <Leaf className="h-5 w-5 text-green-500" />
    }
  }

  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: -300, behavior: "smooth" })
    }
  }

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollBy({ left: 300, behavior: "smooth" })
    }
  }

  if (isLoading) {
    return <div className="flex justify-center p-4">Generating AI insights...</div>
  }

  return (
    <div className="relative">
      {/* Scroll buttons */}
      <div className="absolute left-0 top-1/2 z-10 -translate-y-1/2 md:flex hidden">
        <Button variant="outline" size="icon" className="rounded-full bg-background shadow-sm" onClick={scrollLeft}>
          <ChevronLeft className="h-5 w-5" />
          <span className="sr-only">Scroll left</span>
        </Button>
      </div>
      <div className="absolute right-0 top-1/2 z-10 -translate-y-1/2 md:flex hidden">
        <Button variant="outline" size="icon" className="rounded-full bg-background shadow-sm" onClick={scrollRight}>
          <ChevronRight className="h-5 w-5" />
          <span className="sr-only">Scroll right</span>
        </Button>
      </div>

      {/* Scrollable container */}
      <div
        ref={scrollContainerRef}
        className="flex space-x-4 overflow-x-auto pb-4 scrollbar-hide"
        style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
      >
        {insights.map((insight, index) => (
          <div key={index} className="rounded-lg border bg-card p-5 shadow-sm flex-shrink-0 w-[300px] md:w-[350px]">
            <div className="mb-3 flex items-center gap-2">
              {getIcon(insight.icon)}
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
        ))}
      </div>

      {/* Mobile scroll indicator */}
      <div className="flex justify-center space-x-1 mt-2 md:hidden">
        <div className="h-1 w-20 rounded-full bg-primary/30"></div>
      </div>
    </div>
  )
}


