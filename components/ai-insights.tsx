import { LightbulbIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function AiInsights() {
  const insights = [
    {
      id: "i1",
      title: "Reduce Transportation Emissions",
      description:
        "Switching to public transport twice a week could save you $120/month and reduce your carbon footprint by 30%.",
      savingsAmount: "$120/month",
      carbonReduction: "30%",
      icon: "transportation",
    },
    {
      id: "i2",
      title: "Grocery Shopping Tip",
      description:
        "Buying seasonal produce from local farmers markets can reduce your grocery carbon footprint by 25% and save approximately $15 per week.",
      savingsAmount: "$60/month",
      carbonReduction: "25%",
      icon: "grocery",
    },
    {
      id: "i3",
      title: "Online Shopping Consolidation",
      description:
        "Consolidating your Amazon orders to once per week instead of multiple orders can reduce packaging waste and delivery emissions by 40%.",
      savingsAmount: null,
      carbonReduction: "40%",
      icon: "shopping",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {insights.map((insight) => (
        <div key={insight.id} className="rounded-lg border bg-card p-5 shadow-sm">
          <div className="mb-3 flex items-center gap-2">
            {insight.icon === "transportation" && <LightbulbIcon className="h-5 w-5 text-amber-500" />}
            {insight.icon === "grocery" && <LightbulbIcon className="h-5 w-5 text-amber-500" />}
            {insight.icon === "shopping" && <Leaf className="h-5 w-5 text-green-500" />}
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
  )
}

// Import Leaf icon at the top
import { Leaf } from "lucide-react"

