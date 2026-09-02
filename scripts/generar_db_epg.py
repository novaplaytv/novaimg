import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime

def main():
    print("🚀 Generando Base de Datos de Búsqueda En Vivo desde guide.xml...")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    input_file = os.path.join(base_dir, 'epg', 'guide.xml')
    output_file = os.path.join(base_dir, 'epg-search', 'epg_db.json')

    if not os.path.exists(input_file):
        print(f"❌ Error: No se encuentra {input_file}")
        return

    try:
        tree = ET.parse(input_file)
        root = tree.getroot()

        # 1. Mapear Canales
        channels_map = {}
        for channel in root.findall('channel'):
            ch_id = channel.get('id')
            display_name = channel.find('display-name').text if channel.find('display-name') is not None else ch_id
            icon_elem = channel.find('icon')
            logo = icon_elem.get('src') if icon_elem is not None else ""

            country = "LATAM"
            if '.' in ch_id:
                parts = ch_id.split('.')
                if len(parts) > 1:
                    suffix = parts[1].split('@')[0].split('#')[0]
                    if len(suffix) == 2:
                        country = suffix.upper()

            channels_map[ch_id] = {
                'id': ch_id,
                'name': display_name,
                'logo': logo,
                'country': country,
                'site': ch_id.split('@')[-1] if '@' in ch_id else "XMLTV",
                'progs': [] # Aquí guardaremos la programación mini
            }

        # 2. Mapear Programación (Solo lo más reciente para no inflar el archivo)
        now_str = datetime.utcnow().strftime('%Y%m%d%H%M%S')

        for prog in root.findall('programme'):
            ch_id = prog.get('channel')
            if ch_id in channels_map:
                start = prog.get('start', '')[:14] # YYYYMMDDHHMMSS
                stop = prog.get('stop', '')[:14]
                title = prog.find('title').text if prog.find('title') is not None else "Sin título"

                # Solo guardamos programas del día actual o futuro cercano para ahorrar espacio
                if stop > now_str:
                    channels_map[ch_id]['progs'].append([title, start, stop])

        # 3. Limitar programas (Máximo 5 por canal para el buscador)
        optimized_list = []
        for ch_id in channels_map:
            ch_data = channels_map[ch_id]
            ch_data['progs'].sort(key=lambda x: x[1])
            ch_data['progs'] = ch_data['progs'][:5]
            optimized_list.append(ch_data)

        # 4. Guardar JSON
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(optimized_list, f, separators=(',', ':'), ensure_ascii=False)

        print(f"✓ Éxito: {len(optimized_list)} canales indexados con programación 'En Vivo'.")

    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
