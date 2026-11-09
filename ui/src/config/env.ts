export const env = {
    gatewayUrl: import.meta.env.VITE_GATEWAY_URL || "http://localhost:4000",
    gatewayModel: import.meta.env.VITE_GATEWAY_MODEL || "qwen-local",
    gatewayApiKey: import.meta.env.VITE_GATEWAY_API_KEY || "something",
    gatewayTimeoutMs: 120_000, // Default timeout of 30 seconds
} as const
