from supabase import create_client, Client

# ✅ Configura tu conexión a Supabase

SUPABASE_URL = "SUPABASE_URL"

SUPABASE_KEY = "SUPABASE_KEY"

# 🔹 Crea el cliente global de conexión

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
 