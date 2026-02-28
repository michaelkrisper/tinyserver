$resp = Invoke-WebRequest -UseBasicParsing http://localhost:8080
$etag = $resp.Headers["ETag"]
Write-Host "Got ETag: $etag"

try {
    $resp2 = Invoke-WebRequest -UseBasicParsing http://localhost:8080 -Headers @{"If-None-Match"=$etag}
    Write-Host "Second request status: $($resp2.StatusCode.value__)"
} catch {
    Write-Host "Second request Exception: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Second request status: $($_.Exception.Response.StatusCode.value__)"
    }
}
