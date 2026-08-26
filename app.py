import gc

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


# =========================================================
# CSS
# =========================================================
st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-family:
        "Yu Gothic",
        "YuGothic",
        "Hiragino Kaku Gothic ProN",
        "Meiryo",
        sans-serif;
}

.block-container {
    max-width: 760px;
    padding-top: 2.6rem;
    padding-bottom: 4rem;
}


/* Streamlit上部UIを目立たなく */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    display: none !important;
}


/* Created by */
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


/* タイトル */
.main-title {
    text-align: center;

    font-family:
        "Yu Mincho",
        "YuMincho",
        "Hiragino Mincho ProN",
        serif;

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


/* STEP */
.step-box {
    padding: 15px 20px;
    border-radius: 16px;

    background:
        linear-gradient(
            135deg,
            #E5EFE8 0%,
            #F6EEE5 100%
        );

    border: 1px solid #D9E4DC;
    color: #42564A;

    font-family:
        "Yu Mincho",
        "Hiragino Mincho ProN",
        serif;

    font-weight: 700;
    font-size: 1.15rem;

    margin-bottom: 1.45rem;
}

.score-note {
    font-family:
        "Yu Gothic",
        sans-serif;

    font-size: 0.64rem;
    font-weight: 400;
    color: #849087;
    margin-top: 8px;
}


/* 質問余白 */
.question-space {
    height: 12px;
}


/* STEP2 */
.guide-card {
    background: #FBF7F0;
    border: 1px solid #EADFD2;
    border-radius: 17px;

    padding: 15px 18px;

    margin-top: 3px;
    margin-bottom: 18px;

    color: #474747;

    font-size: 0.92rem;
    line-height: 1.55;
}

.guide-note {
    color: #918881;
    font-size: 0.62rem;
    line-height: 1.45;
}


/* 撮影補足 */
.photo-note {
    color: #979797;
    font-size: 0.61rem;
    line-height: 1.45;

    margin-top: 15px;
    margin-bottom: 17px;
}


/* File uploader 補足を隠す */
[data-testid="stFileUploader"] small {
    display: none !important;
}

[data-testid="stFileUploader"] section small {
    display: none !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] small {
    display: none !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] > div:nth-child(2) {
    display: none !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] div:nth-child(2) {
    display: none !important;
}

/* 200MB per file対策 */
[data-testid="stFileUploader"] section > div > div:nth-child(2) {
    font-size: 0 !important;
    line-height: 0 !important;
}

[data-testid="stFileUploader"] section > div > div:nth-child(2) * {
    display: none !important;
}


/* 結果カード */
.result-card {
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 20px;

    line-height: 1.58;
    font-size: 0.91rem;

    color: #363636;

    border: 1px solid rgba(70, 90, 75, 0.09);

    box-shadow:
        0 4px 14px
        rgba(70, 80, 70, 0.045);
}

.card-beige {
    background: #FAF4EA;
}

.card-orange {
    background: #FFF0E5;
}

.card-green {
    background: #EDF5EF;
}

.card-sage {
    background: #E6F0E9;
}

.card-cream {
    background: #FCF7E9;
}

.card-lavender {
    background: #F1ECF6;
}

.card-rose {
    background: #F9ECEA;
}

.card-aroma {
    background:
        linear-gradient(
            135deg,
            #F0EAF5 0%,
            #F9F2E8 100%
        );
}

.result-main {
    font-size: 1.05rem;
    font-weight: 700;
    color: #405348;
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


/* 6番・9番だけ少しコンパクト */
.compact-card {
    padding-top: 15px !important;
    padding-bottom: 15px !important;
}


/* 免責 */
.disclaimer {
    color: #AAAAAA;
    font-size: 0.48rem;
    line-height: 1.45;
    margin-top: 6px;
    margin-bottom: 14px;
}


/* 見出し */
h3 {
    font-family:
        "Yu Mincho",
        "Hiragino Mincho ProN",
        serif !important;

    color: #42564A !important;
    letter-spacing: 0.02em;
}


/* ボタン */
div.stButton > button {
    width: 100%;
    min-height: 50px;
    border-radius: 14px;
    font-size: 16px;
    font-weight: 700;
}


/* STEP2 戻る/診断する */
.st-key-action_buttons [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns:
        minmax(0, 1fr)
        minmax(0, 1fr) !important;
    gap: 10px !important;
}

.st-key-action_buttons [data-testid="column"] {
    width: auto !important;
    min-width: 0 !important;
    flex: none !important;
}


/* Q7専用 2列 */
.st-key-fatigue_grid [data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns:
        minmax(0, 1fr)
        minmax(0, 1fr) !important;
    gap: 8px 12px !important;
}

.st-key-fatigue_grid [data-testid="column"] {
    width: auto !important;
    min-width: 0 !important;
    flex: none !important;
}


/* スマホ */
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

    .main-title {
        font-size: 2rem;
    }

    .english-title {
        font-size: 0.65rem;
        letter-spacing: 0.13em;
        margin-bottom: 1.9rem;
    }

    .question-space {
        height: 9px;
    }

    .guide-card {
        padding: 14px 16px;
        font-size: 0.88rem;
    }

    .guide-note {
        font-size: 0.58rem;
    }

    .photo-note {
        font-size: 0.57rem;
    }

    .result-card {
        padding: 16px 17px;
        font-size: 0.88rem;
        line-height: 1.55;
        margin-bottom: 18px;
    }

    .result-main {
        font-size: 1rem;
    }

    h3 {
        font-size: 1rem !important;
    }

    .small-note {
        font-size: 0.61rem;
    }

    .disclaimer {
        font-size: 0.44rem;
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
<div class="top-credit">
Created by GamiKazu
</div>

<div class="main-title">
足裏タイプ診断
</div>

<div class="english-title">
REFLEXOLOGY × AROMATHERAPY
</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# 画像軽量化
# =========================================================
def uploaded_to_rgb(
    uploaded_file,
    max_side=640
):

    uploaded_file.seek(0)

    with Image.open(
        uploaded_file
    ) as image:

        image = ImageOps.exif_transpose(
            image
        )

        image = image.convert(
            "RGB"
        )

        image.thumbnail(
            (
                max_side,
                max_side
            ),
            Image.Resampling.LANCZOS
        )

        rgb = np.asarray(
            image,
            dtype=np.uint8
        ).copy()

    return rgb


# =========================================================
# 最大輪郭
# =========================================================
def largest_contour(
    mask
):

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    return max(
        contours,
        key=cv2.contourArea
    )


# =========================================================
# マスク整理
# =========================================================
def clean_mask(
    binary
):

    kernel = np.ones(
        (
            5,
            5
        ),
        np.uint8
    )

    binary = cv2.morphologyEx(
        binary,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    binary = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )

    contour = largest_contour(
        binary
    )

    if contour is None:
        return None

    clean = np.zeros_like(
        binary
    )

    cv2.drawContours(
        clean,
        [
            contour
        ],
        -1,
        255,
        -1
    )

    return clean


# =========================================================
# 足の範囲検出
# =========================================================
def segment_foot(
    rgb
):

    h, w = rgb.shape[
        :2
    ]

    if (
        h < 70
        or
        w < 40
    ):
        return None

    patch_h = max(
        5,
        int(
            h * 0.07
        )
    )

    patch_w = max(
        5,
        int(
            w * 0.07
        )
    )

    corners = np.concatenate(
        [
            rgb[
                :patch_h,
                :patch_w
            ].reshape(
                -1,
                3
            ),

            rgb[
                :patch_h,
                -patch_w:
            ].reshape(
                -1,
                3
            ),

            rgb[
                -patch_h:,
                :patch_w
            ].reshape(
                -1,
                3
            ),

            rgb[
                -patch_h:,
                -patch_w:
            ].reshape(
                -1,
                3
            )
        ],
        axis=0
    )

    background = np.median(
        corners,
        axis=0
    ).astype(
        np.int16
    )

    diff = rgb.astype(
        np.int16
    ) - background

    distance = np.sqrt(
        np.sum(
            diff * diff,
            axis=2
        )
    )

    distance = np.clip(
        distance,
        0,
        255
    ).astype(
        np.uint8
    )

    _, binary = cv2.threshold(
        distance,
        0,
        255,
        cv2.THRESH_BINARY
        +
        cv2.THRESH_OTSU
    )

    mask = clean_mask(
        binary
    )

    if mask is None:
        return None

    contour = largest_contour(
        mask
    )

    if contour is None:
        return None

    ratio = (
        cv2.contourArea(
            contour
        )
        /
        float(
            h * w
        )
    )

    if (
        ratio < 0.07
        or
        ratio > 0.90
    ):
        return None

    return mask


# =========================================================
# 足部分へ切り抜き
# =========================================================
def crop_to_mask(
    rgb,
    mask
):

    ys, xs = np.where(
        mask > 0
    )

    if len(xs) == 0:
        return rgb, mask

    x1 = int(
        xs.min()
    )

    x2 = int(
        xs.max()
    )

    y1 = int(
        ys.min()
    )

    y2 = int(
        ys.max()
    )

    return (
        rgb[
            y1:y2 + 1,
            x1:x2 + 1
        ],
        mask[
            y1:y2 + 1,
            x1:x2 + 1
        ]
    )


# =========================================================
# 回転
# =========================================================
def rotate_bound(
    image,
    angle,
    interpolation,
    border_value
):

    h, w = image.shape[
        :2
    ]

    center = (
        w / 2,
        h / 2
    )

    matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0
    )

    cos = abs(
        matrix[
            0,
            0
        ]
    )

    sin = abs(
        matrix[
            0,
            1
        ]
    )

    new_w = int(
        h * sin
        +
        w * cos
    )

    new_h = int(
        h * cos
        +
        w * sin
    )

    matrix[
        0,
        2
    ] += (
        new_w / 2
        -
        center[0]
    )

    matrix[
        1,
        2
    ] += (
        new_h / 2
        -
        center[1]
    )

    return cv2.warpAffine(
        image,
        matrix,
        (
            new_w,
            new_h
        ),
        flags=interpolation,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value
    )


# =========================================================
# 足の傾き補正
# =========================================================
def straighten_foot(
    rgb,
    mask
):

    contour = largest_contour(
        mask
    )

    if contour is None:
        return rgb, mask

    try:

        rect = cv2.minAreaRect(
            contour
        )

        _, size, angle = rect

        rw, rh = size

        if rw > rh:
            rotation = angle

        else:
            rotation = (
                angle
                -
                90
            )

        rgb = rotate_bound(
            rgb,
            rotation,
            cv2.INTER_LINEAR,
            (
                255,
                255,
                255
            )
        )

        mask = rotate_bound(
            mask,
            rotation,
            cv2.INTER_NEAREST,
            0
        )

    except cv2.error:
        pass

    return rgb, mask


# =========================================================
# 横幅
# =========================================================
def width_in_band(
    mask,
    start,
    end
):

    h, _ = mask.shape

    y1 = int(
        h * start
    )

    y2 = int(
        h * end
    )

    widths = []

    for y in range(
        y1,
        y2
    ):

        xs = np.where(
            mask[
                y
            ] > 0
        )[0]

        if len(xs) > 0:

            widths.append(
                xs.max()
                -
                xs.min()
                +
                1
            )

    if not widths:
        return 0

    return float(
        np.median(
            widths
        )
    )


# =========================================================
# 指側を上へ
# =========================================================
def ensure_toes_top(
    rgb,
    mask
):

    top = width_in_band(
        mask,
        0.03,
        0.24
    )

    bottom = width_in_band(
        mask,
        0.76,
        0.97
    )

    if bottom > top:

        rgb = np.rot90(
            rgb,
            2
        ).copy()

        mask = np.rot90(
            mask,
            2
        ).copy()

    return rgb, mask


# =========================================================
# 輪郭平滑化
# =========================================================
def smooth_curve(
    curve
):

    curve = np.asarray(
        curve,
        dtype=np.float32
    )

    if len(
        curve
    ) < 7:

        return curve

    size = max(
        7,
        int(
            len(
                curve
            )
            *
            0.025
        )
    )

    if size % 2 == 0:
        size += 1

    kernel = np.ones(
        size,
        np.float32
    ) / size

    return np.convolve(
        curve,
        kernel,
        mode="same"
    )


# =========================================================
# 足指側の輪郭
# =========================================================
def build_top_curve(
    mask
):

    h, w = mask.shape

    toe_bottom = int(
        h * 0.43
    )

    curve = np.full(
        w,
        np.nan,
        dtype=np.float32
    )

    for x in range(
        w
    ):

        ys = np.where(
            mask[
                :toe_bottom,
                x
            ] > 0
        )[0]

        if len(
            ys
        ) > 0:

            curve[
                x
            ] = float(
                np.percentile(
                    ys,
                    3
                )
            )

    valid = np.where(
        np.isfinite(
            curve
        )
    )[0]

    if len(
        valid
    ) < 30:

        return None

    x1 = int(
        valid.min()
    )

    x2 = int(
        valid.max()
    )

    curve = curve[
        x1:x2 + 1
    ]

    missing = ~np.isfinite(
        curve
    )

    known = np.where(
        ~missing
    )[0]

    if len(
        known
    ) < 5:

        return None

    curve[
        missing
    ] = np.interp(
        np.where(
            missing
        )[0],
        known,
        curve[
            known
        ]
    )

    return smooth_curve(
        curve
    )


# =========================================================
# 親指・人差し指・中指
# =========================================================
def detect_three_toes(
    mask,
    big_toe_side
):

    curve = build_top_curve(
        mask
    )

    if curve is None:
        return None

    h, _ = mask.shape

    n = len(
        curve
    )

    if big_toe_side == "right":

        curve = curve[
            ::-1
        ]

    windows = [
        (
            0.02,
            0.25
        ),
        (
            0.18,
            0.43
        ),
        (
            0.35,
            0.60
        )
    ]

    values = []

    for start, end in windows:

        sx = int(
            n * start
        )

        ex = int(
            n * end
        )

        if ex <= sx:
            return None

        part = curve[
            sx:ex
        ]

        if len(
            part
        ) < 3:

            return None

        values.append(
            float(
                np.min(
                    part
                )
            )
        )

    return (
        values[
            0
        ],
        values[
            1
        ],
        values[
            2
        ],
        float(
            h
        )
    )


# =========================================================
# 足型判定
# =========================================================
def classify_foot_shape(
    rgb,
    mask,
    big_toe_side
):

    if mask is None:

        return (
            "判定困難",
            0.0
        )

    rgb, mask = crop_to_mask(
        rgb,
        mask
    )

    rgb, mask = straighten_foot(
        rgb,
        mask
    )

    rgb, mask = crop_to_mask(
        rgb,
        mask
    )

    rgb, mask = ensure_toes_top(
        rgb,
        mask
    )

    rgb, mask = crop_to_mask(
        rgb,
        mask
    )

    h, w = mask.shape

    if (
        h < 75
        or
        w < 38
    ):

        return (
            "判定困難",
            0.0
        )

    result = detect_three_toes(
        mask,
        big_toe_side
    )

    if result is None:

        return (
            "判定困難",
            0.0
        )

    big, second, third, foot_length = (
        result
    )


    # =====================================================
    # スクエア
    # 親指・人差し指・中指がほぼ同じ
    # =====================================================
    spread = (
        max(
            big,
            second,
            third
        )
        -
        min(
            big,
            second,
            third
        )
    ) / foot_length

    if spread <= 0.010:

        return (
            "スクエア型",
            0.90
        )


    # =====================================================
    # ギリシャ
    #
    # 人差し指が親指より
    # 足全体の3.5%以上長く見える時だけ
    # =====================================================
    greek_difference = (
        big
        -
        second
    ) / foot_length

    if greek_difference > 0.035:

        confidence = min(
            0.97,
            0.84
            +
            greek_difference
            *
            3.5
        )

        return (
            "ギリシャ型",
            confidence
        )


    # =====================================================
    # それ以外
    # =====================================================
    return (
        "エジプト型",
        0.92
    )


# =========================================================
# 足色
# =========================================================
def analyze_color(
    rgb,
    mask
):

    if mask is None:

        return (
            "判定困難",
            {}
        )

    hsv = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2HSV
    )

    lab = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2LAB
    )

    valid = (
        mask > 0
    )

    brightness = hsv[
        :,
        :,
        2
    ]

    valid &= (
        brightness > 45
    )

    valid &= (
        brightness < 248
    )

    if valid.sum() < 100:

        valid = (
            mask > 0
        )

    H = float(
        np.median(
            hsv[
                :,
                :,
                0
            ][
                valid
            ]
        )
    )

    S = float(
        np.median(
            hsv[
                :,
                :,
                1
            ][
                valid
            ]
        )
    )

    V = float(
        np.median(
            hsv[
                :,
                :,
                2
            ][
                valid
            ]
        )
    )

    A = float(
        np.median(
            lab[
                :,
                :,
                1
            ][
                valid
            ]
        )
    )

    B = float(
        np.median(
            lab[
                :,
                :,
                2
            ][
                valid
            ]
        )
    )

    if (
        S < 35
        and
        V > 185
    ):

        result = "白っぽい"

    elif (
        (
            H <= 5
            or
            H >= 176
        )
        and
        S >= 55
        and
        A >= 135
    ):

        result = "赤み強め"

    elif (
        5 < H <= 17
        and
        S >= 45
    ):

        result = "オレンジ寄り"

    elif (
        17 < H <= 32
        and
        S >= 45
        and
        B >= 135
    ):

        result = "黄み強め"

    else:

        result = "標準的な色味"

    return (
        result,
        {
            "H": H,
            "S": S,
            "V": V
        }
    )


