param(
  [ValidateSet("auto", "chat", "browser", "analysis", "research", "emergency")]
  [string]$Situation = "auto",
  [string]$ContainerName = "moltbot_hub",
  [string]$ConfigPath = "config/clawdbot.json",
  [string]$ReportPath = "workspace/output/model-routing-report.json",
  [int]$LookbackMinutes = 90,
  [int]$GeminiDailyTokenBudget = 180000,
  [int]$NvidiaDailyTokenBudget = 180000,
  [switch]$Apply,
  [switch]$RestartContainer
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-DockerRaw {
  param([string[]]$DockerArgs)
  $output = & docker @DockerArgs 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw ("docker command failed: docker {0}`n{1}" -f ($DockerArgs -join " "), ($output -join [Environment]::NewLine))
  }
  return ($output -join [Environment]::NewLine)
}

function Invoke-NodeJsonInContainer {
  param(
    [string]$Container,
    [string]$JavaScript
  )
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($JavaScript)
  $b64 = [Convert]::ToBase64String($bytes)
  $runner = "eval(Buffer.from('$b64','base64').toString('utf8'))"
  $json = Invoke-DockerRaw -DockerArgs @("exec", $Container, "node", "-e", $runner)
  return ($json | ConvertFrom-Json)
}

function Write-Utf8NoBom {
  param(
    [string]$Path,
    [string]$Content
  )
  $encoding = [System.Text.UTF8Encoding]::new($false)
  $fullPath = [System.IO.Path]::GetFullPath($Path)
  [System.IO.File]::WriteAllText($fullPath, $Content, $encoding)
}

function Move-ToEnd {
  param([System.Collections.Generic.List[string]]$List, [string]$Item)
  if ($List.Contains($Item)) {
    [void]$List.Remove($Item)
    [void]$List.Add($Item)
  }
}

function Remove-ItemIfPresent {
  param([System.Collections.Generic.List[string]]$List, [string]$Item)
  if ($List.Contains($Item)) {
    [void]$List.Remove($Item)
  }
}

function Get-OllamaAvailability {
  param([string]$Container)
  $js = @'
fetch("http://host.docker.internal:11434/api/tags")
  .then((r) => r.json())
  .then((j) => {
    const names = (j.models || []).map((m) => m.name);
    console.log(JSON.stringify({ names }));
  })
  .catch((e) => {
    console.log(JSON.stringify({ names: [], error: String(e && e.message ? e.message : e) }));
  });
'@
  return (Invoke-NodeJsonInContainer -Container $Container -JavaScript $js)
}

