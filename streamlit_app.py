import streamlit as st
from PIL import Image
import io
import math

# ============================================================
# PATTERN STUDIO
# Multi-Motif Seamless Repeat Generator
# ============================================================

st.set_page_config(
    page_title="Pattern Studio",
    page_icon="🌸",
    layout="wide"
)

# ------------------------------------------------------------
# APP TITLE
# ------------------------------------------------------------

st.title("🌸 Pattern Studio")
st.caption("Multi-Motif Seamless Repeat Generator")

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------

if "motifs" not in st.session_state:
    st.session_state.motifs = []

if "layout" not in st.session_state:
    st.session_state.layout = "Free Arrange"

if "tile_size" not in st.session_state:
    st.session_state.tile_size = 1200

# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def resize_and_rotate(image, scale, rotation):
    new_width = max(1, int(image.width * scale))
    new_height = max(1, int(image.height * scale))

    resized = image.resize(
        (new_width, new_height),
        Image.LANCZOS
    )

    if rotation != 0:
        resized = resized.rotate(
            rotation,
            expand=True,
            resample=Image.BICUBIC
        )

    return resized


def paste_with_wrap(canvas, image, x, y):
    """
    Paste motif with wraparound so motifs crossing an edge
    also appear on the opposite side of the repeat tile.
    """

    w = canvas.width
    h = canvas.height

    x = int(x)
    y = int(y)

    positions = [
        (x, y),
        (x - w, y),
        (x + w, y),
        (x, y - h),
        (x, y + h),
        (x - w, y - h),
        (x + w, y - h),
        (x - w, y + h),
        (x + w, y + h),
    ]

    for px, py in positions:
        canvas.alpha_composite(image, (px, py))


def build_pattern():
    tile = st.session_state.tile_size

    bg = hex_to_rgb(st.session_state.background_color)

    canvas = Image.new(
        "RGBA",
        (tile, tile),
        bg + (255,)
    )

    motifs = st.session_state.motifs

    # --------------------------------------------------------
    # FREE ARRANGE
    # --------------------------------------------------------

    if st.session_state.layout == "Free Arrange":

        for motif in motifs:

            img = resize_and_rotate(
                motif["image"],
                motif["scale"],
                motif["rotation"]
            )

            x = int(
                motif["x"] * tile / 100
                - img.width / 2
            )

            y = int(
                motif["y"] * tile / 100
                - img.height / 2
            )

            paste_with_wrap(
                canvas,
                img,
                x,
                y
            )

    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------

    elif st.session_state.layout == "Grid":

        count = len(motifs)

        if count == 0:
            return canvas

        columns = math.ceil(math.sqrt(count))
        rows = math.ceil(count / columns)

        cell_w = tile / columns
        cell_h = tile / rows

        for i, motif in enumerate(motifs):

            col = i % columns
            row = i // columns

            img = resize_and_rotate(
                motif["image"],
                motif["scale"],
                motif["rotation"]
            )

            x = int(
                col * cell_w
                + cell_w / 2
                - img.width / 2
            )

            y = int(
                row * cell_h
                + cell_h / 2
                - img.height / 2
            )

            paste_with_wrap(
                canvas,
                img,
                x,
                y
            )

    # --------------------------------------------------------
    # BRICK
    # --------------------------------------------------------

    elif st.session_state.layout == "Brick":

        count = len(motifs)

        if count == 0:
            return canvas

        columns = 3
        rows = math.ceil(count / columns)

        cell_w = tile / columns
        cell_h = tile / rows

        for i, motif in enumerate(motifs):

            col = i % columns
            row = i // columns

            offset = 0

            if row % 2 == 1:
                offset = cell_w / 2

            img = resize_and_rotate(
                motif["image"],
                motif["scale"],
                motif["rotation"]
            )

            x = int(
                col * cell_w
                + offset
                + cell_w / 2
                - img.width / 2
            )

            y = int(
                row * cell_h
                + cell_h / 2
                - img.height / 2
            )

            paste_with_wrap(
                canvas,
                img,
                x,
                y
            )

    # --------------------------------------------------------
    # HALF DROP
    # --------------------------------------------------------

    elif st.session_state.layout == "Half Drop":

        count = len(motifs)

        if count == 0:
            return canvas

        columns = 3
        rows = math.ceil(count / columns)

        cell_w = tile / columns
        cell_h = tile / rows

        for i, motif in enumerate(motifs):

            col = i % columns
            row = i // columns

            offset = 0

            if col % 2 == 1:
                offset = cell_h / 2

            img = resize_and_rotate(
                motif["image"],
                motif["scale"],
                motif["rotation"]
            )

            x = int(
                col * cell_w
                + cell_w / 2
                - img.width / 2
            )

            y = int(
                row * cell_h
                + cell_h / 2
                + offset
                - img.height / 2
            )

            paste_with_wrap(
                canvas,
                img,
                x,
                y
            )

    # --------------------------------------------------------
    # SCATTER
    # --------------------------------------------------------

    elif st.session_state.layout == "Scatter":

        positions = [
            (18, 20),
            (52, 18),
            (82, 25),
            (25, 55),
            (66, 50),
            (88, 70),
            (12, 84),
            (48, 82),
            (75, 90)
        ]

        for i, motif in enumerate(motifs):

            img = resize_and_rotate(
                motif["image"],
                motif["scale"],
                motif["rotation"]
            )

            px, py = positions[i % len(positions)]

            x = int(
                px * tile / 100
                - img.width / 2
            )

            y = int(
                py * tile / 100
                - img.height / 2
            )

            paste_with_wrap(
                canvas,
                img,
                x,
                y
            )

    # --------------------------------------------------------
    # MIRROR
    # --------------------------------------------------------

    elif st.session_state.layout == "Mirror":

        for i, motif in enumerate(motifs):

            img = resize_and_rotate(
                motif["image"],
                motif["scale"],
                motif["rotation"]
            )

            base_x = int(
                motif["x"] * tile / 100
                - img.width / 2
            )

            base_y = int(
                motif["y"] * tile / 100
                - img.height / 2
            )

            paste_with_wrap(
                canvas,
                img,
                base_x,
                base_y
            )

            mirrored = img.transpose(
                Image.Transpose.FLIP_LEFT_RIGHT
            )

            paste_with_wrap(
                canvas,
                mirrored,
                tile - base_x - img.width,
                base_y
            )

    return canvas


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

