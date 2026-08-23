import os
import json
import html
import urllib.request
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

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def obtener_lista_canales(data):
    """
    Intenta detectar automáticamente dónde está la lista de canales.
    """

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        posibles_claves = [
            "canales",
            "channels",
            "data",
            "items",
            "lista"
        ]

        for clave in posibles_claves:
            if clave in data and isinstance(data[clave], list):
                return data[clave]

    raise ValueError(
        "No se pudo encontrar la lista de canales dentro del JSON."
    )


def obtener_valor(item, claves, defecto=""):
    for clave in claves:
        if clave in item and item[clave] is not None:
            return str(item[clave]).strip()

    return defecto


def procesar_canales(data):

    lista = obtener_lista_canales(data)
    canales = []

    for item in lista:

        if not isinstance(item, dict):
            continue

        nombre = obtener_valor(
            item,
            [
                "name",
                "nombre",
                "canal",
                "title",
                "titulo"
            ]
        )

        url = obtener_valor(
            item,
            [
                "url",
                "link",
                "stream",
                "stream_url",
                "video_url",
                "src"
            ]
        )

        icono = obtener_valor(
            item,
            [
                "icono",
                "icon",
                "image",
                "imagen",
                "logo"
            ]
        )

        numero = obtener_valor(
            item,
            [
                "id",
                "canal_id",
                "numero",
                "channel",
                "number"
            ]
        )

        if not nombre:
            nombre = f"Canal {numero}" if numero else "Sin nombre"

        if not icono:
            continue

        # Si el JSON contiene una URL completa, obtenemos solo el nombre del archivo.
        icono = icono.split("?")[0]
        icono = icono.rstrip("/")
        icono = icono.split("/")[-1]

        canales.append({
            "nombre": nombre,
            "url": url,
            "icono": icono,
            "numero": numero
        })

    return canales


def generar_html(canales):

    fecha = datetime.now(timezone.utc).strftime(
        "%d/%m/%Y %H:%M UTC"
    )

    tarjetas = []

    for canal in canales:

        nombre = html.escape(canal["nombre"])
        icono = html.escape(canal["icono"])
        numero = html.escape(canal["numero"])
        url = html.escape(canal["url"])

        icono_path = f"icons/{icono}"

        numero_html = ""

        if numero:
            numero_html = f"""
                <span class="channel-number">
                    #{numero}
                </span>
            """

        if url:
            url_html = f"""
                <div class="url-section">
                    <div class="url-label">URL</div>

                    <a
                        href="{url}"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="channel-url"
                    >
                        {url}
                    </a>

                    <button
                        class="copy-button"
                        onclick="copiarURL(this)"
                        data-url="{url}"
                    >
                        Copiar
                    </button>
                </div>
            """
        else:
            url_html = """
                <div class="url-section">
                    <div class="url-label">URL</div>
                    <div class="no-url">
                        Sin URL disponible
                    </div>
                </div>
            """

        tarjeta = f"""
        <article class="card">
            <div class="card-header">
                <div>
                    <h2>{nombre}</h2>
                    {numero_html}
                </div>
            </div>

            <div class="content">

                <div class="icon-preview">
                    <img
                        src="{icono_path}"
                        alt="{nombre}"
                        loading="lazy"
                        onerror="this.parentElement.classList.add('image-error')"
                    >
                </div>

                <div class="information">

                    <div class="info-row">
                        <span class="label">Archivo del icono</span>
                        <code>{icono}</code>
                    </div>

                    <div class="info-row">
                        <span class="label">Ruta</span>
                        <code>{icono_path}</code>
                    </div>

                    {url_html}

                </div>

            </div>
        </article>
        """

        tarjetas.append(tarjeta)

    tarjetas_html = "\n".join(tarjetas)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>NovaImg - Catálogo de Iconos</title>

<style>

:root {{
    --bg: #f5f5f7;
    --card: #ffffff;
    --text: #1d1d1f;
    --muted: #6e6e73;
    --border: #d2d2d7;
    --accent: #0066cc;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background: var(--bg);
    color: var(--text);
}}

header {{
    padding: 40px 20px 30px;
    background: var(--card);
    border-bottom: 1px solid var(--border);
}}

.header-container {{
    max-width: 1400px;
    margin: auto;
}}

h1 {{
    margin: 0;
    font-size: 32px;
}}

.subtitle {{
    margin-top: 10px;
    color: var(--muted);
}}

.stats {{
    margin-top: 20px;
    font-size: 14px;
    color: var(--muted);
}}

.controls {{
    max-width: 1400px;
    margin: 25px auto;
    padding: 0 20px;
}}

.search {{
    width: 100%;
    padding: 15px 18px;

    border: 1px solid var(--border);
    border-radius: 10px;

    font-size: 16px;
}}

