import Link from "next/link"
import { ArrowRight } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Overview } from "@/components/overview"
import { RecentTransactions } from "@/components/recent-transactions"
import { CarbonFootprint } from "@/components/carbon-footprint"
import { AiInsights } from "@/components/ai-insights"
import { ChatButton } from "@/components/chat-button"
import { PlaidLinkButton } from "@/components/plaid-link-button"
import { AccountSummary } from "@/components/account-summary"

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen w-full flex-col">
      <main className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Finance & Carbon Footprint Dashboard</h1>
          <div className="flex items-center gap-2">
            <PlaidLinkButton />
          </div>
        </div>

        {/* Account Summary Cards */}
        <AccountSummary />

        {/* AI Insights Section */}
        <Card>
          <CardHeader>
            <CardTitle>AI-Generated Insights</CardTitle>
            <CardDescription>
              Personalized recommendations to improve your finances and reduce your carbon footprint
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AiInsights />
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Card className="lg:col-span-4">
            <CardHeader>
              <CardTitle>Financial Overview</CardTitle>
              <CardDescription>View your spending and saving patterns over time</CardDescription>
            </CardHeader>
            <CardContent className="pl-2">
              <Overview />
            </CardContent>
          </Card>
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>Carbon Footprint</CardTitle>
              <CardDescription>Your monthly carbon emissions by category</CardDescription>
            </CardHeader>
            <CardContent>
              <CarbonFootprint />
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>Your recent financial activities and their carbon impact</CardDescription>
          </CardHeader>
          <CardContent>
            <RecentTransactions />
          </CardContent>
          <CardFooter>
            <Button variant="outline" className="w-full">
              <Link href="/transactions" className="flex items-center justify-center gap-1">
                View All Transactions
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </CardFooter>
        </Card>
      </main>

      {/* Chat Button */}
      <ChatButton />
    </div>
  )
}