# =========================================================
# 乾燥・硬い部分
# =========================================================
def analyze_texture(
    rgb,
    mask
):

    if mask is None:

        return (
            "判定困難",
            "判定困難"
        )

    gray = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2GRAY
    )

    lap = cv2.Laplacian(
        gray,
        cv2.CV_32F
    )

    texture = np.abs(
        lap
    )[
        mask > 0
    ]

    if texture.size > 0:

        texture_score = float(
            np.percentile(
                texture,
                75
            )
        )

    else:

        texture_score = 0

    if texture_score > 28:

        dryness = "乾燥が目立つ"

    elif texture_score > 18:

        dryness = "やや乾燥"

    else:

        dryness = "乾燥は目立たない"


    lab = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2LAB
    )

    candidates = (
        (
            mask > 0
        )
        &
        (
            lab[
                :,
                :,
                0
            ]
            >
            145
        )
        &
        (
            lab[
                :,
                :,
                2
            ]
            >
            138
        )
    )

    ys, xs = np.where(
        candidates
    )

    if len(
        xs
    ) < 80:

        return (
            dryness,
            "なし"
        )

    all_y, all_x = np.where(
        mask > 0
    )

    if len(
        all_x
    ) == 0:

        return (
            dryness,
            "なし"
        )

    x1 = all_x.min()
    x2 = all_x.max()

    y1 = all_y.min()
    y2 = all_y.max()

    cx = float(
        xs.mean()
    )

    cy = float(
        ys.mean()
    )

    nx = (
        cx - x1
    ) / max(
        1,
        x2 - x1
    )

    ny = (
        cy - y1
    ) / max(
        1,
        y2 - y1
    )

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

    return (
        dryness,
        hard_part
    )


