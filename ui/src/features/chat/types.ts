export type Role = "user" | "assistant" | "blocked" | "error"

export interface ChatMessage {
    id: string
    role: Role
    content: string
}
