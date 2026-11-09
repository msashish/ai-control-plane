import { useCallback, useState } from "react";
import { fetchLLMResponse } from "../../../api/gateway";
import { BLOCKED_MESSAGE } from "../constants";
import type { ChatMessage } from "../types";

const newId = () => crypto.randomUUID()

/**
 * Turn a prompt into message to show: LLM answer, a blocked notice
 * or a gateway/network failure
 */
async function handlePrompt(
    prompt: string,
): Promise<Pick<ChatMessage, 'role' | 'content'>> {
    const result = await fetchLLMResponse(prompt)
    if (!result.safe) {
        return { role: 'assistant', content: BLOCKED_MESSAGE}
    }
    return { role: 'assistant', content: result.answer }
}

export function useChat() {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [isLoading, setIsLoading] = useState(false)

    const sendPrompt = useCallback(
        async (rawPrompt: string) => {
            const prompt = rawPrompt.trim()
            if (!prompt || isLoading) return

            setMessages((prev) => [...prev, { id: newId(), role: 'user', content: prompt }])
            setIsLoading(true)

            try {
                const reply = await handlePrompt(prompt)
                setMessages((prev) => [...prev, {id: newId(), ...reply}])
            } catch (err) {
                setMessages((prev) => [
                    ...prev,
                    {
                        id: newId(),
                        role: 'error',
                        content: err instanceof Error ? err.message : String(err),
                    },
                ])
            } finally {
                setIsLoading(false)
            }
        },
        [isLoading],
    )

    const clear = useCallback(() => setMessages([]), [])

    return { messages, isLoading, sendPrompt, clear }
}
