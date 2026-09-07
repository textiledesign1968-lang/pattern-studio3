import streamlit as st
from PIL import Image, ImageOps
import io
import math
import random

# ============================================================
# PATTERN STUDIO
# ============================================================

st.set_page_config(
    page_title="Pattern Studio",
    page_icon="✦",
    layout="wide"
)

# ============================================================
# SESSION STATE
# ============================================================

if "motifs" not in st.session_state:
    st.session_state.motifs = []

if "next_id" not in st.session_state:
    st.session_state.next_id = 1

if "seed" not in st.session_state:
    st.session_state.seed = 42


# ============================================================
# FUNCTIONS
# ============================================================

def create_motif(image, name):
    """Create a motif record."""
    motif = {
        "id": st.session_state.next_id,
        "name": name,
        "image": image.convert("RGBA"),
        "x": 50.0,
        "y": 50.0,
        "scale": 100,
        "rotation": 0,
        "visible": True,
    }

    st.session_state.next_id += 1
    return motif


def resize_motif(image, scale):
    """Resize motif according to percentage."""
    width, height = image.size

    new_width = max(1, int(width * scale / 100))
    new_height = max(1, int(height * scale / 100))

    return image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS
    )


def rotate_motif(image, angle):
    """Rotate motif while preserving transparency."""
    return image.rotate(
        angle,
        expand=True,
        resample=Image.Resampling.BICUBIC
    )


def paste_wrapped(canvas, motif, x, y):
    """
    Paste a motif onto a repeating tile.

    If the motif crosses an edge, the appropriate portion
    automatically appears on the opposite side.
    """

    canvas_width, canvas_height = canvas.size
    motif_width, motif_height = motif.size

    # Center motif on x/y position.
    left = int((x / 100) * canvas_width - motif_width / 2)
    top = int((y / 100) * canvas_height - motif_height / 2)

    # Positions to paste so edges wrap.
    x_positions = [left]

    if left < 0:
        x_positions.append(left + canvas_width)

    if left + motif_width > canvas_width:
        x_positions.append(left - canvas_width)

    y_positions = [top]

    if top < 0:
        y_positions.append(top + canvas_height)

    if top + motif_height > canvas_height:
        y_positions.append(top - canvas_height)

    for px in x_positions:
        for py in y_positions:
            canvas.alpha_composite(motif, (px, py))


def draw_single_motif(canvas, motif):
    """Draw one motif with wrapping."""
    if not motif["visible"]:
        return

    img = resize_motif(
        motif["image"],
        motif["scale"]
    )

    img = rotate_motif(
        img,
        motif["rotation"]
    )

    paste_wrapped(
        canvas,
        img,
        motif["x"],
        motif["y"]
    )


def make_tile(width, height, background, motifs, layout):
    """Create one complete repeating tile."""

    canvas = Image.new(
        "RGBA",
        (width, height),
        background
    )

    if layout == "Grid / Straight":

        for motif in motifs:
            draw_single_motif(canvas, motif)

    elif layout == "Half-Drop":

        # Original column
        for motif in motifs:
            draw_single_motif(canvas, motif)

        # Half-drop copy
        for motif in motifs:

            shifted = motif.copy()

            shifted["x"] = (
                motif["x"] + 50
            ) % 100

            shifted["y"] = (
                motif["y"] + 50
            ) % 100

            draw_single_motif(
                canvas,
                shifted
            )

    elif layout == "Brick / Half-Brick":

        for motif in motifs:
            draw_single_motif(canvas, motif)

        # Horizontal half-brick
        for motif in motifs:

            shifted = motif.copy()

            shifted["x"] = (
                motif["x"] + 50
            ) % 100

            draw_single_motif(
                canvas,
                shifted
            )

    elif layout == "Mirror":

        for motif in motifs:

            draw_single_motif(
                canvas,
                motif
            )

            mirrored = motif.copy()

            mirrored["x"] = (
                100 - motif["x"]
            )

            mirrored["rotation"] = (
                -motif["rotation"]
            )

            draw_single_motif(
                canvas,
                mirrored
            )

    elif layout == "Scatter":

        rng = random.Random(
            st.session_state.seed
        )

        for motif in motifs:

            # Original motif
            draw_single_motif(
                canvas,
                motif
            )

            # Additional scattered copies
            for _ in range(4):

                scattered = motif.copy()

                scattered["x"] = rng.uniform(
                    0,
                    100
                )

                scattered["y"] = rng.uniform(
                    0,
                    100
                )

                scattered["rotation"] = (
                    motif["rotation"]
                    + rng.randint(-25, 25)
                )

                scattered["scale"] = int(
                    motif["scale"]
                    * rng.uniform(0.70, 1.25)
                )

                draw_single_motif(
                    canvas,
                    scattered
                )

    return canvas


