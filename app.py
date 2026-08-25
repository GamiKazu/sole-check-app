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
    padding-top: 2.8rem;
    padding-bottom: 4rem;
}


/* Created by */
.top-credit {
    width: 100%;
    text-align: right;
    font-size: 9px;
    color: #AAAAAA;
    opacity: 0.78;
    letter-spacing: 0.05em;
    margin-top: 18px;
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
    margin-bottom: 2.5rem;
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

    margin-bottom: 1.6rem;
}


/* 質問間 */
.question-space {
    height: 15px;
}


/* STEP2説明 */
.guide-card {
    background: #FBF7F0;
    border: 1px solid #EADFD2;
    border-radius: 17px;

    padding: 20px 22px;

    margin-top: 5px;
    margin-bottom: 22px;

    color: #474747;
    line-height: 1.9;
}

.guide-note {
    color: #918881;
    font-size: 0.67rem;
    line-height: 1.55;
}


/* 写真注意 */
.photo-note {
    color: #989898;
    font-size: 0.65rem;
    line-height: 1.55;
    margin-top: 20px;
    margin-bottom: 20px;
}


/* FileUploader補足を隠す */
[data-testid="stFileUploader"] small {
    display: none !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] small {
    display: none !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] div:nth-child(2) {
    display: none !important;
}


/* 結果 */
.result-card {
    border-radius: 18px;
    padding: 21px 22px;
    margin-bottom: 24px;
    line-height: 1.85;
    color: #363636;

    border: 1px solid rgba(70, 90, 75, 0.09);

    box-shadow:
        0 4px 14px
        rgba(70, 80, 70, 0.05);
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
    font-size: 1.15rem;
    font-weight: 700;
    color: #405348;
}

.care-title {
    font-weight: 700;
    color: #536C5B;
}


/* 免責 */
.disclaimer {
    color: #AAAAAA;
    font-size: 0.52rem;
    line-height: 1.5;
    margin-top: 8px;
    margin-bottom: 16px;
}


h3 {
    font-family:
        "Yu Mincho",
        "Hiragino Mincho ProN",
        serif !important;

    color: #42564A !important;
    letter-spacing: 0.03em;
}


div.stButton > button {
    width: 100%;
    min-height: 52px;
    border-radius: 14px;
    font-size: 16px;
    font-weight: 700;
}


