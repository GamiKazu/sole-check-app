import base64
import gc
import io
import math
import uuid
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageOps
from supabase import create_client


# =========================================================
# ページ設定
# =========================================================
st.set_page_config(
    page_title="足裏タイプ診断",
    layout="centered",
)

ASSET_DIR = Path("assets")


# =========================================================
# Supabase
# =========================================================
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SECRET_KEY"],
    )


if "step" not in st.session_state:
    st.session_state.step = 1

if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False

if "analysis" not in st.session_state:
    st.session_state.analysis = None


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
    padding-top: 0 !important;
    padding-bottom: 4rem;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

[data-testid="stHeader"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

.top-credit {
    width: 100%;
    text-align: left;
    font-size: 9px;
    color: #999999;
    opacity: 0.82;
    letter-spacing: 0.05em;
    margin-top: 5px;
    margin-bottom: 14px;
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


.header-banner-wrap {
    width: calc(100% + 64px);
    margin-left: -32px;
    margin-right: -32px;
    margin-top: 0.15rem;
margin-bottom: 0;
}

.header-banner {
    display: block;
    width: 100%;
    height: auto;
    border: 0;
    box-shadow: none;
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

.question-space { height: 6px; }
.question-space.tight { height: 2px; }
.fatigue-question-label {
    font-size: 0.875rem;
    font-weight: 400;
    color: #262730;
    margin-top: 2px;
    margin-bottom: 0.3rem;
    line-height: 1.25;
}
.st-key-fatigue_checkbox_group [data-testid="stCheckbox"] {
    margin-bottom: -10px;
}
.st-key-fatigue_checkbox_group [data-testid="stCheckbox"] label {
    padding-top: 0.05rem;
    padding-bottom: 0.05rem;
}
.st-key-fatigue_checkbox_group [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
    gap: 0.75rem !important;
    width: 100% !important;
}

.st-key-fatigue_checkbox_group [data-testid="column"] {
    width: 100% !important;
    min-width: 0 !important;
    max-width: none !important;
    flex: none !important;
}

.st-key-fatigue_checkbox_group [data-testid="stCheckbox"] {
    margin-bottom: -8px !important;
}

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

.personality-title {
    font-size: 1.03rem;
    font-weight: 800;
    color: #574D62;
    margin-bottom: 8px;
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

/* スコア */
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
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    white-space: nowrap;
}

.score-grade-badge {
    display: inline-block;
    flex-shrink: 0;
    margin-left: 8px;
    padding: 2px 9px;
    border-radius: 999px;
    background: rgba(83, 108, 91, 0.12);
    border: 1px solid rgba(83, 108, 91, 0.18);
    color: #536C5B;
    font-family: "Yu Gothic", sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
}

.score-message {
    font-family: "Yu Gothic", sans-serif;
    font-size: 13px;
    font-weight: 500;
    margin-top: 22px;
    opacity: 0.72;
}

.score-grade-guide {
    flex: 0 0 auto;
    min-width: 76px;
    font-family: "Yu Gothic", sans-serif;
    font-size: 0.52rem;
    font-weight: 400;
    color: #7F8A82;
    line-height: 1.52;
    text-align: left;
    white-space: nowrap;
    padding-top: 1px;
    transform: translateX(6px);
}

.score-grade-guide-title {
    font-weight: 700;
    margin-bottom: 2px;
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
        padding-top: 0 !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .top-credit {
        font-size: 8px;
        margin-top: 5px;
        margin-bottom: 14px;
    }

    .main-title { font-size: 2rem; }

    .english-title {
        font-size: 0.65rem;
        letter-spacing: 0.13em;
        margin-bottom: 1.9rem;
    }

.header-banner-wrap {
    width: calc(100% + 2rem);
    margin-left: -1rem;
    margin-right: -1rem;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    line-height: 0;
}

    .question-space { height: 4px; }
    .question-space.tight { height: 0px; }
    .fatigue-question-label {
        font-size: 0.875rem;
        font-weight: 400;
        line-height: 1.25;
        margin-bottom: 0.2rem;
    }
    .st-key-fatigue_checkbox_group [data-testid="stCheckbox"] {
        margin-bottom: -12px;
    }
    .st-key-fatigue_checkbox_group [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
        gap: 0.55rem !important;
        width: 100% !important;
    }

    .st-key-fatigue_checkbox_group [data-testid="column"] {
        width: 100% !important;
        min-width: 0 !important;
        max-width: none !important;
        flex: none !important;
    }

    .st-key-fatigue_checkbox_group [data-testid="stCheckbox"] {
        margin-bottom: -10px !important;
    }

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
        gap: 6px;
    }

    .score-result-title {
        font-size: 0.92rem;
        letter-spacing: -0.01em;
    }

    .score-grade-badge {
        margin-left: 6px;
        padding: 2px 6px;
        font-size: 0.65rem;
    }

    .score-message {
        font-size: 12px;
        margin-top: 20px;
    }

    .score-grade-guide {
        min-width: 68px;
        font-size: 0.46rem;
        transform: translateX(8px);
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
    unsafe_allow_html=True,
)



def header_file_to_data_uri(path):
    path = Path(path)
    if not path.exists():
        return None
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


# =========================================================
# HEADER
# =========================================================
banner_uri = header_file_to_data_uri(ASSET_DIR / "header_banner.png")

if banner_uri:
    st.markdown(
        f"""
<div class="header-banner-wrap">
    <img class="header-banner" src="{banner_uri}" alt="足裏タイプ診断">
</div>
<div class="top-credit">Created by GamiKazu</div>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# 共通UI
# =========================================================
def request_scroll_to_top():
    st.session_state.scroll_to_top = True


def run_scroll_to_top_if_needed():
    if not st.session_state.get("scroll_to_top", False):
        return

    st.session_state.scroll_to_top = False

    st.components.v1.html(
        """
<script>
(function () {
    function scrollTopNow() {
        try {
            const parentWindow = window.parent;
            const doc = parentWindow.document;

            parentWindow.scrollTo(0, 0);
            if (doc.documentElement) doc.documentElement.scrollTop = 0;
            if (doc.body) doc.body.scrollTop = 0;

            const candidates = [
                doc.querySelector('[data-testid="stAppViewContainer"]'),
                doc.querySelector('[data-testid="stMain"]'),
                doc.querySelector('section.main')
            ];

            candidates.forEach(function (el) {
                if (el) el.scrollTop = 0;
            });
        } catch (e) {
            window.parent.scrollTo(0, 0);
        }
    }

    scrollTopNow();
    setTimeout(scrollTopNow, 50);
    setTimeout(scrollTopNow, 200);
})();
</script>
        """,
        height=0,
        width=0,
    )


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
        unsafe_allow_html=True,
    )
# =========================================================
# Supabase保存
# =========================================================
def upload_image_to_supabase(uploaded_file, diagnosis_id, label):
    if uploaded_file is None:
        return None

    uploaded_file.seek(0)

    # 撮影画像を読み込み
    # EXIF情報を落とし、保存容量も抑える
    with Image.open(uploaded_file) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")

        # AI学習用として十分なサイズを残しつつ圧縮
        image.thumbnail(
            (1600, 1600),
            Image.Resampling.LANCZOS,
        )

        buffer = io.BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=90,
            optimize=True,
        )

    image_bytes = buffer.getvalue()

    storage_path = (
        f"{diagnosis_id}/{label}.jpg"
    )

    get_supabase().storage.from_(
        "foot-images"
    ).upload(
        path=storage_path,
        file=image_bytes,
        file_options={
            "content-type": "image/jpeg",
            "upsert": "false",
        },
    )

    return storage_path


def save_diagnosis_record(
    diagnosis_id,
    both_path,
    right_path,
    left_path,
    analysis,
    score,
    score_grade,
):
    data = {
        "id": diagnosis_id,

        "q1_cold": st.session_state.get("cold"),
        "q2_swelling": st.session_state.get("swelling"),
        "q3_tired": st.session_state.get("tired"),
        "q4_standing": st.session_state.get("standing"),
        "q5_shoes": st.session_state.get("shoes"),
        "q6_concern": st.session_state.get("foot_concern"),

        "q7_fatigue_area": st.session_state.get(
            "fatigue_area",
            [],
        ),

        "q8_sole_wear": st.session_state.get("sole_wear"),
        "q9_stumble": st.session_state.get("stumble"),
        "q10_aroma_goal": st.session_state.get("aroma_goal"),

        "both_image_path": both_path,
        "right_image_path": right_path,
        "left_image_path": left_path,

        "predicted_shape": analysis.get(
            "overall_shape"
        ),
        "predicted_color": analysis.get(
            "foot_color"
        ),
        "predicted_dryness": analysis.get(
            "dryness"
        ),
        "predicted_hard_part": analysis.get(
            "hard_part"
        ),

        "score": score,
        "grade": score_grade,
    }

    get_supabase().table(
        "diagnosis_records"
    ).insert(
        data
    ).execute()

def file_to_data_uri(path):
    path = Path(path)
    if not path.exists():
        return None

    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
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
                f"</div>"
            )

    st.markdown(
        f"""
<div class="result-card {card_class} {extra_class}">
{image_html}
{body}
</div>
""",
        unsafe_allow_html=True,
    )


def result_card_with_image(
    title,
    result_name,
    description,
    card_class,
    image_path=None,
    image_alt="",
    image_class="foot-image",
    extra_html="",
):
    st.markdown(f"### {title}")

    image_html = ""
    if image_path:
        uri = file_to_data_uri(image_path)
        if uri:
            image_html = (
                f'<div class="result-image-wrap">'
                f'<img class="result-image {image_class}" src="{uri}" alt="{image_alt}">'
                f"</div>"
            )

    st.markdown(
        f"""
<div class="result-card {card_class}">
<div class="result-main visual-result-name">{result_name}</div>
{image_html}
<div class="visual-description">{description}</div>
{extra_html}
</div>
""",
        unsafe_allow_html=True,
    )


def clamp(value, low=0, high=100):
    return max(low, min(high, int(round(value))))


def radar_svg(values):
    labels = list(values.keys())
    scores = [clamp(values[k]) for k in labels]

    cx, cy = 210, 175
    max_r = 108
    angles = [-90, -30, 30, 90, 150, 210]

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
        axes.append(
            f'<line class="radar-axis" x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>'
        )

    data_coords = [
        pt(a, max_r * s / 100.0)
        for a, s in zip(angles, scores)
    ]
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
            f'<text class="radar-value" x="{x}" y="{y + 15}" text-anchor="{anchor}">{score}</text>'
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
        return np.asarray(image, dtype=np.uint8).copy()


def largest_contour(mask):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return None
    return max(contours, key=cv2.contourArea)


def clean_mask(binary):
    kernel = np.ones((5, 5), np.uint8)
    binary = cv2.morphologyEx(
        binary, cv2.MORPH_CLOSE, kernel, iterations=2
    )
    binary = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, kernel, iterations=1
    )

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

    corners = np.concatenate(
        [
            rgb[:patch_h, :patch_w].reshape(-1, 3),
            rgb[:patch_h, -patch_w:].reshape(-1, 3),
            rgb[-patch_h:, :patch_w].reshape(-1, 3),
            rgb[-patch_h:, -patch_w:].reshape(-1, 3),
        ],
        axis=0,
    )

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

    cos_v = abs(matrix[0, 0])
    sin_v = abs(matrix[0, 1])
    new_w = int(h * sin_v + w * cos_v)
    new_h = int(h * cos_v + w * sin_v)

    matrix[0, 2] += new_w / 2 - center[0]
    matrix[1, 2] += new_h / 2 - center[1]

    return cv2.warpAffine(
        image,
        matrix,
        (new_w, new_h),
        flags=interpolation,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value,
    )


def straighten_foot(rgb, mask):
    contour = largest_contour(mask)
    if contour is None:
        return rgb, mask

    try:
        _, size, angle = cv2.minAreaRect(contour)
        rw, rh = size
        rotation = angle if rw > rh else angle - 90

        rgb = rotate_bound(
            rgb, rotation, cv2.INTER_LINEAR, (255, 255, 255)
        )
        mask = rotate_bound(
            mask, rotation, cv2.INTER_NEAREST, 0
        )
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

    curve[missing] = np.interp(
        np.where(missing)[0],
        known,
        curve[known],
    )
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

    spread = (
        max(big, second, third) - min(big, second, third)
    ) / foot_length

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
    rgb_f = rgb.astype(np.float32)

    valid = mask > 0
    brightness = hsv[:, :, 2]

    valid &= brightness > 42
    valid &= brightness < 250

    if valid.sum() < 100:
        valid = mask > 0

    H = float(np.median(hsv[:, :, 0][valid]))
    S = float(np.median(hsv[:, :, 1][valid]))
    V = float(np.median(hsv[:, :, 2][valid]))
    A = float(np.median(lab[:, :, 1][valid]))
    B = float(np.median(lab[:, :, 2][valid]))

    R = float(np.median(rgb_f[:, :, 0][valid]))
    G = float(np.median(rgb_f[:, :, 1][valid]))
    Bl = float(np.median(rgb_f[:, :, 2][valid]))

    red_bias = R - (G + Bl) / 2.0
    yellow_bias = (R + G) / 2.0 - Bl
    blue_bias = Bl - (R + G) / 2.0

    if V >= 198 and S <= 42 and A <= 136:
        result = "白っぽい"
    elif blue_bias >= 3 and A >= 132 and B <= 132:
        result = "紫っぽい"
    elif ((H <= 6 or H >= 174) and S >= 48 and A >= 137) or red_bias >= 24:
        result = "赤み強め"
    elif (5 < H <= 18 and S >= 35) or (
        red_bias >= 10 and yellow_bias >= 14
    ):
        result = "オレンジ寄り"
    elif (17 < H <= 34 and S >= 34 and B >= 134) or yellow_bias >= 24:
        result = "黄み強め"
    elif A >= 132 and A <= 143 and S >= 22 and red_bias >= 5:
        result = "ピンク寄り"
    else:
        result = "標準的な色味"

    return result, {
        "H": H,
        "S": S,
        "V": V,
        "A": A,
        "B": B,
        "R": R,
        "G": G,
        "Blue": Bl,
        "red_bias": red_bias,
        "yellow_bias": yellow_bias,
        "blue_bias": blue_bias,
    }


def analyze_texture(rgb, mask):
    if mask is None:
        return "判定困難", "判定困難"

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_32F)
    texture = np.abs(lap)[mask > 0]
    texture_score = (
        float(np.percentile(texture, 75))
        if texture.size > 0
        else 0
    )

    if texture_score > 28:
        dryness = "乾燥が目立つ"
    elif texture_score > 18:
        dryness = "やや乾燥"
    else:
        dryness = "乾燥は目立たない"

    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    candidates = (
        (mask > 0)
        & (lab[:, :, 0] > 145)
        & (lab[:, :, 2] > 138)
    )

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

    left = rgb[:, : min(w, center + overlap)].copy()
    right = rgb[:, max(0, center - overlap):].copy()

    return left, right


def unify_shapes(shape_results):
    valid = [
        (shape, conf)
        for shape, conf in shape_results
        if shape != "判定困難"
    ]

    if not valid:
        return "判定困難", 0.0

    score_map = {}
    for shape, conf in valid:
        score_map[shape] = score_map.get(shape, 0.0) + conf

    best = max(score_map, key=score_map.get)
    total = sum(score_map.values())
    confidence = score_map[best] / total if total else 0.0
    return best, confidence


def analyze_images(both_rgb=None, right_rgb=None, left_rgb=None):
    shape_results = []
    representative_rgb = None
    representative_mask = None

    candidates = []

    if both_rgb is not None:
        left_part, right_part = split_both(both_rgb)

        left_mask = segment_foot(left_part)
        right_mask = segment_foot(right_part)

        if left_mask is not None:
            shape_results.append(
                classify_foot_shape(
                    left_part,
                    left_mask,
                    big_toe_side="right",
                )
            )
            candidates.append(
                (int(np.sum(left_mask > 0)), left_part, left_mask)
            )

        if right_mask is not None:
            shape_results.append(
                classify_foot_shape(
                    right_part,
                    right_mask,
                    big_toe_side="left",
                )
            )
            candidates.append(
                (int(np.sum(right_mask > 0)), right_part, right_mask)
            )

    if right_rgb is not None:
        right_mask = segment_foot(right_rgb)
        if right_mask is not None:
            shape_results.append(
                classify_foot_shape(
                    right_rgb,
                    right_mask,
                    big_toe_side="left",
                )
            )
            candidates.append(
                (int(np.sum(right_mask > 0)), right_rgb, right_mask)
            )

    if left_rgb is not None:
        left_mask = segment_foot(left_rgb)
        if left_mask is not None:
            shape_results.append(
                classify_foot_shape(
                    left_rgb,
                    left_mask,
                    big_toe_side="right",
                )
            )
            candidates.append(
                (int(np.sum(left_mask > 0)), left_rgb, left_mask)
            )

    if candidates:
        _, representative_rgb, representative_mask = max(
            candidates,
            key=lambda x: x[0],
        )

    overall_shape, shape_conf = unify_shapes(shape_results)

    if representative_rgb is None or representative_mask is None:
        foot_color = "判定困難"
        color_info = {}
        dryness = "判定困難"
        hard_part = "判定困難"
    else:
        foot_color, color_info = analyze_color(
            representative_rgb,
            representative_mask,
        )
        dryness, hard_part = analyze_texture(
            representative_rgb,
            representative_mask,
        )

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
# 結果用データ
# =========================================================
COLOR_TEXT = {
    "白っぽい": (
        "足裏が白っぽく見える時は、冷えや血行の低下、疲れがたまっている時に見られることがあります。"
        "<br><br>足先を温めたり、足首をゆっくり回したりして、めぐりを意識したセルフケアがおすすめです。"
    ),
    "ピンク寄り": (
        "やわらかなピンク色は、比較的バランスの取りやすい色味です。"
        "<br><br>今の状態を保てるよう、保湿や軽いストレッチを続けてみてください。"
    ),
    "赤み強め": (
        "足裏が赤く見える時は、熱がこもっている時や、活動量が多かった時に見られることがあります。"
        "<br><br>イライラや緊張が続いている時にも赤みが強く感じられることがあります。"
        "<br><br>足を休ませ、深呼吸やぬるめの入浴でゆっくりクールダウンしてみてください。"
    ),
    "オレンジ寄り": (
        "オレンジ寄りの色味は、疲れや緊張が続いている時、体が少し頑張りすぎている時に見られることがあります。"
        "<br><br>足裏を軽くほぐし、水分補給と休息を意識してみてください。"
    ),
    "黄み強め": (
        "足裏が黄色っぽく見える時は、疲れやストレスが続いている時、食生活が乱れている時などに見られることがあります。"
        "<br><br>食事の時間を整え、睡眠や休息をしっかり取ることを意識してみてください。"
    ),
    "紫っぽい": (
        "足裏が紫っぽく見える時は、冷えやめぐりの低下がある時に見られることがあります。"
        "<br><br>足先を冷やさないようにし、ふくらはぎや足首をゆっくり動かしてみてください。"
    ),
    "標準的な色味": (
        "今回の写真では、極端な赤み・黄み・青紫などは強く出ていませんでした。"
        "<br><br>写真の光や室内照明でも色は変わるため、今の色味は目安として見てください。"
    ),
    "判定困難": (
        "今回の写真では色味を安定して判定できませんでした。"
        "<br><br>自然光に近い明るさで、影や色付き照明を避けて撮ると判定しやすくなります。"
    ),
}


PERSONALITY_MAP = {
    ("エジプト型", "活動的"): (
        "好奇心旺盛な行動派",
        "新しいことへの興味が強く、思い立ったらまず動いてみるタイプ。自由さを大切にしながら、自分のペースで進める傾向があります。",
    ),
    ("エジプト型", "穏やか"): (
        "マイペースな癒やし系",
        "感覚を大切にし、落ち着いた空気を好むタイプ。周囲に合わせすぎず、自分らしいペースを保ちやすい傾向があります。",
    ),
    ("エジプト型", "慎重"): (
        "繊細なこだわり派",
        "細かな変化に気づきやすく、自分なりの基準を大切にするタイプ。納得してから動く慎重さがあります。",
    ),
    ("ギリシャ型", "活動的"): (
        "エネルギッシュな挑戦者",
        "行動力があり、目標が見えると一気に進めるタイプ。周囲を引っ張る役割にもなりやすい傾向があります。",
    ),
    ("ギリシャ型", "穏やか"): (
        "明るいバランス型",
        "活発さと落ち着きの両方を持ち、場面に合わせて切り替えられるタイプ。人との関わりも自然に楽しめる傾向があります。",
    ),
    ("ギリシャ型", "慎重"): (
        "計画的な努力家",
        "目標意識は高い一方、準備もしっかりしたいタイプ。自分の中で筋道を立ててから動く傾向があります。",
    ),
    ("スクエア型", "活動的"): (
        "頼れる実行タイプ",
        "現実的に考えながら着実に動けるタイプ。周囲から頼られると力を発揮しやすい傾向があります。",
    ),
    ("スクエア型", "穏やか"): (
        "安定感のある調整役",
        "落ち着きがあり、周囲とのバランスを取りながら進めるタイプ。堅実で安心感を与えやすい傾向があります。",
    ),
    ("スクエア型", "慎重"): (
        "堅実な分析タイプ",
        "情報を整理してから判断したいタイプ。急がず確実に進めることを好み、ミスを減らす工夫が得意な傾向があります。",
    ),
}


AROMA_MAP = {
    "リラックス": (
        "ラベンダー",
        "やさしく落ち着いたフローラル系の香りです。",
        "気持ちをゆるめたい時、ゆっくり過ごしたい時、就寝前のリラックスタイムに取り入れやすい香りです。",
        "aroma_lavender.png",
    ),
    "リフレッシュ": (
        "ペパーミント",
        "すっきりとした清涼感のある香りです。",
        "気分を切り替えたい時や、頭をすっきりさせたい時に取り入れやすい香りです。",
        "aroma_peppermint.png",
    ),
    "集中": (
        "ローズマリー",
        "すっきりとしたハーブ系の香りです。",
        "勉強や仕事など、気持ちを切り替えて集中したい時に向いています。",
        "aroma_rosemary.png",
    ),
    "睡眠": (
        "ベルガモット",
        "やわらかな柑橘系で、少し甘さを感じる香りです。",
        "夜に気持ちを落ち着けたい時や、ゆっくり休む準備をしたい時に取り入れやすい香りです。",
        "aroma_bergamot.png",
    ),
    "気分転換": (
        "オレンジ・スイート",
        "明るく親しみやすい甘めの柑橘系の香りです。",
        "気持ちを切り替えたい時や、前向きな気分になりたい時に取り入れやすい香りです。",
        "aroma_orange.png",
    ),
}


REFLEX_MAP = {
    "頭・目": "親指まわり",
    "首": "親指の付け根〜足指の付け根",
    "肩": "足指の付け根まわり",
    "首・肩": "親指の付け根〜足指の付け根",
    "背中": "足裏の内側",
    "腰": "土踏まずの内側〜かかと寄り",
    "胃まわり": "土踏まずの上側",
    "脚": "かかとまわり",
    "全身": "足裏全体",
}


# =========================================================
# 画面遷移後のスクロール
# =========================================================
run_scroll_to_top_if_needed()


# =========================================================
# STEP1
# =========================================================
if st.session_state.step == 1:
    st.markdown(
        '<div class="step-box">STEP 1　簡単な質問</div>',
        unsafe_allow_html=True,
    )

    cold = st.radio(
        "Q1. 足が冷えやすいですか？",
        ["はい", "いいえ"],
        horizontal=True,
        key="q1_cold",
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    swelling = st.radio(
        "Q2. むくみを感じることがありますか？",
        ["はい", "いいえ"],
        horizontal=True,
        key="q2_swelling",
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    tired = st.radio(
        "Q3. 長時間歩いたり立ったりすると、足が疲れやすいですか？",
        ["はい", "いいえ"],
        horizontal=True,
        key="q3_tired",
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    standing = st.radio(
        "Q4. 普段、立っている時間は長いですか？",
        ["はい", "いいえ"],
        horizontal=True,
        key="q4_standing",
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    shoes = st.selectbox(
        "Q5. 普段よく履く靴は？",
        ["スニーカー", "革靴", "パンプス", "サンダル", "ブーツ", "その他"],
        key="q5_shoes",
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    foot_concern = st.selectbox(
        "Q6. 足で一番気になることは？",
        [
            "特にない",
            "疲れやすい",
            "冷え",
            "むくみ",
            "乾燥",
            "硬くなった部分",
            "靴が合いにくい",
            "歩き方が気になる",
        ],
        key="q6_concern",
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="fatigue-question-label">Q7. 今、疲れを感じる場所はありますか？</div>',
        unsafe_allow_html=True,
    )

    with st.container(key="fatigue_checkbox_group"):
        c1, c2 = st.columns(2, gap="small")
        with c1:
            q7_head_eye = st.checkbox("頭・目", key="q7_head_eye")
        with c2:
            q7_neck = st.checkbox("首", key="q7_neck")

        c3, c4 = st.columns(2, gap="small")
        with c3:
            q7_shoulder = st.checkbox("肩", key="q7_shoulder")
        with c4:
            q7_back = st.checkbox("背中", key="q7_back")

        c5, c6 = st.columns(2, gap="small")
        with c5:
            q7_waist = st.checkbox("腰", key="q7_waist")
        with c6:
            q7_stomach = st.checkbox("胃まわり", key="q7_stomach")

        c7, c8 = st.columns(2, gap="small")
        with c7:
            q7_leg = st.checkbox("脚", key="q7_leg")
        with c8:
            q7_whole = st.checkbox("全身", key="q7_whole")

    fatigue_area = []
    if q7_head_eye:
        fatigue_area.append("頭・目")
    if q7_neck:
        fatigue_area.append("首")
    if q7_shoulder:
        fatigue_area.append("肩")
    if q7_back:
        fatigue_area.append("背中")
    if q7_waist:
        fatigue_area.append("腰")
    if q7_stomach:
        fatigue_area.append("胃まわり")
    if q7_leg:
        fatigue_area.append("脚")
    if q7_whole:
        fatigue_area.append("全身")

    st.markdown('<div class="question-space tight"></div>', unsafe_allow_html=True)

    sole_wear = st.selectbox(
        "Q8. 靴底はどこが減りやすいですか？",
        [
            "特に偏りはない",
            "かかとの外側",
            "かかとの内側",
            "つま先側",
            "左右で差がある",
            "分からない",
        ],
        key="q8_sole_wear",
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    stumble = st.radio(
        "Q9. 歩いている時につまずきやすいですか？",
        ["はい", "いいえ"],
        horizontal=True,
        key="q9_stumble",
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    aroma_goal = st.selectbox(
        "Q10. 今、一番求めているものは？",
        ["リラックス", "リフレッシュ", "集中", "睡眠", "気分転換"],
        key="q10_aroma_goal",
    )
    st.markdown('<div class="question-space"></div>', unsafe_allow_html=True)

    if st.button(
        "次へ",
        type="primary",
        use_container_width=True,
    ):
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
        request_scroll_to_top()
        st.rerun()


# =========================================================
# STEP2
# =========================================================
elif st.session_state.step == 2:
    st.markdown(
        '<div class="step-box">STEP 2　足裏写真</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="guide-card">
1枚でも診断できます。下のいずれか1枚以上をアップロードしてください。
<div class="guide-list">・両足<br>・右足<br>・左足</div>
<span class="guide-note">※両足・右足・左足の写真がそろうと、より判定しやすくなります。</span>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="guide-card">
<b>両足の撮り方</b><br>
床に座って両ひざを軽く曲げ、両足をそろえて足裏を正面に向けます。<br>
スマホを足元の前に立てかけ、つま先からかかとまで両足の足裏全体が入るように撮影してください。
<br><br>

<b>片足の撮り方</b><br>
片足を伸ばして座り、撮影する足を反対側の太ももの上に軽くのせます。<br>
足裏をカメラに向け、つま先からかかとまで足裏全体が入るようにスマホを横向きで撮影してください。
</div>
""",
        unsafe_allow_html=True,
    )
    both_feet = st.file_uploader(
        "両足の写真",
        type=["jpg", "jpeg", "png"],
        key="both_feet",
    )
    show_upload_status(both_feet)

    right_foot = st.file_uploader(
        "右足の写真",
        type=["jpg", "jpeg", "png"],
        key="right_foot",
    )
    show_upload_status(right_foot)

    left_foot = st.file_uploader(
        "左足の写真",
        type=["jpg", "jpeg", "png"],
        key="left_foot",
    )
    show_upload_status(left_foot)

    st.markdown(
        """
<div class="photo-note">
※足指からかかとまで画面に入れ、できるだけ真正面から撮影してください。足指同士が重ならない写真がおすすめです。背景はできるだけ無地にしてください。
</div>
""",
        unsafe_allow_html=True,
    )

    has_photo = (
        both_feet is not None
        or right_foot is not None
        or left_foot is not None
    )

    with st.container(key="action_buttons"):
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "戻る",
                use_container_width=True,
            ):
                st.session_state.step = 1
                request_scroll_to_top()
                st.rerun()

        with col2:
            diagnose = st.button(
                "診断する",
                type="primary",
                disabled=not has_photo,
                use_container_width=True,
            )

    if diagnose:
        progress = st.progress(0)
        status = st.empty()

        try:
            status.write("写真を読み込んでいます...")

            both_rgb = (
                uploaded_to_rgb(both_feet)
                if both_feet is not None
                else None
            )
            progress.progress(25)

            right_rgb = (
                uploaded_to_rgb(right_foot)
                if right_foot is not None
                else None
            )
            progress.progress(40)

            left_rgb = (
                uploaded_to_rgb(left_foot)
                if left_foot is not None
                else None
            )
            progress.progress(55)

            status.write("足裏を確認しています...")

            analysis = analyze_images(
                both_rgb=both_rgb,
                right_rgb=right_rgb,
                left_rgb=left_rgb,
            )

            progress.progress(90)
            st.session_state.analysis = analysis

            del both_rgb
            del right_rgb
            del left_rgb
            gc.collect()

            progress.progress(100)
            st.session_state.step = 3
            request_scroll_to_top()
            st.rerun()

        except Exception as error:
            gc.collect()
            st.error(
                "写真をうまく解析できませんでした。別の写真でお試しください。"
            )
            st.caption(str(error))


# =========================================================
# STEP3
# =========================================================
elif st.session_state.step == 3:
    analysis = st.session_state.analysis or {}

    cold = st.session_state.get("cold", "いいえ")
    swelling = st.session_state.get("swelling", "いいえ")
    tired = st.session_state.get("tired", "いいえ")
    standing = st.session_state.get("standing", "いいえ")
    shoes = st.session_state.get("shoes", "スニーカー")
    foot_concern = st.session_state.get("foot_concern", "特にない")
    fatigue_area = st.session_state.get("fatigue_area", [])
    sole_wear = st.session_state.get("sole_wear", "特に偏りはない")
    stumble = st.session_state.get("stumble", "いいえ")
    aroma_goal = st.session_state.get("aroma_goal", "リラックス")

    shape = analysis.get("overall_shape", "判定困難")
    foot_color = analysis.get("foot_color", "判定困難")
    dryness = analysis.get("dryness", "判定困難")
    hard_part = analysis.get("hard_part", "判定困難")

    # -----------------------------------------------------
    # 6つのコンディション
    # 100ほど良好になるよう統一
    # -----------------------------------------------------
    circulation = 92
    if cold == "はい":
        circulation -= 24
    if foot_color in ["白っぽい", "紫っぽい"]:
        circulation -= 18
    elif foot_color == "赤み強め":
        circulation -= 8

    lightness = 92
    if swelling == "はい":
        lightness -= 28
    if standing == "はい":
        lightness -= 10
    if foot_concern == "むくみ":
        lightness -= 16

    foot_energy = 94
    if tired == "はい":
        foot_energy -= 28
    if standing == "はい":
        foot_energy -= 10
    if "脚" in fatigue_area or "全身" in fatigue_area:
        foot_energy -= 12

    walkability = 94
    if stumble == "はい":
        walkability -= 25
    if sole_wear in ["かかとの外側", "かかとの内側", "つま先側", "左右で差がある"]:
        walkability -= 12
    if foot_concern in ["靴が合いにくい", "歩き方が気になる"]:
        walkability -= 12

    sole_condition = 94
    if dryness == "やや乾燥":
        sole_condition -= 14
    elif dryness == "乾燥が目立つ":
        sole_condition -= 28

    if hard_part not in ["なし", "判定困難"]:
        sole_condition -= 12

    if foot_concern == "乾燥":
        sole_condition -= 12
    elif foot_concern == "硬くなった部分":
        sole_condition -= 14

    rest_state = 94
    if fatigue_area:
        rest_state -= min(28, len(fatigue_area) * 6)
    if tired == "はい":
        rest_state -= 12
    if standing == "はい":
        rest_state -= 8
    if aroma_goal == "睡眠":
        rest_state -= 8

    radar_values = {
        "めぐり": clamp(circulation, 35, 100),
        "すっきり感": clamp(lightness, 35, 100),
        "足の元気": clamp(foot_energy, 35, 100),
        "歩きやすさ": clamp(walkability, 35, 100),
        "足裏状態": clamp(sole_condition, 35, 100),
        "休息バランス": clamp(rest_state, 35, 100),
    }

    score = round(
        radar_values["めぐり"] * 0.15
        + radar_values["すっきり感"] * 0.15
        + radar_values["足の元気"] * 0.20
        + radar_values["歩きやすさ"] * 0.15
        + radar_values["足裏状態"] * 0.20
        + radar_values["休息バランス"] * 0.15
    )
    score = clamp(score)

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
# -----------------------------------------------------
    # Supabaseへ自動保存
    # -----------------------------------------------------
    if not st.session_state.get(
        "saved_to_db",
        False,
    ):
        try:
            diagnosis_id = str(uuid.uuid4())

            # ---------------------------------------------
            # 画像保存
            # ---------------------------------------------
            both_path = upload_image_to_supabase(
                st.session_state.get("both_feet"),
                diagnosis_id,
                "both",
            )

            right_path = upload_image_to_supabase(
                st.session_state.get("right_foot"),
                diagnosis_id,
                "right",
            )

            left_path = upload_image_to_supabase(
                st.session_state.get("left_foot"),
                diagnosis_id,
                "left",
            )

            # ---------------------------------------------
            # 回答＋診断結果を保存
            # ---------------------------------------------
            save_diagnosis_record(
                diagnosis_id=diagnosis_id,
                both_path=both_path,
                right_path=right_path,
                left_path=left_path,
                analysis=analysis,
                score=score,
                score_grade=score_grade,
            )

            # Streamlitの再実行で
            # 同じ診断が二重保存されないようにする
            st.session_state.saved_to_db = True

        except Exception as save_error:
            st.session_state.data_save_error = str(
                save_error
            )
    st.markdown(
        f"""
<div class="step-box">
<div class="score-result-row">
  <div class="score-result-main">
    <div class="score-result-title">
      診断結果：{score}点
      <span class="score-grade-badge">評価 {score_grade}</span>
    </div>
    <div class="score-message">{score_message}</div>
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
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        radar_svg(radar_values),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="small-note" style="margin-top:-10px; margin-bottom:22px; line-height:1.65;">
<b>6項目の見方</b><br>
・めぐり：冷えにくく、足先までめぐりが保たれているほど高得点<br>
・すっきり感：むくみや重だるさが少ないほど高得点<br>
・足の元気：立つ・歩くことで疲れにくいほど高得点<br>
・歩きやすさ：つまずきや靴底の偏りが少ないほど高得点<br>
・足裏状態：乾燥や硬くなった部分が少ないほど高得点<br>
・休息バランス：疲れがたまりにくく、休息が取れているほど高得点
</div>
""",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # 1. 足の形
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
        image_class="foot-image",
    )

    # -----------------------------------------------------
    # 2. 足の色
    # -----------------------------------------------------
    original_color_text = {
        "白っぽい": (
            "写真では少し白っぽく見えます。冷えや疲れが続いている時に見られることがあります。"
            "照明やカメラでも色は変わるため、参考として見てください。"
        ),
        "ピンク寄り": (
            "写真では比較的やわらかなピンク色に見えます。"
            "照明やカメラでも色は変わるため、参考として見てください。"
        ),
        "赤み強め": (
            "写真では赤みが強めに見えます。活動量が多かった時や、足に熱がこもった時に見られることがあります。"
            "照明やカメラでも色は変わるため、参考として見てください。"
        ),
        "オレンジ寄り": (
            "写真では少しオレンジ寄りに見えます。"
            "照明やカメラでも色は変わるため、参考として見てください。"
        ),
        "黄み強め": (
            "写真では少し黄みが強く見えます。"
            "照明やカメラでも色は変わるため、参考として見てください。"
        ),
        "紫っぽい": (
            "写真では少し紫っぽく見えます。冷えやめぐりが落ちている時に見られることがあります。"
            "照明やカメラでも色は変わるため、参考として見てください。"
        ),
        "標準的な色味": (
            "写真では標準的な色味に見えます。"
            "照明やカメラでも色は変わるため、参考として見てください。"
        ),
        "判定困難": (
            "今回の写真では色味を安定して判定できませんでした。"
            "照明やカメラでも色は変わるため、参考として見てください。"
        ),
    }

    result_card(
        "2. 足の色",
        f"""
<div class="result-main">{foot_color}</div>
<br>
{original_color_text.get(foot_color, original_color_text["判定困難"])}
""",
        "card-orange",
    )

    # -----------------------------------------------------
    # 3. 今の心と体の傾向
    # -----------------------------------------------------
    body_tendency_parts = []

    if tired == "はい" or standing == "はい":
        body_tendency_parts.append(
            "少し疲れがたまっている可能性があります。短い休憩や気分転換を取り入れるのがおすすめです。"
        )
    else:
        body_tendency_parts.append(
            "今は大きな疲れは出ていないようです。今のペースを保ちながら、こまめな休息も意識してみましょう。"
        )

    if cold == "はい":
        body_tendency_parts.append(
            "冷えが気になる時は、足元を温めたり軽く動かしたりしてみましょう。"
        )

    if swelling == "はい":
        body_tendency_parts.append(
            "むくみが気になる時は、足首を回したり、ふくらはぎを軽く動かすのがおすすめです。"
        )

    result_card(
        "3. 今の心と体の傾向",
        "<br><br>".join(body_tendency_parts),
        "card-green",
    )

    # -----------------------------------------------------
    # 4. 歩き方の傾向
    # -----------------------------------------------------
    walk_parts = []

    if stumble == "はい":
        walk_parts.append(
            "つまずきやすい場合は、歩く時に足先を少し上げることも意識してみましょう。"
        )
    else:
        walk_parts.append(
            "今回の回答では、つまずきやすさは強く出ていません。今の歩き方を基本に、足元への負担が偏らないよう意識してみましょう。"
        )

    if sole_wear == "かかとの外側":
        walk_parts.append(
            "かかとの外側が減りやすい場合は、外側に体重がかかりやすい傾向が考えられます。"
        )
    elif sole_wear == "かかとの内側":
        walk_parts.append(
            "かかとの内側が減りやすい場合は、内側に体重がかかりやすい傾向が考えられます。"
        )
    elif sole_wear == "つま先側":
        walk_parts.append(
            "つま先側が減りやすい場合は、前側に負担がかかりやすい可能性があります。"
        )
    elif sole_wear == "左右で差がある":
        walk_parts.append(
            "左右で靴底の減り方に差がある場合は、立ち方や歩き方に左右差が出ている可能性があります。"
        )

    result_card(
        "4. 歩き方の傾向",
        "<br><br>".join(walk_parts),
        "card-sage",
    )

    # -----------------------------------------------------
    # 5. おすすめの靴
    # -----------------------------------------------------
    if shape == "エジプト型":
        shoe_title = "親指側に余裕のある靴"
        shoe_text = (
            "親指が当たりにくく、つま先全体に適度な余裕がある靴がおすすめです。"
        )
    elif shape == "ギリシャ型":
        shoe_title = "人差し指の先に余裕がある靴"
        shoe_text = (
            "人差し指が前に当たりにくいよう、つま先に十分な長さがある靴がおすすめです。"
        )
    elif shape == "スクエア型":
        shoe_title = "つま先が広めの靴"
        shoe_text = (
            "親指・人差し指・中指の長さが近い足型です。指先が窮屈になりにくい、つま先が広めの靴がおすすめです。"
        )
    else:
        shoe_title = "つま先に無理のない靴"
        shoe_text = (
            "足指が圧迫されず、歩いた時にかかとが浮きにくい靴を選んでみてください。"
        )

    if tired == "はい":
        shoe_text += "<br><br>足が疲れやすい場合は、靴底のやわらかさも確認してみましょう。"

    result_card_with_image(
        "5. おすすめの靴",
        shoe_title,
        shoe_text,
        "card-cream",
        image_path=shoe_image,
        image_alt=f"{shape}に合いやすい靴の参考イラスト",
        image_class="shoe-image",
    )

    # -----------------------------------------------------
    # 6. 足の形から見る性格傾向
    # -----------------------------------------------------
    personality_scores = {"活動的": 0, "穏やか": 0, "慎重": 0}

    if tired == "はい":
        personality_scores["慎重"] += 2
        personality_scores["穏やか"] += 1
    else:
        personality_scores["活動的"] += 2

    if standing == "はい":
        personality_scores["活動的"] += 2
    else:
        personality_scores["穏やか"] += 1
        personality_scores["慎重"] += 1

    if foot_concern in ["疲れやすい", "冷え", "むくみ", "乾燥"]:
        personality_scores["慎重"] += 2
    elif foot_concern in ["靴が合いにくい", "歩き方が気になる"]:
        personality_scores["慎重"] += 1
        personality_scores["活動的"] += 1
    else:
        personality_scores["穏やか"] += 2

    if stumble == "はい":
        personality_scores["慎重"] += 1
    else:
        personality_scores["活動的"] += 1

    if aroma_goal in ["リフレッシュ", "集中", "気分転換"]:
        personality_scores["活動的"] += 2
    else:
        personality_scores["穏やか"] += 2

    personality_axis = max(
        ["穏やか", "活動的", "慎重"],
        key=lambda key: (
            personality_scores[key],
            {"穏やか": 3, "活動的": 2, "慎重": 1}[key],
        ),
    )

    personality_shape = (
        shape if shape in ["エジプト型", "ギリシャ型", "スクエア型"]
        else "スクエア型"
    )
    personality_title, personality_text = PERSONALITY_MAP[
        (personality_shape, personality_axis)
    ]

    result_card(
        "6. 足の形から見る性格傾向",
        f"""
<div class="personality-title">{personality_title}</div>
{personality_text}
""",
        "card-lavender",
        "compact-card",
    )

    # -----------------------------------------------------
    # 7. 疲れた場所・足裏ポイント
    # -----------------------------------------------------
    if fatigue_area:
        blocks = []
        for area in fatigue_area:
            point = REFLEX_MAP.get(area, "足裏全体")
            blocks.append(
                f"<span class='care-title'>{area}</span><br>"
                f"足裏のおすすめポイント：{point}"
            )

        reflex_text = (
            "<br><br>".join(blocks)
            + "<br><br><span class='small-note'>"
            "心地よい強さで5〜10秒ほどゆっくり押してみてください。"
            "</span>"
        )
    else:
        reflex_text = (
            "今回は特に疲れている場所が選択されていません。"
            "<br><br>足裏全体を気持ちいい程度の強さでゆっくりほぐしてみましょう。"
        )

    result_card(
        "7. 疲れた場所・足裏ポイント",
        reflex_text,
        "card-rose",
    )

    # -----------------------------------------------------
    # 8. おすすめアロマ
    # -----------------------------------------------------
    aroma_name, aroma_feature, aroma_when, aroma_file = AROMA_MAP[aroma_goal]
    aroma_image = ASSET_DIR / aroma_file

    # Original screen used a shorter explanation.
    aroma_short = {
        "リラックス": "ゆっくり過ごしたい時や、落ち着きたい時に取り入れやすい香りです。",
        "リフレッシュ": "気分を切り替えたい時や、すっきりしたい時に取り入れやすい香りです。",
        "集中": "勉強や仕事など、集中したい時に取り入れやすい香りです。",
        "睡眠": "夜に気持ちを落ち着けたい時や、休む準備をしたい時に取り入れやすい香りです。",
        "気分転換": "気持ちを切り替えたい時や、前向きな気分になりたい時に取り入れやすい香りです。",
    }

    result_card_with_image(
        "8. おすすめアロマ",
        aroma_name,
        aroma_short.get(aroma_goal, aroma_when),
        "card-aroma",
        image_path=aroma_image,
        image_alt=f"{aroma_name}の参考イラスト",
        image_class="aroma-image",
    )

    # -----------------------------------------------------
    # 9. セルフケア
    # -----------------------------------------------------
    care_blocks = []

    if swelling == "はい" or foot_concern == "むくみ":
        care_blocks.append(
            "<span class='care-title'>むくみが気になる時</span><br>"
            "足首をゆっくり回したり、ふくらはぎを軽く動かしてみましょう。"
        )

    if cold == "はい" or foot_concern == "冷え":
        care_blocks.append(
            "<span class='care-title'>冷えが気になる時</span><br>"
            "足湯や靴下などで、足元を心地よく温めるのがおすすめです。"
        )

    if tired == "はい" or foot_concern == "疲れやすい":
        care_blocks.append(
            "<span class='care-title'>足が疲れている時</span><br>"
            "足を休ませる時間をつくり、軽いストレッチをしてみましょう。"
        )

    if stumble == "はい":
        care_blocks.append(
            "<span class='care-title'>つまずきやすい時</span><br>"
            "足首を軽く動かし、歩く時に足先を少し上げることを意識してみましょう。"
        )

    if dryness in ["やや乾燥", "乾燥が目立つ"] or foot_concern == "乾燥":
        care_blocks.append(
            "<span class='care-title'>乾燥が気になる時</span><br>"
            "入浴後などに足裏をやさしく保湿してみましょう。"
        )

    if not care_blocks:
        care_blocks.append(
            "<span class='care-title'>今の状態を保つために</span><br>"
            "足首を軽く動かしたり、足裏をやさしくほぐしたりしてみましょう。"
        )

    result_card(
        "9. セルフケア",
        "<br><br>".join(care_blocks),
        "card-green",
    )

    st.markdown(
        """
<div class="disclaimer">
このサービスは医療行為や医学的な診断を行うものではありません。写真の色は照明やカメラによって変わることがあります。足裏ポイントや性格傾向には、リフレクソロジーやエンタメとしての考え方が含まれます。診断点数とレーダーチャートは質問と写真から算出した参考値です。強い痛み、しびれ、傷、急な腫れ、大きな色の変化などがある場合は、必要に応じて医療機関へご相談ください。
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button(
        "最初から診断する",
        use_container_width=True,
    ):
        keep_keys = {"step", "scroll_to_top", "analysis"}
        for key in list(st.session_state.keys()):
            if key not in keep_keys:
                del st.session_state[key]
        st.session_state.analysis = None
        st.session_state.step = 1
        request_scroll_to_top()
        st.rerun()
