import streamlit as st
from PIL import Image, ImageOps, ImageColor
import io
import math

st.set_page_config(page_title="Repeat Pattern Builder", layout="wide")

st.title("Repeat Pattern Builder")

# Sidebar controls
st.sidebar.header("Pattern Settings")

# Canvas size
canvas_width = st.sidebar.slider("Canvas width (px)", 800, 4000, 2000, step=100)
canvas_height = st.sidebar.slider("Canvas height (px)", 800, 4000, 2000, step=100)

# Background color
bg_color_str = st.sidebar.color_picker("Background color", "#ffffff")
bg_color = ImageColor.getrgb(bg_color_str)

# Layout type
layout_type = st.sidebar.selectbox(
    "Layout type",
    ["Grid", "Half-drop", "Brick"]
)

# Motif scale
motif_scale = st.sidebar.slider("Motif scale (%)", 10, 300, 100)

# Spacing
x_spacing = st.sidebar.slider("Horizontal spacing (px)", 0, 500, 50)
y_spacing = st.sidebar.slider("Vertical spacing (px)", 0, 500, 50)

# Offsets (to "move" the overall layout)
x_offset = st.sidebar.slider("Global X offset (px)", -500, 500, 0)
y_offset = st.sidebar.slider("Global Y offset (px)", -500, 500, 0)

# Upload motifs
st.header("Upload Motifs")
uploaded_files = st.file_uploader(
    "Upload one or more PNG/JPG motifs",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

generate = st.button("Generate Pattern")

def load_and_scale_motifs(files, scale_percent):
    motifs = []
    for f in files:
        img = Image.open(f).convert("RGBA")
        w, h = img.size
        new_w = int(w * scale_percent / 100)
        new_h = int(h * scale_percent / 100)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        motifs.append(img)
    return motifs

def tile_pattern(canvas_w, canvas_h, motifs, layout, x_space, y_space, x_off, y_off):
    # Create base canvas
    canvas = Image.new("RGBA", (canvas_w, canvas_h), bg_color + (255,))

    if not motifs:
        return canvas

    # Use first motif as base size reference
    base_motif = motifs[0]
    mw, mh = base_motif.size

    # Effective step including spacing
    step_x = mw + x_space
    step_y = mh + y_space

    # Number of repeats needed
    cols = math.ceil(canvas_w / step_x) + 2
    rows = math.ceil(canvas_h / step_y) + 2

    # For variety, cycle through motifs
    motif_count = len(motifs)

    for row in range(rows):
        for col in range(cols):
            motif = motifs[(row * cols + col) % motif_count]

            # Base position
            x = col * step_x + x_off
            y = row * step_y + y_off

            # Layout adjustments
            if layout == "Half-drop":
                # Every other row shifted horizontally by half motif width
                if row % 2 == 1:
                    x += step_x // 2
            elif layout == "Brick":
                # Every other column shifted vertically by half motif height
                if col % 2 == 1:
                    y += step_y // 2

            # Paste motif if within canvas bounds (with some margin)
            if -mw < x < canvas_w and -mh < y < canvas_h:
                canvas.alpha_composite(motif, (int(x), int(y)))

    return canvas

if generate:
    if not uploaded_files:
        st.warning("Please upload at least one motif image.")
    else:
        motifs = load_and_scale_motifs(uploaded_files, motif_scale)
        pattern_img = tile_pattern(
            canvas_width,
            canvas_height,
            motifs,
            layout_type,
            x_spacing,
            y_spacing,
            x_offset,
            y_offset
        )

        st.header("Pattern Preview")
        st.image(pattern_img, use_column_width=True)

        # Export section
        st.header("Export Pattern")
        buf = io.BytesIO()
        # Convert to RGB for saving as PNG without alpha issues
        pattern_rgb = pattern_img.convert("RGB")
        pattern_rgb.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="Download PNG",
            data=byte_im,
            file_name="repeat_pattern.png",
            mime="image/png"
        )

        st.success("Pattern generated. Adjust sliders and regenerate to refine your layout.")
else:
    st.info("Upload motifs, tweak settings in the sidebar, then click 'Generate Pattern'.")
