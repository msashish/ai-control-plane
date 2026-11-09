import { useEffect, useRef, useState } from "react";
import type { FormEvent, KeyboardEvent } from "react";
import styles from "./ChatInput.module.css";

interface ChatInputProps {
  onSend: (prompt: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!disabled) inputRef.current?.focus();
  }, [disabled]);

   const submit = () => {
    const prompt = value.trim()
    if (!prompt || disabled) return
    onSend(prompt)
    setValue("")
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    submit()
  }

   const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      submit()
    }
}

return (
    <form className={styles.form} onSubmit={onSubmit}>
      <textarea
        ref={inputRef}
        className={styles.textarea}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={onKeyDown}
        placeholder="Type your prompt.. (Enter to send, Shift+Enter for new line)"
        aria-label="Prompt"
        rows={2}
        disabled={disabled}
        autoFocus
      />
      <button 
        type="submit" 
        className={styles.sendButton} 
        disabled={!value.trim() || disabled}
        >
        Send
      </button>
    </form>
)
}