function Get-SessionMetrics {
  param([string]$Container, [int]$LookbackMin)
  $lookbackMs = $LookbackMin * 60 * 1000
  $js = @"
const fs = require("fs");
const path = "/root/.openclaw/agents/main/sessions";
const now = Date.now();
const d = new Date();
const dayStart = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), 0, 0, 0, 0);
const lookbackMs = ${lookbackMs};
const stats = {
  now,
  dayStartUtcMs: dayStart,
  tokensToday: { google: 0, nvidia: 0, ollama: 0, unknown: 0 },
  rateLimitRecent: { google: 0, nvidia: 0, ollama: 0, unknown: 0 },
  rateLimitToday: { google: 0, nvidia: 0, ollama: 0, unknown: 0 },
  geminiQuotaExceededToday: false,
  parsedFiles: 0,
  parsedLines: 0
};
function toProvider(p) {
  if (p === "google" || p === "nvidia" || p === "ollama") return p;
  return "unknown";
}
if (!fs.existsSync(path)) {
  console.log(JSON.stringify(stats));
  process.exit(0);
}
for (const file of fs.readdirSync(path)) {
  if (!file.endsWith(".jsonl")) continue;
  stats.parsedFiles++;
  const full = path + "/" + file;
  const text = fs.readFileSync(full, "utf8");
  for (const line of text.split(/\r?\n/)) {
    if (!line.trim()) continue;
    stats.parsedLines++;
    let row;
    try { row = JSON.parse(line); } catch { continue; }
    if (!row || row.type !== "message" || !row.message || row.message.role !== "assistant") continue;
    const p = toProvider(row.message.provider);
    let ts = 0;
    if (typeof row.timestamp === "string") {
      const t = Date.parse(row.timestamp);
      if (!Number.isNaN(t)) ts = t;
    }
    if (!ts && typeof row.message.timestamp === "number") ts = row.message.timestamp;
    const usage = row.message.usage || {};
    const totalTokens = Number(usage.totalTokens ?? usage.total ?? 0) || 0;
    if (ts >= dayStart) {
      stats.tokensToday[p] += totalTokens;
      const err = String(row.message.errorMessage || "");
      const isRateLimit = /"code"\s*:\s*429|rate limit|resource_exhausted|too many requests/i.test(err);
      if (isRateLimit) stats.rateLimitToday[p] += 1;
      if (/generaterequestsperdayperprojectpermodel-freetier|quota exceeded for metric: .*generate_content_free_tier_requests/i.test(err)) {
        stats.geminiQuotaExceededToday = true;
      }
    }
    if (ts >= now - lookbackMs) {
      const err = String(row.message.errorMessage || "");
      if (/"code"\s*:\s*429|rate limit|resource_exhausted|too many requests/i.test(err)) {
        stats.rateLimitRecent[p] += 1;
      }
    }
  }
}
console.log(JSON.stringify(stats));
"@
  return (Invoke-NodeJsonInContainer -Container $Container -JavaScript $js)
}

function Get-BaseOrder {
  param([string]$Mode)
  $gemini = "google/gemini-2.5-flash"
  $nvidia = "nvidia/moonshotai/kimi-k2.5"
  $q05 = "ollama/qwen2.5:0.5b"
  switch ($Mode) {
    # Keep qwen2.5:7b out of automatic routing to avoid host memory pressure.
    "chat"      { return @($q05, $gemini, $nvidia) }
    "browser"   { return @($gemini, $nvidia, $q05) }
    "analysis"  { return @($gemini, $nvidia, $q05) }
    "research"  { return @($gemini, $nvidia, $q05) }
    "emergency" { return @($q05, $gemini, $nvidia) }
    default     { return @($gemini, $nvidia, $q05) }
  }
}

if (-not (Test-Path $ConfigPath)) {
  throw "Config not found: $ConfigPath"
}

$ollamaState = Get-OllamaAvailability -Container $ContainerName
$metrics = Get-SessionMetrics -Container $ContainerName -LookbackMin $LookbackMinutes

$names = @($ollamaState.names)
$hasQ05 = $names -contains "qwen2.5:0.5b"
$hasQ7 = $names -contains "qwen2.5:7b"
$ollamaAvailable = $hasQ05 -or $hasQ7

$geminiUnhealthy = $metrics.geminiQuotaExceededToday -or ($metrics.rateLimitRecent.google -gt 0) -or ($metrics.tokensToday.google -ge $GeminiDailyTokenBudget)
$nvidiaUnhealthy = ($metrics.rateLimitRecent.nvidia -gt 0) -or ($metrics.tokensToday.nvidia -ge $NvidiaDailyTokenBudget)

$ordered = [System.Collections.Generic.List[string]]::new()
foreach ($m in (Get-BaseOrder -Mode $Situation)) { [void]$ordered.Add($m) }

if (-not $hasQ05) { Remove-ItemIfPresent -List $ordered -Item "ollama/qwen2.5:0.5b" }
if (-not $hasQ7) { Remove-ItemIfPresent -List $ordered -Item "ollama/qwen2.5:7b" }

if ($geminiUnhealthy) { Move-ToEnd -List $ordered -Item "google/gemini-2.5-flash" }
if ($nvidiaUnhealthy) { Move-ToEnd -List $ordered -Item "nvidia/moonshotai/kimi-k2.5" }

