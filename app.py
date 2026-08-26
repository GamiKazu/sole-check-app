import base64
import gc
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageOps


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="足裏タイプ診断",
    layout="centered"
)

if "step" not in st.session_state:
    st.session_state.step = 1

ASSET_DIR = Path("assets")


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>
html, body, [class*="css"] {
    font-family: "Yu Gothic", "YuGothic", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
}

.block-container {
    max-width: 760px;
    padding-top: 2.6rem;
    padding-bottom: 4rem;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }

.top-credit {
    width: 100%;
    text-align: right;
    font-size: 10px;
    color: #999999;
    opacity: 0.82;
    letter-spacing: 0.05em;
    margin-top: 20px;
    margin-bottom: 10px;
}

.main-title {
    text-align: center;
    font-family: "Yu Mincho", "YuMincho", "Hiragino Mincho ProN", serif;
    font-size: 2.5rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    line-height: 1.5;
    color: #405348;
    margin-top: 0.2rem;
    margin-bottom: 0.15rem;
}

.english-title {
    text-align: center;
    color: #9B806E;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.20em;
    margin-bottom: 2.2rem;
}

.step-box {
    padding: 15px 20px;
    border-radius: 16px;
    background: linear-gradient(135deg, #E5EFE8 0%, #F6EEE5 100%);
    border: 1px solid #D9E4DC;
    color: #42564A;
    font-family: "Yu Mincho", "Hiragino Mincho ProN", serif;
    font-weight: 700;
    font-size: 1.15rem;
    margin-bottom: 1.45rem;
}

.score-note {
    font-family: "Yu Gothic", sans-serif;
    font-size: 0.64rem;
    font-weight: 400;
    color: #849087;
    margin-top: 8px;
}

.score-guide {
    font-family: "Yu Gothic", sans-serif;
    font-size: 0.56rem;
    font-weight: 400;
    color: #8D968F;
    margin-top: 6px;
    line-height: 1.45;
}

.score-result-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 18px;
}

.score-result-main {
    min-width: 0;
    flex: 1;
}

.score-result-title {
    font-family: "Yu Mincho", "Hiragino Mincho ProN", serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #42564A;
    line-height: 1.5;
}

.score-grade-badge {
    display: inline-block;
    margin-left: 7px;
    padding: 2px 9px;
    border-radius: 999px;
    background: rgba(83, 108, 91, 0.12);
    border: 1px solid rgba(83, 108, 91, 0.18);
    color: #536C5B;
    font-family: "Yu Gothic", sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    vertical-align: 0.08em;
}

.score-message {
    font-family: "Yu Gothic", sans-serif;
    font-size: 13px;
    font-weight: 500;
    margin-top: 5px;
    opacity: 0.72;
}

.score-grade-guide {
    flex: 0 0 auto;
    min-width: 82px;
    font-family: "Yu Gothic", sans-serif;
    font-size: 0.52rem;
    font-weight: 400;
    color: #7F8A82;
    line-height: 1.52;
    text-align: left;
    white-space: nowrap;
    padding-top: 1px;
}

.score-grade-guide-title {
    font-weight: 700;
    margin-bottom: 2px;
}

.question-space { height: 12px; }

.guide-card {
    background: #FBF7F0;
    border: 1px solid #EADFD2;
    border-radius: 17px;
    padding: 14px 16px;
    margin-top: 3px;
    margin-bottom: 16px;
    color: #474747;
    font-size: 0.90rem;
    line-height: 1.45;
}

.guide-list {
    margin-top: 10px;
    margin-bottom: 10px;
    line-height: 1.55;
}

.guide-note {
    color: #918881;
    font-size: 0.60rem;
    line-height: 1.4;
}

.photo-note {
    color: #979797;
    font-size: 0.61rem;
    line-height: 1.45;
    margin-top: 15px;
    margin-bottom: 17px;
}

