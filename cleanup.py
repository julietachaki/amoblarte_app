#!/usr/bin/env python3
"""
Script para limpiar archivos innecesarios del proyecto
"""
import os
import sys


def cleanup_files():
    """Elimina archivos de prueba y scripts innecesarios"""
    files_to_remove = [
        'test_db.py',
        'init_db.py', 
        'init_db_simple.py',
        'create_tables.py',
        'reset_db.py',
        'reset_db.bat'
    ]
    
    print("Limpiando archivos innecesarios...")
    
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ Eliminado: {file}")
            except Exception as e:
                print(f"❌ Error eliminando {file}: {e}")
        else:
            print(f"⚠️  No encontrado: {file}")
    
    print("\n🎉 Limpieza completada!")

if __name__ == "__main__":
    cleanup_files()
