"use client";

import { type DialogProps } from "@radix-ui/react-dialog";
import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { IconSpinner } from "@/components/ui/icons";
import { useCopyToClipboard } from "@/lib/hooks/use-copy-to-clipboard";
import { ServerActionResult, type Chat } from "@/lib/types";

type ShareResult = Chat | { error: string };
interface ChatShareDialogProps extends DialogProps {
	chat: Pick<Chat, "id" | "title"> & { messages?: any[] };
	shareChat: (id: string) => Promise<ShareResult>;
	onCopy: () => void;
}

export function ChatShareDialog({
	chat,
	shareChat,
	onCopy,
	...props
}: ChatShareDialogProps) {
	const { copy } = useCopyToClipboard();
	const [isSharePending, startShareTransition] = React.useTransition();

	const copyShareLink = React.useCallback(
		async (chat: Chat) => {
			if (!chat.sharePath) {
				return toast.error("Could not copy share link to clipboard");
			}

			const url = new URL(window.location.href);
			url.pathname = chat.sharePath;
			copy(url.toString());
			onCopy();
			toast.success("Share link copied to clipboard");
		},
		[copy, onCopy]
	);

	return (
		<Dialog {...props}>
			<DialogContent>
				<DialogHeader>
					<DialogTitle>Share link to chat</DialogTitle>
					<DialogDescription>
						Anyone with the URL will be able to view the shared chat.
					</DialogDescription>
				</DialogHeader>
				<div className="p-4 space-y-1 text-sm border rounded-lg">
					<div className="font-medium">{chat.title}</div>
					{Array.isArray(chat.messages) ? (
						<div className="text-muted-foreground">
							{chat.messages.length} messages
						</div>
					) : null}
				</div>
				<DialogFooter className="items-center">
					<Button
						disabled={isSharePending}
						onClick={() => {
							// @ts-ignore
							startShareTransition(async () => {
								const result = await shareChat(chat.id);

								if (result && "error" in result) {
									toast.error(result.error);
									return;
								}

								copyShareLink(result);
							});
						}}
					>
						{isSharePending ? (
							<>
								<IconSpinner className="mr-2 animate-spin" />
								Copying...
							</>
						) : (
							<>Copy link</>
						)}
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}
