import Link from "next/link"
import { BarChart3, CreditCard, DollarSign, Home, Leaf, LineChart, PiggyBank, Settings } from "lucide-react"

export function Sidebar() {
  return (
    <div className="flex h-screen w-14 flex-col justify-between border-r bg-muted/40 p-3 md:w-64">
      <div className="flex flex-col gap-6">
        <Link href="/" className="flex h-12 items-center justify-center md:justify-start md:px-6">
          <Leaf className="h-6 w-6 text-green-500" />
          <span className="ml-2 hidden text-lg font-bold md:inline-block">EcoFinance</span>
        </Link>
        <nav className="grid gap-1 px-2">
          <Link
            href="/"
            className="flex h-10 items-center rounded-md px-3 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <Home className="h-5 w-5 mr-2" />
            <span className="hidden md:inline-block">Dashboard</span>
          </Link>
          <Link
            href="/accounts"
            className="flex h-10 items-center rounded-md px-3 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <DollarSign className="h-5 w-5 mr-2" />
            <span className="hidden md:inline-block">Accounts</span>
          </Link>
          <Link
            href="/transactions"
            className="flex h-10 items-center rounded-md px-3 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <CreditCard className="h-5 w-5 mr-2" />
            <span className="hidden md:inline-block">Transactions</span>
          </Link>
          <Link
            href="/carbon"
            className="flex h-10 items-center rounded-md px-3 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <Leaf className="h-5 w-5 mr-2" />
            <span className="hidden md:inline-block">Carbon Footprint</span>
          </Link>
          <Link
            href="/savings"
            className="flex h-10 items-center rounded-md px-3 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <PiggyBank className="h-5 w-5 mr-2" />
            <span className="hidden md:inline-block">Savings</span>
          </Link>
          <Link
            href="/reports"
            className="flex h-10 items-center rounded-md px-3 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <BarChart3 className="h-5 w-5 mr-2" />
            <span className="hidden md:inline-block">Reports</span>
          </Link>
          <Link
            href="/insights"
            className="flex h-10 items-center rounded-md px-3 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <LineChart className="h-5 w-5 mr-2" />
            <span className="hidden md:inline-block">AI Insights</span>
          </Link>
        </nav>
      </div>
      <nav className="grid gap-1 px-2">
        <Link
          href="/settings"
          className="flex h-10 items-center rounded-md px-3 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        >
          <Settings className="h-5 w-5 mr-2" />
          <span className="hidden md:inline-block">Settings</span>
        </Link>
      </nav>
    </div>
  )
}

