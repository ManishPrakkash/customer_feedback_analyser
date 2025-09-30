"use client";

import { TooltipProvider } from "@/components/ui/tooltip";
import { SidebarProvider } from "@/lib/hooks/use-sidebar";
import { ClerkProvider } from "@clerk/nextjs";
import { ThemeProviderProps } from "next-themes/dist/types";

export function Providers({ children, ...props }: ThemeProviderProps) {
	const hasClerkEnv =
		typeof process !== "undefined" &&
		!!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

	const content = (
		<SidebarProvider>
			<TooltipProvider>{children}</TooltipProvider>
		</SidebarProvider>
	);

	// If Clerk env vars are not provided, render children without ClerkProvider for local dev
	if (!hasClerkEnv) {
		return content;
	}

	return <ClerkProvider>{content}</ClerkProvider>;
}
