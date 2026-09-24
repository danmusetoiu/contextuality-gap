$dir = 'C:\Users\danmu\Documents\Proiecte\EduClaude\research\contextuality'
Set-Location $dir
python ramsey_theta.py data/r37_21.g6 7 results/ramsey_r37_21.csv --workers 12 2>&1 | Tee-Object -FilePath "$dir\logs\ramsey_r37_21.out"
python ramsey_theta.py data/r38_27.g6 8 results/ramsey_r38_27.csv --workers 12 2>&1 | Tee-Object -FilePath "$dir\logs\ramsey_r38_27.out"
"RAMSEY DONE" | Out-File -Append "$dir\logs\ramsey_r38_27.out"
