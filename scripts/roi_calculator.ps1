param(
    [int]$Seats = 5,
    [int]$HoursPerMonth = 100,
    [ValidateSet(2,4,8)]
    [int]$CoreSize = 4,
    [decimal]$CopilotMonthly = 10,
    [decimal]$TopDogSeatMonthly = 25
)

# Rates for Codespaces compute per hour by core size
$rates = @{ 2 = 0.18; 4 = 0.36; 8 = 0.72 }
if (-not $rates.ContainsKey($CoreSize)) {
    Write-Error "Unsupported CoreSize: $CoreSize. Use 2, 4, or 8."
    exit 1
}
$codespacesRate = [decimal]$rates[$CoreSize]

# Per-seat monthly costs
$topDogPerSeatMonthly = [decimal]$TopDogSeatMonthly
$githubPerSeatMonthly = [decimal]$CopilotMonthly + ([decimal]$HoursPerMonth * $codespacesRate)

# Per-seat yearly costs
$topDogPerSeatYearly = $topDogPerSeatMonthly * 12
$githubPerSeatYearly = $githubPerSeatMonthly * 12

# Team totals
$topDogTeamMonthly = $topDogPerSeatMonthly * $Seats
$githubTeamMonthly = $githubPerSeatMonthly * $Seats
$topDogTeamYearly = $topDogTeamMonthly * 12
$githubTeamYearly = $githubTeamMonthly * 12

# Savings
$monthlySavingsPerSeat = $githubPerSeatMonthly - $topDogPerSeatMonthly
$yearlySavingsPerSeat = $githubPerSeatYearly - $topDogPerSeatYearly
$teamYearlySavings = $githubTeamYearly - $topDogTeamYearly

# Output
Write-Host "=== ROI Calculator: Top Dog Teams vs Copilot + Codespaces ===" -ForegroundColor Cyan
Write-Host "Seats: $Seats | Hours/Month: $HoursPerMonth | Cores: $CoreSize | Copilot: $$CopilotMonthly/mo | Top Dog: $$TopDogSeatMonthly/seat/mo"
Write-Host "Codespaces Rate: $$codespacesRate/hour"

Write-Host "`nPer-Seat Monthly:  Top Dog $$topDogPerSeatMonthly    | GitHub $$githubPerSeatMonthly"
Write-Host "Per-Seat Yearly:   Top Dog $$topDogPerSeatYearly | GitHub $$githubPerSeatYearly"
Write-Host "Team Monthly:      Top Dog $$topDogTeamMonthly   | GitHub $$githubTeamMonthly"
Write-Host "Team Yearly:       Top Dog $$topDogTeamYearly  | GitHub $$githubTeamYearly"

Write-Host "`nSavings Per Seat:  Monthly $$monthlySavingsPerSeat | Yearly $$yearlySavingsPerSeat" -ForegroundColor Green
Write-Host "Savings (Team Yearly): $$teamYearlySavings" -ForegroundColor Green
