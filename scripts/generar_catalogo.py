import os
import json
import html
import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timezone


JSON_URL = os.environ.get("NOVAPLAY_JSON_URL")


if not JSON_URL:
    raise SystemExit(
        "ERROR: No existe la variable NOVAPLAY_JSON_URL. "
        "Configúrala como GitHub Secret."
    )


def descargar_json():
    print("Descargando datos de NovaPlay...")

    request = urllib.request.Request(
        JSON_URL,
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

    return os.path.basename(
        icono_url.split("?")[0]
    )


def procesar_items(items, categoria_nombre):

    canales = []

    if not isinstance(items, list):
        return canales

    for item in items:

        if not isinstance(item, dict):
            continue

        nombre = str(
            item.get("name", "")
        ).strip()

        numero = str(
            item.get("canal", "")
        ).strip()

        icono_url = str(
            item.get("icono", "")
        ).strip()

        if not icono_url:
            print(
                f"⚠ Canal sin icono: "
                f"{nombre or numero}"
            )
            continue

        icono = obtener_archivo_icono(
            icono_url
        )

        if not icono:
            print(
                f"⚠ No se pudo obtener archivo del icono: "
                f"{nombre}"
            )
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

        print(
            f"Elementos principales encontrados: "
            f"{len(data)}"
        )

        for grupo in data:

            if not isinstance(grupo, dict):
                continue

            categoria_nombre = str(
                grupo.get(
                    "title",
                    grupo.get(
                        "name",
                        "SIN CATEGORÍA"
                    )
                )
            ).strip()

            # Caso normal:
            # categoría -> items
            if isinstance(
                grupo.get("items"),
                list
            ):

                items = grupo["items"]

                print(
                    f"Procesando categoría: "
                    f"{categoria_nombre} "
                    f"({len(items)} items)"
                )

                canales.extend(
                    procesar_items(
                        items,
                        categoria_nombre
                    )
                )

            # Por si el elemento principal
            # es directamente un canal
            elif "icono" in grupo:

                canales.extend(
                    procesar_items(
                        [grupo],
                        categoria_nombre
                    )
                )

    elif isinstance(data, dict):

        # Caso:
        # { "items": [...] }
        if isinstance(
            data.get("items"),
            list
        ):

            canales.extend(
                procesar_items(
                    data["items"],
                    str(
                        data.get(
                            "title",
                            "SIN CATEGORÍA"
                        )
                    )
                )
            )

        # Buscar categorías conocidas
        else:

            for clave, valor in data.items():

                if isinstance(valor, list):

                    canales.extend(
                        procesar_items(
                            valor,
                            clave
                        )
                    )

    return canales


def ordenar_canal(canal):

    numero = canal.get(
        "numero",
        ""
    )

    try:
        return (
            0,
            int(numero)
        )
    except (
        ValueError,
        TypeError
    ):
        return (
            1,
            canal["nombre"].lower()
        )


def generar_tarjetas(canales):

    tarjetas = []

    for canal in canales:

        nombre = html.escape(
            canal["nombre"]
        )

        numero = html.escape(
            canal["numero"]
        )

        categoria = html.escape(
            canal["categoria"]
        )

        icono = html.escape(
            canal["icono"]
        )

        icono_url = html.escape(
            canal["icono_url"],
            quote=True
        )

        ruta_local = f"icons/{icono}"

        tarjeta = f"""
        <article
            class="card"
            data-search="{nombre} {numero} {categoria} {icono} {icono_url}"
        >

            <div class="card-header">

                <div class="channel-number">
                    CANAL {numero if numero else "—"}
                </div>

                <h2>{nombre}</h2>

                <div class="category">
                    {categoria}
                </div>

            </div>

            <div class="card-content">

                <div class="icon-preview">

                    <img
                        src="{ruta_local}"
                        alt="{nombre}"
                        loading="lazy"
                        onerror="
                            this.style.display='none';
                            this.nextElementSibling.style.display='flex';
                        "
                    >

                    <div class="missing-image">
                        Imagen no encontrada
                    </div>

                </div>

                <div class="details">

                    <div class="detail">

                        <span class="label">
                            Archivo
                        </span>

                        <code>
                            {icono}
                        </code>

                    </div>

                    <div class="detail">

                        <span class="label">
                            Ruta local
                        </span>

                        <code>
                            {ruta_local}
                        </code>

                    </div>

                    <div class="detail">

                        <span class="label">
                            URL del icono
                        </span>

                        <div class="url-row">

                            <a
                                href="{icono_url}"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="icon-url"
                            >
                                {icono_url}
                            </a>

                            <button
                                class="copy-button"
                                data-url="{icono_url}"
                                onclick="copiarURL(this)"
                                title="Copiar URL del icono"
                            >
                                Copiar
                            </button>

                        </div>

                    </div>

                </div>

            </div>

        </article>
        """

        tarjetas.append(
            tarjeta
        )

    return "\n".join(
        tarjetas
    )


def generar_html(canales):

    fecha = datetime.now(
        timezone.utc
    ).strftime(
        "%d/%m/%Y %H:%M UTC"
    )

    tarjetas = generar_tarjetas(
        canales
    )

    return f"""<!DOCTYPE html>
<html lang="es">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>NovaImg - Catálogo de Iconos</title>

<link rel="icon" type="image/webp" href="https://raw.githubusercontent.com/novaplaytv/novaimg/main/novasplash.webp">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
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
    --accent: #e50914;
    --nav-height: 70px;
}}

* {{
    box-sizing: border-box;
    outline: none;
}}

body {{
    margin: 0;
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    -webkit-font-smoothing: antialiased;
}}

/* Navegación Premium - Estandarizada */
.nova-nav {{ position: fixed; top: 0; width: 100%; z-index: 10000; background: rgba(0,0,0,0.7); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255,255,255,0.05); transition: 0.3s; }}
.nav-inner {{ max-width: 1400px; margin: auto; height: 70px; padding: 0 30px; display: flex; align-items: center; justify-content: space-between; }}
.nav-brand {{ display: flex; align-items: center; gap: 12px; text-decoration: none; color: #fff; font-weight: 900; font-size: 22px; letter-spacing: -1px; }}
.nav-brand img {{ width: 36px; height: 32px; border-radius: 8px; }}
.nav-links {{ display: flex; gap: 15px; align-items: center; }}
.nav-links a {{ color: #ccc; text-decoration: none; font-size: 14px; font-weight: 600; transition: 0.2s; padding: 10px 15px; border-radius: 10px; }}
.nav-links a:hover {{ color: #fff; background: rgba(255,255,255,0.05); }}
.nav-links a.active {{ color: #e50914; }}
.btn-login-nav, .btn-logout {{ background: #e50914; color: #fff !important; font-weight: 800 !important; box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3); border: none; cursor: pointer; padding: 10px 20px; border-radius: 10px; text-decoration: none; font-size: 14px; transition: 0.2s; display: none; }}
.btn-login-nav:hover, .btn-logout:hover {{ transform: scale(1.05); background: #b91c1c; }}

header {{
    background: linear-gradient(to bottom, #11151f, var(--bg));
    color: white;
    padding: 120px 20px 40px;
    border-bottom: 1px solid var(--border);
    text-align: center;
}}

.header-content {{
    max-width: 1400px;
    margin: auto;
}}

header img {{
    width: 64px;
    height: 64px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 0 20px rgba(229, 9, 20, 0.3);
}}

h1 {{
    margin: 0;
    font-size: 36px;
    font-weight: 900;
    letter-spacing: -1px;
}}

.subtitle {{
    margin-top: 8px;
    color: var(--text-muted);
    font-size: 18px;
}}

.stats {{
    margin-top: 15px;
    font-size: 14px;
    color: var(--primary);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.controls {{
    max-width: 1400px;
    margin: auto;
    padding: 30px 20px;
}}

#search {{
    width: 100%;
    padding: 18px 25px;
    background: var(--input-bg);
    border: 1px solid var(--border);
    border-radius: 15px;
    color: #fff;
    font-size: 16px;
    transition: 0.3s;
}}

#search:focus {{
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 20px rgba(229, 9, 20, 0.2);
}}

.container {{
    max-width: 1400px;
    margin: auto;
    padding: 0 20px 50px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
    gap: 25px;
}}

.card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    overflow: hidden;
    transition: 0.3s;
}}

.card:hover {{
    transform: translateY(-5px);
    border-color: var(--primary);
    box-shadow: 0 15px 40px rgba(0,0,0,0.4);
}}

.card.hidden {{
    display: none;
}}

.card-header {{
    padding: 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.channel-number {{
    font-size: 11px;
    font-weight: 900;
    color: var(--primary);
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.card h2 {{
    margin: 0;
    font-size: 20px;
    font-weight: 800;
}}

.category {{
    display: inline-block;
    padding: 5px 12px;
    background: rgba(229, 9, 20, 0.1);
    color: var(--primary);
    border-radius: 20px;
    font-size: 11px;
    font-weight: 800;
}}

.card-content {{
    display: flex;
    gap: 20px;
    padding: 20px;
    align-items: center;
}}

.icon-preview {{
    width: 120px;
    height: 120px;
    background: #000;
    border: 1px solid var(--border);
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    flex-shrink: 0;
}}

.icon-preview img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}}

.missing-image {{
    display: none;
    color: var(--error);
    font-size: 12px;
    font-weight: 700;
}}

.details {{
    flex: 1;
    min-width: 0;
}}

.detail {{
    margin-bottom: 12px;
}}

.label {{
    display: block;
    margin-bottom: 4px;
    font-size: 10px;
    font-weight: 800;
    color: var(--text-muted);
    text-transform: uppercase;
}}

code {{
    display: block;
    background: #080a10;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 11px;
    color: #eee;
    border: 1px solid var(--border);
    word-break: break-all;
}}

.url-row {{
    display: flex;
    gap: 8px;
    margin-top: 5px;
}}

.icon-url {{
    flex: 1;
    color: var(--primary);
    font-size: 11px;
    text-decoration: none;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}

.copy-button {{
    background: #2d3548;
    color: #fff;
    border: 0;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
}}

.copy-button:hover {{
    background: #3d465c;
}}

footer {{
    padding: 50px 20px;
    text-align: center;
    color: #444;
    border-top: 1px solid var(--border);
    font-size: 13px;
}}

@media (max-width: 768px) {{
    .grid {{ grid-template-columns: 1fr; }}
    .card-content {{ flex-direction: column; text-align: center; }}
    .nav-inner {{ padding: 0 15px; }}
    .nav-links {{ display: none; }}
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
            <a href="#" class="btn-login-nav" id="navLogin">INGRESAR</a>
            <button class="btn-logout" id="navLogout" onclick="cerrarSesion()">SALIR</button>
        </div>
    </div>
</nav>

<header>

    <div class="header-content">
        <img src="https://raw.githubusercontent.com/novaplaytv/novaimg/main/novasplash.webp" alt="NovaPlay">
        <h1>📺 NovaImg</h1>

        <div class="subtitle">
            Catálogo automático de canales e iconos
        </div>

        <div class="stats">
            {len(canales)} canales encontrados
        </div>

    </div>

</header>

<section class="controls">

    <input
        id="search"
        type="search"
        placeholder="Buscar canal, categoría, archivo o URL del icono..."
    >

</section>

<main class="container">

    <div class="grid">

        {tarjetas}

    </div>

</main>

<footer>
    <p>© 2026 NOVAPLAY TV - Sistema de Gestión de Activos</p>
    <p>Última actualización automática: {fecha}</p>
</footer>

<script>

const search =
    document.getElementById("search");


search.addEventListener(
    "input",
    function() {{

        const query =
            this.value
                .toLowerCase()
                .trim();

        const cards =
            document.querySelectorAll(".card");

        cards.forEach(card => {{

            const searchable =
                card.dataset.search
                    .toLowerCase();

            const encontrado =
                searchable.includes(query);

            card.classList.toggle(
                "hidden",
                !encontrado
            );

        }});

    }}
);


function copiarURL(button) {{

    const url =
        button.dataset.url;

    navigator.clipboard
        .writeText(url)
        .then(() => {{

            const textoOriginal =
                button.textContent;

            button.textContent =
                "✓ Copiado";

            setTimeout(() => {{

                button.textContent =
                    textoOriginal;

            }}, 1500);

        }})
        .catch(() => {{

            button.textContent =
                "Error";

        }});

}}

// Session Visibility
if (localStorage.getItem("novaimg_session_token") || localStorage.getItem("novaplay_session_token")) {{
    document.getElementById("navLogin").style.display = 'none';
    document.getElementById("navLogout").style.display = 'block';
}} else {{
    document.getElementById("navLogin").style.display = 'block';
    document.getElementById("navLogout").style.display = 'none';
}}
function cerrarSesion() {{
    localStorage.removeItem("novaimg_session_token");
    localStorage.removeItem("novaplay_session_token");
    location.reload();
}}

</script>

</body>

</html>
"""


def main():

    data = descargar_json()

    canales = procesar_canales(
        data
    )

    print(
        f"Total de canales encontrados: "
        f"{len(canales)}"
    )

    if not canales:
        raise SystemExit(
            "ERROR: No se encontraron canales con iconos."
        )

    canales.sort(
        key=ordenar_canal
    )

    contenido = generar_html(
        canales
    )

    with open(
        "index.html",
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            contenido
        )

    print(
        "✓ index.html generado correctamente."
    )


if __name__ == "__main__":
    main()
