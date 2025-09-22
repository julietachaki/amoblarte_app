# Este archivo se mantiene para compatibilidad
# La aplicación web principal está en app.py

from app import app

if __name__ == "__main__":
    print("Iniciando aplicación web Amoblarte...")
    print("Abre tu navegador en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
