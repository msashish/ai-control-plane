import { useChat } from '../hooks/useChat'
import { ChatHeader } from './ChatHeader'
import { ChatInput } from './ChatInput'
import { MessageList } from '././MessageList'
import styles from './ChatPage.module.css'

export const ChatPage = () => {
  const { messages, isLoading, sendPrompt, clear } = useChat()

  return (
    <div className={styles.page}>
        <ChatHeader 
        onClear={clear}
        canClear={messages.length > 0 && !isLoading}
        />
        <MessageList messages={messages} isLoading={isLoading} />
        <ChatInput onSend={sendPrompt} disabled={isLoading} />
    </div>
  )
}