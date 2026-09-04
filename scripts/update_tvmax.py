import os
from datetime import datetime, timedelta

def update_epg():
    template_path = 'epg_notweb/tvmax.template.xml'
    output_path = 'epg_notweb/tvmax.xml'

    if not os.path.exists(template_path):
        print(f"❌ Error: No se encuentra {template_path}")
        return

    # 1. Calcular el "Hoy" en Paraguay (UTC-4)
    # GitHub Actions corre en UTC, le restamos 4 horas para tener la fecha real de Paraguay
    now_py = datetime.utcnow() - timedelta(hours=4)

    # 2. Encontrar el lunes de la semana actual
    # .weekday() devuelve 0 para Lunes, 4 para Viernes...
    monday_py = now_py - timedelta(days=now_py.weekday())

    print(f"📅 Sincronizando EPG para Paraguay (Hoy: {now_py.strftime('%Y-%m-%d')})")
    print(f"📅 Semana iniciada el Lunes: {monday_py.strftime('%Y-%m-%d')}")

    # 3. Preparar los reemplazos para cada día
    days_tags = {
        "{{LUNES}}": (monday_py + timedelta(days=0)).strftime('%Y%m%d'),
        "{{MARTES}}": (monday_py + timedelta(days=1)).strftime('%Y%m%d'),
        "{{MIERCOLES}}": (monday_py + timedelta(days=2)).strftime('%Y%m%d'),
        "{{JUEVES}}": (monday_py + timedelta(days=3)).strftime('%Y%m%d'),
        "{{VIERNES}}": (monday_py + timedelta(days=4)).strftime('%Y%m%d'),
        "{{SABADO}}": (monday_py + timedelta(days=5)).strftime('%Y%m%d'),
        "{{DOMINGO}}": (monday_py + timedelta(days=6)).strftime('%Y%m%d')
    }

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content
    for tag, date_str in days_tags.items():
        new_content = new_content.replace(tag, date_str)
        print(f"   🔄 {tag} -> {date_str}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ Archivo tvmax.xml actualizado y sincronizado con el calendario de Paraguay.")

if __name__ == "__main__":
    update_epg()
