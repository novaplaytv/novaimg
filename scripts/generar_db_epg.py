import json
import os
import re
from datetime import datetime, timezone

def parse_xmltv_date(date_str):
    if not date_str: return ""
    try:
        # Extraer los primeros 14 números (YYYYMMDDHHMMSS)
        clean = re.sub(r'[^0-9]', '', date_str)[:14]
        return clean
    except:
        return date_str[:14]

def main():
    print("🚀 Generando Base de Datos de Búsqueda (Modo Ultra-Resiliente)...")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    input_file = os.path.join(base_dir, 'epg', 'guide.xml')
    output_file = os.path.join(base_dir, 'epg-search', 'epg_db.json')

    if not os.path.exists(input_file):
        print(f"❌ Error: No se encuentra {input_file}")
        return

    channels_map = {}
    now_utc = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')

    # Expresiones regulares para extracción veloz sin importar si el XML está roto
    re_channel = re.compile(r'<channel id="([^"]+)">')
    re_display_name = re.compile(r'<display-name[^>]*>(.*?)</display-name>')
    re_icon = re.compile(r'<icon src="([^"]+)"')
    re_prog = re.compile(r'<programme start="([^"]+)" stop="([^"]+)" channel="([^"]+)">')
    re_title = re.compile(r'<title[^>]*>(.*?)</title>')

    try:
        print("📖 Leyendo guía por bloques...")
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            current_prog = None

            for line in f:
                line = line.strip()

                # 1. Capturar Canales
                if '<channel' in line:
                    match = re_channel.search(line)
                    if match:
                        ch_id = match.group(1)
                        name_match = re_display_name.search(line)
                        icon_match = re_icon.search(line)

                        name = name_match.group(1) if name_match else ch_id
                        icon = icon_match.group(1) if icon_match else ""

                        country = "LATAM"
                        if '#' in ch_id: country = ch_id.split('#')[0].upper()

                        channels_map[ch_id] = {
                            'id': ch_id, 'name': name, 'logo': icon, 'country': country,
                            'site': ch_id.split('@')[-1] if '@' in ch_id else "XMLTV",
                            'progs': []
                        }
                    continue

                # 2. Capturar Programas
                if '<programme' in line:
                    match = re_prog.search(line)
                    if match:
                        start = parse_xmltv_date(match.group(1))
                        stop = parse_xmltv_date(match.group(2))
                        ch_id = match.group(3)

                        if ch_id in channels_map and stop > now_utc:
                            title_match = re_title.search(line)
                            title = title_match.group(1) if title_match else "Sin título"
                            # Limpiar entidades HTML simples
                            title = title.replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'")

                            if len(channels_map[ch_id]['progs']) < 5:
                                channels_map[ch_id]['progs'].append([title, start, stop])
                    continue

        # Filtrar solo canales con programación útil y convertirlos en lista
        final_list = []
        for ch_id in channels_map:
            data = channels_map[ch_id]
            # Ordenar por hora de inicio
            data['progs'].sort(key=lambda x: x[1])
            final_list.append(data)

        # Ordenar canales por nombre
        final_list.sort(key=lambda x: x['name'])

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_list, f, separators=(',', ':'), ensure_ascii=False)

        print(f"✓ Éxito: {len(final_list)} canales indexados en el buscador.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        exit(1)

if __name__ == "__main__":
    main()
