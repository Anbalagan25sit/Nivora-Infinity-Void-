@echo off
cd C:\Users\Nivorichi\Downloads\Nivora-Ver-loop-main\Nivora-Ver-loop-main
.\venv\Scripts\python.exe run_checks.py > output.txt 2>&1
type output.txt
