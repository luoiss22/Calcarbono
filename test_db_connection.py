import psycopg2

try:
    # Intenta conectar a PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        port="5433",
        user="postgres",
        password="root",
        client_encoding='UTF8'
    )
    
    # Si llega aquí, la conexión fue exitosa
    print("¡Conexión exitosa a PostgreSQL!")
    
    # Crear cursor
    cursor = conn.cursor()
    
    # Verificar si la base de datos calcarb existe
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'calcarb'")
    exists = cursor.fetchone()
    
    if exists:
        print("La base de datos 'calcarb' ya existe.")
    else:
        print("La base de datos 'calcarb' no existe, intentando crearla...")
        
        # Cerrar la conexión actual
        conn.close()
        
        # Conectar a 'postgres' para poder crear base de datos
        conn = psycopg2.connect(
            host="localhost",
            port="5433",
            user="postgres",
            password="root",
            database="postgres",
            client_encoding='UTF8'
        )
        conn.autocommit = True  # Necesario para CREATE DATABASE
        cursor = conn.cursor()
        
        # Crear base de datos
        cursor.execute("CREATE DATABASE calcarb WITH ENCODING 'UTF8'")
        print("Base de datos 'calcarb' creada exitosamente.")
    
    # Cerrar la conexión
    if conn:
        cursor.close()
        conn.close()
        print("Conexión cerrada.")

except Exception as e:
    print(f"Error al conectar a PostgreSQL: {e}")
    print("Detalles del error:", str(e).encode('utf-8'))
