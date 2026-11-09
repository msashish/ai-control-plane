import type { Role } from '../types'
import styles from './MessageBubble.module.css'

interface MessageBubbleProps {
    role: Role
    content: string
}

export const MessageBubble = ({ role, content }: MessageBubbleProps) => {
    return (
        <div className={`${styles.row} ${styles[role]}`} data-role={role}>
            <div className={styles.bubble}>
                {content}
            </div>
        </div>
    )
}
