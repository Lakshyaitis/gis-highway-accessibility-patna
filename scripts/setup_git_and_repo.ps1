<#
===============================================================================
Git Repository Initializer and GitHub Upload Helper
===============================================================================
#>

$minGitPath = "C:\Users\laksh\AppData\Local\Programs\MinGit\cmd"
$ghPath = "C:\Users\laksh\AppData\Local\Programs\gh\bin"

if (Test-Path "$minGitPath\git.exe") {
    $env:PATH = "$minGitPath;" + $env:PATH
}
if (Test-Path "$ghPath\gh.exe") {
    $env:PATH = "$ghPath;" + $env:PATH
}

$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "[ERROR] Git executable not found. Please ensure MinGit is installed." -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Git detected: $($gitCmd.Source)" -ForegroundColor Green
$projectRoot = "C:\Users\laksh\.gemini\antigravity\scratch\gis-highway-accessibility-patna"
Set-Location $projectRoot

# Configure Git Identity if not set
$userName = & git config user.name
if (-not $userName) {
    & git config --global user.name "Civil Engineering Candidate"
    & git config --global user.email "civil.portfolio@example.com"
    Write-Host "[INFO] Configured default local git user identity." -ForegroundColor Cyan
}

# Initialize Git repository
if (-not (Test-Path "$projectRoot\.git")) {
    & git init -b main
    Write-Host "[SUCCESS] Initialized Git repository on branch main." -ForegroundColor Green
} else {
    Write-Host "[INFO] Git repository already initialized." -ForegroundColor Yellow
}

# Stage and commit
& git add .
$status = & git status --porcelain
if ($status) {
    & git commit -m "feat: GIS-Based Highway Network & Accessibility Analysis project for Patna, Bihar"
    Write-Host "[SUCCESS] Committed all project deliverables to main branch." -ForegroundColor Green
} else {
    Write-Host "[INFO] Working tree is clean. Nothing to commit." -ForegroundColor Cyan
}

& git log -n 1 --oneline
