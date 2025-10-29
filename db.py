from supabase import create_client, Client

# Configura tu conexión a Supabase

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 🔹 Crea el cliente global de conexión

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
 