# =========================================================
# 両足分割
# =========================================================
def split_both(
    rgb
):

    _, w = rgb.shape[
        :2
    ]

    center = (
        w // 2
    )

    overlap = int(
        w * 0.02
    )

    left = rgb[
        :,
        :min(
            w,
            center
            +
            overlap
        )
    ].copy()

    right = rgb[
        :,
        max(
            0,
            center
            -
            overlap
        ):
    ].copy()

    return (
        left,
        right
    )


# =========================================================
# 足型統合
# =========================================================
def unify_shapes(
    results
):

    usable = [
        result
        for result
        in results
        if result[
            0
        ]
        !=
        "判定困難"
    ]

    if not usable:

        return (
            "判定困難",
            0
        )

    counts = {
        "エジプト型": 0,
        "ギリシャ型": 0,
        "スクエア型": 0
    }

    scores = {
        "エジプト型": 0,
        "ギリシャ型": 0,
        "スクエア型": 0
    }

    for shape, conf in usable:

        counts[
            shape
        ] += 1

        scores[
            shape
        ] += conf


    max_count = max(
        counts.values()
    )

    winners = [
        shape
        for shape, count
        in counts.items()
        if (
            count
            ==
            max_count
            and
            count > 0
        )
    ]


    if len(
        winners
    ) == 1:

        chosen = winners[
            0
        ]

        return (
            chosen,
            scores[
                chosen
            ]
            /
            counts[
                chosen
            ]
        )


    # エジプトとギリシャで割れた場合は
    # ギリシャがかなり強い時だけギリシャ
    if (
        scores[
            "ギリシャ型"
        ]
        >
        scores[
            "エジプト型"
        ]
        *
        1.35
    ):

        return (
            "ギリシャ型",
            scores[
                "ギリシャ型"
            ]
        )


    if scores[
        "エジプト型"
    ] > 0:

        return (
            "エジプト型",
            scores[
                "エジプト型"
            ]
        )


    chosen = max(
        scores,
        key=scores.get
    )

    return (
        chosen,
        scores[
            chosen
        ]
    )


