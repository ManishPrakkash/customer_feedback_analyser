"use client";

import { UserMessage } from "@/components/chat/message";
import { EmptyScreen } from "@/components/empty-screen";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useScrollToBottom } from "@/components/use-scroll-to-bottom";
import { PlusCircleIcon, Send } from "lucide-react";
import { ReactNode, useRef, useState } from "react";
import { FeedbackAgentMessage } from "@/components/feedback-agent-msg";

// Simple state management without RSC for now
interface Message {
	id: string;
	role: "user" | "assistant";
	content: string;
	display?: ReactNode;
}

export default function FeedbackChat() {
	const [messages, setMessages] = useState<Message[]>([]);
	const [input, setInput] = useState("");
	const [isLoading, setIsLoading] = useState(false);

	const inputRef = useRef<HTMLInputElement>(null);
	const [messagesContainerRef, messagesEndRef] =
		useScrollToBottom<HTMLDivElement>();

	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();

		if (!input.trim()) return;

		const userMessage: Message = {
			id: Date.now().toString(),
			role: "user",
			content: input,
			display: <UserMessage>{input}</UserMessage>,
		};

		setMessages((prevMessages) => [...prevMessages, userMessage]);
		setInput("");
		setIsLoading(true);

		try {
			// Call the backend directly
			const response = await fetch('/api/analyze', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ feedback: input }),
			});

			if (response.ok) {
				const data = await response.json();
				const assistantMessage: Message = {
					id: (Date.now() + 1).toString(),
					role: "assistant",
					content: JSON.stringify(data),
					display: <FeedbackAgentMessage 
						agentMessage="" 
						feedbackAnalysis={data} 
					/>,
				};
				setMessages((prevMessages) => [...prevMessages, assistantMessage]);
			}
		} catch (error) {
			console.error("Error sending message:", error);
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="flex flex-col h-screen font-sans w-full ">
			<div className="flex w-full mx-auto max-w-6xl px-4 sm:px-6 md:px-8 py-2 relative">
				<div className="flex-1 flex flex-col  w-full h-[96vh] py-4">
					<ScrollArea
						className="flex-1  mb-4 pb-4"
						ref={messagesContainerRef}
					>
						{messages.length ? (
							<div className="relative mx-auto max-w-5xl grid auto-rows-max gap-8 px-4 text-neutral-950">
								{messages.map((message: Message, idx: number) => {
									return (
										<div
											key={message.id}
											className={`${
												message.role === "assistant"
													? "border-b-2 border-stone-300 pb-4"
													: ""
											}`}
										>
											{message.display}
										</div>
									);
								})}
							</div>
						) : (
							<EmptyScreen />
						)}
						{/* <div ref={messagesEndRef} /> */}
					</ScrollArea>
					<form
						onSubmit={handleSubmit}
						className="flex space-x-2 mb-4 bg-[#f4f4f8] rounded-full p-4 shadow-sm shadow-[#9ba5b7]"
					>
						<Button
							size={"icon"}
							className="rounded-full bg-white border-gray-300   focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 hover:bg-[#0058dd]/20"
						>
							<PlusCircleIcon className="size-5 text-[#0058dd] " />
						</Button>
						<Input
							ref={inputRef}
							className="flex-1 rounded-full bg-white border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 text-[#323E59] font-poppins"
							placeholder="Paste your feedback here..."
							value={input}
							onChange={(e) => setInput(e.target.value)}
						/>
						<Button
							type="submit"
							className="rounded-full bg-[#0058dd] hover:bg-[#1968e0] text-white"
						>
							<Send className="h-4 w-4" />
							<span className="sr-only">Send</span>
						</Button>
					</form>
				</div>
			</div>
		</div>
	);
}