/* スマホ */
@media (max-width: 600px) {

    .block-container {
        padding-top: 2.8rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .top-credit {
        font-size: 8px;
        margin-top: 28px;
        margin-bottom: 11px;
    }

    .main-title {
        font-size: 2rem;
    }

    .english-title {
        font-size: 0.66rem;
        letter-spacing: 0.14em;
    }

    .question-space {
        height: 11px;
    }

    .guide-note {
        font-size: 0.60rem;
    }

    .photo-note {
        font-size: 0.59rem;
    }

    .result-card {
        padding: 18px;
    }

    h3 {
        font-size: 1.03rem !important;
    }

    .disclaimer {
        font-size: 0.48rem;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# ヘッダー
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
# 画像読み込み
#
# 最重要：
# 巨大画像をnumpy化する前に700pxへ縮小する
# =========================================================
def uploaded_to_rgb(
    uploaded_file,
    max_side=700
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
# 共通
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
# 軽量足領域抽出
#
# 1. まず背景色との差で高速処理
# 2. うまくいかなければGrabCutを1回だけ
# =========================================================
def segment_foot(
    rgb
):

    h, w = rgb.shape[
        :2
    ]

    if (
        h < 80
        or
        w < 50
    ):
        return None


    # =====================================================
    # 軽量方式
    # 四隅の色を背景色として推定
    # =====================================================
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

    corner_pixels = np.concatenate(
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
        corner_pixels,
        axis=0
    ).astype(
        np.float32
    )

    image_float = rgb.astype(
        np.float32
    )

    distance = np.sqrt(
        np.sum(
            (
                image_float
                -
                background
            )
            **
            2,
            axis=2
        )
    )

    distance_u8 = np.clip(
        distance,
        0,
        255
    ).astype(
        np.uint8
    )

    _, binary = cv2.threshold(
        distance_u8,
        0,
        255,
        cv2.THRESH_BINARY
        +
        cv2.THRESH_OTSU
    )

    quick_mask = clean_mask(
        binary
    )

    if quick_mask is not None:

        contour = largest_contour(
            quick_mask
        )

        if contour is not None:

            ratio = (
                cv2.contourArea(
                    contour
                )
                /
                float(
                    h * w
                )
            )

            # 足としてそれなりに自然なら
            # GrabCutせず終了
            if (
                0.10
                <=
                ratio
                <=
                0.82
            ):

                return quick_mask


    # 不要配列を少し早く解放
    del image_float
    del distance
    del distance_u8
    del binary
    del corner_pixels


    # =====================================================
    # フォールバック
    # GrabCutは1iterationのみ
    # =====================================================
    bgr = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2BGR
    )

    grab_mask = np.zeros(
        (
            h,
            w
        ),
        np.uint8
    )

    mx = max(
        3,
        int(
            w * 0.05
        )
    )

    my = max(
        3,
        int(
            h * 0.04
        )
    )

    rect = (
        mx,
        my,
        max(
            2,
            w
            -
            mx * 2
        ),
        max(
            2,
            h
            -
            my * 2
        )
    )

    bgd = np.zeros(
        (
            1,
            65
        ),
        np.float64
    )

    fgd = np.zeros(
        (
            1,
            65
        ),
        np.float64
    )

    try:

        cv2.grabCut(
            bgr,
            grab_mask,
            rect,
            bgd,
            fgd,
            1,
            cv2.GC_INIT_WITH_RECT
        )

        binary = np.where(
            (
                grab_mask
                ==
                cv2.GC_FGD
            )
            |
            (
                grab_mask
                ==
                cv2.GC_PR_FGD
            ),
            255,
            0
        ).astype(
            np.uint8
        )

        return clean_mask(
            binary
        )

    except cv2.error:

        return quick_mask


# =========================================================
# マスク範囲切り抜き
# =========================================================
def crop_to_mask(
    rgb,
    mask
):

    ys, xs = np.where(
        mask > 0
    )

    if len(xs) == 0:

        return (
            rgb,
            mask
        )

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


def straighten_foot(
    rgb,
    mask
):

    contour = largest_contour(
        mask
    )

    if contour is None:

        return (
            rgb,
            mask
        )

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

    return (
        rgb,
        mask
    )


# =========================================================
# 足先方向
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
            mask[y] > 0
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


def ensure_toes_top(
    rgb,
    mask
):

    top_width = width_in_band(
        mask,
        0.03,
        0.24
    )

    bottom_width = width_in_band(
        mask,
        0.76,
        0.97
    )

    if (
        bottom_width
        >
        top_width
    ):

        rgb = np.rot90(
            rgb,
            2
        ).copy()

        mask = np.rot90(
            mask,
            2
        ).copy()

    return (
        rgb,
        mask
    )


# =========================================================
# 足指輪郭
# =========================================================
def smooth_curve(
    values
):

    values = np.asarray(
        values,
        dtype=np.float32
    )

    if len(values) < 7:
        return values

    size = max(
        7,
        int(
            len(values)
            *
            0.025
        )
    )

    if size % 2 == 0:
        size += 1

    kernel = np.ones(
        size,
        dtype=np.float32
    ) / size

    return np.convolve(
        values,
        kernel,
        mode="same"
    )


def build_top_curve(
    mask
):

    h, w = mask.shape

    toe_bottom = int(
        h * 0.44
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

        if len(ys) > 0:

            curve[x] = float(
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

    if len(valid) < 30:
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

    if len(known) < 5:
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
# 指先候補
# =========================================================
def find_toe_peaks(
    curve,
    foot_height
):

    n = len(
        curve
    )

    radius = max(
        5,
        int(
            n * 0.035
        )
    )

    minimum_gap = max(
        7,
        int(
            n * 0.075
        )
    )

    candidates = []

    for i in range(
        radius,
        n - radius
    ):

        local = curve[
            i - radius:
            i + radius + 1
        ]

        if (
            curve[i]
            >
            np.min(
                local
            )
            +
            0.6
        ):
            continue

        left = local[
            :radius
        ]

        right = local[
            radius + 1:
        ]

        if (
            len(left) == 0
            or
            len(right) == 0
        ):
            continue

        shoulder = (
            float(
                np.percentile(
                    left,
                    70
                )
            )
            +
            float(
                np.percentile(
                    right,
                    70
                )
            )
        ) / 2

        prominence = (
            shoulder
            -
            float(
                curve[i]
            )
        )

        if prominence < (
            foot_height
            *
            0.003
        ):
            continue

        candidates.append(
            {
                "x": i,
                "y": float(
                    curve[i]
                ),
                "prominence":
                    prominence
            }
        )

    candidates = sorted(
        candidates,
        key=lambda p:
            p["prominence"],
        reverse=True
    )

    selected = []

    for item in candidates:

        if all(
            abs(
                item["x"]
                -
                old["x"]
            )
            >=
            minimum_gap

            for old in selected
        ):

            selected.append(
                item
            )

        if len(selected) >= 6:
            break

    return sorted(
        selected,
        key=lambda p:
            p["x"]
    )


# =========================================================
# 親指・第2趾・第3趾
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

    peaks = find_toe_peaks(
        curve,
        h
    )

    n = len(
        curve
    )

    # 親指側を左に統一
    if big_toe_side == "right":

        curve = curve[
            ::-1
        ]

        converted = []

        for peak in peaks:

            converted.append(
                {
                    "x":
                        n
                        -
                        1
                        -
                        peak["x"],

                    "y":
                        peak["y"],

                    "prominence":
                        peak["prominence"]
                }
            )

        peaks = sorted(
            converted,
            key=lambda p:
                p["x"]
        )

    peaks = [
        p
        for p in peaks
        if (
            p["x"]
            >
            n * 0.015
            and
            p["x"]
            <
            n * 0.72
        )
    ]

    if len(peaks) >= 3:

        first_three = peaks[
            :3
        ]

        gap1 = (
            first_three[1]["x"]
            -
            first_three[0]["x"]
        )

        gap2 = (
            first_three[2]["x"]
            -
            first_three[1]["x"]
        )

        if (
            gap1
            >
            n * 0.045
            and
            gap2
            >
            n * 0.045
        ):

            return (
                float(
                    first_three[0]["y"]
                ),
                float(
                    first_three[1]["y"]
                ),
                float(
                    first_three[2]["y"]
                ),
                float(
                    h
                )
            )


    # フォールバック
    windows = [
        (
            0.02,
            0.26
        ),
        (
            0.17,
            0.43
        ),
        (
            0.34,
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

        if len(part) < 3:
            return None

        values.append(
            float(
                np.min(
                    part
                )
            )
        )

    return (
        values[0],
        values[1],
        values[2],
        float(
            h
        )
    )


# =========================================================
# 足型
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
        h < 80
        or
        w < 40
    ):

        return (
            "判定困難",
            0.0
        )

    detected = detect_three_toes(
        mask,
        big_toe_side
    )

    if detected is None:

        return (
            "判定困難",
            0.0
        )

    big, second, third, foot_length = (
        detected
    )


    # =====================================================
    # スクエア
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

    if spread <= 0.016:

        return (
            "スクエア型",
            0.88
        )


    # =====================================================
    # ギリシャ
    # 第2趾が親指より明確に長い
    # =====================================================
    greek_difference = (
        big
        -
        second
    ) / foot_length

    if greek_difference > 0.012:

        confidence = min(
            0.95,
            0.79
            +
            greek_difference
            *
            5
        )

        return (
            "ギリシャ型",
            confidence
        )


    # =====================================================
    # その他はエジプト
    # =====================================================
    egypt_difference = (
        second
        -
        big
    ) / foot_length

    confidence = min(
        0.97,
        0.86
        +
        max(
            0,
            egypt_difference
        )
        *
        4
    )

    return (
        "エジプト型",
        confidence
    )


# =========================================================
# 色
# =========================================================
def color_analysis(
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
        brightness
        >
        45
    )

    valid &= (
        brightness
        <
        248
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
            ][valid]
        )
    )

    S = float(
        np.median(
            hsv[
                :,
                :,
                1
            ][valid]
        )
    )

    V = float(
        np.median(
            hsv[
                :,
                :,
                2
            ][valid]
        )
    )

    A = float(
        np.median(
            lab[
                :,
                :,
                1
            ][valid]
        )
    )

    B = float(
        np.median(
            lab[
                :,
                :,
                2
            ][valid]
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
        5
        <
        H
        <=
        17
        and
        S >= 45
    ):

        result = "オレンジ寄り"

    elif (
        17
        <
        H
        <=
        32
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
            "H": round(
                H,
                1
            ),
            "S": round(
                S,
                1
            ),
            "V": round(
                V,
                1
            )
        }
    )


# =========================================================
# 乾燥・角質
# =========================================================
def texture_and_callus(
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

    if len(xs) < 80:

        return (
            dryness,
            "なし"
        )

    all_y, all_x = np.where(
        mask > 0
    )

    if len(all_x) == 0:

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
        cx
        -
        x1
    ) / max(
        1,
        x2
        -
        x1
    )

    ny = (
        cy
        -
        y1
    ) / max(
        1,
        y2
        -
        y1
    )

    if ny > 0.72:

        callus = "かかと"

    elif ny < 0.45:

        callus = "前足部"

    elif nx < 0.35:

        callus = "左側"

    elif nx > 0.65:

        callus = "右側"

    else:

        callus = "中央"

    return (
        dryness,
        callus
    )


# =========================================================
# 結果統合
# =========================================================
def unify_shape(
    result1,
    result2
):

    shape1, conf1 = result1
    shape2, conf2 = result2

    if (
        shape1 == shape2
        and
        shape1 != "判定困難"
    ):

        return (
            shape1,
            max(
                conf1,
                conf2
            )
        )

    if shape1 == "判定困難":

        return (
            shape2,
            conf2
        )

    if shape2 == "判定困難":

        return (
            shape1,
            conf1
        )


    # エジプト / ギリシャで割れたら
    # 明確な差でなければエジプト優先
    if {
        shape1,
        shape2
    } == {
        "エジプト型",
        "ギリシャ型"
    }:

        if shape1 == "エジプト型":

            egypt_conf = conf1
            greek_conf = conf2

        else:

            egypt_conf = conf2
            greek_conf = conf1

        if (
            greek_conf
            >
            egypt_conf
            +
            0.14
        ):

            return (
                "ギリシャ型",
                greek_conf
            )

        return (
            "エジプト型",
            max(
                egypt_conf,
                0.86
            )
        )


    if conf1 >= conf2:

        return (
            shape1,
            conf1
        )

    return (
        shape2,
        conf2
    )


# =========================================================
# 両足分割
# =========================================================
def split_both_rgb(
    rgb
):

    _, w = rgb.shape[
        :2
    ]

    middle = (
        w // 2
    )

    overlap = int(
        w * 0.02
    )

    return (
        rgb[
            :,
            :min(
                w,
                middle
                +
                overlap
            )
        ].copy(),

        rgb[
            :,
            max(
                0,
                middle
                -
                overlap
            ):
        ].copy()
    )


# =========================================================
# 全解析
# =========================================================
def analyze_images(
    both_rgb=None,
    right_rgb=None,
    left_rgb=None
):

    shape_results = []

    representative_rgb = None
    representative_mask = None


    # =====================================================
    # 右足単体
    # 精度が高いので優先
    # =====================================================
    if right_rgb is not None:

        mask = segment_foot(
            right_rgb
        )

        result = classify_foot_shape(
            right_rgb,
            mask,
            big_toe_side="left"
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
                        0.04
                    )
                )
            )

        if representative_rgb is None:

            representative_rgb = right_rgb
            representative_mask = mask


    # =====================================================
    # 左足単体
    # =====================================================
    if left_rgb is not None:

        mask = segment_foot(
            left_rgb
        )

        result = classify_foot_shape(
            left_rgb,
            mask,
            big_toe_side="right"
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
                        0.04
                    )
                )
            )

        if representative_rgb is None:

            representative_rgb = left_rgb
            representative_mask = mask


    # =====================================================
    # 両足写真
    # =====================================================
    if both_rgb is not None:

        left_part, right_part = (
            split_both_rgb(
                both_rgb
            )
        )

        left_mask = segment_foot(
            left_part
        )

        left_result = classify_foot_shape(
            left_part,
            left_mask,
            big_toe_side="right"
        )


        right_mask = segment_foot(
            right_part
        )

        right_result = classify_foot_shape(
            right_part,
            right_mask,
            big_toe_side="left"
        )


        both_result = unify_shape(
            left_result,
            right_result
        )

        if both_result[
            0
        ] != "判定困難":

            shape_results.append(
                both_result
            )


        # 他に単体写真がない場合のみ
        # 両足の片側を色などに使用
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

                representative_rgb = right_part
                representative_mask = right_mask

            else:

                representative_rgb = left_part
                representative_mask = left_mask


        del left_part
        del right_part
        del left_mask
        del right_mask


    # =====================================================
    # 最終足型
    # =====================================================
    if not shape_results:

        overall_shape = "判定困難"
        overall_conf = 0.0

    else:

        overall_shape, overall_conf = (
            shape_results[
                0
            ]
        )

        for result in shape_results[
            1:
        ]:

            (
                overall_shape,
                overall_conf
            ) = unify_shape(
                (
                    overall_shape,
                    overall_conf
                ),
                result
            )


    # =====================================================
    # 色・乾燥
    # =====================================================
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
        callus = "判定困難"

    else:

        foot_color, color_info = (
            color_analysis(
                representative_rgb,
                representative_mask
            )
        )

        dryness, callus = (
            texture_and_callus(
                representative_rgb,
                representative_mask
            )
        )


    gc.collect()


    return {
        "overall_shape":
            overall_shape,

        "shape_conf":
            overall_conf,

        "foot_color":
            foot_color,

        "color_info":
            color_info,

        "dryness":
            dryness,

        "callus":
            callus
    }


