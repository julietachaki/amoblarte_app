# Amoblarte - Sistema de Gestión de Presupuestos

Sistema web para la gestión de clientes y presupuestos con generación automática de PDFs.

## Características

- ✅ Gestión completa de clientes (nombre, apellido, celular, dirección)
- ✅ Gestión de presupuestos con descripción e imágenes
- ✅ Cálculo de precios (materiales, mano de obra, opción con tarjeta)
- ✅ Generación automática de PDFs
- ✅ Guardado automático en carpeta del escritorio
- ✅ Interfaz web moderna y responsive
- ✅ Edición y eliminación de registros

## Instalación

### Método Automático (Recomendado)

1. **Ejecutar instalador:**
   - Doble clic en `install.bat` (Windows)
   - O desde consola: `install.bat`

2. **Ejecutar aplicación:**
   - Doble clic en `run.bat` (Windows)
   - O desde consola: `run.bat`

3. **Abrir en el navegador:**
   ```
   http://localhost:5000
   ```

### Método Manual

1. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   # o
   source venv/bin/activate  # En Linux/Mac
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inicializar base de datos:**
   ```bash
   python init_flask_db.py
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

## Uso

### Gestión de Clientes
- **Agregar cliente:** Navega a "Clientes" → "Nuevo Cliente"
- **Editar cliente:** Haz clic en el botón de editar en la lista de clientes
- **Eliminar cliente:** Haz clic en el botón de eliminar (con confirmación)

### Gestión de Presupuestos
- **Crear presupuesto:** Navega a "Presupuestos" → "Nuevo Presupuesto"
- **Asociar cliente:** Selecciona un cliente existente o crea uno nuevo
- **Agregar descripción:** Describe el trabajo a realizar
- **Subir imagen:** Opcional, puedes agregar una imagen del proyecto
- **Configurar precios:**
  - Precio de materiales
  - Precio de mano de obra
  - Opcional: Precio con tarjeta
- **Generar PDF:** Se crea automáticamente al guardar

### Características del PDF
- Información completa del cliente
- Detalles del presupuesto
- Cálculo automático de totales
- Guardado en carpeta "Presupuestos" del escritorio
- Nombre del archivo: `[Nombre Cliente]_[Número Presupuesto].pdf`

## Estructura del Proyecto

```
amoblarte_app/
├── app.py                 # Aplicación Flask principal
├── database.py           # Configuración de base de datos
├── models/               # Modelos de datos
│   ├── cliente.py
│   └── presupuesto.py
├── templates/            # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── clientes.html
│   ├── nuevo_cliente.html
│   ├── editar_cliente.html
│   ├── presupuestos.html
│   ├── nuevo_presupuesto.html
│   └── editar_presupuesto.html
├── static/               # Archivos estáticos
│   └── uploads/          # Imágenes subidas
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## Base de Datos

La aplicación utiliza SQLite como base de datos. El archivo `amoblarte.db` se crea automáticamente al ejecutar la aplicación por primera vez.

### Tablas:
- **clientes:** Información de clientes
- **presupuestos:** Presupuestos asociados a clientes

## Personalización

### Cambiar carpeta de PDFs
Modifica la variable `PDF_FOLDER` en `app.py`:
```python
app.config['PDF_FOLDER'] = 'ruta/personalizada'
```

### Cambiar clave secreta
Modifica la variable `SECRET_KEY` en `app.py`:
```python
app.config['SECRET_KEY'] = 'tu_clave_secreta_personalizada'
```

## Solución de Problemas

### Error: "no such table: clientes"
**Solución:** Ejecuta el script de inicialización:
```bash
python init_flask_db.py
```

### Error de permisos en Windows
Si tienes problemas con permisos para crear carpetas, ejecuta la aplicación como administrador.

### Error de dependencias
Asegúrate de tener Python 3.7+ instalado y todas las dependencias del `requirements.txt`.

### Base de datos corrupta
**Opción 1:** Ejecuta el script de reset:
```bash
python reset_db.py
```

**Opción 2:** Elimina manualmente el archivo `amoblarte.db` y ejecuta `init_db.py`

### Error: "AttributeError: type object 'Cliente' has no attribute 'query'"
Este error indica que la base de datos no está inicializada. Ejecuta:
```bash
python init_flask_db.py
```

## Soporte

Para reportar problemas o solicitar nuevas funcionalidades, contacta al desarrollador.
