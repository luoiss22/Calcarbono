#!/usr/bin/env python
"""
Script para facilitar la configuración inicial del proyecto CalCarb con SQLite.
Este script realiza las siguientes operaciones:
1. Aplica las migraciones
2. Carga los datos iniciales
3. Crea un superusuario si se desea
"""

import os
import sys
import subprocess
import getpass

def apply_migrations():
    """Aplica las migraciones a la base de datos"""
    print("\nAplicando migraciones...")
    
    try:
        # Cambiar al directorio del proyecto
        os.chdir("CalculadoraCarbono")
        
        # Crear migraciones
        subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
        
        # Aplicar migraciones
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        
        print("✅ Migraciones aplicadas correctamente.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al aplicar migraciones: {e}")
        return False
    finally:
        # Volver al directorio original
        os.chdir("..")

def load_fixtures():
    """Carga los datos iniciales"""
    print("\nCargando datos iniciales...")
    
    try:
        # Cambiar al directorio del proyecto
        os.chdir("CalculadoraCarbono")
        
        # Cargar fixtures
        subprocess.run([sys.executable, "manage.py", "loaddata", "miapp/fixtures/initial_data.json"], check=True)
        
        print("✅ Datos iniciales cargados correctamente.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al cargar datos iniciales: {e}")
        return False
    finally:
        # Volver al directorio original
        os.chdir("..")

def create_superuser():
    """Crea un superusuario"""
    print("\nCreando superusuario...")
    
    create_user = input("\u00bfDeseas crear un superusuario ahora? (s/n): ").lower()
    if create_user != "s":
        print("\u2139️ No se creará un superusuario ahora.")
        return True
    
    try:
        # Cambiar al directorio del proyecto
        os.chdir("CalculadoraCarbono")
        
        # Ejecutar createsuperuser interactivamente
        subprocess.run([sys.executable, "manage.py", "createsuperuser"], check=True)
        
        print("\u2705 Superusuario creado correctamente.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\u274c Error al crear superusuario: {e}")
        return False
    finally:
        # Volver al directorio original
        os.chdir("..")

def main():
    print("=" * 60)
    print("  Configuración inicial del proyecto CalCarb con SQLite")
    print("=" * 60)
    
    # Aplicar migraciones
    apply_migrations()
    
    # Cargar fixtures
    load_fixtures()
    
    # Crear superusuario
    create_superuser()
    
    print("\n" + "=" * 60)
    print("  \u00a1Configuración completada!")
    print("=" * 60)
    print("\nPara iniciar el servidor de desarrollo:")
    print("  1. Activar el entorno virtual (si no está activado)")
    print("  2. cd CalculadoraCarbono")
    print("  3. python manage.py runserver")
    print("\nLa API estará disponible en http://localhost:8000/api/")
    print("La documentación de la API estará en http://localhost:8000/swagger/")
    print("El panel de administración estará en http://localhost:8000/admin/")

if __name__ == "__main__":
    main()