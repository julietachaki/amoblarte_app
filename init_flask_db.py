#!/usr/bin/env python3
"""
Script para inicializar la base de datos de Amoblarte con Flask-SQLAlchemy
"""
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_flask_database():
    """Inicializa la base de datos usando Flask-SQLAlchemy"""
    print("Inicializando base de datos con Flask-SQLAlchemy...")
    
    try:
        # Importar la aplicación Flask
        from app import Cliente, Presupuesto, app, db
        
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Verificar que las tablas existen
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tablas en la base de datos: {tables}")
            
            if 'clientes' in tables and 'presupuestos' in tables:
                print("✅ Base de datos inicializada correctamente")
                return True
            else:
                print("❌ Error: No se encontraron las tablas esperadas")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_flask_database()
    if success:
        print("\n🎉 ¡Base de datos lista para usar!")
        print("Ahora puedes ejecutar: python app.py")
    else:
        print("\n❌ Error al inicializar la base de datos")
        sys.exit(1)

