import json
import os
import re
from datetime import datetime, timezone

def parse_xmltv_date(date_str):
    """Convierte fechas XMLTV (con o sin offset) a string YYYYMMDDHHMMSS en UTC."""
    if not date_str: return ""
    try:
        # Extraer fecha y offset: 20260904073000 -0300
        match = re.search(r'(\d{14})\s*([+-]\d{4})?', date_str)
        if match:
            date_part = match.group(1)
            offset_part = match.group(2)
            if offset_part:
                # Parsear con zona horaria
                dt = datetime.strptime(date_part + offset_part, "%Y%m%d%H%M%S%z")
            else:
                # Si no hay offset, asumir UTC
                dt = datetime.strptime(date_part, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)

            # Devolver siempre en UTC
            return dt.astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')
    except Exception as e:
        print(f"⚠️ Error parseando fecha {date_str}: {e}")

    return date_str[:14]

def main():
    print("🚀 Generando Base de Datos de EPG Sincronizada (v97)...")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    input_file = os.path.join(base_dir, 'epg', 'guide.xml')
    output_file = os.path.join(base_dir, 'epg-search', 'epg_db.json')

    if not os.path.exists(input_file):
        print(f"❌ Error: No se encuentra {input_file}")
        return

    channels_map = {}
    # Hora actual en UTC para el filtrado inicial
    now_utc = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')

    re_channel = re.compile(r'<channel id="([^"]+)">')
    re_display_name = re.compile(r'<display-name[^>]*>(.*?)</display-name>')
    re_icon = re.compile(r'<icon src="([^"]+)"')
    re_prog = re.compile(r'<programme start="([^"]+)" stop="([^"]+)" channel="([^"]+)">')
    re_title = re.compile(r'<title[^>]*>(.*?)</title>')

    try:
        print("📖 Procesando guía y normalizando a UTC...")
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()

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

                if '<programme' in line:
                    match = re_prog.search(line)
                    if match:
                        # NORMALIZACIÓN A UTC
                        start = parse_xmltv_date(match.group(1))
                        stop = parse_xmltv_date(match.group(2))
                        ch_id = match.group(3)

                        if ch_id in channels_map and stop > now_utc:
                            title_match = re_title.search(line)
                            title = title_match.group(1) if title_match else "Sin título"
                            title = title.replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'")

                            if len(channels_map[ch_id]['progs']) < 5:
                                channels_map[ch_id]['progs'].append([title, start, stop])
                    continue

        final_list = []
        for ch_id in channels_map:
            data = channels_map[ch_id]
            data['progs'].sort(key=lambda x: x[1])
            final_list.append(data)

        final_list.sort(key=lambda x: x['name'])

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_list, f, separators=(',', ':'), ensure_ascii=False)

        print(f"✓ Éxito: {len(final_list)} canales sincronizados en UTC.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        exit(1)

if __name__ == "__main__":
    main()