/* File uploader */
[data-testid="stFileUploader"] small { display: none !important; }
[data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
[data-testid="stFileUploaderFile"] {
    background: #EDF5EF !important;
    border: 1px solid #D8E7DC !important;
    border-radius: 10px !important;
    padding: 6px 9px !important;
}

.upload-status {
    background: #EDF5EF;
    border: 1px solid #D8E7DC;
    border-radius: 10px;
    padding: 7px 11px;
    margin-top: 5px;
    margin-bottom: 13px;
    color: #536C5B;
    font-size: 0.73rem;
    line-height: 1.4;
    font-weight: 600;
}

.upload-change-note {
    color: #8A968D;
    font-size: 0.58rem;
    font-weight: 400;
    margin-top: 3px;
}

/* 結果 */
.result-card {
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 20px;
    line-height: 1.58;
    font-size: 0.91rem;
    color: #363636;
    border: 1px solid rgba(70, 90, 75, 0.09);
    box-shadow: 0 4px 14px rgba(70, 80, 70, 0.045);
}

.card-beige { background: #FAF4EA; }
.card-orange { background: #FFF0E5; }
.card-green { background: #EDF5EF; }
.card-sage { background: #E6F0E9; }
.card-cream { background: #FCF7E9; }
.card-lavender { background: #F1ECF6; }
.card-rose { background: #F9ECEA; }
.card-aroma { background: linear-gradient(135deg, #F0EAF5 0%, #F9F2E8 100%); }

.result-main {
    font-size: 1.05rem;
    font-weight: 700;
    color: #405348;
}
.visual-result-name {
    display: block;
    margin-bottom: 10px;
}

.result-image-wrap {
    width: fit-content;
    max-width: 100%;
    display: block;
    margin: 10px auto 14px auto;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    min-height: 0 !important;
    height: auto !important;
    line-height: 0;
}

.result-image {
    width: auto;
    height: auto;
    display: block;
    margin: 0 auto;
    padding: 0;
    object-fit: contain;
    background: transparent !important;
    border: 0;
    box-shadow: none;
}

.result-image.foot-image {
    max-width: 185px;
    max-height: 215px;
}

.result-image.shoe-image {
    max-width: 265px;
    max-height: 150px;
}

.result-image.aroma-image {
    max-width: 165px;
    max-height: 165px;
}

.visual-description {
    display: block;
    margin-top: 2px;
}
.care-title {
    font-weight: 700;
    color: #536C5B;
}

.small-note {
    font-size: 0.64rem;
    line-height: 1.45;
    color: #8E8E8E;
}

.compact-card {
    padding-top: 15px !important;
    padding-bottom: 15px !important;
}

.disclaimer {
    color: #AAAAAA;
    font-size: 0.48rem;
    line-height: 1.45;
    margin-top: 6px;
    margin-bottom: 14px;
}

h3 {
    font-family: "Yu Mincho", "Hiragino Mincho ProN", serif !important;
    color: #42564A !important;
    letter-spacing: 0.02em;
}

div.stButton > button {
    width: 100%;
    min-height: 50px;
    border-radius: 14px;
    font-size: 16px;
    font-weight: 700;
}

.st-key-action_buttons [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
    gap: 10px !important;
}

.st-key-action_buttons [data-testid="column"] {
    width: auto !important;
    min-width: 0 !important;
    flex: none !important;
}

.st-key-fatigue_grid [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
    gap: 5px 12px !important;
}

.st-key-fatigue_grid [data-testid="column"] {
    width: auto !important;
    min-width: 0 !important;
    flex: none !important;
}

/* レーダーチャート */
.radar-card {
    background: #FBFCFA;
    border: 1px solid #E0E8E2;
    border-radius: 18px;
    padding: 14px 10px 8px 10px;
    margin-top: -2px;
    margin-bottom: 24px;
}

.radar-title {
    text-align: center;
    color: #52665A;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 2px;
}

.radar-note {
    text-align: center;
    color: #929A94;
    font-size: 0.55rem;
    margin-top: -2px;
}

.radar-card svg {
    width: 100%;
    max-width: 430px;
    height: auto;
    display: block;
    margin: 0 auto;
    overflow: visible;
}

.radar-grid {
    fill: none;
    stroke: #D9E1DB;
    stroke-width: 1;
}

.radar-axis {
    stroke: #E3E9E5;
    stroke-width: 1;
}

.radar-fill {
    fill: rgba(127, 163, 139, 0.22);
    stroke: #6F927B;
    stroke-width: 2.1;
}

.radar-dot {
    fill: #6F927B;
}

.radar-label {
    font-family: "Yu Gothic", "Hiragino Kaku Gothic ProN", sans-serif;
    font-size: 13px;
    fill: #53655B;
    font-weight: 600;
}

.radar-value {
    font-family: "Yu Gothic", "Hiragino Kaku Gothic ProN", sans-serif;
    font-size: 10px;
    fill: #8A968E;
}

@media (max-width: 600px) {
    .block-container {
        padding-top: 2.7rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .top-credit {
        font-size: 9px;
        margin-top: 26px;
        margin-bottom: 10px;
    }
    .main-title { font-size: 2rem; }
    .english-title {
        font-size: 0.65rem;
        letter-spacing: 0.13em;
        margin-bottom: 1.9rem;
    }
    .question-space { height: 9px; }
    .guide-card {
        padding: 13px 15px;
        font-size: 0.86rem;
        line-height: 1.4;
    }
    .guide-list {
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .guide-note { font-size: 0.56rem; }
    .photo-note { font-size: 0.57rem; }
    .upload-status {
        font-size: 0.68rem;
        padding: 7px 10px;
    }
    .upload-change-note { font-size: 0.54rem; }
    .result-card {
        padding: 16px 17px;
        font-size: 0.88rem;
        line-height: 1.55;
        margin-bottom: 18px;
    }
    .result-main { font-size: 1rem; }
    .score-result-row {
        gap: 10px;
    }
    .score-result-title {
        font-size: 1.02rem;
    }
    .score-grade-badge {
        margin-left: 4px;
        padding: 2px 7px;
        font-size: 0.70rem;
    }
    .score-message {
        font-size: 12px;
    }
    .score-grade-guide {
        min-width: 73px;
        font-size: 0.48rem;
    }
    h3 { font-size: 1rem !important; }
    .small-note { font-size: 0.61rem; }
    .disclaimer { font-size: 0.44rem; }
    .radar-card { padding: 10px 3px 7px 3px; }
    .radar-label { font-size: 12px; }
    .radar-value { font-size: 9px; }

    .result-image.foot-image {
        max-width: 170px;
        max-height: 195px;
    }

    .result-image.shoe-image {
        max-width: 245px;
        max-height: 140px;
    }

    .result-image.aroma-image {
        max-width: 150px;
        max-height: 150px;
    }

    .visual-result-name {
        margin-bottom: 8px;
    }

    .result-image-wrap {
        margin-top: 8px;
        margin-bottom: 12px;
    }
}
</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
<div class="top-credit">Created by GamiKazu</div>
<div class="main-title">足裏タイプ診断</div>
<div class="english-title">REFLEXOLOGY × AROMATHERAPY</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# 共通UI
# =========================================================
def show_upload_status(uploaded_file):
    if uploaded_file is None:
        return

    st.markdown(
        f"""
<div class="upload-status">
✓ アップロード済み：{uploaded_file.name}
<div class="upload-change-note">
別の写真に変える場合は、上のファイル表示から削除して選び直してください。
</div>
</div>
""",
        unsafe_allow_html=True
    )


def file_to_data_uri(path):
    path = Path(path)
    if not path.exists():
        return None
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def result_card(title, body, card_class, extra_class="", image_path=None, image_alt=""):
    st.markdown(f"### {title}")

    image_html = ""
    if image_path:
        uri = file_to_data_uri(image_path)
        if uri:
            image_html = (
                f'<div class="result-image-wrap">'
                f'<img class="result-image" src="{uri}" alt="{image_alt}">'
                f'</div>'
            )

    st.markdown(
        f"""
<div class="result-card {card_class} {extra_class}">
{image_html}
{body}
</div>
""",
        unsafe_allow_html=True
    )


def result_card_with_image(title, result_name, description, card_class, image_path, image_alt="", image_class="foot-image", extra_html=""):
    st.markdown(f"### {title}")

    image_html = ""
    if image_path:
        uri = file_to_data_uri(image_path)
        if uri:
            image_html = (
                f'<div class="result-image-wrap">'
                f'<img class="result-image {image_class}" src="{uri}" alt="{image_alt}">'
                f'</div>'
            )

    # ①結果名 → ②小さめの透過画像 → ③補足文
    st.markdown(
        f"""
<div class="result-card {card_class}">
<div class="result-main visual-result-name">{result_name}</div>
{image_html}
<div class="visual-description">{description}</div>
{extra_html}
</div>
""",
        unsafe_allow_html=True
    )


def clamp(value, low=0, high=100):
    return max(low, min(high, int(round(value))))


def radar_svg(values):
    labels = list(values.keys())
    scores = [clamp(values[k]) for k in labels]

    cx, cy = 210, 175
    max_r = 108
    angles = [-90, -30, 30, 90, 150, 210]

    import math

    def pt(angle_deg, radius):
        a = math.radians(angle_deg)
        return (cx + radius * math.cos(a), cy + radius * math.sin(a))

    grid_polys = []
    for ratio in [0.25, 0.5, 0.75, 1.0]:
        coords = [pt(a, max_r * ratio) for a in angles]
        points = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
        grid_polys.append(f'<polygon class="radar-grid" points="{points}"/>')

    axes = []
    for a in angles:
        x, y = pt(a, max_r)
        axes.append(f'<line class="radar-axis" x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>')

    data_coords = [pt(a, max_r * s / 100.0) for a, s in zip(angles, scores)]
    data_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in data_coords)

    dots = "".join(
        f'<circle class="radar-dot" cx="{x:.1f}" cy="{y:.1f}" r="3.1"/>'
        for x, y in data_coords
    )

    label_positions = [
        (210, 35, "middle"),
        (404, 98, "end"),
        (404, 260, "end"),
        (210, 330, "middle"),
        (16, 260, "start"),
        (16, 98, "start"),
    ]

    label_html = []
    for label, score, (x, y, anchor) in zip(labels, scores, label_positions):
        label_html.append(
            f'<text class="radar-label" x="{x}" y="{y}" text-anchor="{anchor}">{label}</text>'
            f'<text class="radar-value" x="{x}" y="{y+15}" text-anchor="{anchor}">{score}</text>'
        )

    return f"""
<div class="radar-card">
<div class="radar-title">6つのコンディション</div>
<svg viewBox="0 0 420 350" role="img" aria-label="6項目のレーダーチャート">
{''.join(grid_polys)}
{''.join(axes)}
<polygon class="radar-fill" points="{data_points}"/>
{dots}
{''.join(label_html)}
</svg>
<div class="radar-note">※100に近いほど、今回の回答・写真では良好な傾向です。</div>
</div>
"""


# =========================================================
# 画像解析
# =========================================================
def uploaded_to_rgb(uploaded_file, max_side=640):
    uploaded_file.seek(0)
    with Image.open(uploaded_file) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
        rgb = np.asarray(image, dtype=np.uint8).copy()
    return rgb


def largest_contour(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    return max(contours, key=cv2.contourArea)


def clean_mask(binary):
    kernel = np.ones((5, 5), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    contour = largest_contour(binary)
    if contour is None:
        return None
    clean = np.zeros_like(binary)
    cv2.drawContours(clean, [contour], -1, 255, -1)
    return clean


def segment_foot(rgb):
    h, w = rgb.shape[:2]
    if h < 70 or w < 40:
        return None

    patch_h = max(5, int(h * 0.07))
    patch_w = max(5, int(w * 0.07))

    corners = np.concatenate([
        rgb[:patch_h, :patch_w].reshape(-1, 3),
        rgb[:patch_h, -patch_w:].reshape(-1, 3),
        rgb[-patch_h:, :patch_w].reshape(-1, 3),
        rgb[-patch_h:, -patch_w:].reshape(-1, 3),
    ], axis=0)

    background = np.median(corners, axis=0).astype(np.int16)
    diff = rgb.astype(np.int16) - background
    distance = np.sqrt(np.sum(diff * diff, axis=2))
    distance = np.clip(distance, 0, 255).astype(np.uint8)

    _, binary = cv2.threshold(
        distance, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    mask = clean_mask(binary)
    if mask is None:
        return None

    contour = largest_contour(mask)
    if contour is None:
        return None

    ratio = cv2.contourArea(contour) / float(h * w)
    if ratio < 0.07 or ratio > 0.90:
        return None

    return mask


def crop_to_mask(rgb, mask):
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return rgb, mask

    x1, x2 = int(xs.min()), int(xs.max())
    y1, y2 = int(ys.min()), int(ys.max())
    return rgb[y1:y2 + 1, x1:x2 + 1], mask[y1:y2 + 1, x1:x2 + 1]


def rotate_bound(image, angle, interpolation, border_value):
    h, w = image.shape[:2]
    center = (w / 2, h / 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    cos = abs(matrix[0, 0])
    sin = abs(matrix[0, 1])
    new_w = int(h * sin + w * cos)
    new_h = int(h * cos + w * sin)

    matrix[0, 2] += new_w / 2 - center[0]
    matrix[1, 2] += new_h / 2 - center[1]

    return cv2.warpAffine(
        image,
        matrix,
        (new_w, new_h),
        flags=interpolation,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value
    )


def straighten_foot(rgb, mask):
    contour = largest_contour(mask)
    if contour is None:
        return rgb, mask

    try:
        _, size, angle = cv2.minAreaRect(contour)
        rw, rh = size
        rotation = angle if rw > rh else angle - 90

        rgb = rotate_bound(rgb, rotation, cv2.INTER_LINEAR, (255, 255, 255))
        mask = rotate_bound(mask, rotation, cv2.INTER_NEAREST, 0)
    except cv2.error:
        pass

    return rgb, mask


def width_in_band(mask, start, end):
    h, _ = mask.shape
    y1, y2 = int(h * start), int(h * end)
    widths = []

    for y in range(y1, y2):
        xs = np.where(mask[y] > 0)[0]
        if len(xs) > 0:
            widths.append(xs.max() - xs.min() + 1)

    return float(np.median(widths)) if widths else 0


def ensure_toes_top(rgb, mask):
    top = width_in_band(mask, 0.03, 0.24)
    bottom = width_in_band(mask, 0.76, 0.97)

    if bottom > top:
        rgb = np.rot90(rgb, 2).copy()
        mask = np.rot90(mask, 2).copy()

    return rgb, mask


def smooth_curve(curve):
    curve = np.asarray(curve, dtype=np.float32)
    if len(curve) < 7:
        return curve

    size = max(7, int(len(curve) * 0.025))
    if size % 2 == 0:
        size += 1

    kernel = np.ones(size, np.float32) / size
    return np.convolve(curve, kernel, mode="same")


def build_top_curve(mask):
    h, w = mask.shape
    toe_bottom = int(h * 0.43)
    curve = np.full(w, np.nan, dtype=np.float32)

    for x in range(w):
        ys = np.where(mask[:toe_bottom, x] > 0)[0]
        if len(ys) > 0:
            curve[x] = float(np.percentile(ys, 3))

    valid = np.where(np.isfinite(curve))[0]
    if len(valid) < 30:
        return None

    x1, x2 = int(valid.min()), int(valid.max())
    curve = curve[x1:x2 + 1]
    missing = ~np.isfinite(curve)
    known = np.where(~missing)[0]

    if len(known) < 5:
        return None

    curve[missing] = np.interp(np.where(missing)[0], known, curve[known])
    return smooth_curve(curve)


def detect_three_toes(mask, big_toe_side):
    curve = build_top_curve(mask)
    if curve is None:
        return None

    h, _ = mask.shape
    n = len(curve)

    if big_toe_side == "right":
        curve = curve[::-1]

    windows = [
        (0.02, 0.25),
        (0.18, 0.43),
        (0.35, 0.60),
    ]

    values = []
    for start, end in windows:
        sx, ex = int(n * start), int(n * end)
        if ex <= sx:
            return None
        part = curve[sx:ex]
        if len(part) < 3:
            return None
        values.append(float(np.min(part)))

    return values[0], values[1], values[2], float(h)


def classify_foot_shape(rgb, mask, big_toe_side):
    if mask is None:
        return "判定困難", 0.0

    rgb, mask = crop_to_mask(rgb, mask)
    rgb, mask = straighten_foot(rgb, mask)
    rgb, mask = crop_to_mask(rgb, mask)
    rgb, mask = ensure_toes_top(rgb, mask)
    rgb, mask = crop_to_mask(rgb, mask)

    h, w = mask.shape
    if h < 75 or w < 38:
        return "判定困難", 0.0

    result = detect_three_toes(mask, big_toe_side)
    if result is None:
        return "判定困難", 0.0

    big, second, third, foot_length = result

    spread = (max(big, second, third) - min(big, second, third)) / foot_length
    if spread <= 0.010:
        return "スクエア型", 0.90

    greek_difference = (big - second) / foot_length
    if greek_difference > 0.035:
        confidence = min(0.97, 0.84 + greek_difference * 3.5)
        return "ギリシャ型", confidence

    return "エジプト型", 0.92


def analyze_color(rgb, mask):
    if mask is None:
        return "判定困難", {}

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)

    valid = mask > 0
    brightness = hsv[:, :, 2]
    valid &= brightness > 45
    valid &= brightness < 248

    if valid.sum() < 100:
        valid = mask > 0

    H = float(np.median(hsv[:, :, 0][valid]))
    S = float(np.median(hsv[:, :, 1][valid]))
    V = float(np.median(hsv[:, :, 2][valid]))
    A = float(np.median(lab[:, :, 1][valid]))
    B = float(np.median(lab[:, :, 2][valid]))

    if S < 35 and V > 185:
        result = "白っぽい"
    elif (H <= 5 or H >= 176) and S >= 55 and A >= 135:
        result = "赤み強め"
    elif 5 < H <= 17 and S >= 45:
        result = "オレンジ寄り"
    elif 17 < H <= 32 and S >= 45 and B >= 135:
        result = "黄み強め"
    else:
        result = "標準的な色味"

    return result, {"H": H, "S": S, "V": V}


def analyze_texture(rgb, mask):
    if mask is None:
        return "判定困難", "判定困難"

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_32F)
    texture = np.abs(lap)[mask > 0]
    texture_score = float(np.percentile(texture, 75)) if texture.size > 0 else 0

    if texture_score > 28:
        dryness = "乾燥が目立つ"
    elif texture_score > 18:
        dryness = "やや乾燥"
    else:
        dryness = "乾燥は目立たない"

    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    candidates = (mask > 0) & (lab[:, :, 0] > 145) & (lab[:, :, 2] > 138)
    ys, xs = np.where(candidates)

    if len(xs) < 80:
        return dryness, "なし"

    all_y, all_x = np.where(mask > 0)
    if len(all_x) == 0:
        return dryness, "なし"

    x1, x2 = all_x.min(), all_x.max()
    y1, y2 = all_y.min(), all_y.max()
    cx, cy = float(xs.mean()), float(ys.mean())

    nx = (cx - x1) / max(1, x2 - x1)
    ny = (cy - y1) / max(1, y2 - y1)

    if ny > 0.72:
        hard_part = "かかと"
    elif ny < 0.45:
        hard_part = "足の前側"
    elif nx < 0.35:
        hard_part = "足裏の左側"
    elif nx > 0.65:
        hard_part = "足裏の右側"
    else:
        hard_part = "足裏の中央"

    return dryness, hard_part


def split_both(rgb):
    _, w = rgb.shape[:2]
    center = w // 2
    overlap = int(w * 0.02)
    left = rgb[:, :min(w, center + overlap)].copy()
    right = rgb[:, max(0, center - overlap):].copy()
    return left, right


def unify_shapes(results):
    usable = [r for r in results if r[0] != "判定困難"]
    if not usable:
        return "判定困難", 0

    counts = {"エジプト型": 0, "ギリシャ型": 0, "スクエア型": 0}
    scores = {"エジプト型": 0, "ギリシャ型": 0, "スクエア型": 0}

    for shape, conf in usable:
        counts[shape] += 1
        scores[shape] += conf

    max_count = max(counts.values())
    winners = [s for s, c in counts.items() if c == max_count and c > 0]

    if len(winners) == 1:
        chosen = winners[0]
        return chosen, scores[chosen] / counts[chosen]

    if scores["ギリシャ型"] > scores["エジプト型"] * 1.35:
        return "ギリシャ型", scores["ギリシャ型"]

    if scores["エジプト型"] > 0:
        return "エジプト型", scores["エジプト型"]

    chosen = max(scores, key=scores.get)
    return chosen, scores[chosen]


def analyze_images(both_rgb=None, right_rgb=None, left_rgb=None):
    shape_results = []
    representative_rgb = None
    representative_mask = None

    if right_rgb is not None:
        mask = segment_foot(right_rgb)
        result = classify_foot_shape(right_rgb, mask, "left")
        if result[0] != "判定困難":
            shape_results.append((result[0], min(0.99, result[1] + 0.05)))
        if representative_rgb is None:
            representative_rgb = right_rgb
            representative_mask = mask

    if left_rgb is not None:
        mask = segment_foot(left_rgb)
        result = classify_foot_shape(left_rgb, mask, "right")
        if result[0] != "判定困難":
            shape_results.append((result[0], min(0.99, result[1] + 0.05)))
        if representative_rgb is None:
            representative_rgb = left_rgb
            representative_mask = mask

    if both_rgb is not None:
        left_part, right_part = split_both(both_rgb)
        left_mask = segment_foot(left_part)
        right_mask = segment_foot(right_part)

        left_result = classify_foot_shape(left_part, left_mask, "right")
        right_result = classify_foot_shape(right_part, right_mask, "left")
        both_result = unify_shapes([left_result, right_result])

        if both_result[0] != "判定困難":
            shape_results.append(both_result)

        if representative_rgb is None:
            left_area = np.count_nonzero(left_mask) if left_mask is not None else 0
            right_area = np.count_nonzero(right_mask) if right_mask is not None else 0

            if right_area >= left_area:
                representative_rgb = right_part
                representative_mask = right_mask
            else:
                representative_rgb = left_part
                representative_mask = left_mask

    overall_shape, shape_conf = unify_shapes(shape_results)

    if representative_rgb is None or representative_mask is None:
        foot_color = "判定困難"
        color_info = {}
        dryness = "判定困難"
        hard_part = "判定困難"
    else:
        foot_color, color_info = analyze_color(representative_rgb, representative_mask)
        dryness, hard_part = analyze_texture(representative_rgb, representative_mask)

    gc.collect()

    return {
        "overall_shape": overall_shape,
        "shape_conf": shape_conf,
        "foot_color": foot_color,
        "color_info": color_info,
        "dryness": dryness,
        "hard_part": hard_part,
    }


# =========================================================
# STEP1
# =========================================================
if st.session_state.step == 1:
    st.markdown('<div class="step-box">STEP 1　簡単な質問</div>', unsafe_allow_html=True)

    cold = st.radio("Q1. 足が冷えやすいですか？", ["はい", "いいえ"], horizontal=True)
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    swelling = st.radio("Q2. むくみを感じることがありますか？", ["はい", "いいえ"], horizontal=True)
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    tired = st.radio("Q3. 長時間歩いたり立ったりすると、足が疲れやすいですか？", ["はい", "いいえ"], horizontal=True)
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    standing = st.radio("Q4. 普段、立っている時間は長いですか？", ["はい", "いいえ"], horizontal=True)
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    shoes = st.selectbox("Q5. 普段よく履く靴は？", ["スニーカー", "革靴", "パンプス", "サンダル", "ブーツ", "その他"])
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    foot_concern = st.selectbox(
        "Q6. 足で一番気になることは？",
        ["特にない", "疲れやすい", "冷え", "むくみ", "乾燥", "硬くなった部分", "靴が合いにくい", "歩き方が気になる"]
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    st.write("Q7. 今、疲れを感じる場所はありますか？")
    fatigue_area = []

    with st.container(key="fatigue_grid"):
        row1 = st.columns(2)
        with row1[0]:
            if st.checkbox("頭・目", key="fatigue_head"):
                fatigue_area.append("頭・目")
        with row1[1]:
            if st.checkbox("首", key="fatigue_neck"):
                fatigue_area.append("首")

        row2 = st.columns(2)
        with row2[0]:
            if st.checkbox("肩", key="fatigue_shoulder"):
                fatigue_area.append("肩")
        with row2[1]:
            if st.checkbox("背中", key="fatigue_back"):
                fatigue_area.append("背中")

        row3 = st.columns(2)
        with row3[0]:
            if st.checkbox("腰", key="fatigue_waist"):
                fatigue_area.append("腰")
        with row3[1]:
            if st.checkbox("胃まわり", key="fatigue_stomach"):
                fatigue_area.append("胃まわり")

        row4 = st.columns(2)
        with row4[0]:
            if st.checkbox("脚", key="fatigue_leg"):
                fatigue_area.append("脚")
        with row4[1]:
            if st.checkbox("全身", key="fatigue_all"):
                fatigue_area.append("全身")

    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    sole_wear = st.selectbox(
        "Q8. 靴底はどこが減りやすいですか？",
        ["分からない", "かかとの外側", "かかとの内側", "つま先側", "全体的に均等"]
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    stumble = st.radio("Q9. 歩いている時につまずきやすいですか？", ["はい", "いいえ"], horizontal=True)
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    aroma_goal = st.selectbox("Q10. 今、一番求めているものは？", ["リラックス", "リフレッシュ", "集中", "睡眠", "気分転換"])
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    if st.button("次へ", type="primary", use_container_width=True):
        st.session_state.cold = cold
        st.session_state.swelling = swelling
        st.session_state.tired = tired
        st.session_state.standing = standing
        st.session_state.shoes = shoes
        st.session_state.foot_concern = foot_concern
        st.session_state.fatigue_area = fatigue_area
        st.session_state.sole_wear = sole_wear
        st.session_state.stumble = stumble
        st.session_state.aroma_goal = aroma_goal
        st.session_state.step = 2
        st.rerun()


# =========================================================
# STEP2
# =========================================================
elif st.session_state.step == 2:
    st.markdown('<div class="step-box">STEP 2　足裏写真</div>', unsafe_allow_html=True)

    st.markdown(
        """
<div class="guide-card">
下のいずれか1枚以上をアップロードしてください。
<div class="guide-list">・両足<br>・右足<br>・左足</div>
<span class="guide-note">※より正確な判定には、3種類すべての撮影がおすすめです。</span>
</div>
""",
        unsafe_allow_html=True
    )

    both_feet = st.file_uploader("両足の写真（任意）", type=["jpg", "jpeg", "png"], key="both_feet")
    show_upload_status(both_feet)

    right_foot = st.file_uploader("右足の写真（任意）", type=["jpg", "jpeg", "png"], key="right_foot")
    show_upload_status(right_foot)

    left_foot = st.file_uploader("左足の写真（任意）", type=["jpg", "jpeg", "png"], key="left_foot")
    show_upload_status(left_foot)

    st.markdown(
        """
<div class="photo-note">
※足指からかかとまで画面に入れ、できるだけ真正面から撮影してください。足指同士が重ならない写真がおすすめです。背景はできるだけ無地にしてください。
</div>
""",
        unsafe_allow_html=True
    )

    has_photo = both_feet is not None or right_foot is not None or left_foot is not None

    with st.container(key="action_buttons"):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("戻る", use_container_width=True):
                st.session_state.step = 1
                st.rerun()

        with col2:
            diagnose = st.button(
                "診断する",
                type="primary",
                disabled=not has_photo,
                use_container_width=True
            )

    if diagnose:
        progress = st.progress(0)
        status = st.empty()

        try:
            status.write("写真を読み込んでいます...")

            both_rgb = uploaded_to_rgb(both_feet) if both_feet is not None else None
            progress.progress(25)

            right_rgb = uploaded_to_rgb(right_foot) if right_foot is not None else None
            progress.progress(40)

            left_rgb = uploaded_to_rgb(left_foot) if left_foot is not None else None
            progress.progress(55)

            status.write("足裏を確認しています...")

            analysis = analyze_images(
                both_rgb=both_rgb,
                right_rgb=right_rgb,
                left_rgb=left_rgb
            )

            progress.progress(90)
            st.session_state.analysis = analysis

            del both_rgb
            del right_rgb
            del left_rgb
            gc.collect()

            progress.progress(100)
            st.session_state.step = 3
            st.rerun()

        except Exception as error:
            gc.collect()
            st.error("写真をうまく解析できませんでした。別の写真でお試しください。")
            st.caption(str(error))


# =========================================================
# STEP3
# =========================================================
elif st.session_state.step == 3:
    analysis = st.session_state.analysis

    cold = st.session_state.cold
    swelling = st.session_state.swelling
    tired = st.session_state.tired
    standing = st.session_state.standing
    fatigue_area = st.session_state.fatigue_area
    sole_wear = st.session_state.sole_wear
    stumble = st.session_state.stumble
    aroma_goal = st.session_state.aroma_goal

    shape = analysis["overall_shape"]
    color = analysis["foot_color"]

    # -----------------------------------------------------
    # 6つのコンディション
    # -----------------------------------------------------
    circulation = 100
    if cold == "はい":
        circulation -= 32
    if color == "白っぽい":
        circulation -= 10

    freshness = 100
    if swelling == "はい":
        freshness -= 35
    if standing == "はい":
        freshness -= 8

    energy = 100
    if tired == "はい":
        energy -= 35
    if standing == "はい":
        energy -= 12

    walkability = 100
    if stumble == "はい":
        walkability -= 30
    if sole_wear in ["かかとの外側", "かかとの内側", "つま先側"]:
        walkability -= 12

    sole_condition = 100
    if analysis["dryness"] == "やや乾燥":
        sole_condition -= 18
    elif analysis["dryness"] == "乾燥が目立つ":
        sole_condition -= 32

    if analysis["hard_part"] not in ["なし", "判定困難"]:
        sole_condition -= 15

    if color in ["赤み強め", "オレンジ寄り", "白っぽい"]:
        sole_condition -= 8

    rest_balance = 100
    rest_balance -= min(36, len(fatigue_area) * 8)
    if tired == "はい":
        rest_balance -= 12

    radar_values = {
        "めぐり": clamp(circulation, 35, 100),
        "すっきり感": clamp(freshness, 35, 100),
        "足の元気": clamp(energy, 35, 100),
        "歩きやすさ": clamp(walkability, 35, 100),
        "足裏状態": clamp(sole_condition, 35, 100),
        "休息状態": clamp(rest_balance, 35, 100),
    }

    # -----------------------------------------------------
    # 総合スコア
    # 6つのコンディションから加重平均で算出
    # -----------------------------------------------------
    score = round(
        radar_values["めぐり"] * 0.15
        + radar_values["すっきり感"] * 0.15
        + radar_values["足の元気"] * 0.20
        + radar_values["歩きやすさ"] * 0.15
        + radar_values["足裏状態"] * 0.20
        + radar_values["休息状態"] * 0.15
    )

    score = max(0, min(100, score))

    # -----------------------------------------------------
    # A〜E評価
    # -----------------------------------------------------
    if score >= 90:
        score_grade = "A"
        score_message = "今はとてもバランスの良い状態です"
    elif score >= 75:
        score_grade = "B"
        score_message = "今は比較的良い状態です"
    elif score >= 55:
        score_grade = "C"
        score_message = "少しセルフケアを意識したい状態です"
    elif score >= 40:
        score_grade = "D"
        score_message = "今日は休息とセルフケアを意識しましょう"
    else:
        score_grade = "E"
        score_message = "無理をせず、しっかり休むことを意識しましょう"

    st.markdown(
        f"""
<div class="step-box">
    <div class="score-result-row">
        <div class="score-result-main">
            <div class="score-result-title">
                診断結果：{score}点
                <span class="score-grade-badge">評価 {score_grade}</span>
            </div>
            <div class="score-message">
                {score_message}
            </div>
        </div>

        <div class="score-grade-guide">
            <div class="score-grade-guide-title">評価基準</div>
            90〜100：A<br>
            75〜89：B<br>
            55〜74：C<br>
            40〜54：D<br>
            0〜39：E
        </div>
    </div>

    <div class="score-note">
        ※6つのコンディションから算出した、このアプリ独自の参考スコアです。
    </div>
</div>
""",
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 6角形レーダーチャート
    # -----------------------------------------------------
    st.markdown(radar_svg(radar_values), unsafe_allow_html=True)

    # -----------------------------------------------------
    # 1 足の形
    # -----------------------------------------------------
    if shape == "エジプト型":
        shape_text = "親指が一番長く、小指に向かって少しずつ短くなるタイプです。"
        foot_image = ASSET_DIR / "foot_egypt.png"
        shoe_image = ASSET_DIR / "shoes_egypt.png"
    elif shape == "ギリシャ型":
        shape_text = "人差し指が親指よりはっきり長いタイプです。"
        foot_image = ASSET_DIR / "foot_greek.png"
        shoe_image = ASSET_DIR / "shoes_greek.png"
    elif shape == "スクエア型":
        shape_text = "親指・人差し指・中指の長さがかなり近いタイプです。"
        foot_image = ASSET_DIR / "foot_square.png"
        shoe_image = ASSET_DIR / "shoes_square.png"
    else:
        shape_text = "今回の写真では足の形をはっきり判定できませんでした。"
        foot_image = None
        shoe_image = None

    result_card_with_image(
        "1. 足の形",
        shape,
        shape_text,
        "card-beige",
        image_path=foot_image,
        image_alt=f"{shape}の参考イラスト",
        image_class="foot-image"
    )

    # -----------------------------------------------------
    # 2 足の色
    # -----------------------------------------------------
    if color == "赤み強め":
        color_text = (
            "写真では赤みがやや強く見えます。"
            "<br><br><span class='care-title'>足の色から見る傾向</span><br>"
            "足の色から見る考え方では、赤みが強い時は、活動量が多い時や足元が温まっている時など、"
            "体の活動が色に表れている状態として捉えられることがあります。"
            "少し休んだあとに色の変化を見てみるのもおすすめです。"
            "<br><br><span class='small-note'>※写真の色は照明・カメラ・肌の色によって変わります。医療的な診断ではありません。</span>"
        )
    elif color == "オレンジ寄り":
        color_text = (
            "写真では少しオレンジ寄りに見えます。赤みと黄みの中間に見える色合いです。"
            "<br><br><span class='care-title'>足の色から見る傾向</span><br>"
            "足の色から見る考え方では、活動による温まりや疲れが重なっている時に、"
            "オレンジ寄りに見えることがあるとされています。"
            "今は比較的よく動いている状態の目安として、参考程度に見てください。"
            "<br><br><span class='small-note'>※写真の色は照明・カメラ・肌の色によって変わります。医療的な診断ではありません。</span>"
        )
    elif color == "黄み強め":
        color_text = (
            "写真では少し黄みが強く見えます。"
            "<br><br><span class='care-title'>足の色から見る傾向</span><br>"
            "足の色から見る考え方では、疲れがたまっている時のサインとして捉えられることがあります。"
            "また、乾燥や硬くなった部分、照明の影響でも黄みは強く見えるため、"
            "色だけで判断せず足裏全体の状態と一緒に見てみましょう。"
            "<br><br><span class='small-note'>※写真の色は照明・カメラ・肌の色によって変わります。医療的な診断ではありません。</span>"
        )
    elif color == "白っぽい":
        color_text = (
            "写真ではやや白っぽく見えます。"
            "<br><br><span class='care-title'>足の色から見る傾向</span><br>"
            "足の色から見る考え方では、疲れや冷えを感じている時の状態として捉えられることがあります。"
            "ただし、撮影時の明るさでも白っぽく見えるため、自然光に近い場所で見比べるのがおすすめです。"
            "<br><br><span class='small-note'>※写真の色は照明・カメラ・肌の色によって変わります。医療的な診断ではありません。</span>"
        )
    elif color == "判定困難":
        color_text = (
            "今回の写真では色をうまく確認できませんでした。"
            "明るすぎない場所で撮り直すと判定しやすくなります。"
        )
    else:
        color_text = (
            "写真では大きな色の偏りは目立ちませんでした。"
            "<br><br><span class='care-title'>足の色から見る傾向</span><br>"
            "足の色から見る考え方では、強い赤み・黄み・白っぽさなどの偏りが少ない、"
            "比較的バランスのよい色合いとして捉えられます。"
            "今の色合いをひとつの目安として見てください。"
            "<br><br><span class='small-note'>※写真の色は照明・カメラ・肌の色によって変わります。医療的な診断ではありません。</span>"
        )

    result_card(
        "2. 足の色",
        f"<span class='result-main'>{color}</span><br><br>{color_text}",
        "card-orange"
    )

    # -----------------------------------------------------
    # 3 心と体
    # -----------------------------------------------------
    rest_score = 0
    if cold == "はい":
        rest_score += 2
    if swelling == "はい":
        rest_score += 1
    if tired == "はい":
        rest_score += 2
    if len(fatigue_area) >= 2:
        rest_score += 2
    elif len(fatigue_area) == 1:
        rest_score += 1

    if rest_score >= 6:
        mind_text = "今は疲れがたまりやすい状態かもしれません。休む時間や睡眠を少し意識してみましょう。"
    elif rest_score >= 3:
        mind_text = "少し疲れがたまっている可能性があります。短い休憩や気分転換を取り入れるのがおすすめです。"
    else:
        mind_text = "今は比較的バランスが取れているようです。今の状態を保ちながら、無理をしすぎないようにしましょう。"

    result_card("3. 今の心と体の傾向", mind_text, "card-green")

    # -----------------------------------------------------
    # 4 歩き方
    # -----------------------------------------------------
    walk_points = []

    if sole_wear == "かかとの外側":
        walk_points.append("靴底の減り方から、足の外側に体重がかかりやすいようです。")
    elif sole_wear == "かかとの内側":
        walk_points.append("靴底の減り方から、足の内側に体重がかかりやすいようです。")
    elif sole_wear == "つま先側":
        walk_points.append("つま先側に負担が集まりやすいようです。")
    elif sole_wear == "全体的に均等":
        walk_points.append("靴底の減り方には、大きな偏りは見られないようです。")

    hard_part = analysis["hard_part"]
    if hard_part == "足の前側":
        walk_points.append("写真でも足の前側に負担がかかっている可能性があります。")
    elif hard_part == "かかと":
        walk_points.append("写真では、かかとに負担がかかっている可能性があります。")

    if stumble == "はい":
        walk_points.append("つまずきやすい場合は、歩く時に足先を少し上げることも意識してみましょう。")

    if not walk_points:
        walk_points.append("今回の結果では、歩き方に大きな偏りは見られませんでした。")

    result_card("4. 歩き方の傾向", "<br><br>".join(walk_points), "card-sage")

    # -----------------------------------------------------
    # 5 おすすめの靴
    # -----------------------------------------------------
    if shape == "エジプト型":
        shoe_title = "つま先に丸みのある靴"
        shoe_text = "親指が一番長い足型です。親指が靴の先に当たりにくい、つま先に丸みと少し余裕のある靴がおすすめです。"
    elif shape == "ギリシャ型":
        shoe_title = "つま先に余裕のある靴"
        shoe_text = "人差し指が長めの足型です。人差し指が靴の先に当たりにくい、つま先にゆとりのある靴がおすすめです。"
    elif shape == "スクエア型":
        shoe_title = "つま先が広めの靴"
        shoe_text = "親指・人差し指・中指の長さが近い足型です。指先が窮屈になりにくい、つま先が広めの靴がおすすめです。"
    else:
        shoe_title = "つま先に余裕のある靴"
        shoe_text = "指先が窮屈にならず、足の横幅にも合った靴がおすすめです。"

    if tired == "はい":
        shoe_text += "<br><br>足が疲れやすい場合は、靴底のやわらかさも確認してみましょう。"

    result_card_with_image(
        "5. おすすめの靴",
        shoe_title,
        shoe_text,
        "card-cream",
        image_path=shoe_image,
        image_alt=f"{shape}に合いやすい男女別の靴イラスト",
        image_class="shoe-image"
    )

    # -----------------------------------------------------
    # 6 性格
    # -----------------------------------------------------
    if shape == "エジプト型":
        personality = "足の形から見る性格としては、感受性が豊かで、マイペース。自分の好きなことにはこだわりを持ちやすく、想像力があるタイプと言われることがあります。"
    elif shape == "ギリシャ型":
        personality = "足の形から見る性格としては、行動力があり、好奇心旺盛。新しいことに挑戦するのが好きで、周囲を引っ張るタイプと言われることがあります。"
    elif shape == "スクエア型":
        personality = "足の形から見る性格としては、現実的で安定感があり、物事をコツコツ進めるタイプ。落ち着いて判断するのが得意と言われることがあります。"
    else:
        personality = "今回は足型をはっきり判定できなかったため、この項目は判定できませんでした。"

    result_card(
        "6. 足の形から見る性格傾向",
        personality + "<br><br><span class='small-note'>※性格を科学的に判断するものではありません。エンタメとしてお楽しみください。</span>",
        "card-lavender",
        "compact-card"
    )

    # -----------------------------------------------------
    # 7 足裏ポイント
    # -----------------------------------------------------
    reflex_map = {
        "頭・目": "親指まわり",
        "首": "親指の付け根",
        "肩": "足指の付け根〜小指側",
        "背中": "足裏の内側",
        "腰": "土踏まずの内側〜かかと寄り",
        "胃まわり": "土踏まずの上側",
        "脚": "かかとまわり",
        "全身": "足裏全体",
    }

    if fatigue_area:
        blocks = []
        for area in fatigue_area:
            blocks.append(
                f"<span class='care-title'>{area}</span><br>"
                f"足裏のおすすめポイント：{reflex_map[area]}"
            )

        reflex_text = (
            "<br><br>".join(blocks)
            + "<br><br><span class='small-note'>"
            "リフレクソロジーでは、これらの場所を体の各部位に対応する「反射区」として扱います。"
            "心地よい強さで5〜10秒ほどゆっくり押してみてください。"
            "</span>"
        )
    else:
        reflex_text = "今回は特に疲れている場所が選択されていません。<br><br>足裏全体を気持ちいい程度の強さでゆっくりほぐしてみましょう。"

    result_card("7. 疲れた場所・足裏ポイント", reflex_text, "card-rose")

    # -----------------------------------------------------
    # 8 アロマ
    # -----------------------------------------------------
    aroma_map = {
        "リラックス": (
            "ラベンダー",
            "やさしく落ち着いたフローラル系の香りです。"
            "<br><br><span class='care-title'>香りの特徴</span><br>"
            "リラックスしたい時や、気持ちをゆるめたい時、ゆっくり過ごしたい時間に取り入れやすい香りです。",
            ASSET_DIR / "aroma_lavender.png"
        ),
        "リフレッシュ": (
            "レモン",
            "すっきり爽やかな柑橘系の香りです。"
            "<br><br><span class='care-title'>香りの特徴</span><br>"
            "気分を切り替えたい時や、頭をすっきりさせたい時、朝や作業前にも取り入れやすい香りです。",
            ASSET_DIR / "aroma_lemon.png"
        ),
        "集中": (
            "ローズマリー",
            "シャープで清涼感のあるハーブ系の香りです。"
            "<br><br><span class='care-title'>香りの特徴</span><br>"
            "集中したい時や、気持ちを引き締めたい時、仕事や勉強の前後に取り入れやすい香りです。",
            ASSET_DIR / "aroma_rosemary.png"
        ),
        "睡眠": (
            "ラベンダー",
            "やさしく落ち着いたフローラル系の香りです。"
            "<br><br><span class='care-title'>香りの特徴</span><br>"
            "寝る前や、静かに過ごしたい時、心を落ち着けたい夜の時間に取り入れやすい香りです。",
            ASSET_DIR / "aroma_lavender.png"
        ),
        "気分転換": (
            "スイートオレンジ",
            "甘くやわらかな柑橘系の香りです。"
            "<br><br><span class='care-title'>香りの特徴</span><br>"
            "気分転換したい時や、穏やかな気持ちで過ごしたい時、リラックスしたい時間に取り入れやすい香りです。",
            ASSET_DIR / "aroma_orange.png"
        ),
    }

    aroma, aroma_text, aroma_image = aroma_map[aroma_goal]

    result_card_with_image(
        "8. おすすめアロマ",
        aroma,
        aroma_text,
        "card-aroma",
        image_path=aroma_image,
        image_alt=f"{aroma}の参考イラスト",
        image_class="aroma-image"
    )

    # -----------------------------------------------------
    # 9 セルフケア
    # -----------------------------------------------------
    care = []

    if swelling == "はい":
        care.append("<span class='care-title'>むくみが気になる時</span><br>足首をゆっくり回したり、ふくらはぎを軽く動かしてみましょう。")

    if cold == "はい":
        care.append("<span class='care-title'>冷えが気になる時</span><br>足湯や靴下などで、足元を心地よく温めるのがおすすめです。")

    if tired == "はい":
        care.append("<span class='care-title'>足が疲れている時</span><br>足を休ませる時間をつくり、軽いストレッチをしてみましょう。")

    if analysis["dryness"] in ["やや乾燥", "乾燥が目立つ"]:
        care.append("<span class='care-title'>乾燥が気になる時</span><br>お風呂上がりなどに足裏を保湿するのがおすすめです。")

    if stumble == "はい":
        care.append("<span class='care-title'>つまずきやすい時</span><br>足首を軽く動かし、歩く時に足先を少し上げることを意識してみましょう。")

    if not care:
        care.append("<span class='care-title'>毎日のケア</span><br>足裏の保湿や軽いストレッチを取り入れるのがおすすめです。")

    result_card("9. セルフケア", "<br><br>".join(care), "card-green", "compact-card")

    # -----------------------------------------------------
    # 免責
    # -----------------------------------------------------
    st.markdown(
        """
<div class="disclaimer">
このサービスは医療行為や医学的な診断を行うものではありません。
写真の色は照明やカメラによって変わることがあります。
足裏ポイントや性格傾向には、リフレクソロジーやエンタメとしての考え方が含まれます。
診断点数とレーダーチャートは質問と写真から算出した参考値です。
強い痛み、しびれ、傷、急な腫れ、大きな色の変化などがある場合は、必要に応じて医療機関へご相談ください。
</div>
""",
        unsafe_allow_html=True
    )

    if st.button("最初から診断する", use_container_width=True):
        if "analysis" in st.session_state:
            del st.session_state["analysis"]
        gc.collect()
        st.session_state.step = 1
        st.rerun()