if ($geminiUnhealthy -and $nvidiaUnhealthy -and $ollamaAvailable) {
  $forced = [System.Collections.Generic.List[string]]::new()
  if ($hasQ05) { [void]$forced.Add("ollama/qwen2.5:0.5b") }
  [void]$forced.Add("google/gemini-2.5-flash")
  [void]$forced.Add("nvidia/moonshotai/kimi-k2.5")
  $ordered = $forced
}

if ($ordered.Count -eq 0) {
  throw "No model candidates left after truth-table filtering."
}

$primary = $ordered[0]
$fallbacks = @()
if ($ordered.Count -gt 1) { $fallbacks = @($ordered[1..($ordered.Count - 1)]) }

$timeoutSeconds = 180
$maxConcurrent = 1
$subagentsConcurrent = 2
if ($primary -like "ollama/*") {
  $timeoutSeconds = 180
  $maxConcurrent = 1
  $subagentsConcurrent = 2
}

$config = Get-Content -Raw $ConfigPath | ConvertFrom-Json
$config.agents.defaults.model.primary = $primary
$config.agents.defaults.model.fallbacks = [object[]]$fallbacks
$config.agents.defaults.timeoutSeconds = $timeoutSeconds
$config.agents.defaults.maxConcurrent = $maxConcurrent
$config.agents.defaults.subagents.maxConcurrent = $subagentsConcurrent

$decision = [ordered]@{
  generatedAt = (Get-Date).ToString("o")
  situation = $Situation
  container = $ContainerName
  signals = [ordered]@{
    geminiQuotaExceededToday = $metrics.geminiQuotaExceededToday
    geminiRecentRateLimitCount = $metrics.rateLimitRecent.google
    nvidiaRecentRateLimitCount = $metrics.rateLimitRecent.nvidia
    geminiTokensToday = $metrics.tokensToday.google
    nvidiaTokensToday = $metrics.tokensToday.nvidia
    geminiTokenBudget = $GeminiDailyTokenBudget
    nvidiaTokenBudget = $NvidiaDailyTokenBudget
    hasQwen05 = $hasQ05
    hasQwen7 = $hasQ7
    ollamaAvailable = $ollamaAvailable
    geminiUnhealthy = $geminiUnhealthy
    nvidiaUnhealthy = $nvidiaUnhealthy
  }
  decision = [ordered]@{
    primary = $primary
    fallbacks = $fallbacks
    timeoutSeconds = $timeoutSeconds
    maxConcurrent = $maxConcurrent
    subagentsMaxConcurrent = $subagentsConcurrent
  }
}

$reportDir = Split-Path -Parent $ReportPath
if ($reportDir -and -not (Test-Path $reportDir)) {
  New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}
$reportJson = $decision | ConvertTo-Json -Depth 20
Write-Utf8NoBom -Path $ReportPath -Content $reportJson

if ($Apply) {
  $configJson = $config | ConvertTo-Json -Depth 100
  Write-Utf8NoBom -Path $ConfigPath -Content $configJson
  if ($RestartContainer) {
    Invoke-DockerRaw -DockerArgs @("restart", $ContainerName) | Out-Null
  }
}

Write-Host "Model truth-table decision:"
Write-Host ("- situation: " + $Situation)
Write-Host ("- primary: " + $primary)
Write-Host ("- fallbacks: " + (($fallbacks -join ", ")))
Write-Host ("- timeoutSeconds: " + $timeoutSeconds)
Write-Host ("- maxConcurrent: " + $maxConcurrent)
Write-Host ("- subagents.maxConcurrent: " + $subagentsConcurrent)
Write-Host ("- report: " + $ReportPath)
if ($Apply) {
  Write-Host "- applied: yes"
  if ($RestartContainer) { Write-Host "- container restarted: yes" }
  else { Write-Host "- container restarted: no" }
} else {
  Write-Host "- applied: no (dry run)"
}
