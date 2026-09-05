import os
import json
import requests

from io import BytesIO
from PIL import Image


JSON_FILE = "novaplay.json"
ICON_DIR = "icons"

GITHUB_ICON_URL = (
    "https://raw.githubusercontent.com/"
    "ThedarkSoldier996/novaimg/main/icons/"
)

os.makedirs(ICON_DIR, exist_ok=True)


print("======================================", flush=True)
print("       NOVAPLAY ICON SYNC", flush=True)
print("======================================", flush=True)


# ==================================================
# LEER EL JSON ORIGINAL
# ==================================================

with open(
    JSON_FILE,
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


print(
    "novaplay.json cargado correctamente.",
    flush=True
)


# ==================================================
# RECORRER CATEGORÍAS Y CANALES
# ==================================================

channels = []


if isinstance(data, list):

    for category in data:

        if not isinstance(category, dict):
            continue

        items = category.get("items")

        if not isinstance(items, list):
            continue

        for item in items:

            if not isinstance(item, dict):
                continue

            # Solo canales que tienen icono
            if "icono" in item:

                channels.append(item)


print(
    f"Canales con icono encontrados: {len(channels)}",
    flush=True
)


# ==================================================
# DESCARGAR Y CONVERTIR
# ==================================================

session = requests.Session()

successful = 0
failed = 0

index = []


for position, channel in enumerate(
    channels,
    start=1
):

    name = channel.get(
        "name",
        ""
    )

    original_url = channel.get(
        "icono"
    )

    filename = f"{position:03d}.webp"

    output_path = os.path.join(
        ICON_DIR,
        filename
    )


    print("", flush=True)

    print(
        f"[{position}/{len(channels)}] {name}",
        flush=True
    )

    print(
        f"Original: {original_url}",
        flush=True
    )

    print(
        f"Archivo: {filename}",
        flush=True
    )


    # ==================================================
    # VALIDAR URL
    # ==================================================

    if not isinstance(
        original_url,
        str
    ) or not original_url.startswith(
        ("http://", "https://")
    ):

        print(
            "URL inválida. Se mantiene sin modificar.",
            flush=True
        )

        index.append({
            "numero": position,
            "name": name,
            "icono": original_url,
            "archivo": None
        })

        continue


    try:

        # ==================================================
        # DESCARGAR IMAGEN ORIGINAL
        # ==================================================

        response = session.get(
            original_url,
            timeout=(15, 60)
        )

        response.raise_for_status()


        if not response.content:

            raise Exception(
                "La imagen descargada está vacía."
            )


        # ==================================================
        # ABRIR IMAGEN
        # ==================================================

        image = Image.open(
            BytesIO(response.content)
        )

        image.load()


        # ==================================================
        # CONVERTIR A WEBP
        # ==================================================

        if image.mode in (
            "RGBA",
            "LA"
        ):

            image = image.convert(
                "RGBA"
            )

        else:

            image = image.convert(
                "RGB"
            )


        image.save(
            output_path,
            "WEBP",
            quality=90,
            method=6
        )


        # ==================================================
        # NUEVA URL
        # ==================================================

        new_url = (
            GITHUB_ICON_URL
            + filename
        )


        # ==================================================
        # MODIFICAR ÚNICAMENTE "icono"
        # ==================================================

        channel["icono"] = new_url


        print(
            f"OK: {filename}",
            flush=True
        )

        print(
            f"Nueva URL: {new_url}",
            flush=True
        )


        # ==================================================
        # INDEX
        # ==================================================

        index.append({
            "numero": position,
            "name": name,
            "icono": new_url,
            "archivo": filename,
            "icono_original": original_url
        })


        successful += 1


    except Exception as error:

        print(
            f"ERROR: {error}",
            flush=True
        )

        # Si falla, NO cambia el icono
        index.append({
            "numero": position,
            "name": name,
            "icono": original_url,
            "archivo": None,
            "error": str(error)
        })

        failed += 1


# ==================================================
# GUARDAR NOVAPLAY.JSON
# ==================================================

print("", flush=True)

print(
    "Guardando novaplay.json...",
    flush=True
)


with open(
    JSON_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2
    )

    file.write("\n")


print(
    "novaplay.json actualizado.",
    flush=True
)


# ==================================================
# GUARDAR INDEX.JSON
# ==================================================

with open(
    os.path.join(
        ICON_DIR,
        "index.json"
    ),
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        index,
        file,
        ensure_ascii=False,
        indent=2
    )

    file.write("\n")


# ==================================================
# RESULTADO
# ==================================================

print("", flush=True)

print(
    "======================================",
    flush=True
)

print(
    "             RESULTADO",
    flush=True
)

print(
    "======================================",
    flush=True
)

print(
    f"Canales encontrados : {len(channels)}",
    flush=True
)

print(
    f"Convertidos         : {successful}",
    flush=True
)

print(
    f"Errores             : {failed}",
    flush=True
)

print(
    "======================================",
    flush=True
)
