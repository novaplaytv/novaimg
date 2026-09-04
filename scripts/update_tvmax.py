import os
from datetime import datetime, timedelta

def update_epg():
    # Rutas relativas al repositorio
    template_path = 'epg_notweb/tvmax.template.xml'
    output_path = 'epg_notweb/tvmax.xml'

    if not os.path.exists(template_path):
        print(f"❌ Error: No se encuentra {template_path}")
        return

    # Obtener fecha de hoy y calcular el Lunes de la semana actual
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())

    print(f"📅 Actualizando EPG para la semana del {monday.strftime('%Y-%m-%d')}")

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Mapear los 7 días de la semana
    new_content = content
    for i in range(7):
        # El template tiene fechas 20260901, 20260902... 20260907
        old_day_str = f"202609{i+1:02d}"
        new_day_str = (monday + timedelta(days=i)).strftime('%Y%m%d')

        new_content = new_content.replace(old_day_str, new_day_str)
        print(f"   🔄 {old_day_str} -> {new_day_str}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ Archivo tvmax.xml actualizado correctamente.")

if __name__ == "__main__":
    update_epg()