def make_repeat_preview(tile, columns, rows):
    """Repeat the finished tile to show a larger pattern preview."""

    tile_width, tile_height = tile.size

    preview = Image.new(
        "RGBA",
        (
            tile_width * columns,
            tile_height * rows
        )
    )

    for row in range(rows):
        for column in range(columns):

            preview.alpha_composite(
                tile,
                (
                    column * tile_width,
                    row * tile_height
                )
            )

    return preview


def image_to_bytes(image):
    """Convert PIL image to downloadable PNG bytes."""

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# TITLE
# ============================================================

st.title("✦ Pattern Studio")

st.write(
    "Upload motifs, arrange them, create seamless repeats, "
    "and export your finished pattern."
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Pattern Settings")

    # --------------------------------------------------------
    # TILE SIZE
    # --------------------------------------------------------

    tile_preset = st.selectbox(
        "Tile Size",
        [
            "1000 × 1000",
            "2000 × 2000",
            "3000 × 3000",
            "Custom"
        ]
    )

    if tile_preset == "Custom":

        tile_width = st.number_input(
            "Width",
            min_value=100,
            max_value=10000,
            value=2000,
            step=100
        )

        tile_height = st.number_input(
            "Height",
            min_value=100,
            max_value=10000,
            value=2000,
            step=100
        )

    else:

        size = tile_preset.split(" × ")

        tile_width = int(size[0])
        tile_height = int(size[1])

    # --------------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------------

    st.subheader("Background")

    background_color = st.color_picker(
        "Background Color",
        "#FFFFFF"
    )

    # --------------------------------------------------------
    # REPEAT
    # --------------------------------------------------------

    st.subheader("Repeat Type")

    layout = st.selectbox(
        "Layout",
        [
            "Grid / Straight",
            "Half-Drop",
            "Brick / Half-Brick",
            "Mirror",
            "Scatter"
        ]
    )

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    st.subheader("Preview")

    preview_columns = st.slider(
        "Columns",
        1,
        5,
        3
    )

    preview_rows = st.slider(
        "Rows",
        1,
        5,
        3
    )

    # --------------------------------------------------------
    # SCATTER SEED
    # --------------------------------------------------------

    if layout == "Scatter":

        st.subheader("Scatter")

        if st.button("↻ New Scatter Arrangement"):

            st.session_state.seed = random.randint(
                0,
                1000000
            )

            st.rerun()


# ============================================================
# MOTIF UPLOAD
# ============================================================

st.header("1. Upload Motifs")

uploaded_files = st.file_uploader(
    "Upload one or more motif images",
    type=[
        "png",
        "jpg",
        "jpeg",
        "webp"
    ],
    accept_multiple_files=True
)

if uploaded_files:

    existing_names = [
        motif["name"]
        for motif in st.session_state.motifs
    ]

    for uploaded_file in uploaded_files:

        if uploaded_file.name in existing_names:
            continue

        image = Image.open(
            uploaded_file
        ).convert("RGBA")

        motif = create_motif(
            image,
            uploaded_file.name
        )

        st.session_state.motifs.append(
            motif
        )

    st.success(
        f"{len(st.session_state.motifs)} motif(s) loaded."
    )


# ============================================================
# MOTIF CONTROLS
# ============================================================

st.header("2. Arrange Your Motifs")

if not st.session_state.motifs:

    st.info(
        "Upload one or more motif images above to begin."
    )

else:

    for index, motif in enumerate(
        st.session_state.motifs
    ):

        with st.expander(
            f"✦ {motif['name']}",
            expanded=True
        ):

            control_col, preview_col = st.columns(
                [2, 1]
            )

            # ------------------------------------------------
            # CONTROLS
            # ------------------------------------------------

            with control_col:

                visible = st.checkbox(
                    "Show motif",
                    value=motif["visible"],
                    key=f"visible_{motif['id']}"
                )

                motif["visible"] = visible

                # LEFT / RIGHT
                motif["x"] = st.slider(
                    "Move Left / Right",
                    min_value=-50.0,
                    max_value=150.0,
                    value=float(motif["x"]),
                    step=1.0,
                    key=f"x_{motif['id']}"
                )

                # UP / DOWN
                motif["y"] = st.slider(
                    "Move Up / Down",
                    min_value=-50.0,
                    max_value=150.0,
                    value=float(motif["y"]),
                    step=1.0,
                    key=f"y_{motif['id']}"
                )

                # SIZE
                motif["scale"] = st.slider(
                    "Size",
                    min_value=10,
                    max_value=400,
                    value=int(motif["scale"]),
                    step=5,
                    key=f"scale_{motif['id']}"
                )

                # ROTATION
                motif["rotation"] = st.slider(
                    "Rotation",
                    min_value=-180,
                    max_value=180,
                    value=int(motif["rotation"]),
                    step=1,
                    key=f"rotation_{motif['id']}"
                )

                # ------------------------------------------------
                # DUPLICATE / DELETE
                # ------------------------------------------------

                button_col1, button_col2 = st.columns(2)

                with button_col1:

                    if st.button(
                        "Duplicate",
                        key=f"duplicate_{motif['id']}"
                    ):

                        new_motif = motif.copy()

                        new_motif["id"] = (
                            st.session_state.next_id
                        )

                        st.session_state.next_id += 1

                        new_motif["name"] = (
                            motif["name"]
                            + " copy"
                        )

                        new_motif["x"] = (
                            motif["x"] + 10
                        ) % 100

                        new_motif["y"] = (
                            motif["y"] + 10
                        ) % 100

                        st.session_state.motifs.insert(
                            index + 1,
                            new_motif
                        )

                        st.rerun()

                with button_col2:

                    if st.button(
                        "Delete",
                        key=f"delete_{motif['id']}"
                    ):

                        st.session_state.motifs.pop(
                            index
                        )

                        st.rerun()

            # ------------------------------------------------
            # MOTIF PREVIEW
            # ------------------------------------------------

            with preview_col:

                preview_image = resize_motif(
                    motif["image"],
                    motif["scale"]
                )

                preview_image = rotate_motif(
                    preview_image,
                    motif["rotation"]
                )

                st.image(
                    preview_image,
                    caption=motif["name"],
                    use_container_width=True
                )


# ============================================================
# RESET
# ============================================================

if st.session_state.motifs:

    st.divider()

    if st.button("Reset All Motifs"):

        st.session_state.motifs = []

        st.session_state.next_id = 1

        st.rerun()


# ============================================================
# GENERATE PATTERN
# ============================================================

st.divider()

st.header("3. Pattern Preview")

if st.session_state.motifs:

    # Convert hex background to RGBA
    bg = background_color.lstrip("#")

    background_rgba = (
        int(bg[0:2], 16),
        int(bg[2:4], 16),
        int(bg[4:6], 16),
        255
    )

    # Generate tile
    tile = make_tile(
        tile_width,
        tile_height,
        background_rgba,
        st.session_state.motifs,
        layout
    )

    # Generate larger preview
    full_preview = make_repeat_preview(
        tile,
        preview_columns,
        preview_rows
    )

    st.image(
        full_preview,
        caption=f"{layout} Repeat",
        use_container_width=True
    )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.subheader("Export")

    tile_bytes = image_to_bytes(
        tile
    )

    st.download_button(
        label="⬇ Download Pattern Tile as PNG",
        data=tile_bytes,
        file_name="pattern_tile.png",
        mime="image/png"
    )

    # ========================================================
    # TILE INFORMATION
    # ========================================================

    st.caption(
        f"Export size: {tile_width} × {tile_height} px"
    )

else:

    st.info(
        "Upload motifs to generate your pattern."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Pattern Studio • Create • Repeat • Export"
)
