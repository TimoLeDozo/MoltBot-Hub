# Model Truth Table

## Goal
Switch automatically between `gemini`, `nvidia`, and `qwen` based on:
- current situation (`chat`, `browser`, `analysis`, `research`, `emergency`, `auto`)
- provider health (recent 429/rate-limit/quota errors)
- daily token budgets
- local model availability

## Inputs
- `situation`
- `gemini_quota_exceeded_today`
- `gemini_recent_rate_limit`
- `nvidia_recent_rate_limit`
- `gemini_tokens_today >= gemini_token_budget`
- `nvidia_tokens_today >= nvidia_token_budget`
- `ollama_qwen_0_5b_available`
- `ollama_qwen_7b_available`

## Base Order By Situation
| Situation | Base order (primary -> fallbacks) |
|---|---|
| `chat` | `qwen2.5:0.5b`, `qwen2.5:7b`, `gemini`, `nvidia` |
| `browser` | `gemini`, `nvidia`, `qwen2.5:7b`, `qwen2.5:0.5b` |
| `analysis` | `gemini`, `nvidia`, `qwen2.5:7b`, `qwen2.5:0.5b` |
| `research` | `gemini`, `nvidia`, `qwen2.5:7b`, `qwen2.5:0.5b` |
| `emergency` | `qwen2.5:0.5b`, `qwen2.5:7b`, `gemini`, `nvidia` |
| `auto` | `gemini`, `nvidia`, `qwen2.5:7b`, `qwen2.5:0.5b` |

## Override Rules (Applied in order)
| Rule | Condition | Action |
|---|---|---|
| R1 | `ollama_qwen_0_5b_available = false` | remove `qwen2.5:0.5b` from candidates |
| R1b | `ollama_qwen_7b_available = false` | remove `qwen2.5:7b` from candidates |
| R2 | `gemini_quota_exceeded_today = true` | push `gemini` to end |
| R3 | `gemini_recent_rate_limit = true` | push `gemini` to end |
| R4 | `nvidia_recent_rate_limit = true` | push `nvidia` to end |
| R5 | `gemini_token_budget_exceeded = true` | push `gemini` to end |
| R6 | `nvidia_token_budget_exceeded = true` | push `nvidia` to end |
| R7 | both cloud providers unhealthy and local available | force `qwen2.5:0.5b` primary |

## Runtime Tuning
- if primary is local qwen:
  - `timeoutSeconds = 300`
  - `maxConcurrent = 1`
  - `subagents.maxConcurrent = 2`
- if primary is cloud:
  - `timeoutSeconds = 210`
  - `maxConcurrent = 2`
  - `subagents.maxConcurrent = 4`

## Command
Use `scripts/model-truth-router.ps1` to compute and apply these rules.
