import os
import json
import html
import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timezone


JSON_URL = os.environ.get("NOVAPLAY_JSON_URL")


if not JSON_URL:
    raise SystemExit(
        "ERROR: No existe la variable NOVAPLAY_JSON_URL."
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


def obtener_archivo_icono(icono):
    """
    Convierte:
    https://.../icons/006.webp
    en:
    006.webp
    """

    if not icono:
        return ""

    icono = str(icono).strip()

    parsed = urlparse(icono)

    if parsed.path:
        return os.path.basename(parsed.path)

    return os.path.basename(
        icono.split("?")[0]
    )


def procesar_canales(data):

    canales = []

    if not isinstance(data, list):
        raise ValueError(
            "La estructura principal del JSON debe ser una lista."
        )

    print(
        f"Categorías encontradas: {len(data)}"
    )

    for categoria in data:

        if not isinstance(categoria, dict):
            continue

        categoria_nombre = str(
            categoria.get(
                "title",
                "SIN CATEGORÍA"
            )
        ).strip()

        items = categoria.get("items", [])

        if not isinstance(items, list):
            continue

        print(
            f"Procesando categoría: "
            f"{categoria_nombre} "
            f"({len(items)} canales)"
        )

        for item in items:

            if not isinstance(item, dict):
                continue

            nombre = str(
                item.get("name", "")
            ).strip()

            numero = str(
                item.get("canal", "")
            ).strip()

            url = str(
                item.get("url", "")
            ).strip()

            icono_url = str(
                item.get("icono", "")
            ).strip()

            icono = obtener_archivo_icono(
                icono_url
            )

            if not nombre:
                nombre = (
                    f"Canal {numero}"
                    if numero
                    else "Sin nombre"
                )

            if not icono:
                print(
                    f"⚠ Sin icono: {nombre}"
                )
                continue

            canales.append({
                "nombre": nombre,
                "numero": numero,
                "url": url,
                "icono": icono,
                "categoria": categoria_nombre
            })

    return canales


def ordenar_canal(canal):

    numero = canal.get("numero", "")

    try:
        return (
            0,
            int(numero)
        )
    except ValueError:
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

        url = html.escape(
            canal["url"],
            quote=True
        )

        ruta_icono = f"icons/{icono}"

        if url:

            url_html = f"""
                <div class="url-box">
                    <span class="label">
                        URL del canal
                    </span>

                    <div class="url-row">

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
                            data-url="{url}"
                            onclick="copiarURL(this)"
                        >
                            Copiar
                        </button>

                    </div>
                </div>
            """

        else:

            url_html = """
                <div class="url-box">
                    <span class="label">
                        URL del canal
                    </span>

                    <span class="no-url">
                        Sin URL disponible
                    </span>
                </div>
            """

        tarjeta = f"""
        <article
            class="card"
            data-search="
                {nombre}
                {numero}
                {categoria}
                {icono}
                {url}
            "
        >

            <div class="card-top">

                <div class="channel-info">

                    <div class="channel-number">
                        CANAL {numero or "—"}
                    </div>

                    <h2>
                        {nombre}
                    </h2>

                    <div class="category">
                        {categoria}
                    </div>

                </div>

            </div>

            <div class="card-body">

                <div class="icon-container">

                    <img
                        src="{ruta_icono}"
                        alt="{nombre}"
                        loading="lazy"
                        onerror="
                            this.style.display='none';
                            this.nextElementSibling.style.display='flex';
                        "
                    >

                    <div
                        class="missing-image"
                    >
                        Imagen no encontrada
                    </div>

                </div>

                <div class="details">

                    <div class="detail">

                        <span class="label">
                            Icono actual
                        </span>

                        <code>
                            {icono}
                        </code>

                    </div>

                    <div class="detail">

                        <span class="label">
                            Ruta en repositorio
                        </span>

                        <code>
                            {ruta_icono}
                        </code>

                    </div>

                    {url_html}

                </div>

            </div>

        </article>
        """

        tarjetas.append(tarjeta)

    return "\n".join(tarjetas)


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

<title>
    NovaImg - Catálogo de Iconos
</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family:
        Arial,
        Helvetica,
        sans-serif;
    background: #f3f4f6;
    color: #111827;
}}

header {{
    background: #111827;
    color: white;
    padding: 32px 20px;
}}

