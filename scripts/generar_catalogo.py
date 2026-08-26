import os
import json
import html
import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timezone


def descargar_json(url):
    print("Descargando datos de NovaPlay...")

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "NovaImg-Catalog-Generator/1.0"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=60
    ) as response:
        return json.load(response)


def obtener_archivo_icono(icono_url):
    """
    Convierte una URL como:
    https://servidor.com/icons/006.webp
    en:
    006.webp
    """
    if not icono_url:
        return ""
    icono_url = str(icono_url).strip()
    parsed = urlparse(icono_url)
    ruta = parsed.path
    if ruta:
        return os.path.basename(ruta)
    return os.path.basename(icono_url.split("?")[0])


def procesar_items(items, categoria_nombre):
    canales = []
    if not isinstance(items, list):
        return canales
    for item in items:
        if not isinstance(item, dict):
            continue
        nombre = str(item.get("name", "")).strip()
        numero = str(item.get("canal", "")).strip()
        icono_url = str(item.get("icono", "")).strip()

        if not icono_url:
            print(f"⚠ Canal sin icono: {nombre or numero}")
            continue

        icono = obtener_archivo_icono(icono_url)
        if not icono:
            print(f"⚠ No se pudo obtener archivo del icono: {nombre}")
            continue

        if not nombre:
            if numero:
                nombre = f"Canal {numero}"
            else:
                nombre = "Sin nombre"

        canales.append({
            "nombre": nombre,
            "numero": numero,
            "icono": icono,
            "icono_url": icono_url,
            "categoria": categoria_nombre
        })
    return canales


def procesar_canales(data):
    canales = []
    if isinstance(data, list):
        print(f"Elementos principales encontrados: {len(data)}")
        for grupo in data:
            if not isinstance(grupo, dict):
                continue
            categoria_nombre = str(grupo.get("title", grupo.get("name", "SIN CATEGORÍA"))).strip()
            if isinstance(grupo.get("items"), list):
                items = grupo["items"]
                print(f"Procesando categoría: {categoria_nombre} ({len(items)} items)")
                canales.extend(procesar_items(items, categoria_nombre))
            elif "icono" in grupo:
                canales.extend(procesar_items([grupo], categoria_nombre))
    elif isinstance(data, dict):
        if isinstance(data.get("items"), list):
            canales.extend(procesar_items(data["items"], str(data.get("title", "SIN CATEGORÍA"))))
        else:
            for clave, valor in data.items():
                if isinstance(valor, list):
                    canales.extend(procesar_items(valor, clave))
    return canales


def ordenar_canal(canal):
    numero = canal.get("numero", "")
    try:
        return (0, int(numero))
    except (ValueError, TypeError):
        return (1, canal["nombre"].lower())


def generar_tarjetas(canales):
    tarjetas = []
    for canal in canales:
        nombre = html.escape(canal["nombre"])
        numero = html.escape(canal["numero"])
        categoria = html.escape(canal["categoria"])
        icono = html.escape(canal["icono"])
        icono_url = html.escape(canal["icono_url"], quote=True)
        ruta_local = f"icons/{icono}"

        tarjeta = f"""
        <article class="card" data-search="{nombre} {numero} {categoria} {icono} {icono_url}">
            <div class="card-header">
                <div class="header-info">
                    <div class="channel-number">CANAL {numero if numero else "—"}</div>
                    <h2>{nombre}</h2>
                </div>
                <div class="category">{categoria}</div>
            </div>

            <div class="card-content">
                <div class="icon-preview">
                    <img src="{ruta_local}" alt="{nombre}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
                    <div class="missing-image">
                        <i class="fas fa-image" style="font-size: 24px; margin-bottom: 8px; opacity: 0.3;"></i>
                        <br>No disponible
                    </div>
                </div>

                <div class="details">
                    <div class="detail">
                        <span class="label">Archivo</span>
                        <code>{icono}</code>
                    </div>
                    <div class="detail">
                        <span class="label">URL Origen</span>
                        <div class="url-row">
                            <a href="{icono_url}" target="_blank" rel="noopener noreferrer" class="icon-url">{icono_url}</a>
                            <button class="copy-button" data-url="{icono_url}" onclick="copiarURL(this)" title="Copiar URL">
                                <i class="fas fa-copy"></i> <span>Copiar</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </article>
        """
        tarjetas.append(tarjeta)
    return "\n".join(tarjetas)


