import { useEffect, useRef } from 'react'
import type { ChatMessage } from '../types'
import { MessageBubble } from './MessageBubble'
import { TypingIndicator } from './TypingIndicator'
import styles from './MessageList.module.css'

interface MessageListProps {
    messages: ChatMessage[]
    isLoading: boolean
}

export function MessageList({ messages, isLoading }: MessageListProps) {
    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth'})
    }, [messages, isLoading])

    return (
        <main className={styles.list} aria-live="polite">
            {messages.length === 0 && !isLoading && (
                <p className={styles.empty}>Type a Prompt below to get started..</p>
            )}

            {messages.map((m) => (
                <MessageBubble key={m.id} role={m.role} content={m.content} />
            ))}

            {isLoading && <TypingIndicator />}
            <div ref={bottomRef} />
        </main>
    )
}