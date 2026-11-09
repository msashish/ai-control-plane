import styles from "./ChatHeader.module.css"

interface ChatHeaderProps {
    onClear: () => void
    canClear: boolean
}

export function ChatHeader({ onClear, canClear }: ChatHeaderProps) {
    return (
        <header className={styles.header}>
            <h1 className={styles.title}>AI Control Plane</h1>
            <button 
                type="button"
                className={styles.clearButton}
                onClick={onClear}
                disabled={!canClear}
            >
                Clear Chat
            </button>
        </header>
    )
}