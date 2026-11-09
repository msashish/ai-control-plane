import axios from 'axios'
import { env } from '../config/env'
import { client } from './client'
import type { ChatCompletion, GatewayError, LLMResponse } from './types'

export type { LLMResponse } from './types'

export async function fetchLLMResponse(prompt: string): Promise<LLMResponse> {
    try {
        const response = await client.post<ChatCompletion>('/v1/chat/completions', 
            { model: env.gatewayModel, 
              messages: [{ role: 'user', content: prompt }],
            })

        return {
            answer: response.data.choices[0].message.content ?? "",
            safe: true,
            recommended_llm: response.data.model,
        }

    } catch (e) {
        if (axios.isAxiosError<GatewayError>(e)) {
            const message = e.response?.data?.error?.message ?? e.message

            if (e.response?.status === 400 && /blocked/i.test(message)) {
                return {
                    answer: message,
                    safe: false,
                    recommended_llm: '',
                }
            }
            if (!e.response) {
                throw new Error('cannot reach ai-gateway at ${env.gatewayUrl} (${e.message})', { cause: e })
            }
            throw new Error('Gateway error ${e.response?.status}: ${message}', { cause: e })
        }
        console.error('Unexpected error in fetchLLMResponse:', e)
        throw e
    }
}