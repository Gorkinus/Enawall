# autobackup.ps1 — guarda y sube cambios del proyecto a GitHub automaticamente
# Uso: ejecutar manualmente o via Task Scheduler

$PROJECT = "C:\Users\nikik\Documents\00_vida_nueva\04_firewall_win"
$LOG     = "$PROJECT\backup.log"

Set-Location $PROJECT

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Verificar si hay cambios
$status = git status --porcelain
if (-not $status) {
    Add-Content $LOG "[$timestamp] Sin cambios — nada que guardar"
    exit 0
}

# Commit + push
git add firewall_v2.py .gitignore
git commit -m "auto-backup $timestamp"

if ($?) {
    git push origin main 2>&1
    if ($?) {
        Add-Content $LOG "[$timestamp] OK — backup subido a GitHub"
    } else {
        Add-Content $LOG "[$timestamp] WARN — commit OK pero push fallo (sin internet?)"
    }
} else {
    Add-Content $LOG "[$timestamp] ERROR — commit fallo"
}
