import json
import requests
import os

CHANNELS_API = 'https://iptv-org.github.io/api/channels.json'
GUIDES_API = 'https://iptv-org.github.io/api/guides.json'

# Países prioritarios para NovaPlay
TARGET_COUNTRIES = ['AR', 'PY', 'UY', 'MX', 'US', 'CA', 'CL', 'CO', 'PE', 'ES', 'BR']

# Sitios que usamos en nuestro generador
ENABLED_SITES = [
    'mi.tv', 'gatotv.com', 'directv.com.ar', 'reportv.com.ar',
    'programacion.tcc.com.uy', 'directv.com.uy', 'ontvtonight.com',
    'directv.com', 'tvguide.com', 'tvpassport.com'
]

def main():
    print("Sincronizando base de datos de EPG (NovaPlay Edition)...")

    try:
        # 1. Cargar canales para saber a qué país pertenecen
        resp_ch = requests.get(CHANNELS_API, timeout=30)
        channels = resp_ch.json()

        channel_meta = {}
        for ch in channels:
            # Obtener códigos de país
            countries = [c['code'] for c in ch.get('countries', [])]
            # Si el canal pertenece a uno de nuestros países objetivo
            if any(c in TARGET_COUNTRIES for c in countries):
                channel_meta[ch['id']] = {
                    'n': ch.get('name', ''),
                    'l': ch.get('logo', ''),
                    'c': ', '.join([c['name'] for c in ch.get('countries', [])])
                }

        # 2. Cargar guías y filtrar
        resp_gd = requests.get(GUIDES_API, timeout=30)
        guides = resp_gd.json()

        optimized_db = []
        for g in guides:
            ch_id = g.get('channel')
            site = g.get('site')

            # Solo incluir si el canal es de interés Y el sitio está habilitado
            if ch_id in channel_meta and site in ENABLED_SITES:
                meta = channel_meta[ch_id]
                optimized_db.append({
                    'id': ch_id,
                    'name': meta['n'],
                    'logo': meta['l'],
                    'country': meta['c'],
                    'site': site
                })

        # Guardar base de datos optimizada
        os.makedirs('epg-search', exist_ok=True)
        with open('epg-search/epg_db.json', 'w', encoding='utf-8') as f:
            json.dump(optimized_db, f, separators=(',', ':'), ensure_ascii=False)

        print(f"Éxito: Base de datos creada con {len(optimized_db)} canales optimizados.")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
