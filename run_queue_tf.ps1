$dir = 'C:\Users\danmu\Documents\Proiecte\EduClaude\research\contextuality'
Set-Location $dir
while (-not (Select-String -Path "$dir\logs\n11.out" -Pattern 'ALL DONE' -Quiet)) { Start-Sleep -Seconds 20 }
python run_geng.py --n 12 --tag tf12 --geng "-c -t" --mod 10 --thr 0.70 2>&1 | Tee-Object -FilePath "$dir\logs\tf12.out"
python run_geng.py --n 13 --tag tf13 --geng "-c -t" --mod 20 --thr 0.74 2>&1 | Tee-Object -FilePath "$dir\logs\tf13.out"
"QUEUE DONE" | Out-File -Append "$dir\logs\tf13.out"
