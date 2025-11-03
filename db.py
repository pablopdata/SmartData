from supabase import create_client, Client
import io

import os

# Configura tu conexión a Supabase

SUPABASE_URL = os.getenv("https://bxgpbkimoqyzfnehgnhh.supabase.co")

SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4Z3Bia2ltb3F5emZuZWhnbmhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwMzc1NjMsImV4cCI6MjA3NjYxMzU2M30.dTaMH4d0hNUd3OP740stlhb5lvmG8ufgSWqNFHwtFTs")

# 🔹 Crea el cliente global de conexión

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
 