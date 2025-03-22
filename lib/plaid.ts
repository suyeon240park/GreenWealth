/*
Item: login to a financial institution
link: client-side widget

1. Clinet requests a link token
2. Server requests a link token and returns it to the client
3. Client calls link and user signs in and user signs in
4. Plaid sends back a public token
5. Client sends the public token to the server
6. Server sends public token to Plaid and gets back an access token (to access this item in future)
*/

export async function createLinkToken(clientId: string) {
  try {
    const response = await fetch("http://localhost:5000/api/create_link_token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ client_id: clientId }),
    })

    if (!response.ok) {
      throw new Error("Failed to create link token")
    }

    const data = await response.json()
    return data.link_token
  } catch (error) {
    console.error("Error creating link token:", error)
    throw error
  }
}

export async function exchangePublicToken(publicToken: string, clientId: string) {
  try {
    const response = await fetch("http://localhost:5000/api/exchange_public_token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        public_token: publicToken,
        client_id: clientId,
      }),
    })

    if (!response.ok) {
      throw new Error("Failed to exchange public token")
    }

    return await response.json()
  } catch (error) {
    console.error("Error exchanging public token:", error)
    throw error
  }
}

export async function fetchTransactions(clientId: string) {
  try {
    const response = await fetch(`http://localhost:5000/api/transactions?client_id=${clientId}`)

    if (!response.ok) {
      throw new Error("Failed to fetch transactions")
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching transactions:", error)
    throw error
  }
}

export async function fetchCarbonFootprint(clientId: string) {
  try {
    const response = await fetch(`http://localhost:5000/api/carbon_footprint?client_id=${clientId}`)

    if (!response.ok) {
      throw new Error("Failed to fetch carbon footprint data")
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching carbon footprint:", error)
    throw error
  }
}

export async function fetchFinancialOverview(clientId: string) {
  try {
    const response = await fetch(`http://localhost:5000/api/financial_overview?client_id=${clientId}`)

    if (!response.ok) {
      throw new Error("Failed to fetch financial overview data")
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching financial overview:", error)
    throw error
  }
}

export async function fetchAccountSummary(clientId: string) {
  try {
    const response = await fetch(`http://localhost:5000/api/account_summary?client_id=${clientId}`)

    if (!response.ok) {
      throw new Error("Failed to fetch account summary data")
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching account summary:", error)
    throw error
  }
}