.container {{
    max-width: 1400px;

    margin: auto;

    padding:
        0
        20px
        50px;
}}

.grid {{
    display: grid;

    grid-template-columns:
        repeat(
            auto-fill,
            minmax(380px, 1fr)
        );

    gap: 20px;
}}

.card {{
    background: var(--card);

    border:
        1px
        solid
        var(--border);

    border-radius: 14px;

    overflow: hidden;

    transition:
        transform .2s ease,
        box-shadow .2s ease;
}}

.card:hover {{
    transform: translateY(-3px);

    box-shadow:
        0 10px 30px
        rgba(0,0,0,.08);
}}

.card-header {{
    padding: 18px 20px;

    border-bottom:
        1px
        solid
        var(--border);
}}

.card-header h2 {{
    margin: 0;

    font-size: 20px;
}}

.channel-number {{
    display: inline-block;

    margin-top: 8px;

    color: var(--muted);

    font-size: 13px;
}}

.content {{
    display: flex;

    gap: 20px;

    padding: 20px;
}}

.icon-preview {{
    width: 130px;
    height: 130px;

    flex-shrink: 0;

    display: flex;

    align-items: center;
    justify-content: center;

    background:
        repeating-conic-gradient(
            #eee 0% 25%,
            #fff 0% 50%
        )
        50% / 20px 20px;

    border:
        1px
        solid
        var(--border);

    border-radius: 12px;

    overflow: hidden;
}}

.icon-preview img {{
    max-width: 100%;
    max-height: 100%;

    object-fit: contain;
}}

.image-error::after {{
    content: "Imagen no encontrada";

    color: #b00020;

    text-align: center;

    padding: 10px;

    font-size: 13px;
}}

.information {{
    flex: 1;

    min-width: 0;
}}

.info-row {{
    margin-bottom: 14px;
}}

.label,
.url-label {{
    display: block;

    margin-bottom: 5px;

    font-size: 12px;

    font-weight: bold;

    color: var(--muted);

    text-transform: uppercase;
}}

code {{
    display: inline-block;

    padding: 6px 8px;

    background: #f1f1f3;

    border-radius: 6px;

    font-size: 13px;

    word-break: break-all;
}}

.channel-url {{
    display: block;

    margin-bottom: 8px;

    color: var(--accent);

    font-size: 13px;

    word-break: break-all;
}}

.copy-button {{
    padding:
        7px
        12px;

    border: 1px solid var(--border);

    background: white;

    border-radius: 6px;

    cursor: pointer;
}}

.copy-button:hover {{
    background: #f5f5f7;
}}

.no-url {{
    color: var(--muted);

    font-size: 13px;
}}

.hidden {{
    display: none;
}}

footer {{
    text-align: center;

    padding: 25px;

    color: var(--muted);

    font-size: 13px;
}}

@media (max-width: 600px) {{

    .content {{
        flex-direction: column;
    }}

    .icon-preview {{
        width: 100%;
        height: 180px;
    }}

}}

</style>

</head>

<body>

<header>

    <div class="header-container">

        <h1>📺 NovaImg</h1>

        <div class="subtitle">
            Catálogo automático de canales e iconos
        </div>

        <div class="stats">
            {len(canales)} canales encontrados
        </div>

    </div>

</header>

<div class="controls">

    <input
        type="search"
        id="search"
        class="search"
        placeholder="Buscar canal, icono o URL..."
    >

</div>

<main class="container">

    <div class="grid" id="channels">

        {tarjetas_html}

    </div>

</main>

<footer>
    Última actualización automática: {fecha}
</footer>

<script>

const search = document.getElementById("search");

search.addEventListener("input", function() {{

    const value =
        this.value
            .toLowerCase()
            .trim();

    const cards =
        document.querySelectorAll(".card");

    cards.forEach(card => {{

        const text =
            card.innerText.toLowerCase();

        const visible =
            text.includes(value);

        card.classList.toggle(
            "hidden",
            !visible
        );

    }});

}});


function copiarURL(button) {{

    const url =
        button.dataset.url;

    navigator.clipboard
        .writeText(url)
        .then(() => {{

            const original =
                button.textContent;

            button.textContent =
                "✓ Copiado";

            setTimeout(() => {{
                button.textContent =
                    original;
            }}, 1500);

        }});

}}

</script>

</body>
</html>
"""


def main():

    data = descargar_json()

    canales = procesar_canales(data)

    if not canales:
        raise SystemExit(
            "ERROR: No se encontraron canales con iconos."
        )

    canales.sort(
        key=lambda x:
        x["nombre"].lower()
    )

    contenido = generar_html(canales)

    with open(
        "index.html",
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(contenido)

    print(
        f"Catálogo generado correctamente: "
        f"{len(canales)} canales"
    )


if __name__ == "__main__":
    main()
