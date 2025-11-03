@echo off
call .venv310\Scripts\activate
python main.py --test-auth --visible --log-level DEBUG
pause