.header-content {{
    max-width: 1400px;
    margin: auto;
}}

h1 {{
    margin: 0;
    font-size: 32px;
}}

.subtitle {{
    margin-top: 8px;
    color: #d1d5db;
}}

.stats {{
    margin-top: 14px;
    font-size: 14px;
    color: #9ca3af;
}}

.controls {{
    max-width: 1400px;
    margin: auto;
    padding: 24px 20px;
}}

#search {{
    width: 100%;
    padding: 15px 18px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    font-size: 16px;
}}

#search:focus {{
    outline: 2px solid #2563eb;
    border-color: transparent;
}}

.container {{
    max-width: 1400px;
    margin: auto;
    padding: 0 20px 50px;
}}

.grid {{
    display: grid;
    grid-template-columns:
        repeat(
            auto-fill,
            minmax(420px, 1fr)
        );
    gap: 20px;
}}

.card {{
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    overflow: hidden;
    box-shadow:
        0 2px 8px
        rgba(0,0,0,.04);
}}

.card.hidden {{
    display: none;
}}

.card-top {{
    padding: 18px 20px;
    border-bottom:
        1px solid #e5e7eb;
}}

.channel-number {{
    font-size: 12px;
    font-weight: bold;
    color: #6b7280;
}}

.card h2 {{
    margin: 6px 0;
    font-size: 22px;
}}

.category {{
    display: inline-block;
    padding: 4px 9px;
    background: #eef2ff;
    color: #3730a3;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
}}

.card-body {{
    display: flex;
    gap: 20px;
    padding: 20px;
}}

.icon-container {{
    width: 150px;
    height: 150px;
    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    border: 1px solid #e5e7eb;
    border-radius: 12px;

    background:
        linear-gradient(
            45deg,
            #f9fafb 25%,
            transparent 25%
        ),
        linear-gradient(
            -45deg,
            #f9fafb 25%,
            transparent 25%
        );

    overflow: hidden;
}}

.icon-container img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}}

.missing-image {{
    display: none;
    padding: 15px;
    text-align: center;
    color: #dc2626;
    font-size: 13px;
}}

.details {{
    flex: 1;
    min-width: 0;
}}

.detail,
.url-box {{
    margin-bottom: 16px;
}}

.label {{
    display: block;
    margin-bottom: 6px;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    color: #6b7280;
}}

code {{
    display: inline-block;
    max-width: 100%;
    padding: 7px 9px;
    background: #f3f4f6;
    border-radius: 6px;
    font-size: 12px;
    word-break: break-all;
}}

.url-row {{
    display: flex;
    gap: 8px;
    align-items: flex-start;
}}

.channel-url {{
    flex: 1;
    color: #2563eb;
    font-size: 12px;
    word-break: break-all;
}}

.copy-button {{
    border: 1px solid #d1d5db;
    background: white;
    border-radius: 7px;
    padding: 7px 10px;
    cursor: pointer;
}}

.copy-button:hover {{
    background: #f3f4f6;
}}

.no-url {{
    color: #9ca3af;
    font-size: 13px;
}}

footer {{
    padding: 25px;
    text-align: center;
    color: #6b7280;
    font-size: 12px;
}}

@media (
    max-width: 600px
) {{

    .grid {{
        grid-template-columns: 1fr;
    }}

    .card-body {{
        flex-direction: column;
    }}

    .icon-container {{
        width: 100%;
        height: 180px;
    }}

}}

</style>

</head>

<body>

<header>

    <div class="header-content">

        <h1>
            📺 NovaImg
        </h1>

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
        placeholder="
            Buscar por canal, nombre,
            categoría, icono o URL...
        "
    >

</section>

<main class="container">

    <div class="grid">

        {tarjetas}

    </div>

</main>

<footer>

    Última actualización automática:
    {fecha}

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

        document
            .querySelectorAll(".card")
            .forEach(card => {{

                const text =
                    card.dataset.search
                        .toLowerCase();

                card.classList.toggle(
                    "hidden",
                    !text.includes(query)
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

            const original =
                button.textContent;

            button.textContent =
                "✓ Copiado";

            setTimeout(() => {{
                button.textContent =
                    original;
            }}, 1500);

        }})
        .catch(() => {{
            button.textContent =
                "Error";
        }});

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
        "index.html generado correctamente."
    )


if __name__ == "__main__":
    main()