# =========================================================
# 全体解析
# =========================================================
def analyze_images(
    both_rgb=None,
    right_rgb=None,
    left_rgb=None
):

    shape_results = []

    representative_rgb = None
    representative_mask = None


    # 右足単体
    if right_rgb is not None:

        mask = segment_foot(
            right_rgb
        )

        result = classify_foot_shape(
            right_rgb,
            mask,
            "left"
        )

        if result[
            0
        ] != "判定困難":

            shape_results.append(
                (
                    result[
                        0
                    ],
                    min(
                        0.99,
                        result[
                            1
                        ]
                        +
                        0.05
                    )
                )
            )

        if representative_rgb is None:

            representative_rgb = (
                right_rgb
            )

            representative_mask = (
                mask
            )


    # 左足単体
    if left_rgb is not None:

        mask = segment_foot(
            left_rgb
        )

        result = classify_foot_shape(
            left_rgb,
            mask,
            "right"
        )

        if result[
            0
        ] != "判定困難":

            shape_results.append(
                (
                    result[
                        0
                    ],
                    min(
                        0.99,
                        result[
                            1
                        ]
                        +
                        0.05
                    )
                )
            )

        if representative_rgb is None:

            representative_rgb = (
                left_rgb
            )

            representative_mask = (
                mask
            )


    # 両足
    if both_rgb is not None:

        left_part, right_part = (
            split_both(
                both_rgb
            )
        )

        left_mask = segment_foot(
            left_part
        )

        right_mask = segment_foot(
            right_part
        )

        left_result = classify_foot_shape(
            left_part,
            left_mask,
            "right"
        )

        right_result = classify_foot_shape(
            right_part,
            right_mask,
            "left"
        )

        both_result = unify_shapes(
            [
                left_result,
                right_result
            ]
        )

        if both_result[
            0
        ] != "判定困難":

            shape_results.append(
                both_result
            )


        if representative_rgb is None:

            left_area = (
                np.count_nonzero(
                    left_mask
                )
                if left_mask
                is not None
                else
                0
            )

            right_area = (
                np.count_nonzero(
                    right_mask
                )
                if right_mask
                is not None
                else
                0
            )

            if right_area >= left_area:

                representative_rgb = (
                    right_part
                )

                representative_mask = (
                    right_mask
                )

            else:

                representative_rgb = (
                    left_part
                )

                representative_mask = (
                    left_mask
                )


    overall_shape, shape_conf = (
        unify_shapes(
            shape_results
        )
    )


    if (
        representative_rgb
        is None
        or
        representative_mask
        is None
    ):

        foot_color = "判定困難"

        color_info = {}

        dryness = "判定困難"

        hard_part = "判定困難"

    else:

        foot_color, color_info = (
            analyze_color(
                representative_rgb,
                representative_mask
            )
        )

        dryness, hard_part = (
            analyze_texture(
                representative_rgb,
                representative_mask
            )
        )


    gc.collect()


    return {
        "overall_shape":
            overall_shape,

        "shape_conf":
            shape_conf,

        "foot_color":
            foot_color,

        "color_info":
            color_info,

        "dryness":
            dryness,

        "hard_part":
            hard_part
    }


