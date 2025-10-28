from supabase import create_client, Client

# ✅ Configura tu conexión a Supabase

SUPABASE_URL = "TU_SUPABASE_URL"

SUPABASE_KEY = "TU_SUPABASE_KEY"

# 🔹 Crea el cliente global de conexión

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
 