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

<style>

:root {{
    --background: #f3f4f6;
    --card: #ffffff;
    --text: #111827;
    --muted: #6b7280;
    --border: #e5e7eb;
    --accent: #2563eb;
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

    background: var(--background);
    color: var(--text);
}}

header {{
    background: #111827;
    color: white;
    padding: 35px 20px;
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
    margin-top: 15px;
    font-size: 14px;
    color: #9ca3af;
}}

.controls {{
    max-width: 1400px;
    margin: auto;
    padding: 25px 20px;
}}

#search {{
    width: 100%;
    padding: 16px 18px;

    border: 1px solid #d1d5db;
    border-radius: 10px;

    font-size: 16px;
}}

#search:focus {{
    outline: 2px solid var(--accent);
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
    background: var(--card);

    border:
        1px
        solid
        var(--border);

    border-radius: 14px;

    overflow: hidden;

    box-shadow:
        0 2px 8px
        rgba(0, 0, 0, 0.04);

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}}

.card:hover {{
    transform: translateY(-3px);

    box-shadow:
        0 12px 30px
        rgba(0, 0, 0, 0.08);
}}

.card.hidden {{
    display: none;
}}

.card-header {{
    padding: 18px 20px;

    border-bottom:
        1px
        solid
        var(--border);
}}

.channel-number {{
    font-size: 11px;
    font-weight: bold;
    color: var(--muted);
    letter-spacing: 0.5px;
}}

.card h2 {{
    margin: 6px 0 10px;
    font-size: 22px;
}}

.category {{
    display: inline-block;

    padding: 5px 10px;

    background: #eef2ff;
    color: #3730a3;

    border-radius: 20px;

    font-size: 11px;
    font-weight: bold;
}}

.card-content {{
    display: flex;
    gap: 20px;
    padding: 20px;
}}

.icon-preview {{
    width: 150px;
    height: 150px;

    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    border:
        1px
        solid
        var(--border);

    border-radius: 12px;

    overflow: hidden;

    background:
        repeating-conic-gradient(
            #f1f1f1 0% 25%,
            white 0% 50%
        )
        50% / 24px 24px;
}}

.icon-preview img {{
    max-width: 100%;
    max-height: 100%;

    object-fit: contain;
}}

.missing-image {{
    display: none;

    padding: 15px;

    color: #dc2626;

    text-align: center;

    font-size: 13px;
}}

.details {{
    flex: 1;
    min-width: 0;
}}

.detail {{
    margin-bottom: 16px;
}}

.label {{
    display: block;

    margin-bottom: 6px;

    font-size: 11px;
    font-weight: bold;

    color: var(--muted);

    text-transform: uppercase;
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
    gap: 10px;
    align-items: flex-start;
}}

.icon-url {{
    flex: 1;

    color: var(--accent);

    font-size: 12px;

    word-break: break-all;
}}

.copy-button {{
    flex-shrink: 0;

    padding: 7px 11px;

    border:
        1px
        solid
        #d1d5db;

    background: white;

    border-radius: 7px;

    cursor: pointer;

    font-size: 12px;
}}

.copy-button:hover {{
    background: #f3f4f6;
}}

footer {{
    padding: 30px;

    text-align: center;

    color: var(--muted);

    font-size: 12px;
}}

@media (max-width: 650px) {{

    .grid {{
        grid-template-columns: 1fr;
    }}

    .card-content {{
        flex-direction: column;
    }}

    .icon-preview {{
        width: 100%;
        height: 200px;
    }}

}}

</style>

</head>

<body>

<header>

    <div class="header-content">

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
