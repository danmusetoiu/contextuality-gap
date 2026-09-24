$dir = 'C:\Users\danmu\Documents\Proiecte\EduClaude\research\contextuality'
Set-Location $dir
while (-not (Select-String -Path "$dir\logs\tf14.out" -Pattern 'ALL DONE' -Quiet)) { Start-Sleep -Seconds 30 }
# rerun the n=13 triangle-free screen at threshold 0.80 into a fresh tag (parts 5-19 of the first run used 0.95)
python run_geng.py --n 13 --tag tf13b --geng "-c -t" --mod 20 --thr 0.80 2>&1 | Tee-Object -FilePath "$dir\logs\tf13b_rerun.out"
"TF13B DONE" | Out-File -Append "$dir\logs\tf13b_rerun.out"
