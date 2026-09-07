import streamlit as st
from PIL import Image, ImageOps, ImageColor
import io
import math
import random

st.set_page_config(page_title="Hybrid Pattern Engine", layout="wide")
st.title("Hybrid Pattern Engine – Design + Seamless Repeat")

# -----------------------------
# Sidebar – Canvas & Layout
# -----------------------------
st.sidebar.header("Canvas & Layout")

canvas_width = st.sidebar.slider("Canvas width (px)", 800, 4000, 2000, step=100)
canvas_height = st.sidebar.slider("Canvas height (px)", 800, 4000, 2000, step=100)

bg_color_str = st.sidebar.color_picker("Background color", "#ffffff")
bg_color = ImageColor.getrgb(bg_color_str)

layout_type = st.sidebar.selectbox(
    "Repeat layout",
    [
        "Freeform (Design)",
        "Full Drop",
        "Half Drop",
        "Third Drop",
        "Brick",
        "Mirror",
        "Diagonal",
        "Hex",
        "Toss Scatter"
    ]
)

x_spacing = st.sidebar.slider("Horizontal spacing (px)", 0, 500, 50)
y_spacing = st.sidebar.slider("Vertical spacing (px)", 0, 500, 50)

# -----------------------------
# Upload Motifs
# -----------------------------
st.header("Upload Motifs")
uploaded_files = st.file_uploader(
    "Upload PNG/JPG motifs",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

motif_settings = []

if uploaded_files:
    st.subheader("Motif Controls")
    for idx, file in enumerate(uploaded_files):
        st.markdown(f"**{file.name}**")
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            scale = st.slider(f"Scale (%) – {idx}", 10, 300, 100, key=f"scale_{idx}")
        with c2:
            offset_x = st.slider(f"Offset X – {idx}", -canvas_width, canvas_width, 0, key=f"offsetx_{idx}")
        with c3:
            offset_y = st.slider(f"Offset Y – {idx}", -canvas_height, canvas_height, 0, key=f"offsety_{idx}")
        with c4:
            rotate = st.slider(f"Rotate (°) – {idx}", 0, 360, 0, key=f"rotate_{idx}")

        flip_h = st.checkbox(f"Flip horizontally – {idx}", key=f"fliph_{idx}", value=False)
        flip_v = st.checkbox(f"Flip vertically – {idx}", key=f"flipv_{idx}", value=False)

        motif_settings.append({
            "file": file,
            "scale": scale,
            "offset_x": offset_x,
            "offset_y": offset_y,
            "rotate": rotate,
            "flip_h": flip_h,
            "flip_v": flip_v
        })

generate = st.button("Generate Pattern")

# -----------------------------
# Helper Functions
# -----------------------------
def prepare_motif(settings):
    img = Image.open(settings["file"]).convert("RGBA")
    w, h = img.size
    new_w = int(w * settings["scale"] / 100)
    new_h = int(h * settings["scale"] / 100)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    img = img.rotate(settings["rotate"], expand=True)
    if settings["flip_h"]:
        img = ImageOps.mirror(img)
    if settings["flip_v"]:
        img = ImageOps.flip(img)
    return img

def make_canvas(w, h, bg_rgb):
    return Image.new("RGBA", (w, h), bg_rgb + (255,))

def freeform_pattern(canvas_w, canvas_h, prepared):
    canvas = make_canvas(canvas_w, canvas_h, bg_color)
    for motif_img, s in prepared:
        x = s["offset_x"]
        y = s["offset_y"]
        canvas.alpha_composite(motif_img, (int(x), int(y)))
    return canvas

def tile_pattern(canvas_w, canvas_h, motifs, layout, x_space, y_space):
    canvas = make_canvas(canvas_w, canvas_h, bg_color)
    if not motifs:
        return canvas

    base = motifs[0]
    mw, mh = base.size
    step_x = mw + x_space
    step_y = mh + y_space

    cols = math.ceil(canvas_w / step_x) + 2
    rows = math.ceil(canvas_h / step_y) + 2

    for row in range(rows):
        for col in range(cols):
            for i, motif in enumerate(motifs):
                x = col * step_x
                y = row * step_y

                # Layout variations
                if layout == "Half Drop":
                    if row % 2 == 1:
                        x += step_x / 2
                elif layout == "Third Drop":
                    x += (row % 3) * (step_x / 3)
                elif layout == "Brick":
                    if col % 2 == 1:
                        y += step_y / 2
                elif layout == "Diagonal":
                    x += row * (step_x / 2)
                elif layout == "Hex":
                    if row % 2 == 1:
                        x += step_x / 2
                    y = row * (mh * 0.75 + y_space)
                elif layout == "Mirror":
                    if (row + col + i) % 2 == 1:
                        motif = ImageOps.mirror(motif)

                canvas.alpha_composite(motif, (int(x), int(y)))

    return canvas

def toss_scatter(canvas_w, canvas_h, motifs, count=200):
    canvas = make_canvas(canvas_w, canvas_h, bg_color)
    if not motifs:
        return canvas
    for _ in range(count):
        motif = random.choice(motifs)
        mw, mh = motif.size
        x = random.randint(-mw, canvas_w)
        y = random.randint(-mh, canvas_h)
        canvas.alpha_composite(motif, (x, y))
    return canvas

# -----------------------------
# Generate Pattern
# -----------------------------
if generate:
    if not motif_settings:
        st.warning("Upload motifs first.")
    else:
        prepared = []
        for s in motif_settings:
            motif_img = prepare_motif(s)
            prepared.append((motif_img, s))

        if layout_type == "Freeform (Design)":
            pattern_img = freeform_pattern(canvas_width, canvas_height, prepared)
        elif layout_type == "Toss Scatter":
            motif_list = [p[0] for p in prepared]
            pattern_img = toss_scatter(canvas_width, canvas_height, motif_list)
        else:
            motif_list = [p[0] for p in prepared]
            pattern_img = tile_pattern(
                canvas_width,
                canvas_height,
                motif_list,
                layout_type,
                x_spacing,
                y_spacing
            )

        st.header("Pattern Preview")
        st.image(pattern_img, use_column_width=True)

        # Export seamless tile
        buf = io.BytesIO()
        pattern_rgb = pattern_img.convert("RGB")
        pattern_rgb.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="Download Seamless Tile",
            data=byte_im,
            file_name="hybrid_repeat_tile.png",
            mime="image/png"
        )

        st.success("Pattern generated.")
else:
    st.info("Upload motifs, adjust controls, then click Generate Pattern.")