st.sidebar.header("Pattern Settings")

st.session_state.tile_size = st.sidebar.selectbox(
    "Repeat Tile Size",
    [600, 800, 1000, 1200, 1600, 2000],
    index=2
)

st.session_state.background_color = st.sidebar.color_picker(
    "Background Color",
    "#FFFFFF"
)

st.sidebar.markdown("---")

st.sidebar.subheader("Layout")

layout_options = [
    "Free Arrange",
    "Grid",
    "Brick",
    "Half Drop",
    "Scatter",
    "Mirror"
]

selected_layout = st.sidebar.radio(
    "Choose a layout",
    layout_options,
    index=layout_options.index(
        st.session_state.layout
    )
)

st.session_state.layout = selected_layout

# ------------------------------------------------------------
# RESET
# ------------------------------------------------------------

if st.sidebar.button("Reset All Motifs"):
    st.session_state.motifs = []
    st.rerun()

# ============================================================
# STEP 1 — UPLOAD
# ============================================================

st.header("1. Upload Motifs")

uploaded_files = st.file_uploader(
    "Upload your floral, botanical, geometric, or other motif artwork.",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:

    existing_names = {
        motif["name"]
        for motif in st.session_state.motifs
    }

    for uploaded_file in uploaded_files:

        if uploaded_file.name in existing_names:
            continue

        try:

            image = Image.open(
                uploaded_file
            ).convert("RGBA")

            st.session_state.motifs.append(
                {
                    "name": uploaded_file.name,
                    "image": image,
                    "x": 50,
                    "y": 50,
                    "scale": 0.35,
                    "rotation": 0
                }
            )

        except Exception:
            st.error(
                f"Could not load {uploaded_file.name}"
            )

# ============================================================
# STEP 2 — MOTIFS
# ============================================================

st.header("2. Motifs")

if not st.session_state.motifs:

    st.info(
        "Upload one or more motifs above to begin."
    )

else:

    st.write(
        f"{len(st.session_state.motifs)} motif(s) loaded."
    )

    for index, motif in enumerate(
        st.session_state.motifs
    ):

        with st.expander(
            f"{index + 1}. {motif['name']}",
            expanded=True
        ):

            col1, col2 = st.columns(
                [1, 2]
            )

            with col1:

                st.image(
                    motif["image"],
                    caption=motif["name"],
                    width=180
                )

                if st.button(
                    "Remove Motif",
                    key=f"remove_{index}"
                ):

                    st.session_state.motifs.pop(
                        index
                    )

                    st.rerun()

            with col2:

                st.markdown(
                    "**Position**"
                )

                motif["x"] = st.slider(
                    "Horizontal Position",
                    min_value=0,
                    max_value=100,
                    value=int(motif["x"]),
                    key=f"x_{index}"
                )

                motif["y"] = st.slider(
                    "Vertical Position",
                    min_value=0,
                    max_value=100,
                    value=int(motif["y"]),
                    key=f"y_{index}"
                )

                st.markdown(
                    "**Size & Rotation**"
                )

                motif["scale"] = st.slider(
                    "Motif Size",
                    min_value=0.05,
                    max_value=1.50,
                    value=float(motif["scale"]),
                    step=0.05,
                    key=f"scale_{index}"
                )

                motif["rotation"] = st.slider(
                    "Rotation",
                    min_value=-180,
                    max_value=180,
                    value=int(motif["rotation"]),
                    step=5,
                    key=f"rotation_{index}"
                )

# ============================================================
# STEP 3 — PATTERN PREVIEW
# ============================================================

st.header("3. Pattern Preview")

if st.session_state.motifs:

    pattern = build_pattern()

    st.image(
        pattern,
        caption=f"{st.session_state.layout} • {st.session_state.tile_size}px repeat tile",
        use_container_width=True
    )

    # --------------------------------------------------------
    # QUICK INFO
    # --------------------------------------------------------

    st.markdown(
        f"""
**Current Layout:** {st.session_state.layout}  
**Tile Size:** {st.session_state.tile_size} × {st.session_state.tile_size} px  
**Motifs:** {len(st.session_state.motifs)}
"""
    )

else:

    st.info(
        "Your pattern preview will appear here."
    )

# ============================================================
# STEP 4 — EXPORT
# ============================================================

st.header("4. Export")

if st.session_state.motifs:

    export_pattern = build_pattern()

    png_output = io.BytesIO()

    export_pattern.save(
        png_output,
        format="PNG"
    )

    png_output.seek(0)

    st.download_button(
        label="⬇️ Download Repeat Tile as PNG",
        data=png_output,
        file_name="pattern_studio_repeat.png",
        mime="image/png"
    )

    st.caption(
        "The exported PNG contains the repeat tile shown in the preview."
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Pattern Studio • Version 1"
)
