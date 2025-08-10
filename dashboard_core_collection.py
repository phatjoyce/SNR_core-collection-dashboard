import os, io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, UnidentifiedImageError
from colorthief import ColorThief

# ---------- CONFIG ----------
IMG_DIR = "data/raw/snr_core_collection"
PALETTE_SIZE = 6  # colors per image
APP_TITLE = "🎨 Sporty & Rich — Core Collection Color Analysis"
# ----------------------------

st.set_page_config(page_title="Core Collection Color Analysis", layout="wide")
st.title(APP_TITLE)

# ---------- helpers ----------
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*[int(x) for x in rgb])

def safe_image_bytes(path: str) -> bytes:
    """
    Open image robustly, convert to RGB, re-encode as PNG bytes.
    Skips corrupt/unsupported files without crashing.
    """
    try:
        with open(path, "rb") as f:
            raw = f.read()
        im = Image.open(io.BytesIO(raw))
        im.load()  # force decode now (catches truncated files)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        return buf.getvalue()
    except (FileNotFoundError, UnidentifiedImageError, OSError):
        return b""

def get_palette(img_path: str, n: int) -> list[str]:
    with open(img_path, "rb") as f:
        ct = ColorThief(f)
        return [rgb_to_hex(c) for c in ct.get_palette(color_count=n)]
# ----------------------------

# ---------- guards ----------
if not os.path.isdir(IMG_DIR):
    st.error(f"Folder not found: `{IMG_DIR}`. Add ~20–40 images to this path in your repo.")
    st.stop()

image_files = sorted(
    f for f in os.listdir(IMG_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
)

if not image_files:
    st.warning(f"No images found in `{IMG_DIR}`.")
    st.stop()
# ----------------------------

# ---------- render + collect ----------
rows = []
cols = st.columns(3)
valid = 0

for i, fname in enumerate(image_files):
    path = os.path.join(IMG_DIR, fname)
    data = safe_image_bytes(path)
    if not data:
        st.warning(f"Skipping unreadable image: {fname}")
        continue

    # palette (fail-soft)
    try:
        hex_colors = get_palette(path, PALETTE_SIZE)
    except Exception:
        hex_colors = []

    with cols[i % 3]:
        # compatibility for older/newer Streamlit
        try:
            st.image(data, caption=fname, use_container_width=True)
        except TypeError:
            st.image(data, caption=fname, use_column_width=True)

        if hex_colors:
            swatches = "".join(
                f"<div style='display:inline-block;width:30px;height:30px;"
                f"background:{h};border-radius:4px;margin-right:4px;margin-top:6px'></div>"
                for h in hex_colors
            )
            st.markdown(swatches, unsafe_allow_html=True)

    for h in hex_colors:
        rows.append({"image": fname, "hex": h})
    valid += 1

if valid == 0:
    st.error("No readable images were processed.")
    st.stop()
# ----------------------------

# ---------- tables + downloads ----------
df = pd.DataFrame(rows)
st.subheader("Per-image palette (preview)")
st.dataframe(df.head(50), use_container_width=True)

st.download_button(
    "⬇️ Download per-image palette CSV",
    df.to_csv(index=False).encode("utf-8"),
    file_name="core_collection_per_image_palette.csv",
    mime="text/csv",
)
# ----------------------------

# ---------- aggregate chart + csv ----------
st.subheader("Aggregate top colors across collection")
color_counts = df["hex"].value_counts().reset_index()
color_counts.columns = ["color_hex", "frequency"]

fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(color_counts["color_hex"], color_counts["frequency"], color=color_counts["color_hex"])
ax.set_ylabel("Frequency")
ax.set_title("Top Colors Across Collection")
ax.set_xticklabels([])  # keep clean; hex labels are long
st.pyplot(fig)

st.download_button(
    "⬇️ Download aggregate colors CSV",
    color_counts.to_csv(index=False).encode("utf-8"),
    file_name="core_collection_aggregate_colors.csv",
    mime="text/csv",
)
# ----------------------------
