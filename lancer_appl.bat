@echo off
echo ==========================================
echo    Lancement de l'outil EDA - Orthophonie
echo ==========================================
echo.
echo 🔄 Mise a jour de l'application depuis GitHub...
git pull origin main

echo.
echo 🚀 Ouverture de l'interface web dans votre navigateur...
:: Au lieu de "python main.py", on utilise la commande de Streamlit
streamlit run interface_web.py

echo.
pause