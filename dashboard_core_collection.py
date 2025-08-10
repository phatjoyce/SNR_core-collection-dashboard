import os
from PIL import Image
from colorthief import ColorThief
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

IMG_DIR = "data/raw/snr_core_collection"

def get_palette(img_path, color_count=6):
    with open(img_path, 'rb') as f:
        ct = ColorThief(f)
        return ct.get_palette(color_count=color_count)

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

st.set_page_config(page_title="Core Collection Color Analysis", layout="wide")
st.title("🎨 Sporty & Rich — Core Collection Color Analysis")

image_files = [f for f in os.listdir(IMG_DIR) if f.lower().endswith(('.jpg','.png','.jpeg','.webp'))]

all_colors = []
cols = st.columns(3)

for i, fname in enumerate(image_files):
    img_path = os.path.join(IMG_DIR, fname)
    palette = get_palette(img_path, color_count=6)
    hex_colors = [rgb_to_hex(c) for c in palette]
    all_colors.extend(hex_colors)

    with cols[i % 3]:
        st.image(Image.open(img_path), caption=fname, use_container_width=True)
        st.markdown("".join([f"<div style='display:inline-block;width:30px;height:30px;background:{h}'></div>" for h in hex_colors]), unsafe_allow_html=True)

# Aggregate palette across all images
color_counts = pd.Series(all_colors).value_counts()
fig, ax = plt.subplots(figsize=(8,4))
ax.bar(color_counts.index, color_counts.values, color=color_counts.index)
ax.set_ylabel("Frequency")
ax.set_title("Top Colors Across Collection")
st.pyplot(fig)

# --- Download button ---
csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download colors CSV",
    data=csv_bytes,
    file_name="core_collection_colors.csv",
    mime="text/csv",
)
