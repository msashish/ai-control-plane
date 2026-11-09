import axios from "axios"
import { env } from "../config/env"

export const client = axios.create({
  baseURL: env.gatewayUrl,
  timeout: env.gatewayTimeoutMs,
  headers: {
    "Authorization": `Bearer ${env.gatewayApiKey}`,
  },
})
