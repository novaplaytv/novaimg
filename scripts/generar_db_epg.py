import json
import urllib.request
import os

CHANNELS_API = 'https://iptv-org.github.io/api/channels.json'
GUIDES_API = 'https://iptv-org.github.io/api/guides.json'

# Países de Latinoamérica y el Caribe (LATAC)
TARGET_COUNTRIES = [
    'AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV',
    'GT', 'HT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'PR', 'UY',
    'VE', 'BS', 'BB', 'JM', 'LC', 'TT', 'AW', 'CW', 'GP', 'MQ'
]

# Sitios especializados en la región habilitados en NovaPlay
ENABLED_SITES = [
    'mi.tv', 'gatotv.com', 'directv.com.ar', 'reportv.com.ar',
    'programacion.tcc.com.uy', 'directv.com.uy', 'tv.movistar.com.pe',
    'tv.movistar.co', 'siba.com.co', 'claro.com.co', 'clarotv.com.br'
]

def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def main():
    print("🚀 Iniciando generación de Base de Datos EPG NovaPlay...")

    # Obtener ruta absoluta del script para guardar el JSON en el lugar correcto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, 'epg-search')
    output_file = os.path.join(output_dir, 'epg_db.json')

    try:
        # 1. Cargar canales
        channels = get_json(CHANNELS_API)
        channel_meta = {}
        for ch in channels:
            cid = ch.get('id')
            country = ch.get('country')
            if cid and country in TARGET_COUNTRIES:
                channel_meta[cid] = {
                    'n': ch.get('name', ''),
                    'l': ch.get('logo', ''),
                    'c': country
                }

        print(f"✓ {len(channel_meta)} canales mapeados en la región.")

        # 2. Cargar guías y filtrar
        guides = get_json(GUIDES_API)
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
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(optimized_db, f, separators=(',', ':'), ensure_ascii=False)

        print(f"✓ Éxito: {len(optimized_db)} registros generados en {output_file}")

    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
