@echo off
echo Startar Region Dalarna PDF Downloader...
echo.

if not exist venv (
    echo Skapar virtuell miljö...
    python -m venv venv
)

echo Aktiverar virtuell miljö...
call venv\Scripts\activate

echo Installerar beroenden...
pip install -q -r requirements.txt

echo Startar Streamlit-appen...
streamlit run src\app.py