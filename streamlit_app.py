import streamlit as st
from PIL import Image
import io
import uuid

# ============================================================
# PATTERN STUDIO — VERSION 1
# Multi-Motif Seamless Repeat Generator
# ============================================================

st.set_page_config(
    page_title="Pattern Studio",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 Pattern Studio")
st.subheader("Multi-Motif Seamless Repeat Generator")

st.write(
    "Upload motifs, arrange them on a repeat tile, and create a seamless pattern."
)

# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

st.sidebar.header("Pattern Settings")

tile_size = st.sidebar.slider(
    "Repeat Tile Size",
    min_value=256,
    max_value=2048,
    value=1024,
    step=128
)

background_color = st.sidebar.color_picker(
    "Background Color",
    "#FFFFFF"
)

# ------------------------------------------------------------
# MOTIF UPLOAD
# ------------------------------------------------------------

st.header("1. Upload Your Motifs")

uploaded_files = st.file_uploader(
    "Upload PNG or JPG motif files",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

motifs = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            image = Image.open(uploaded_file).convert("RGBA")

            motifs.append({
                "name": uploaded_file.name,
                "image": image
            })

        except Exception:
            st.error(f"Could not load {uploaded_file.name}")

# ------------------------------------------------------------
# DISPLAY MOTIFS
# ------------------------------------------------------------

if motifs:
    st.header("2. Your Motifs")

    columns = st.columns(min(len(motifs), 4))

    for index, motif in enumerate(motifs):
        with columns[index % len(columns)]:
            st.image(
                motif["image"],
                caption=motif["name"],
                width=180
            )

    st.success(f"{len(motifs)} motif(s) uploaded.")

else:
    st.info("Upload one or more motifs to begin.")

# ------------------------------------------------------------
# PATTERN PREVIEW
# ------------------------------------------------------------

st.header("3. Pattern Preview")

if motifs:

    # Create blank tile
    tile = Image.new(
        "RGBA",
        (tile_size, tile_size),
        background_color
    )

    # Simple automatic arrangement
    positions = []

    if len(motifs) == 1:
        positions = [
            (tile_size // 4, tile_size // 4),
            (tile_size * 3 // 4, tile_size // 4),
            (tile_size // 4, tile_size * 3 // 4),
            (tile_size * 3 // 4, tile_size * 3 // 4)
        ]

    elif len(motifs) == 2:
        positions = [
            (tile_size // 4, tile_size // 4),
            (tile_size * 3 // 4, tile_size * 3 // 4)
        ]

    else:
        positions = [
            (tile_size // 4, tile_size // 4),
            (tile_size * 3 // 4, tile_size // 4),
            (tile_size // 4, tile_size * 3 // 4),
            (tile_size * 3 // 4, tile_size * 3 // 4)
        ]

    for index, motif in enumerate(motifs):

        image = motif["image"].copy()

        # Scale motif
        max_dimension = tile_size // 3

        ratio = min(
            max_dimension / image.width,
            max_dimension / image.height
        )

        new_size = (
            max(1, int(image.width * ratio)),
            max(1, int(image.height * ratio))
        )

        image = image.resize(new_size, Image.LANCZOS)

        x, y = positions[index % len(positions)]

        x -= image.width // 2
        y -= image.height // 2

        tile.alpha_composite(image, (x, y))

    st.image(
        tile,
        caption="Repeat Tile Preview",
        use_container_width=True
    )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.header("4. Export")

    output = io.BytesIO()

    tile.save(
        output,
        format="PNG"
    )

    output.seek(0)

    filename = f"pattern_studio_{uuid.uuid4().hex[:8]}.png"

    st.download_button(
        label="⬇️ Download Pattern Tile",
        data=output,
        file_name=filename,
        mime="image/png"
    )

else:

    st.write("Your pattern preview will appear here.")

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.divider()

st.caption(
    "Pattern Studio — Version 1"
)