def generar_html(canales):
    fecha = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    tarjetas = generar_tarjetas(canales)
    categorias = sorted(list(set(c['categoria'] for c in canales)))

    filtro_botones = '<button class="filter-btn active" data-category="Todas">Todas</button>'
    for cat in categorias:
        filtro_botones += f'\n<button class="filter-btn" data-category="{html.escape(cat)}">{html.escape(cat)}</button>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NovaImg - Catálogo de Iconos</title>
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#e50914">
<link rel="icon" type="image/webp" href="https://raw.githubusercontent.com/novaplaytv/novaimg/main/novasplash.webp">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<style>
:root {{
    --primary: #e50914;
    --primary-hover: #b91c1c;
    --bg: #080a10;
    --card-bg: #11151f;
    --input-bg: #1a1f2e;
    --text: #ffffff;
    --text-muted: #9aa3b2;
    --border: #293246;
    --nav-height: 70px;
}}
* {{ box-sizing: border-box; outline: none; }}
body {{
    margin: 0; font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text);
    -webkit-font-smoothing: antialiased; overflow-x: hidden;
}}
.nova-nav {{
    position: fixed; top: 0; width: 100%; z-index: 10000;
    background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: 0.3s;
}}
.nav-inner {{
    max-width: 1400px; margin: auto; height: 70px; padding: 0 30px;
    display: flex; align-items: center; justify-content: space-between;
}}
.nav-brand {{
    display: flex; align-items: center; gap: 12px; text-decoration: none;
    color: #fff; font-weight: 900; font-size: 22px; letter-spacing: -1px;
}}
.nav-brand img {{ width: 36px; height: 32px; border-radius: 8px; }}
.nav-links {{ display: flex; gap: 15px; align-items: center; }}
.nav-links a {{
    color: #ccc; text-decoration: none; font-size: 14px; font-weight: 600;
    transition: 0.2s; padding: 10px 15px; border-radius: 10px;
}}
.nav-links a:hover {{ color: #fff; background: rgba(255, 255, 255, 0.05); }}

.btn-login-nav, .btn-logout {{
    background: var(--primary); color: #fff !important; font-weight: 800 !important;
    padding: 10px 20px; border-radius: 10px; text-decoration: none; font-size: 14px;
    transition: 0.3s; border: none; cursor: pointer; box-shadow: 0 4px 15px rgba(229, 9, 20, 0.2);
    display: none;
}}
.btn-login-nav:hover, .btn-logout:hover {{
    transform: translateY(-2px); background: var(--primary-hover);
    box-shadow: 0 6px 20px rgba(229, 9, 20, 0.3);
}}
header {{
    background: linear-gradient(to bottom, #11151f, var(--bg));
    padding: 100px 20px 30px; text-align: center; border-bottom: 1px solid var(--border);
}}
.header-content {{ max-width: 800px; margin: auto; }}
.header-logo {{ width: 50px; height: 50px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); }}
.subtitle {{ margin: 0; font-size: 28px; font-weight: 900; letter-spacing: -1px; color: #fff; }}
.description {{ margin-top: 12px; color: var(--text-muted); font-size: 15px; }}
.stats {{
    display: inline-block; margin-top: 25px; padding: 8px 20px;
    background: rgba(229, 9, 20, 0.1); color: var(--primary); font-size: 13px;
    font-weight: 800; text-transform: uppercase; border-radius: 30px;
    border: 1px solid rgba(229, 9, 20, 0.2);
}}
.controls {{
    max-width: 1400px; margin: auto; padding: 40px 20px 10px;
    position: sticky; top: 70px; z-index: 100; background: var(--bg);
}}
#search {{
    width: 100%; padding: 20px 30px; background: var(--input-bg);
    border: 1px solid var(--border); border-radius: 20px; color: #fff;
    font-size: 16px; transition: 0.3s; margin-bottom: 20px;
}}
#search:focus {{ border-color: var(--primary); box-shadow: 0 0 0 4px rgba(229, 9, 20, 0.1); }}

.category-filters {{
    display: flex; gap: 10px; overflow-x: auto; padding-bottom: 15px;
    scrollbar-width: thin; scrollbar-color: var(--primary) transparent;
}}
.category-filters::-webkit-scrollbar {{ height: 4px; }}
.category-filters::-webkit-scrollbar-thumb {{ background: var(--primary); border-radius: 10px; }}
.filter-btn {{
    background: var(--card-bg); color: var(--text-muted); border: 1px solid var(--border);
    padding: 10px 20px; border-radius: 12px; font-size: 13px; font-weight: 700;
    cursor: pointer; transition: 0.3s; white-space: nowrap;
}}
.filter-btn:hover {{ background: var(--border); color: #fff; }}
.filter-btn.active {{ background: var(--primary); color: #fff; border-color: var(--primary); }}

.container {{ max-width: 1400px; margin: auto; padding: 0 20px 80px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 30px; }}
.card {{
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 24px;
    overflow: hidden; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}}
.card:hover {{ transform: translateY(-10px); border-color: var(--primary); box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
.card.hidden {{ display: none; }}
.card-header {{ padding: 25px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: flex-start; }}
.channel-number {{ font-size: 10px; font-weight: 800; color: var(--primary); text-transform: uppercase; margin-bottom: 5px; }}
.card h2 {{ margin: 0; font-size: 20px; font-weight: 800; }}
.category {{ padding: 6px 14px; background: rgba(255, 255, 255, 0.05); color: #fff; border-radius: 12px; font-size: 10px; font-weight: 700; }}
.card-content {{ display: flex; gap: 25px; padding: 25px; align-items: center; }}
.icon-preview {{
    width: 110px; height: 110px; background: #000; border: 1px solid var(--border);
    border-radius: 20px; display: flex; align-items: center; justify-content: center;
    padding: 12px; flex-shrink: 0; transition: 0.3s;
}}
.icon-preview img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
.missing-image {{ display: none; color: var(--text-muted); font-size: 10px; font-weight: 700; text-align: center; }}
.details {{ flex: 1; min-width: 0; }}
.detail {{ margin-bottom: 15px; }}
.label {{ display: block; margin-bottom: 6px; font-size: 9px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; }}
code {{
    display: block; background: rgba(0,0,0,0.3); padding: 10px 12px; border-radius: 10px;
    font-size: 11px; color: #eee; border: 1px solid var(--border); word-break: break-all;
}}
.url-row {{ display: flex; gap: 8px; align-items: center; }}
.icon-url {{
    flex: 1; color: var(--primary); font-size: 11px; text-decoration: none; font-weight: 600;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.copy-button {{
    background: #293246; color: #fff; border: 0; padding: 8px 15px; border-radius: 10px;
    font-size: 10px; font-weight: 700; cursor: pointer; transition: 0.2s;
}}
footer {{ padding: 80px 20px; text-align: center; border-top: 1px solid var(--border); background: #06080d; }}
footer p {{ margin: 10px 0; font-size: 14px; color: var(--text-muted); }}

/* NovaToast System */
#toast-container {{
    position: fixed; bottom: 30px; right: 30px; z-index: 99999;
    display: flex; flex-direction: column; gap: 12px;
}}
.nova-toast {{
    background: rgba(26, 31, 46, 0.8); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1); color: #fff; padding: 16px 24px;
    border-radius: 16px; font-size: 14px; font-weight: 600; display: flex;
    align-items: center; gap: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    animation: toastSlideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); min-width: 280px;
}}
.nova-toast.success {{ border-left: 4px solid #10b981; }}
.nova-toast.error {{ border-left: 4px solid #ef4444; }}
.nova-toast i {{ font-size: 18px; }}
.nova-toast.success i {{ color: #10b981; }}
.nova-toast.error i {{ color: #ef4444; }}
@keyframes toastSlideIn {{
    from {{ transform: translateX(100%) scale(0.9); opacity: 0; }}
    to {{ transform: translateX(0) scale(1); opacity: 1; }}
}}
.toast-fade-out {{ animation: toastFadeOut 0.4s forwards; }}
@keyframes toastFadeOut {{ to {{ transform: translateX(20px); opacity: 0; }} }}

@media (max-width: 900px) {{ .nav-links {{ display: none; }} }}
@media (max-width: 600px) {{
    .grid {{ grid-template-columns: 1fr; }}
    .card-content {{ flex-direction: column; text-align: center; }}
    .icon-preview {{ width: 140px; height: 140px; margin: 0 auto; }}
    .url-row {{ flex-direction: column; align-items: stretch; }}
    .subtitle {{ font-size: 24px; }}
}}
</style>
</head>
<body>
<nav class="nova-nav">
    <div class="nav-inner">
        <a class="nav-brand" href="https://novaplaytv.github.io/">
            <img src="https://raw.githubusercontent.com/novaplaytv/novaimg/main/novasplash.webp" alt="Logo">
            NOVAPLAY
        </a>
        <div class="nav-links">
            <a href="https://novaplaytv.github.io/">INICIO</a>
            <a href="https://novaplaytv.github.io/DEMO-NOVAPLAY/">WEB DEMO</a>
            <a href="https://novaplaytv.github.io/novaimg/actualizar-icono/" id="navPanelIconos">ICONOS</a>
            <a href="https://novaplaytv.github.io/panel-canales/" id="navPanelCanales">CANALES</a>
            <a href="https://novaplaytv.github.io/novaimg/login/" class="btn-login-nav" id="navLogin">INGRESAR</a>
            <button class="btn-logout" id="navLogout" onclick="cerrarSesion()">SALIR</button>
        </div>
    </div>
</nav>
<header>
    <div class="header-content">
        <img src="https://raw.githubusercontent.com/novaplaytv/novaimg/main/novasplash.webp" alt="NovaPlay" class="header-logo">
        <h1 class="subtitle">Catálogo de Activos</h1>
        <p class="description">Gestión centralizada de canales, logotipos e identidades visuales para el ecosistema NovaPlay.</p>
        <div class="stats">
            <i class="fas fa-tv"></i> &nbsp; {len(canales)} canales indexados
        </div>
    </div>
</header>
<section class="controls">
    <input id="search" type="search" placeholder="Buscar canal, categoría o nombre de archivo...">
    <section class="category-filters">
        {filtro_botones}
    </section>
</section>
<main class="container">
    <div class="grid" id="mainGrid">{tarjetas}</div>
</main>
<footer>
    <p>© 2026 NOVAPLAY TV - Todos los derechos reservados.</p>
    <p style="font-size: 11px; opacity: 0.5;">Sincronización automática: {fecha}</p>
</footer>

<div id="toast-container"></div>

<script>
const searchInput = document.getElementById("search");
const filterBtns = document.querySelectorAll(".filter-btn");
let activeCategory = "Todas";

function filterCards() {{
    const query = searchInput.value.toLowerCase().trim();
    const cards = document.querySelectorAll(".card");

    cards.forEach(card => {{
        const searchable = card.dataset.search.toLowerCase();
        const category = card.querySelector(".category").textContent;

        const matchesSearch = searchable.includes(query);
        const matchesCategory = activeCategory === "Todas" || category === activeCategory;

        card.classList.toggle("hidden", !(matchesSearch && matchesCategory));
    }});
}}

searchInput.addEventListener("input", filterCards);

filterBtns.forEach(btn => {{
    btn.addEventListener("click", () => {{
        filterBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        activeCategory = btn.dataset.category;
        filterCards();
    }});
}});

function novaToast(message, type = 'success') {{
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `nova-toast ${{type}}`;
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';

    toast.innerHTML = `
        <i class="fas ${{icon}}"></i>
        <span>${{message}}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {{
        toast.classList.add('toast-fade-out');
        setTimeout(() => toast.remove(), 400);
    }}, 3000);
}}

function copiarURL(button) {{
    const url = button.dataset.url;
    navigator.clipboard.writeText(url).then(() => {{
        novaToast("URL copiada al portapapeles", "success");
        const copyText = button.querySelector('span');
        if (copyText) {{
            copyText.textContent = "Copiado";
            setTimeout(() => {{ copyText.textContent = "Copiar"; }}, 2000);
        }}
    }});
}}

function checkAuth() {{
    const token = localStorage.getItem("novaimg_session_token") || localStorage.getItem("novaplay_session_token");
    const loginBtn = document.getElementById("navLogin");
    const logoutBtn = document.getElementById("navLogout");
    if (loginBtn) loginBtn.style.display = token ? 'none' : 'block';
    if (logoutBtn) logoutBtn.style.display = token ? 'block' : 'none';
}}

function cerrarSesion() {{
    localStorage.removeItem("novaimg_session_token");
    localStorage.removeItem("novaplay_session_token");
    location.reload();
}}

if ('serviceWorker' in navigator) {{
    window.addEventListener('load', () => {{
        navigator.serviceWorker.register('sw.js')
            .then(reg => console.log('SW Registered', reg))
            .catch(err => console.log('SW registration failed', err));
    }});
}}

document.addEventListener('DOMContentLoaded', () => {{
    checkAuth();
}});
</script>
</body>
</html>
"""


def main():
    JSON_URL = os.environ.get("NOVAPLAY_JSON_URL")
    if not JSON_URL:
        print("ERROR: No existe la variable NOVAPLAY_JSON_URL.")
        return

    data = descargar_json(JSON_URL)
    canales = procesar_canales(data)
    print(f"Total de canales encontrados: {len(canales)}")

    if not canales:
        raise SystemExit("ERROR: No se encontraron canales con iconos.")

    canales.sort(key=ordenar_canal)
    contenido = generar_html(canales)

    with open("index.html", "w", encoding="utf-8") as archivo:
        archivo.write(contenido)

    print("✓ index.html generado correctamente.")


if __name__ == "__main__":
    main()
