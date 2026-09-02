import json
import requests
import os

CHANNELS_API = 'https://iptv-org.github.io/api/channels.json'
GUIDES_API = 'https://iptv-org.github.io/api/guides.json'

# Países de Latinoamérica y el Caribe (LATAC)
TARGET_COUNTRIES = [
    'AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV',
    'GT', 'HT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'UY',
    'VE', 'BS', 'BB', 'JM', 'LC', 'TT', 'AW', 'CW', 'GP', 'MQ'
]

# Sitios especializados en la región
ENABLED_SITES = [
    'mi.tv', 'gatotv.com', 'directv.com.ar', 'reportv.com.ar',
    'programacion.tcc.com.uy', 'directv.com.uy', 'tv.movistar.com.pe',
    'tv.movistar.co', 'siba.com.co', 'claro.com.co', 'clarotv.com.br'
]

def main():
    print("Filtrando Base de Datos EPG para Latinoamérica y el Caribe...")

    try:
        # 1. Cargar canales para saber a qué país pertenecen
        resp_ch = requests.get(CHANNELS_API, timeout=30)
        channels = resp_ch.json()

        channel_meta = {}
        for ch in channels:
            countries = [c['code'] for c in ch.get('countries', [])]
            # Filtrado estricto por región solicitada
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

            if ch_id in channel_meta and site in ENABLED_SITES:
                meta = channel_meta[ch_id]
                optimized_db.append({
                    'id': ch_id,
                    'name': meta['n'],
                    'logo': meta['l'],
                    'country': meta['c'],
                    'site': site
                })

        os.makedirs('epg-search', exist_ok=True)
        with open('epg-search/epg_db.json', 'w', encoding='utf-8') as f:
            json.dump(optimized_db, f, separators=(',', ':'), ensure_ascii=False)

        print(f"✓ Base de Datos LATAM lista: {len(optimized_db)} canales.")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