# =========================================================
# 結果カード
# =========================================================
def result_card(
    title,
    body,
    card_class,
    extra_class=""
):

    st.markdown(
        f"### {title}"
    )

    st.markdown(
        f"""
<div class="result-card {card_class} {extra_class}">
{body}
</div>
""",
        unsafe_allow_html=True
    )


# =========================================================
# STEP1
# =========================================================
if st.session_state.step == 1:

    st.markdown(
        """
<div class="step-box">
STEP 1　簡単な質問
</div>
""",
        unsafe_allow_html=True
    )


    cold = st.radio(
        "Q1. 足が冷えやすいですか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )

    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    swelling = st.radio(
        "Q2. むくみを感じることがありますか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )

    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    tired = st.radio(
        "Q3. 長時間歩いたり立ったりすると、足が疲れやすいですか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )

    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    standing = st.radio(
        "Q4. 普段、立っている時間は長いですか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )

    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    shoes = st.selectbox(
        "Q5. 普段よく履く靴は？",
        [
            "スニーカー",
            "革靴",
            "パンプス",
            "サンダル",
            "ブーツ",
            "その他"
        ]
    )

    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


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
            "歩き方が気になる"
        ]
    )

    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    # =====================================================
    # Q7 スマホ2列固定
    # =====================================================
    st.write(
        "Q7. 今、疲れを感じる場所はありますか？"
    )

    fatigue_area = []


    with st.container(
        key="fatigue_grid"
    ):

        row1 = st.columns(
            2
        )

        with row1[
            0
        ]:

            if st.checkbox(
                "頭・目",
                key="fatigue_head"
            ):

                fatigue_area.append(
                    "頭・目"
                )


        with row1[
            1
        ]:

            if st.checkbox(
                "首",
                key="fatigue_neck"
            ):

                fatigue_area.append(
                    "首"
                )


        row2 = st.columns(
            2
        )

        with row2[
            0
        ]:

            if st.checkbox(
                "肩",
                key="fatigue_shoulder"
            ):

                fatigue_area.append(
                    "肩"
                )


        with row2[
            1
        ]:

            if st.checkbox(
                "背中",
                key="fatigue_back"
            ):

                fatigue_area.append(
                    "背中"
                )


        row3 = st.columns(
            2
        )

        with row3[
            0
        ]:

            if st.checkbox(
                "腰",
                key="fatigue_waist"
            ):

                fatigue_area.append(
                    "腰"
                )


        with row3[
            1
        ]:

            if st.checkbox(
                "胃まわり",
                key="fatigue_stomach"
            ):

                fatigue_area.append(
                    "胃まわり"
                )


        row4 = st.columns(
            2
        )

        with row4[
            0
        ]:

            if st.checkbox(
                "脚",
                key="fatigue_leg"
            ):

                fatigue_area.append(
                    "脚"
                )


        with row4[
            1
        ]:

            if st.checkbox(
                "全身",
                key="fatigue_all"
            ):

                fatigue_area.append(
                    "全身"
                )


    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    sole_wear = st.selectbox(
        "Q8. 靴底はどこが減りやすいですか？",
        [
            "分からない",
            "かかとの外側",
            "かかとの内側",
            "つま先側",
            "全体的に均等"
        ]
    )

    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    stumble = st.radio(
        "Q9. 歩いている時につまずきやすいですか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )

    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    aroma_goal = st.selectbox(
        "Q10. 今、一番求めているものは？",
        [
            "リラックス",
            "リフレッシュ",
            "集中",
            "睡眠",
            "気分転換"
        ]
    )


    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    if st.button(
        "次へ",
        type="primary",
        use_container_width=True
    ):

        st.session_state.cold = (
            cold
        )

        st.session_state.swelling = (
            swelling
        )

        st.session_state.tired = (
            tired
        )

        st.session_state.standing = (
            standing
        )

        st.session_state.shoes = (
            shoes
        )

        st.session_state.foot_concern = (
            foot_concern
        )

        st.session_state.fatigue_area = (
            fatigue_area
        )

        st.session_state.sole_wear = (
            sole_wear
        )

        st.session_state.stumble = (
            stumble
        )

        st.session_state.aroma_goal = (
            aroma_goal
        )

        st.session_state.step = 2

        st.rerun()


# =========================================================
# STEP2
# =========================================================
elif st.session_state.step == 2:

    st.markdown(
        """
<div class="step-box">
STEP 2　足裏写真
</div>
""",
        unsafe_allow_html=True
    )


    st.markdown(
        """
<div class="guide-card">

下のいずれか1枚以上をアップロードしてください。

<br><br>

・両足<br>
・右足<br>
・左足

<br><br>

<span class="guide-note">
※より正確な判定には、3種類すべての撮影がおすすめです。
</span>

</div>
""",
        unsafe_allow_html=True
    )


    both_feet = st.file_uploader(
        "両足の写真（任意）",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key="both_feet"
    )


    right_foot = st.file_uploader(
        "右足の写真（任意）",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key="right_foot"
    )


    left_foot = st.file_uploader(
        "左足の写真（任意）",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key="left_foot"
    )


    st.markdown(
        """
<div class="photo-note">
※足指からかかとまで画面に入れ、できるだけ真正面から撮影してください。足指同士が重ならない写真がおすすめです。背景はできるだけ無地にしてください。
</div>
""",
        unsafe_allow_html=True
    )


    has_photo = (
        both_feet is not None
        or
        right_foot is not None
        or
        left_foot is not None
    )


    with st.container(
        key="action_buttons"
    ):

        col1, col2 = st.columns(
            2
        )


        with col1:

            if st.button(
                "戻る",
                use_container_width=True
            ):

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

        progress = st.progress(
            0
        )

        status = st.empty()

        try:

            status.write(
                "写真を読み込んでいます..."
            )


            both_rgb = (
                uploaded_to_rgb(
                    both_feet
                )
                if both_feet
                is not None
                else None
            )

            progress.progress(
                25
            )


            right_rgb = (
                uploaded_to_rgb(
                    right_foot
                )
                if right_foot
                is not None
                else None
            )

            progress.progress(
                40
            )


            left_rgb = (
                uploaded_to_rgb(
                    left_foot
                )
                if left_foot
                is not None
                else None
            )

            progress.progress(
                55
            )


            status.write(
                "足裏を確認しています..."
            )


            analysis = analyze_images(
                both_rgb=both_rgb,
                right_rgb=right_rgb,
                left_rgb=left_rgb
            )


            progress.progress(
                90
            )


            st.session_state.analysis = (
                analysis
            )


            del both_rgb
            del right_rgb
            del left_rgb

            gc.collect()


            progress.progress(
                100
            )


            st.session_state.step = 3

            st.rerun()


        except Exception as error:

            gc.collect()

            st.error(
                "写真をうまく解析できませんでした。"
                "別の写真でお試しください。"
            )

            st.caption(
                str(
                    error
                )
            )


# =========================================================
# STEP3
# =========================================================
elif st.session_state.step == 3:

    analysis = (
        st.session_state.analysis
    )

    cold = (
        st.session_state.cold
    )

    swelling = (
        st.session_state.swelling
    )

    tired = (
        st.session_state.tired
    )

    standing = (
        st.session_state.standing
    )

    fatigue_area = (
        st.session_state.fatigue_area
    )

    sole_wear = (
        st.session_state.sole_wear
    )

    stumble = (
        st.session_state.stumble
    )

    aroma_goal = (
        st.session_state.aroma_goal
    )


    shape = (
        analysis[
            "overall_shape"
        ]
    )

    color = (
        analysis[
            "foot_color"
        ]
    )


    # =====================================================
    # 点数
    # =====================================================
    score = 100


    if cold == "はい":
        score -= 8

    if swelling == "はい":
        score -= 8

    if tired == "はい":
        score -= 10

    if standing == "はい":
        score -= 4

    if stumble == "はい":
        score -= 6


    if len(
        fatigue_area
    ) == 1:

        score -= 4

    elif len(
        fatigue_area
    ) >= 2:

        score -= 8


    if (
        analysis[
            "dryness"
        ]
        ==
        "やや乾燥"
    ):

        score -= 5


    elif (
        analysis[
            "dryness"
        ]
        ==
        "乾燥が目立つ"
    ):

        score -= 10


    if (
        analysis[
            "hard_part"
        ]
        not in [
            "なし",
            "判定困難"
        ]
    ):

        score -= 5


    if color == "赤み強め":

        score -= 5

    elif color == "オレンジ寄り":

        score -= 3

    elif color == "白っぽい":

        score -= 4


    score = max(
        40,
        min(
            100,
            score
        )
    )


    if score >= 85:

        score_message = (
            "今は比較的良い状態です"
        )

    elif score >= 70:

        score_message = (
            "大きな偏りは少ない状態です"
        )

    elif score >= 55:

        score_message = (
            "少しセルフケアを意識したい状態です"
        )

    else:

        score_message = (
            "今日はゆっくり休むことを意識しましょう"
        )


    st.markdown(
        f"""
<div class="step-box">

診断結果：{score}点

<div style="
font-family:'Yu Gothic',sans-serif;
font-size:13px;
font-weight:500;
margin-top:5px;
opacity:0.72;
">
{score_message}
</div>

<div class="score-note">
※質問と写真から算出した参考スコアです。
</div>

</div>
""",
        unsafe_allow_html=True
    )


    # =====================================================
    # 1 足
    # =====================================================
    if shape == "エジプト型":

        shape_text = (
            "親指が一番長く、小指に向かって"
            "少しずつ短くなるタイプです。"
        )

    elif shape == "ギリシャ型":

        shape_text = (
            "人差し指が親指より"
            "はっきり長いタイプです。"
        )

    elif shape == "スクエア型":

        shape_text = (
            "親指・人差し指・中指の長さが"
            "かなり近いタイプです。"
        )

    else:

        shape_text = (
            "今回の写真では足の形を"
            "はっきり判定できませんでした。"
        )


    result_card(
        "1. 足の形",
        (
            f"<span class='result-main'>"
            f"{shape}"
            f"</span>"
            "<br><br>"
            f"{shape_text}"
        ),
        "card-beige"
    )


    # =====================================================
    # 2 色
    # =====================================================
    if color == "赤み強め":

        color_text = (
            "写真では赤みがやや強く見えます。"
            "活動した後や、足が温まっている時にも"
            "見られる色合いです。"
        )

    elif color == "オレンジ寄り":

        color_text = (
            "写真では少しオレンジ寄りに見えます。"
            "照明やカメラでも色は変わるため、"
            "参考として見てください。"
        )

    elif color == "黄み強め":

        color_text = (
            "写真では少し黄みが強く見えます。"
            "照明やカメラでも色は変わります。"
        )

    elif color == "白っぽい":

        color_text = (
            "写真ではやや白っぽく見えます。"
            "照明や撮影環境でも色は変わります。"
        )

    elif color == "判定困難":

        color_text = (
            "今回の写真では色を"
            "うまく確認できませんでした。"
        )

    else:

        color_text = (
            "写真では大きな色の偏りは"
            "目立ちませんでした。"
        )


    result_card(
        "2. 足の色",
        (
            f"<span class='result-main'>"
            f"{color}"
            f"</span>"
            "<br><br>"
            f"{color_text}"
        ),
        "card-orange"
    )


    # =====================================================
    # 3 心と体
    # =====================================================
    rest_score = 0

    if cold == "はい":
        rest_score += 2

    if swelling == "はい":
        rest_score += 1

    if tired == "はい":
        rest_score += 2

    if len(
        fatigue_area
    ) >= 2:

        rest_score += 2

    elif len(
        fatigue_area
    ) == 1:

        rest_score += 1


    if rest_score >= 6:

        mind_text = (
            "今は疲れがたまりやすい状態かもしれません。"
            "休む時間や睡眠を少し意識してみましょう。"
        )

    elif rest_score >= 3:

        mind_text = (
            "少し疲れがたまっている可能性があります。"
            "短い休憩や気分転換を取り入れるのがおすすめです。"
        )

    else:

        mind_text = (
            "今は比較的バランスが取れているようです。"
            "今の状態を保ちながら、"
            "無理をしすぎないようにしましょう。"
        )


    result_card(
        "3. 今の心と体の傾向",
        mind_text,
        "card-green"
    )


    # =====================================================
    # 4 歩き方
    # =====================================================
    walk_points = []


    if sole_wear == "かかとの外側":

        walk_points.append(
            "靴底の減り方から、"
            "足の外側に体重がかかりやすいようです。"
        )

    elif sole_wear == "かかとの内側":

        walk_points.append(
            "靴底の減り方から、"
            "足の内側に体重がかかりやすいようです。"
        )

    elif sole_wear == "つま先側":

        walk_points.append(
            "つま先側に負担が集まりやすいようです。"
        )

    elif sole_wear == "全体的に均等":

        walk_points.append(
            "靴底の減り方には、"
            "大きな偏りは見られないようです。"
        )


    hard_part = (
        analysis[
            "hard_part"
        ]
    )


    if hard_part == "足の前側":

        walk_points.append(
            "写真でも足の前側に"
            "負担がかかっている可能性があります。"
        )

    elif hard_part == "かかと":

        walk_points.append(
            "写真では、かかとに"
            "負担がかかっている可能性があります。"
        )


    if stumble == "はい":

        walk_points.append(
            "つまずきやすい場合は、"
            "歩く時に足先を少し上げることも"
            "意識してみましょう。"
        )


    if not walk_points:

        walk_points.append(
            "今回の結果では、"
            "歩き方に大きな偏りは見られませんでした。"
        )


    result_card(
        "4. 歩き方の傾向",
        "<br><br>".join(
            walk_points
        ),
        "card-sage"
    )


    # =====================================================
    # 5 靴
    # =====================================================
    if shape == "エジプト型":

        shoe_title = (
            "つま先に丸みのあるスニーカー"
        )

        shoe_text = (
            "親指が一番長い足型です。"
            "親指が靴の先に当たりにくい、"
            "つま先に少し余裕のある靴がおすすめです。"
        )

    elif shape == "ギリシャ型":

        shoe_title = (
            "つま先に余裕のあるスニーカー"
        )

        shoe_text = (
            "人差し指が長めの足型です。"
            "人差し指が靴の先に当たりにくい、"
            "少し余裕のある靴がおすすめです。"
        )

    elif shape == "スクエア型":

        shoe_title = (
            "つま先が広めのスニーカー"
        )

        shoe_text = (
            "親指・人差し指・中指の長さが近い足型です。"
            "指先が窮屈になりにくい、"
            "つま先が広めの靴がおすすめです。"
        )

    else:

        shoe_title = (
            "つま先に余裕のある靴"
        )

        shoe_text = (
            "指先が窮屈にならず、"
            "足の横幅にも合った靴がおすすめです。"
        )


    if tired == "はい":

        shoe_text += (
            "<br><br>"
            "足が疲れやすい場合は、"
            "クッション性も確認してみましょう。"
        )


    result_card(
        "5. おすすめの靴",
        (
            f"<span class='result-main'>"
            f"{shoe_title}"
            f"</span>"
            "<br><br>"
            f"{shoe_text}"
        ),
        "card-cream"
    )


    # =====================================================
    # 6 性格
    # =====================================================
    if shape == "エジプト型":

        personality = (
            "足型を使ったエンタメ診断では、"
            "落ち着いていて、自分のペースを大切にする"
            "タイプと言われることがあります。"
        )

    elif shape == "ギリシャ型":

        personality = (
            "足型を使ったエンタメ診断では、"
            "好奇心があり、新しいことに挑戦しやすい"
            "タイプと言われることがあります。"
        )

    elif shape == "スクエア型":

        personality = (
            "足型を使ったエンタメ診断では、"
            "安定感があり、物事をコツコツ進める"
            "タイプと言われることがあります。"
        )

    else:

        personality = (
            "今回は足型をはっきり判定できなかったため、"
            "この項目は判定できませんでした。"
        )


    result_card(
        "6. 足の形から見る性格傾向",
        (
            personality
            +
            "<br><br>"
            "<span class='small-note'>"
            "※性格を科学的に判断するものではありません。"
            "エンタメとしてお楽しみください。"
            "</span>"
        ),
        "card-lavender",
        "compact-card"
    )


    # =====================================================
    # 7 足裏ポイント
    # =====================================================
    reflex_map = {

        "頭・目":
            "親指まわり",

        "首":
            "親指の付け根",

        "肩":
            "足指の付け根〜小指側",

        "背中":
            "足裏の内側",

        "腰":
            "土踏まずの内側〜かかと寄り",

        "胃まわり":
            "土踏まずの上側",

        "脚":
            "かかとまわり",

        "全身":
            "足裏全体"
    }


    if fatigue_area:

        blocks = []

        for area in fatigue_area:

            blocks.append(
                f"<span class='care-title'>"
                f"{area}"
                f"</span>"
                "<br>"
                f"足裏のおすすめポイント："
                f"{reflex_map[area]}"
            )


        reflex_text = (
            "<br><br>".join(
                blocks
            )
            +
            "<br><br>"
            "<span class='small-note'>"
            "リフレクソロジーでは、これらの場所を"
            "体の各部位に対応する「反射区」として扱います。"
            "心地よい強さで5〜10秒ほど"
            "ゆっくり押してみてください。"
            "</span>"
        )

    else:

        reflex_text = (
            "今回は特に疲れている場所が"
            "選択されていません。"
            "<br><br>"
            "足裏全体を気持ちいい程度の強さで"
            "ゆっくりほぐしてみましょう。"
        )


    result_card(
        "7. 疲れた場所・足裏ポイント",
        reflex_text,
        "card-rose"
    )


    # =====================================================
    # 8 アロマ
    # =====================================================
    aroma_map = {

        "リラックス": (
            "ラベンダー",
            "ゆっくり過ごしたい時や、"
            "落ち着きたい時に取り入れやすい香りです。"
        ),

        "リフレッシュ": (
            "レモン",
            "すっきり気分を切り替えたい時に"
            "取り入れやすい香りです。"
        ),

        "集中": (
            "ローズマリー",
            "仕事や勉強など、"
            "集中したい時間に取り入れやすい香りです。"
        ),

        "睡眠": (
            "ラベンダー",
            "寝る前など、"
            "ゆったり過ごしたい時に取り入れやすい香りです。"
        ),

        "気分転換": (
            "スイートオレンジ",
            "気持ちを切り替えたい時に取り入れやすい、"
            "やわらかな柑橘系の香りです。"
        )
    }


    aroma, aroma_text = (
        aroma_map[
            aroma_goal
        ]
    )


    result_card(
        "8. おすすめアロマ",
        (
            f"<span class='result-main'>"
            f"{aroma}"
            f"</span>"
            "<br><br>"
            f"{aroma_text}"
        ),
        "card-aroma"
    )


    # =====================================================
    # 9 セルフケア
    # =====================================================
    care = []


    if swelling == "はい":

        care.append(
            "<span class='care-title'>"
            "むくみが気になる時"
            "</span>"
            "<br>"
            "足首をゆっくり回したり、"
            "ふくらはぎを軽く動かしてみましょう。"
        )


    if cold == "はい":

        care.append(
            "<span class='care-title'>"
            "冷えが気になる時"
            "</span>"
            "<br>"
            "足湯や靴下などで、"
            "足元を心地よく温めるのがおすすめです。"
        )


    if tired == "はい":

        care.append(
            "<span class='care-title'>"
            "足が疲れている時"
            "</span>"
            "<br>"
            "足を休ませる時間をつくり、"
            "軽いストレッチをしてみましょう。"
        )


    if (
        analysis[
            "dryness"
        ]
        in [
            "やや乾燥",
            "乾燥が目立つ"
        ]
    ):

        care.append(
            "<span class='care-title'>"
            "乾燥が気になる時"
            "</span>"
            "<br>"
            "お風呂上がりなどに"
            "足裏を保湿するのがおすすめです。"
        )


    if stumble == "はい":

        care.append(
            "<span class='care-title'>"
            "つまずきやすい時"
            "</span>"
            "<br>"
            "足首を軽く動かし、"
            "歩く時に足先を少し上げることを"
            "意識してみましょう。"
        )


    if not care:

        care.append(
            "<span class='care-title'>"
            "毎日のケア"
            "</span>"
            "<br>"
            "足裏の保湿や軽いストレッチを"
            "取り入れるのがおすすめです。"
        )


    result_card(
        "9. セルフケア",
        "<br><br>".join(
            care
        ),
        "card-green",
        "compact-card"
    )


    # =====================================================
    # 免責
    # =====================================================
    st.markdown(
        """
<div class="disclaimer">

このサービスは医療行為や医学的な診断を行うものではありません。
写真の色は照明やカメラによって変わることがあります。
足裏ポイントや性格傾向には、リフレクソロジーやエンタメとしての考え方が含まれます。
診断点数は質問と写真から算出した参考値です。
強い痛み、しびれ、傷、急な腫れ、大きな色の変化などがある場合は、必要に応じて医療機関へご相談ください。

</div>
""",
        unsafe_allow_html=True
    )


    if st.button(
        "最初から診断する",
        use_container_width=True
    ):

        if "analysis" in st.session_state:

            del st.session_state[
                "analysis"
            ]

        gc.collect()

        st.session_state.step = 1

        st.rerun()