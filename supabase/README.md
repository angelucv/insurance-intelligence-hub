# Supabase / PostgreSQL

1. Crea un proyecto en [Supabase](https://supabase.com) (tier gratuito).
2. En **Project Settings → Database**, copia la **Connection string** (URI, modo *Transaction* o *Session* con contraseña).
3. En **SQL Editor**, pega y ejecuta `migrations/001_initial.sql`, luego `migrations/002_market_sudeaseg.sql` (tablas de referencia SUDEASEG para el ETL).

Opcional más adelante: activar **Row Level Security** y políticas por rol cuando integres Supabase Auth.
