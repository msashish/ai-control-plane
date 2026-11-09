import styles from './TypingIndicator.module.css'

export function TypingIndicator() {
    return (
        <div className={styles.row}>
            <div className={styles.bubble} role="status" aria-label="Thinking">
                <span />
                <span />
                <span />
            </div>
        </div>
    )
}
