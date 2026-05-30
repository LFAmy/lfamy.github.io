# Copy new root-level pages to _deploy
Copy-Item "G:\lam-fung-academy\student.html" -Destination "G:\lam-fung-academy\_deploy\student.html" -Force
Write-Host "Copied: student.html"

Copy-Item "G:\lam-fung-academy\parent.html" -Destination "G:\lam-fung-academy\_deploy\parent.html" -Force
Write-Host "Copied: parent.html"

# Copy updated JS files
Copy-Item "G:\lam-fung-academy\docs\data\lf-navbar.js" -Destination "G:\lam-fung-academy\_deploy\docs\data\lf-navbar.js" -Force
Write-Host "Copied: lf-navbar.js"

Copy-Item "G:\lam-fung-academy\docs\data\lf-payment.js" -Destination "G:\lam-fung-academy\_deploy\docs\data\lf-payment.js" -Force
Write-Host "Copied: lf-payment.js"

Copy-Item "G:\lam-fung-academy\docs\data\lf-ux-enhance.js" -Destination "G:\lam-fung-academy\_deploy\docs\data\lf-ux-enhance.js" -Force
Write-Host "Copied: lf-ux-enhance.js"

# Copy updated HTML pages that were modified
$updatedPages = @(
    "docs\enroll.html",
    "docs\parent-portal.html",
    "docs\student-practice.html",
    "docs\student-platform.html",
    "parent-dashboard.html"
)
foreach ($page in $updatedPages) {
    $src = "G:\lam-fung-academy\$page"
    $dst = "G:\lam-fung-academy\_deploy\$page"
    if (Test-Path $src) {
        $dstDir = Split-Path $dst -Parent
        if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
        Copy-Item $src -Destination $dst -Force
        Write-Host "Copied: $page"
    }
}

Write-Host "`nSync complete! Ready for: firebase deploy --only hosting"