# =========================================================
# 結果カード
# =========================================================
def result_card(
    title,
    body,
    card_class
):

    st.markdown(
        f"### {title}"
    )

    st.markdown(
        f"""
<div class="result-card {card_class}">
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
        "Q3. 長時間歩いたり立っていると、足が疲れやすいですか？",
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
            "角質",
            "靴が合いにくい",
            "歩き方が気になる"
        ]
    )

    st.markdown(
        '<div class="question-space"></div>',
        unsafe_allow_html=True
    )


    # =====================================================
    # Q7
    # =====================================================
    st.write(
        "Q7. 今、疲れを感じる場所はありますか？"
    )

    fatigue_area = []

    q7_col1, q7_col2 = st.columns(
        2
    )

    with q7_col1:

        if st.checkbox(
            "頭・目",
            key="fatigue_head"
        ):

            fatigue_area.append(
                "頭・目"
            )

        if st.checkbox(
            "肩",
            key="fatigue_shoulder"
        ):

            fatigue_area.append(
                "肩"
            )

        if st.checkbox(
            "腰",
            key="fatigue_waist"
        ):

            fatigue_area.append(
                "腰"
            )

        if st.checkbox(
            "脚",
            key="fatigue_leg"
        ):

            fatigue_area.append(
                "脚"
            )


    with q7_col2:

        if st.checkbox(
            "首",
            key="fatigue_neck"
        ):

            fatigue_area.append(
                "首"
            )

        if st.checkbox(
            "背中",
            key="fatigue_back"
        ):

            fatigue_area.append(
                "背中"
            )

        if st.checkbox(
            "胃まわり",
            key="fatigue_stomach"
        ):

            fatigue_area.append(
                "胃まわり"
            )

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

        st.session_state.cold = cold
        st.session_state.swelling = swelling
        st.session_state.tired = tired
        st.session_state.standing = standing
        st.session_state.shoes = shoes

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
下の3種類の写真のうち、1枚以上アップロードしてください。
<br><br>
・両足の写真<br>
・右足の写真<br>
・左足の写真
<br><br>
<span class="guide-note">
※足の形をより正確に判定するため、可能であれば「両足・右足・左足」の3種類すべてを撮影することをおすすめします。
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
※足指からかかとまで画面に収め、できるだけ真正面から撮影してください。足指同士が重ならない写真がおすすめです。
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

            progress.progress(
                10
            )


            both_rgb = (
                uploaded_to_rgb(
                    both_feet
                )
                if both_feet
                is not None
                else
                None
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
                else
                None
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
                else
                None
            )


            progress.progress(
                50
            )

            status.write(
                "足裏を解析しています..."
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

            status.write(
                "解析完了"
            )


            st.session_state.step = 3

            st.rerun()


        except Exception as error:

            gc.collect()

            st.error(
                "画像解析中にエラーが発生しました。"
                "写真を減らすか、別の写真でお試しください。"
            )

            st.code(
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


    # =====================================================
    # スコア
    # =====================================================
    total_score = 100

    if cold == "はい":
        total_score -= 8

    if swelling == "はい":
        total_score -= 8

    if tired == "はい":
        total_score -= 10

    if standing == "はい":
        total_score -= 4

    if stumble == "はい":
        total_score -= 6

    if len(
        fatigue_area
    ) == 1:

        total_score -= 4

    elif len(
        fatigue_area
    ) >= 2:

        total_score -= 8


    if (
        analysis[
            "dryness"
        ]
        ==
        "やや乾燥"
    ):

        total_score -= 5

    elif (
        analysis[
            "dryness"
        ]
        ==
        "乾燥が目立つ"
    ):

        total_score -= 10


    if (
        analysis[
            "callus"
        ]
        not in [
            "なし",
            "判定困難"
        ]
    ):

        total_score -= 5


    if (
        analysis[
            "foot_color"
        ]
        ==
        "赤み強め"
    ):

        total_score -= 5

    elif (
        analysis[
            "foot_color"
        ]
        ==
        "オレンジ寄り"
    ):

        total_score -= 3

    elif (
        analysis[
            "foot_color"
        ]
        ==
        "白っぽい"
    ):

        total_score -= 4


    total_score = max(
        40,
        min(
            100,
            total_score
        )
    )


    if total_score >= 85:

        score_message = (
            "とても良いコンディションです"
        )

    elif total_score >= 70:

        score_message = (
            "比較的良いコンディションです"
        )

    elif total_score >= 55:

        score_message = (
            "少しセルフケアを意識したい状態です"
        )

    else:

        score_message = (
            "今日はゆっくりケアを意識しましょう"
        )


    st.markdown(
        f"""
<div class="step-box">
診断結果：{total_score}点
<div style="
font-family:'Yu Gothic',sans-serif;
font-size:13px;
font-weight:500;
margin-top:5px;
opacity:0.72;
">
{score_message}
</div>
</div>
""",
        unsafe_allow_html=True
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
    # 1 足形
    # =====================================================
    result_card(
        "1. 足の形",
        (
            f"<span class='result-main'>"
            f"{shape}"
            f"</span>"
        ),
        "card-beige"
    )


    # =====================================================
    # 2 色
    # =====================================================
    if color == "赤み強め":

        color_text = (
            "写真上では赤みが比較的強く見られます。"
            "リフレクソロジーでは、活動量が多い時や"
            "緊張感が高まっている時の傾向として"
            "捉える考え方があります。"
        )

    elif color == "オレンジ寄り":

        color_text = (
            "写真上ではオレンジ寄りの色味が見られます。"
            "リフレクソロジーでは、活動性が高い一方で、"
            "疲れもたまりやすい状態として"
            "捉える考え方があります。"
        )

    elif color == "黄み強め":

        color_text = (
            "写真上では黄みが比較的強く見られます。"
            "リフレクソロジーでは、気分転換や休息を"
            "意識したい時の傾向として"
            "捉える考え方があります。"
        )

    elif color == "白っぽい":

        color_text = (
            "写真上では白っぽい色味が見られます。"
            "リフレクソロジーでは、休息やリラックスを"
            "意識したい状態として"
            "捉える考え方があります。"
        )

    elif color == "判定困難":

        color_text = (
            "今回の写真では足の色を"
            "安定して判定できませんでした。"
        )

    else:

        color_text = (
            "写真上では大きな色味の偏りは"
            "目立ちません。"
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
    # 3 心身
    # =====================================================
    rest_score = 0

    if color == "赤み強め":
        rest_score += 2

    elif color == "オレンジ寄り":
        rest_score += 1

    elif color == "白っぽい":
        rest_score += 1

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


    if rest_score >= 7:

        mind_body = (
            "診断結果より、現在は疲れが蓄積しやすく、"
            "心身ともに休息を意識したい傾向です。"
            "睡眠やゆったり過ごす時間を"
            "確保することを意識してみましょう。"
        )

    elif rest_score >= 4:

        mind_body = (
            "診断結果より、やや疲れがたまりやすい傾向です。"
            "普段の生活の中に短時間の休息や"
            "気分転換を取り入れるのがおすすめです。"
        )

    else:

        mind_body = (
            "診断結果より、現在は比較的"
            "バランスが取れている傾向です。"
            "今の状態を保ちながら、"
            "こまめなセルフケアを取り入れてみましょう。"
        )


    result_card(
        "3. 心身傾向",
        mind_body,
        "card-green"
    )


    # =====================================================
    # 4 歩き方
    # =====================================================
    walk_points = []

    if sole_wear == "かかとの外側":

        walk_points.append(
            "靴底の減り方から、足の外側へ"
            "荷重しやすい傾向が考えられます。"
        )

    elif sole_wear == "かかとの内側":

        walk_points.append(
            "靴底の減り方から、足の内側へ"
            "荷重しやすい傾向が考えられます。"
        )

    elif sole_wear == "つま先側":

        walk_points.append(
            "前足部へ負担が集まりやすい"
            "傾向が考えられます。"
        )

    elif sole_wear == "全体的に均等":

        walk_points.append(
            "靴底の減り方からは、"
            "大きな偏りは目立たない傾向です。"
        )


    callus = (
        analysis[
            "callus"
        ]
    )

    if callus == "前足部":

        walk_points.append(
            "写真上でも前足部への負担が"
            "比較的大きい可能性があります。"
        )

    elif callus == "かかと":

        walk_points.append(
            "写真上ではかかと側への負担が"
            "比較的大きい可能性があります。"
        )


    if stumble == "はい":

        walk_points.append(
            "つまずきやすさがあるため、"
            "歩行時の足の上げ方も意識してみましょう。"
        )


    if not walk_points:

        walk_points.append(
            "今回の診断では、歩き方に"
            "大きな偏りは明確には見られませんでした。"
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
            "ラウンドトゥ系スニーカー・"
            "ウォーキングシューズ"
        )

        shoe_detail = (
            "親指が最も長い足型のため、"
            "親指側を圧迫しにくいラウンドトゥがおすすめです。"
            "親指の前に適度な余裕があるモデルを選びましょう。"
        )

    elif shape == "ギリシャ型":

        shoe_title = (
            "前足部に余裕のあるスニーカー・"
            "ウォーキングシューズ"
        )

        shoe_detail = (
            "第2趾が長い足型のため、"
            "第2趾が靴先に当たりにくいよう、"
            "つま先方向に余裕がある靴がおすすめです。"
        )

    elif shape == "スクエア型":

        shoe_title = (
            "ワイドタイプのスニーカー・"
            "幅広ウォーキングシューズ"
        )

        shoe_detail = (
            "親指・第2趾・第3趾の長さが近いため、"
            "指先を横に広げやすい"
            "ワイドトゥボックスがおすすめです。"
        )

    else:

        shoe_title = (
            "つま先に余裕のあるスニーカー"
        )

        shoe_detail = (
            "足幅と足長に合い、"
            "指先を圧迫しにくい靴を選ぶのがおすすめです。"
        )


    if tired == "はい":

        shoe_detail += (
            "<br><br>"
            "足が疲れやすい傾向もあるため、"
            "クッション性の高さも重視しましょう。"
        )


    if standing == "はい":

        shoe_detail += (
            "<br><br>"
            "立っている時間が長いため、"
            "かかと周りの安定感もポイントです。"
        )


    result_card(
        "5. おすすめの靴",
        (
            f"<span class='result-main'>"
            f"{shoe_title}"
            f"</span>"
            "<br><br>"
            f"{shoe_detail}"
        ),
        "card-cream"
    )


    # =====================================================
    # 6 性格
    # =====================================================
    if shape == "エジプト型":

        personality = (
            "足型を使ったエンタメ診断では、"
            "落ち着きがあり、自分のペースを大切にする"
            "タイプとして捉えられることがあります。"
        )

    elif shape == "ギリシャ型":

        personality = (
            "足型を使ったエンタメ診断では、"
            "好奇心や行動力があり、"
            "新しいことへ積極的なタイプとして"
            "捉えられることがあります。"
        )

    elif shape == "スクエア型":

        personality = (
            "足型を使ったエンタメ診断では、"
            "安定感があり、物事を着実に進める"
            "現実派タイプとして捉えられることがあります。"
        )

    else:

        personality = (
            "今回は足型を明確に判定できなかったため、"
            "性格傾向も判定困難となりました。"
        )


    result_card(
        "6. 足から見る性格傾向",
        (
            personality
            +
            "<br><br>"
            "※足の形から科学的に性格を判断するものではなく、"
            "エンタメとしての診断です。"
        ),
        "card-lavender"
    )


    # =====================================================
    # 7 反射区
    # =====================================================
    reflex_map = {

        "頭・目": (
            "足の親指周辺"
        ),

        "首": (
            "親指の付け根周辺"
        ),

        "肩": (
            "足指の付け根から小指側"
        ),

        "背中": (
            "足裏の内側ライン"
        ),

        "腰": (
            "土踏まずの内側からかかと寄り"
        ),

        "胃まわり": (
            "土踏まずの上部周辺"
        ),

        "脚": (
            "かかと周辺"
        ),

        "全身": (
            "足裏全体"
        )
    }


    if fatigue_area:

        reflex_blocks = []

        for area in fatigue_area:

            zone = (
                reflex_map[
                    area
                ]
            )

            reflex_blocks.append(
                f"<span class='care-title'>"
                f"{area}"
                f"</span>"
                "<br>"
                f"おすすめ部位：{zone}"
                "<br>"
                "リフレクソロジーでは、この周辺を"
                "対応する反射区として扱います。"
                "心地よい程度の強さで、"
                "5〜10秒ほどゆっくり刺激してみてください。"
            )

        reflex_text = (
            "<br><br>".join(
                reflex_blocks
            )
        )

    else:

        reflex_text = (
            "特に疲労箇所は選択されていません。"
            "足裏全体を心地よい強さで"
            "ゆっくりほぐすのがおすすめです。"
        )


    result_card(
        "7. 疲労箇所・反射区",
        reflex_text,
        "card-rose"
    )


    # =====================================================
    # 8 アロマ
    # =====================================================
    aroma_map = {

        "リラックス": (
            "ラベンダー",
            "ゆっくり過ごしたい時間や、"
            "気持ちを落ち着けたい時に取り入れやすい香りです。"
        ),

        "リフレッシュ": (
            "レモン",
            "気持ちを切り替えたい時に"
            "取り入れやすい爽やかな香りです。"
        ),

        "集中": (
            "ローズマリー",
            "仕事や勉強など、集中したい時間に"
            "取り入れやすい香りです。"
        ),

        "睡眠": (
            "ラベンダー",
            "就寝前など、落ち着いて過ごしたい時間に"
            "取り入れやすい香りです。"
        ),

        "気分転換": (
            "スイートオレンジ",
            "気分を切り替えたい時に取り入れやすい"
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
    care_blocks = []


    if swelling == "はい":

        care_blocks.append(
            "<span class='care-title'>"
            "むくみケアのため"
            "</span>"
            "<br>"
            "足首をゆっくり回したり、"
            "ふくらはぎを無理のない範囲で軽く動かしてみましょう。"
        )


    if cold == "はい":

        care_blocks.append(
            "<span class='care-title'>"
            "冷え対策のため"
            "</span>"
            "<br>"
            "足湯や靴下などを活用し、"
            "足元を心地よく温める時間をつくるのがおすすめです。"
        )


    if tired == "はい":

        care_blocks.append(
            "<span class='care-title'>"
            "足の疲労ケアのため"
            "</span>"
            "<br>"
            "帰宅後などに足を休ませる時間をつくり、"
            "軽いストレッチを取り入れてみましょう。"
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

        care_blocks.append(
            "<span class='care-title'>"
            "足裏の乾燥ケアのため"
            "</span>"
            "<br>"
            "入浴後など、皮膚が清潔な状態で"
            "保湿ケアを取り入れるのがおすすめです。"
        )


    if stumble == "はい":

        care_blocks.append(
            "<span class='care-title'>"
            "歩行時の安定を意識するため"
            "</span>"
            "<br>"
            "無理のない範囲で足首を動かし、"
            "歩く時には足先を少し上げることを意識してみましょう。"
        )


    if not care_blocks:

        care_blocks.append(
            "<span class='care-title'>"
            "日々のコンディション維持のため"
            "</span>"
            "<br>"
            "足裏の保湿や軽いストレッチを"
            "定期的に取り入れるのがおすすめです。"
        )


    result_card(
        "9. セルフケア",
        "<br><br>".join(
            care_blocks
        ),
        "card-green"
    )


    # =====================================================
    # 免責
    # =====================================================
    st.markdown(
        """
<div class="disclaimer">
このサービスは医療行為・医学的診断を目的としたものではありません。足の色は照明やカメラ補正などの影響を受けます。心身傾向・反射区・性格傾向には、リフレクソロジーやエンタメ的な考え方が含まれます。強い痛み、しびれ、傷、急な腫れ、色の大きな変化などがある場合は、必要に応じて医療機関等へ相談してください。
</div>
""",
        unsafe_allow_html=True
    )


    if st.button(
        "最初から診断する",
        use_container_width=True
    ):

        # 古い解析結果も捨てる
        if "analysis" in st.session_state:

            del st.session_state[
                "analysis"
            ]

        gc.collect()

        st.session_state.step = 1

        st.rerun()