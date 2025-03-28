#!/usr/bin/env python
"""
Script para facilitar la configuración inicial del proyecto CalCarb.
Este script realiza las siguientes operaciones:
1. Verifica que PostgreSQL esté instalado y accesible
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

def check_postgres():
    """Verifica que PostgreSQL esté instalado y accesible"""
    print("Verificando instalación de PostgreSQL...")
    
    # Solicitar credenciales de PostgreSQL
    pg_user = input("Usuario de PostgreSQL [postgres]: ") or "postgres"
    pg_password = getpass.getpass("Contraseña de PostgreSQL: ")
    pg_host = input("Host de PostgreSQL [localhost]: ") or "localhost"
    pg_port = input("Puerto de PostgreSQL [5432]: ") or "5432"
    
    try:
        # Intentar conectar a PostgreSQL
        conn = psycopg2.connect(
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port,
            dbname="postgres"  # Base de datos por defecto
        )
        conn.close()
        print("✅ Conexión a PostgreSQL establecida correctamente.")
        return pg_user, pg_password, pg_host, pg_port
    except Exception as e:
        print(f"❌ Error al conectar a PostgreSQL: {e}")
        print("Por favor, verifica que PostgreSQL esté instalado y las credenciales sean correctas.")
        sys.exit(1)

def create_database(pg_user, pg_password, pg_host, pg_port):
    """Crea la base de datos si no existe"""
    db_name = input("Nombre de la base de datos [calcarb_db]: ") or "calcarb_db"
    
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            user=pg_user,
            password=pg_password,
            host=pg_host,
            port=pg_port,
            dbname="postgres"  # Base de datos por defecto
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar si la base de datos ya existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            # Crear la base de datos
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            print(f"✅ Base de datos '{db_name}' creada correctamente.")
        else:
            print(f"ℹ️ La base de datos '{db_name}' ya existe.")
        
        cursor.close()
        conn.close()
        return db_name
    except Exception as e:
        print(f"❌ Error al crear la base de datos: {e}")
        sys.exit(1)

def update_settings(pg_user, pg_password, pg_host, pg_port, db_name):
    """Actualiza el archivo settings.py con las credenciales de la base de datos"""
    settings_path = os.path.join("CalculadoraCarbono", "CalculadoraCarbono", "settings.py")
    
    try:
        with open(settings_path, "r") as f:
            settings_content = f.read()
        
        # Buscar y reemplazar la configuración de la base de datos
        db_config = f"""DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '{db_name}',
        'USER': '{pg_user}',
        'PASSWORD': '{pg_password}',
        'HOST': '{pg_host}',
        'PORT': '{pg_port}',
    }}
}}"""
        
        # Buscar el bloque DATABASES
        start_index = settings_content.find("DATABASES = {")
        if start_index == -1:
            print("❌ No se encontró la configuración de DATABASES en settings.py")
            return False
        
        # Encontrar el final del bloque
        depth = 0
        end_index = start_index
        for i in range(start_index, len(settings_content)):
            if settings_content[i] == "{":
                depth += 1
            elif settings_content[i] == "}":
                depth -= 1
                if depth == 0:
                    end_index = i + 1
                    break
        
        # Reemplazar el bloque
        new_settings = settings_content[:start_index] + db_config + settings_content[end_index:]
        
        with open(settings_path, "w") as f:
            f.write(new_settings)
        
        print("✅ Archivo settings.py actualizado correctamente.")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar settings.py: {e}")
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
    print("  Configuración inicial del proyecto CalCarb")
    print("=" * 60)
    
    # Verificar PostgreSQL
    pg_user, pg_password, pg_host, pg_port = check_postgres()
    
    # Crear base de datos
    db_name = create_database(pg_user, pg_password, pg_host, pg_port)
    
    # Actualizar settings.py
    update_settings(pg_user, pg_password, pg_host, pg_port, db_name)
    
    # Aplicar migraciones
    apply_migrations()
    
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
