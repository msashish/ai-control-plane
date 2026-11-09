export interface LLMResponse {
    answer: string
    safe: boolean
    recommended_llm: string
}

export interface ChatCompletion {
    model: string
    choices: {
        message: {
            content: string | null
        }
    }[]
}

export interface GatewayError {
    error?: { message?: string }
}
