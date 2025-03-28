#!/usr/bin/env python
"""
Script para facilitar la configuración inicial del proyecto CalCarb con PostgreSQL.
Este script realiza las siguientes operaciones:
1. Verifica la conexión a PostgreSQL
2. Crea la base de datos si no existe
3. Aplica las migraciones
4. Carga los datos iniciales
5. Crea un superusuario si se desea
"""

import os
import sys
import subprocess
import getpass
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def check_postgres_connection():
    """Verifica la conexión a PostgreSQL y crea la base de datos si no existe"""
    print("\nVerificando conexión a PostgreSQL...")
    
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port="5433",
            user="postgres",
            password="root"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Conexión a PostgreSQL establecida correctamente.")
        
        # Verificar si la base de datos calcarb existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'calcarb'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creando base de datos 'calcarb'...")
            cursor.execute(sql.SQL("CREATE DATABASE calcarb"))
            print("✅ Base de datos 'calcarb' creada correctamente.")
        else:
            print("✅ Base de datos 'calcarb' ya existe.")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error al conectar con PostgreSQL: {e}")
        print("Por favor, asegúrate de que PostgreSQL está instalado y en ejecución.")
        print("Verifica que las credenciales en settings.py son correctas.")
        return False

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
        
        # Verificar si existe el archivo de fixtures
        fixtures_path = "miapp/fixtures/initial_data.json"
        if os.path.exists(fixtures_path):
            # Cargar fixtures
            subprocess.run([sys.executable, "manage.py", "loaddata", fixtures_path], check=True)
            print("✅ Datos iniciales cargados correctamente.")
        else:
            print("⚠️ No se encontró el archivo de fixtures. Omitiendo este paso.")
        
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
    
    create_user = input("¿Deseas crear un superusuario ahora? (s/n): ").lower()
    if create_user != "s":
        print("ℹ️ No se creará un superusuario ahora.")
        return True
    
    try:
        # Cambiar al directorio del proyecto
        os.chdir("CalculadoraCarbono")
        
        # Ejecutar createsuperuser interactivamente
        subprocess.run([sys.executable, "manage.py", "createsuperuser"], check=True)
        
        print("✅ Superusuario creado correctamente.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear superusuario: {e}")
        return False
    finally:
        # Volver al directorio original
        os.chdir("..")

def main():
    print("=" * 60)
    print("  Configuración inicial del proyecto CalCarb con PostgreSQL")
    print("=" * 60)
    
    # Verificar conexión a PostgreSQL y crear base de datos
    if not check_postgres_connection():
        print("❌ No se pudo configurar la conexión a PostgreSQL. Abortando.")
        return
    
    # Aplicar migraciones
    if not apply_migrations():
        print("❌ Error al aplicar migraciones. Abortando.")
        return
    
    # Cargar fixtures
    load_fixtures()
    
    # Crear superusuario
    create_superuser()
    
    print("\n" + "=" * 60)
    print("  ¡Configuración completada!")
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