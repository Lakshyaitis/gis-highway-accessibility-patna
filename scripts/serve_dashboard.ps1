<#
===============================================================================
Simple Local Web Server for Patna GIS Dashboard
Runs a lightweight HTTP server on port 8080 and opens the browser.
===============================================================================
#>

$port = 8080
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

$listener = New-Object System.Net.HttpListener
$prefix = "http://localhost:$port/"
$listener.Prefixes.Add($prefix)

try {
    $listener.Start()
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host " Patna GIS Dashboard Server running at: http://localhost:$port/dashboard/" -ForegroundColor Green
    Write-Host " Press Ctrl+C in this window to stop the server." -ForegroundColor Yellow
    Write-Host "=================================================================" -ForegroundColor Cyan

    Start-Process "http://localhost:$port/dashboard/index.html"

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response

        $relPath = $request.Url.LocalPath.TrimStart('/')
        if (-not $relPath -or $relPath -eq "dashboard" -or $relPath -eq "dashboard/") {
            $relPath = "dashboard/index.html"
        }

        $filePath = Join-Path $projectRoot ($relPath -replace '/', '\')

        if (Test-Path $filePath -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            $mime = switch ($ext) {
                ".html" { "text/html; charset=utf-8" }
                ".css"  { "text/css; charset=utf-8" }
                ".js"   { "application/javascript; charset=utf-8" }
                ".json" { "application/json; charset=utf-8" }
                ".geojson" { "application/geo+json; charset=utf-8" }
                ".svg"  { "image/svg+xml" }
                ".png"  { "image/png" }
                ".csv"  { "text/csv; charset=utf-8" }
                default { "application/octet-stream" }
            }
            $response.ContentType = $mime
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
        } else {
            $response.StatusCode = 404
            $errBytes = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found: $relPath")
            $response.ContentLength64 = $errBytes.Length
            $response.OutputStream.Write($errBytes, 0, $errBytes.Length)
        }
        $response.OutputStream.Close()
    }
} finally {
    $listener.Stop()
    $listener.Close()
}
