"use client";

import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  type ChatModelAdapter,
  unstable_useRemoteThreadListRuntime as useRemoteThreadListRuntime,
  useThreadListItem,
    RuntimeAdapterProvider,

  type ThreadHistoryAdapter,
  useLocalThreadRuntime,
} from "@assistant-ui/react";
import { Thread } from "@/components/assistant-ui/thread";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { ThreadListSidebar } from "@/components/assistant-ui/threadlist-sidebar";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useMemo } from "react";

import {
  AttachmentAdapter,
  PendingAttachment,
  CompleteAttachment,
} from "@assistant-ui/react";

class CustomAttachmentAdapter implements AttachmentAdapter {
  accept = "image/*,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,.xlsx,.xls,text/csv,application/csv,.csv";

  async add({ file }: { file: File }): Promise<PendingAttachment> {
    const maxSize = 20 * 1024 * 1024;
    if (file.size > maxSize) throw new Error("File size exceeds 20MB limit");
    return {
      id: crypto.randomUUID(),
      contentType: file.type.startsWith("image/") ? "image" : "file",
      type: file.type.startsWith("image/") ? "image" : "file",
      name: file.name,
      file,
        status: {
        type: "running",
        reason: "uploading",
        progress: 50,
      },
    };
  }

  async send(attachment: PendingAttachment): Promise<CompleteAttachment> {
    const formData = new FormData();
    formData.append("file", attachment.file);

    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) throw new Error("Failed to upload file");
    const data = await res.json();

    if(attachment.type==="image") 
      return {
      id: attachment.id,
      type: attachment.type,
      contentType: attachment.type,
      name: attachment.name,
      content: [{ type: "image", image: data.url }], 
      status: { type: "complete" },
    };
      return {
      id: attachment.id,
      type: attachment.type,
      contentType: attachment.type,
      name: attachment.name,
      content: [{ type: "text", text: data.url }], 
      status: { type: "complete" },
    };
  }

  async remove(_: PendingAttachment) {}
}

// Types for SSE events
interface SSETextDelta {
  type: "text-delta";
  textDelta: string;
}

interface SSEFinish {
  type: "finish";
}

interface SSEError {
  type: "error";
  error: string;
}

interface SSEImage {
  type: "image";
  image: string;
}

type SSEEvent = SSETextDelta | SSEFinish | SSEError|SSEImage;

// Configuration
const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  chatEndpoint: "/api/chat",
} as const;

/**
 * SSE Chat Model Adapter using @microsoft/fetch-event-source
 */
const createSSEModelAdapter = (apiUrl: string): ChatModelAdapter => ({
  async *run({ messages, abortSignal }) {
    const endpoint = `${apiUrl}${API_CONFIG.chatEndpoint}`;
    let accumulated = "";
    const imageURL:string[]=[];
    let streamError: Error | null = null;
    
    // Queue to store events as they arrive
    const eventQueue: SSEEvent[] = [];
    let resolveNext: ((value: SSEEvent | null) => void) | null = null;
    let isDone = false;

    const pushEvent = (event: SSEEvent | null) => {
      if (resolveNext) {
        resolveNext(event);
        resolveNext = null;
      } else {
        if (event) eventQueue.push(event);
      }
    };

    const getNextEvent = (): Promise<SSEEvent | null> => {
      if (eventQueue.length > 0) {
        return Promise.resolve(eventQueue.shift()!);
      }
      if (isDone) {
        return Promise.resolve(null);
      }
      return new Promise((resolve) => {
        resolveNext = resolve;
      });
    };

    // Start the SSE connection
    const fetchPromise = fetchEventSource(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ messages }),
      signal: abortSignal,
      
      onopen: async (response) => {
        if (!response.ok) {
          const errorText = await response.text().catch(() => "Unknown error");
          throw new Error(`Server error (${response.status}): ${errorText}`);
        }
      },
      
      onmessage: (event) => {
        if (!event.data) return;
        
        try {
          const data = JSON.parse(event.data) as SSEEvent;
          pushEvent(data);
        } catch (error) {
          console.error("Failed to parse SSE data:", event.data);
        }
      },
      
      onerror: (error) => {
        streamError = error instanceof Error ? error : new Error("Stream error");
        isDone = true;
        pushEvent(null);
        throw error;
      },
      
      onclose: () => {
        isDone = true;
        pushEvent(null);
      },
    }).catch((error) => {
      if (error.name !== "AbortError") {
        streamError = error;
      }
    });

    try {
      while (true) {
        const event = await getNextEvent();
        
        if (!event) break;
        
        switch (event.type) {
          case "text-delta":
            accumulated += event.textDelta;
            yield {
              content: [
                ...imageURL.map((url) => ({
                    type: "image" as const,
                    image: url,
                })),
                {
                  type: "text" as const,
                  text: accumulated,
                },
              ],
            };
            break;
          case "image":
            imageURL.push(event.image)
            yield {
              content: [
                ...imageURL.map((url) => ({
                    type: "image" as const,
                    image: url,
                })),
                {
                  type: "text" as const,
                  text: accumulated,
                },
              ],
            };
            break;
          case "finish":
            console.log("Stream completed successfully");
            return;

          case "error":
            throw new Error(`Server error: ${event.error}`);
        }
      }
      
      if (streamError) {
        throw streamError;
      }
    } finally {
      isDone = true;
      await fetchPromise;
    }
  },
});

export const Assistant = () => {
  const runtime = useLocalRuntime(
    createSSEModelAdapter(API_CONFIG.baseUrl),{
  adapters: {
    attachments: new CustomAttachmentAdapter(),
  },});

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <SidebarProvider>
        <div className="flex h-dvh w-full pr-0.5">
          {/* <ThreadListSidebar /> */}
          <SidebarInset>
            {/* <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
              <SidebarTrigger />
            </header> */}
            <div className="flex-1 overflow-hidden">
              <Thread />
            </div>
          </SidebarInset>
        </div>
      </SidebarProvider>
    </AssistantRuntimeProvider>
  );
};