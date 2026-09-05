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
                dt = datetime.strptime(date_part + offset_part, "%Y%m%d%H%M%S%z")
            else:
                dt = datetime.strptime(date_part, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')
    except:
        pass
    return date_str[:14]

def main():
    print("🚀 Generando Base de Datos EPG Ultra-Resiliente (v100)...")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    input_file = os.path.join(base_dir, 'epg', 'guide.xml')
    output_file = os.path.join(base_dir, 'epg-search', 'epg_db.json')

    if not os.path.exists(input_file):
        print(f"❌ Error: No se encuentra {input_file}")
        return

    # 1. CARGAR BASE DE DATOS ACTUAL (Para protección contra borrado accidental)
    current_db_count = 0
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                current_db_count = len(old_data)
        except:
            pass

    channels_map = {}
    now_utc = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')

    # Regex robustos para extracción directa
    re_channel = re.compile(r'<channel id="([^"]+)">')
    re_display_name = re.compile(r'<display-name[^>]*>(.*?)</display-name>')
    re_icon = re.compile(r'<icon src="([^"]+)"')
    re_prog = re.compile(r'<programme start="([^" ]+)[^"]*" stop="([^" ]+)[^"]*" channel="([^"]+)">')
    re_title = re.compile(r'<title[^>]*>(.*?)</title>')

    try:
        print("📖 Analizando guía por flujo de datos...")
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
                        start = parse_xmltv_date(match.group(1))
                        stop = parse_xmltv_date(match.group(2))
                        ch_id = match.group(3)

                        if ch_id in channels_map and stop > now_utc:
                            title_match = re_title.search(line)
                            title = title_match.group(1) if title_match else "Sin título"
                            title = title.replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'")

                            if len(channels_map[ch_id]['progs']) < 5:
                                channels_map[ch_id]['progs'].append([title, start, stop])

        # 2. VALIDACIÓN DE CALIDAD DE DATOS
        final_list = []
        total_progs = 0
        for ch_id in channels_map:
            data = channels_map[ch_id]
            if data['progs']:
                data['progs'].sort(key=lambda x: x[1])
                final_list.append(data)
                total_progs += len(data['progs'])

        print(f"📊 Estadísticas: {len(final_list)} canales con programación, {total_progs} programas totales.")

        # UMBRAL DE SEGURIDAD: Si los datos nuevos son sospechosamente pocos, abortar
        if len(final_list) < 100 or total_progs < 500:
            if current_db_count > 0:
                print("⚠️ ADVERTENCIA: La nueva guía tiene muy pocos datos. Abortando para proteger el buscador.")
                return

        final_list.sort(key=lambda x: x['name'])

        # 3. GUARDAR RESULTADO
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_list, f, separators=(',', ':'), ensure_ascii=False)

        print(f"✓ Éxito: Base de datos actualizada con {len(final_list)} canales.")

    except Exception as e:
        print(f"❌ Error crítico procesando EPG: {e}")
        exit(1)

if __name__ == "__main__":
    main()
