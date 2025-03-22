"use client"

import { useState } from "react"
import { MessageCircle, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"

export function ChatButton() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {isOpen && (
        <Card className="fixed bottom-20 right-6 w-80 md:w-96 z-50 shadow-lg">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Smart Assistant</CardTitle>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsOpen(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="h-80 overflow-y-auto space-y-4 pb-2">
            <div className="bg-muted p-3 rounded-lg rounded-tl-none max-w-[80%]">
              <p className="text-sm">
                Hi there! I'm your personal finance and sustainability assistant. How can I help you today?
              </p>
            </div>
            <div className="bg-primary text-primary-foreground p-3 rounded-lg rounded-tr-none max-w-[80%] ml-auto">
              <p className="text-sm">How can I reduce my carbon footprint?</p>
            </div>
            <div className="bg-muted p-3 rounded-lg rounded-tl-none max-w-[80%]">
              <p className="text-sm">
                Based on your spending patterns, I recommend:
                <br />
                <br />
                1. Switch to public transport twice a week
                <br />
                2. Buy seasonal produce from local markets
                <br />
                3. Consolidate your online shopping orders
                <br />
                <br />
                These changes could reduce your carbon footprint by up to 30%!
              </p>
            </div>
          </CardContent>
          <CardFooter className="pt-2">
            <div className="flex w-full items-center space-x-2">
              <Input placeholder="Ask a question..." className="flex-1" />
              <Button size="icon">
                <MessageCircle className="h-4 w-4" />
                <span className="sr-only">Send message</span>
              </Button>
            </div>
          </CardFooter>
        </Card>
      )}

      <Button
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg"
        size="icon"
        onClick={() => setIsOpen(!isOpen)}
      >
        <MessageCircle className="h-6 w-6" />
        <span className="sr-only">Open chat</span>
      </Button>
    </>
  )
}

