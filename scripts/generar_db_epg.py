import json
import os
import xml.etree.ElementTree as ET

def main():
    print("🚀 Generando Base de Datos de Búsqueda desde guide.xml...")

    # Obtener ruta absoluta del script para localizar archivos
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_dir)
    input_file = os.path.join(base_dir, 'epg', 'guide.xml')
    output_file = os.path.join(base_dir, 'epg-search', 'epg_db.json')

    if not os.path.exists(input_file):
        print(f"❌ Error: No se encuentra {input_file}")
        return

    try:
        # Parsear el XMLTV real que acabamos de generar
        tree = ET.parse(input_file)
        root = tree.getroot()

        optimized_db = []
        # Extraer canales definidos en el XML
        for channel in root.findall('channel'):
            ch_id = channel.get('id')
            display_name = channel.find('display-name').text if channel.find('display-name') is not None else ch_id
            icon_elem = channel.find('icon')
            logo = icon_elem.get('src') if icon_elem is not None else ""

            # Deducir país desde el ID (ej: Telefe.ar@SD -> AR)
            country = "LATAM"
            if '.' in ch_id:
                parts = ch_id.split('.')
                if len(parts) > 1:
                    # Extraer el código de país (ej: ar, py, uy)
                    suffix = parts[1].split('@')[0].split('#')[0]
                    if len(suffix) == 2:
                        country = suffix.upper()

            optimized_db.append({
                'id': ch_id,
                'name': display_name,
                'logo': logo,
                'country': country,
                'site': ch_id.split('@')[-1] if '@' in ch_id else "XMLTV"
            })

        # Guardar base de datos optimizada para el buscador web
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(optimized_db, f, separators=(',', ':'), ensure_ascii=False)

        print(f"✓ Éxito: {len(optimized_db)} IDs reales indexados en epg_db.json")

    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
