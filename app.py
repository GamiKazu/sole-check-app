import cv2
import numpy as np
import streamlit as st
from PIL import Image


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
# デザイン
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


/* =========================
   Created by
========================= */

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


/* =========================
   タイトル
========================= */

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


/* =========================
   STEP
========================= */

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


/* =========================
   STEP2説明
========================= */

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

    font-size: 0.68rem;

    line-height: 1.55;
}


/* 撮影補足 */
.photo-note {
    color: #969696;

    font-size: 0.66rem;

    line-height: 1.55;

    margin-top: 18px;
    margin-bottom: 18px;
}


/* =========================
   ファイルアップロード補足非表示
========================= */

div[data-testid="stFileUploader"] small {
    display: none !important;
}

div[data-testid="stFileUploaderDropzoneInstructions"] small {
    display: none !important;
}


/* =========================
   結果カード
========================= */

.result-card {
    border-radius: 18px;

    padding: 21px 22px;

    margin-bottom: 24px;

    line-height: 1.85;

    color: #363636;

    border:
        1px solid
        rgba(70, 90, 75, 0.09);

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


/* =========================
   注意書き
========================= */

.disclaimer {
    font-size: 0.56rem;

    line-height: 1.5;

    color: #AAAAAA;

    margin-top: 10px;
    margin-bottom: 18px;
}


/* =========================
   見出し
========================= */

h3 {
    font-family:
        "Yu Mincho",
        "Hiragino Mincho ProN",
        serif !important;

    color: #42564A !important;

    letter-spacing: 0.03em;
}


/* =========================
   ボタン
========================= */

div.stButton > button {
    width: 100%;

    min-height: 52px;

    border-radius: 14px;

    font-size: 16px;

    font-weight: 700;
}


/* 戻る / 診断 を横並び固定 */
.st-key-nav_buttons [data-testid="stHorizontalBlock"] {
    display: flex !important;

    flex-direction: row !important;

    flex-wrap: nowrap !important;

    gap: 0.75rem !important;
}

.st-key-nav_buttons [data-testid="column"] {
    flex: 1 1 50% !important;

    width: 50% !important;

    min-width: 0 !important;
}


/* =========================
   スマホ
========================= */

@media (max-width: 600px) {

    .block-container {
        padding-top: 2.9rem;

        padding-left: 1rem;
        padding-right: 1rem;
    }

    .top-credit {
        font-size: 8px;

        margin-top: 27px;
        margin-bottom: 10px;

        padding-right: 2px;
    }

    .main-title {
        font-size: 2rem;
    }

    .english-title {
        font-size: 0.66rem;

        letter-spacing: 0.14em;
    }

    .result-card {
        padding: 18px;
    }

    h3 {
        font-size: 1.04rem !important;
    }

    .guide-note {
        font-size: 0.61rem;
    }

    .photo-note {
        font-size: 0.60rem;

        margin-top: 20px;
    }

    .disclaimer {
        font-size: 0.50rem;
    }

    .st-key-nav_buttons [data-testid="stHorizontalBlock"] {
        display: flex !important;

        flex-direction: row !important;

        flex-wrap: nowrap !important;
    }

    .st-key-nav_buttons [data-testid="column"] {
        flex: 1 1 50% !important;

        width: 50% !important;

        min-width: 0 !important;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# Created by
# =========================================================
st.markdown(
    """
<div class="top-credit">
Created by GamiKazu
</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# タイトル
# =========================================================
st.markdown(
    """
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
# 基本関数
# =========================================================
def pil_to_rgb(image):

    return np.array(
        image.convert("RGB")
    )


def largest_contour(mask):

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
# 足領域抽出
# =========================================================
def segment_foot(rgb):

    h, w = rgb.shape[:2]

    if h < 80 or w < 50:
        return None

    bgr = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2BGR
    )

    grab_mask = np.zeros(
        (h, w),
        np.uint8
    )

    mx = max(
        2,
        int(w * 0.04)
    )

    my = max(
        2,
        int(h * 0.03)
    )

    rect = (
        mx,
        my,
        max(
            2,
            w - mx * 2
        ),
        max(
            2,
            h - my * 2
        )
    )

    bgd = np.zeros(
        (1, 65),
        np.float64
    )

    fgd = np.zeros(
        (1, 65),
        np.float64
    )

    try:

        cv2.grabCut(
            bgr,
            grab_mask,
            rect,
            bgd,
            fgd,
            4,
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

    except cv2.error:

        gray = cv2.cvtColor(
            bgr,
            cv2.COLOR_BGR2GRAY
        )

        _, binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY
            +
            cv2.THRESH_OTSU
        )

    kernel = np.ones(
        (5, 5),
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

    area_ratio = (
        cv2.contourArea(
            contour
        )
        /
        float(
            h * w
        )
    )

    if area_ratio < 0.07:
        return None

    clean = np.zeros_like(
        binary
    )

    cv2.drawContours(
        clean,
        [contour],
        -1,
        255,
        -1
    )

    return clean


# =========================================================
# マスク範囲へ切り抜き
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
# 回転時に画像が切れないようにする
# =========================================================
def rotate_bound(
    image,
    angle,
    interpolation,
    border_value
):

    h, w = image.shape[:2]

    center = (
        w / 2.0,
        h / 2.0
    )

    matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0
    )

    cos = abs(
        matrix[0, 0]
    )

    sin = abs(
        matrix[0, 1]
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

    matrix[0, 2] += (
        new_w / 2.0
        -
        center[0]
    )

    matrix[1, 2] += (
        new_h / 2.0
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
# 足の長軸を縦にする
# =========================================================
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

    if len(contour) < 5:

        return (
            rgb,
            mask
        )

    try:

        rect = cv2.minAreaRect(
            contour
        )

        (
            center,
            size,
            angle
        ) = rect

        rw, rh = size

        if rw > rh:

            rotate_angle = (
                angle
            )

        else:

            rotate_angle = (
                angle
                -
                90
            )

        rotated_rgb = rotate_bound(
            rgb,
            rotate_angle,
            cv2.INTER_LINEAR,
            (
                255,
                255,
                255
            )
        )

        rotated_mask = rotate_bound(
            mask,
            rotate_angle,
            cv2.INTER_NEAREST,
            0
        )

        return (
            rotated_rgb,
            rotated_mask
        )

    except cv2.error:

        return (
            rgb,
            mask
        )


# =========================================================
# 横方向の幅を測る
# =========================================================
def row_width(
    mask,
    start_ratio,
    end_ratio
):

    h, _ = mask.shape

    y1 = int(
        h * start_ratio
    )

    y2 = int(
        h * end_ratio
    )

    widths = []

    for y in range(
        max(
            0,
            y1
        ),
        min(
            h,
            y2
        )
    ):

        xs = np.where(
            mask[y] > 0
        )[0]

        if len(xs) > 0:

            widths.append(
                float(
                    xs.max()
                    -
                    xs.min()
                    +
                    1
                )
            )

    if not widths:
        return 0.0

    return float(
        np.median(
            widths
        )
    )


# =========================================================
# 指先側を上に統一
# =========================================================
def ensure_toes_top(
    rgb,
    mask
):

    top_width = row_width(
        mask,
        0.02,
        0.25
    )

    bottom_width = row_width(
        mask,
        0.75,
        0.98
    )

    # 通常、指側の方がかかと側より広い
    if (
        bottom_width
        >
        top_width
    ):

        rgb = np.rot90(
            rgb,
            2
        )

        mask = np.rot90(
            mask,
            2
        )

    return (
        rgb,
        mask
    )


# =========================================================
# 1次元データ平滑化
# =========================================================
def smooth_1d(
    values,
    sigma
):

    array = np.asarray(
        values,
        dtype=np.float32
    ).reshape(
        1,
        -1
    )

    k = max(
        5,
        int(
            sigma * 6
        )
        |
        1
    )

    result = cv2.GaussianBlur(
        array,
        (
            k,
            1
        ),
        sigmaX=sigma
    )

    return result.reshape(
        -1
    )


# =========================================================
# 足指の上側輪郭を作る
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

        if len(ys) > 0:

            # 数ピクセルのノイズ対策
            curve[x] = float(
                np.percentile(
                    ys,
                    4
                )
            )

    valid = np.where(
        np.isfinite(
            curve
        )
    )[0]

    if len(valid) < 40:
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

    sigma = max(
        1.5,
        len(
            curve
        )
        *
        0.008
    )

    curve = smooth_1d(
        curve,
        sigma
    )

    return (
        curve,
        x1,
        x2
    )


# =========================================================
# 輪郭から局所的な指先候補を検出
# =========================================================
def find_tip_candidates(
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

    min_gap = max(
        7,
        int(
            n * 0.075
        )
    )

    raw = []

    for i in range(
        radius,
        n - radius
    ):

        local = curve[
            i - radius:
            i + radius + 1
        ]

        if curve[i] > (
            np.min(
                local
            )
            +
            0.8
        ):

            continue

        left = curve[
            max(
                0,
                i - radius
            ):
            i
        ]

        right = curve[
            i + 1:
            min(
                n,
                i + radius + 1
            )
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
        ) / 2.0

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
            0.0035
        ):

            continue

        raw.append(
            {
                "i":
                    i,

                "y":
                    float(
                        curve[i]
                    ),

                "prominence":
                    prominence
            }
        )


    # 同じ指の周辺から複数候補が出るのを防止
    raw = sorted(
        raw,
        key=lambda p:
            p["prominence"],
        reverse=True
    )

    selected = []

    for candidate in raw:

        too_close = False

        for chosen in selected:

            if (
                abs(
                    chosen["i"]
                    -
                    candidate["i"]
                )
                <
                min_gap
            ):

                too_close = True
                break

        if not too_close:

            selected.append(
                candidate
            )

        if len(selected) >= 7:
            break

    return sorted(
        selected,
        key=lambda p:
            p["i"]
    )


# =========================================================
# 指先を3本取得
# =========================================================
def detect_three_toes(
    mask,
    big_toe_side
):

    built = build_top_curve(
        mask
    )

    if built is None:
        return None

    curve, x1, x2 = (
        built
    )

    h, _ = mask.shape

    candidates = find_tip_candidates(
        curve,
        h
    )

    n = len(
        curve
    )


    # =====================================================
    # 親指側が必ず左になるよう内部的に反転
    # =====================================================
    if big_toe_side == "right":

        medial_curve = curve[
            ::-1
        ]

        medial_candidates = []

        for p in candidates:

            medial_candidates.append(
                {
                    "i":
                        n
                        -
                        1
                        -
                        p["i"],

                    "y":
                        p["y"],

                    "prominence":
                        p["prominence"]
                }
            )

        medial_candidates = sorted(
            medial_candidates,
            key=lambda p:
                p["i"]
        )

    else:

        medial_curve = curve.copy()

        medial_candidates = candidates


    # =====================================================
    # 端の輪郭を指と誤認しない
    # =====================================================
    start_limit = int(
        n * 0.025
    )

    end_limit = int(
        n * 0.70
    )

    filtered = [
        p
        for p
        in medial_candidates
        if (
            p["i"]
            >=
            start_limit
            and
            p["i"]
            <=
            end_limit
        )
    ]


    # =====================================================
    # 実際の輪郭候補から
    # 親指 → 第2趾 → 第3趾
    # =====================================================
    first_three = []

    min_spacing = max(
        6,
        int(
            n * 0.07
        )
    )

    for p in filtered:

        if not first_three:

            first_three.append(
                p
            )

        else:

            if (
                p["i"]
                -
                first_three[
                    -1
                ]["i"]
                >=
                min_spacing
            ):

                first_three.append(
                    p
                )

        if len(first_three) == 3:
            break


    # =====================================================
    # 輪郭候補が足りない場合は
    # 解剖学的な検索範囲を使って補完
    # =====================================================
    if len(first_three) < 3:

        # 親指・第2趾・第3趾の
        # おおよその位置
        search_windows = [
            (
                0.02,
                0.27
            ),
            (
                0.17,
                0.42
            ),
            (
                0.34,
                0.59
            )
        ]

        fallback = []

        for start_ratio, end_ratio in search_windows:

            sx = int(
                n
                *
                start_ratio
            )

            ex = int(
                n
                *
                end_ratio
            )

            if ex <= sx:

                return None

            section = medial_curve[
                sx:ex
            ]

            if len(section) < 3:

                return None

            local_index = int(
                np.argmin(
                    section
                )
            )

            index = (
                sx
                +
                local_index
            )

            fallback.append(
                {
                    "i":
                        index,

                    "y":
                        float(
                            medial_curve[
                                index
                            ]
                        ),

                    "prominence":
                        0.0
                }
            )

        first_three = fallback


    if len(first_three) != 3:
        return None


    first_three = sorted(
        first_three,
        key=lambda p:
            p["i"]
    )


    # 同じ山を重複して取っていないかチェック
    if (
        first_three[1]["i"]
        -
        first_three[0]["i"]
        <
        n * 0.045
    ):

        return None

    if (
        first_three[2]["i"]
        -
        first_three[1]["i"]
        <
        n * 0.045
    ):

        return None


    big = float(
        first_three[0]["y"]
    )

    second = float(
        first_three[1]["y"]
    )

    third = float(
        first_three[2]["y"]
    )

    return (
        big,
        second,
        third,
        float(
            h
        )
    )


# =========================================================
# 足型判定
#
# スクエア:
# 親指・第2趾・第3趾がほぼ同じ
#
# ギリシャ:
# 第2趾が親指より長い
#
# それ以外:
# エジプト
# =========================================================
def classify_foot_shape(
    rgb,
    big_toe_side
):

    mask = segment_foot(
        rgb
    )

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
        h < 100
        or
        w < 45
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


    (
        big,
        second,
        third,
        foot_length
    ) = detected


    # yが小さいほど指が長い

    first_three_range = (
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


    # =====================================================
    # 1. スクエア型
    # =====================================================
    square_threshold = 0.016

    if (
        first_three_range
        <=
        square_threshold
    ):

        return (
            "スクエア型",
            0.88
        )


    # =====================================================
    # 2. ギリシャ型
    #
    # 第2趾が親指より明確に長い場合だけ
    # 小さな撮影誤差ではギリシャにしない
    # =====================================================
    greek_difference = (
        big
        -
        second
    ) / foot_length

    greek_threshold = 0.010

    if (
        greek_difference
        >
        greek_threshold
    ):

        confidence = min(
            0.96,
            0.80
            +
            greek_difference
            *
            5.0
        )

        return (
            "ギリシャ型",
            confidence
        )


    # =====================================================
    # 3. その他はエジプト型
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
            0.0,
            egypt_difference
        )
        *
        4.0
    )

    return (
        "エジプト型",
        confidence
    )


# =========================================================
# 足の色
# =========================================================
def color_analysis(
    rgb
):

    mask = segment_foot(
        rgb
    )

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


    if valid.sum() < 200:

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

        result = (
            "白っぽい"
        )


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

        result = (
            "赤み強め"
        )


    elif (
        5 < H <= 17
        and
        S >= 45
    ):

        result = (
            "オレンジ寄り"
        )


    elif (
        17 < H <= 32
        and
        S >= 45
        and
        B >= 135
    ):

        result = (
            "黄み強め"
        )


    else:

        result = (
            "標準的な色味"
        )


    return (
        result,
        {
            "H":
                round(
                    H,
                    1
                ),

            "S":
                round(
                    S,
                    1
                ),

            "V":
                round(
                    V,
                    1
                ),

            "a":
                round(
                    A,
                    1
                ),

            "b":
                round(
                    B,
                    1
                )
        }
    )


# =========================================================
# 乾燥・角質
# =========================================================
def texture_and_callus(
    rgb
):

    mask = segment_foot(
        rgb
    )

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
        cv2.CV_64F
    )


    texture = np.abs(
        lap
    )[
        mask > 0
    ]


    if texture.size:

        texture_score = float(
            np.percentile(
                texture,
                75
            )
        )

    else:

        texture_score = 0


    if texture_score > 28:

        dryness = (
            "乾燥が目立つ"
        )


    elif texture_score > 18:

        dryness = (
            "やや乾燥"
        )


    else:

        dryness = (
            "乾燥は目立たない"
        )


    lab = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2LAB
    )


    light = lab[
        :,
        :,
        0
    ]

    yellow = lab[
        :,
        :,
        2
    ]


    candidates = (
        (
            mask > 0
        )
        &
        (
            light > 145
        )
        &
        (
            yellow > 138
        )
    )


    ys, xs = np.where(
        candidates
    )


    if len(xs) < 100:

        return (
            dryness,
            "なし"
        )


    all_y, all_x = np.where(
        mask > 0
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

        callus = (
            "かかと"
        )


    elif ny < 0.45:

        callus = (
            "前足部"
        )


    elif nx < 0.35:

        callus = (
            "左側"
        )


    elif nx > 0.65:

        callus = (
            "右側"
        )


    else:

        callus = (
            "中央"
        )


    return (
        dryness,
        callus
    )


# =========================================================
# 両足写真を左右へ分割
# =========================================================
def split_both_feet(
    image
):

    rgb = pil_to_rgb(
        image
    )

    h, w = rgb.shape[
        :2
    ]


    middle = (
        w // 2
    )


    # 足同士が少し中央へ寄っていても
    # 切れないよう軽くオーバーラップ
    overlap = int(
        w * 0.03
    )


    left_part = rgb[
        :,
        :min(
            w,
            middle
            +
            overlap
        )
    ]


    right_part = rgb[
        :,
        max(
            0,
            middle
            -
            overlap
        ):
    ]


    return (
        left_part,
        right_part
    )


# =========================================================
# 両足結果を1タイプへ統一
# =========================================================
def unify_both_shape(
    left_result,
    right_result
):

    (
        left_shape,
        left_conf
    ) = left_result


    (
        right_shape,
        right_conf
    ) = right_result


    # 両方同じならそのまま
    if (
        left_shape
        ==
        right_shape
        and
        left_shape
        !=
        "判定困難"
    ):

        return (
            left_shape,
            max(
                left_conf,
                right_conf
            )
        )


    # 片方だけ判定可能
    if (
        left_shape
        !=
        "判定困難"
        and
        right_shape
        ==
        "判定困難"
    ):

        return (
            left_shape,
            left_conf
        )


    if (
        right_shape
        !=
        "判定困難"
        and
        left_shape
        ==
        "判定困難"
    ):

        return (
            right_shape,
            right_conf
        )


    # 両方判定困難
    if (
        left_shape
        ==
        "判定困難"
        and
        right_shape
        ==
        "判定困難"
    ):

        return (
            "判定困難",
            0.0
        )


    # =====================================================
    # 左右で異なる場合
    #
    # エジプト vs ギリシャで僅差なら
    # 誤認識を考慮しエジプトを優先
    # =====================================================
    shapes = {
        left_shape,
        right_shape
    }


    if shapes == {
        "エジプト型",
        "ギリシャ型"
    }:

        if left_shape == "エジプト型":

            egypt_conf = (
                left_conf
            )

            greek_conf = (
                right_conf
            )

        else:

            egypt_conf = (
                right_conf
            )

            greek_conf = (
                left_conf
            )


        # ギリシャがかなり明確な時のみギリシャ
        if (
            greek_conf
            >
            egypt_conf
            +
            0.10
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


    # スクエアを含む場合などは
    # 信頼度が高い方
    if left_conf >= right_conf:

        return (
            left_shape,
            left_conf
        )


    return (
        right_shape,
        right_conf
    )


# =========================================================
# 全画像解析
# =========================================================
def analyze_uploaded_images(
    both_image=None,
    right_image=None,
    left_image=None
):

    left_shape = (
        "未撮影"
    )

    right_shape = (
        "未撮影"
    )


    left_conf = 0.0
    right_conf = 0.0


    # =====================================================
    # 両足写真を最初に解析
    # =====================================================
    if both_image is not None:

        (
            both_left,
            both_right
        ) = split_both_feet(
            both_image
        )


        both_left_result = classify_foot_shape(
            both_left,
            big_toe_side="right"
        )


        both_right_result = classify_foot_shape(
            both_right,
            big_toe_side="left"
        )


        (
            unified_shape,
            unified_conf
        ) = unify_both_shape(
            both_left_result,
            both_right_result
        )


        # 両足写真では必ず同一タイプ
        left_shape = (
            unified_shape
        )

        right_shape = (
            unified_shape
        )


        left_conf = (
            unified_conf
        )

        right_conf = (
            unified_conf
        )


    # =====================================================
    # 片足写真が両方存在する場合
    #
    # こちらの方が足が大きく写るため
    # 足型判定に優先利用
    # =====================================================
    individual_results = []


    if left_image is not None:

        left_rgb = pil_to_rgb(
            left_image
        )


        left_individual = classify_foot_shape(
            left_rgb,
            big_toe_side="right"
        )


        if (
            left_individual[0]
            !=
            "判定困難"
        ):

            individual_results.append(
                left_individual
            )


    if right_image is not None:

        right_rgb = pil_to_rgb(
            right_image
        )


        right_individual = classify_foot_shape(
            right_rgb,
            big_toe_side="left"
        )


        if (
            right_individual[0]
            !=
            "判定困難"
        ):

            individual_results.append(
                right_individual
            )


    # =====================================================
    # 片足写真が2枚ある場合も
    # 最終的には1タイプに統一
    # =====================================================
    if len(
        individual_results
    ) == 2:

        (
            final_shape,
            final_conf
        ) = unify_both_shape(
            individual_results[0],
            individual_results[1]
        )


        left_shape = (
            final_shape
        )

        right_shape = (
            final_shape
        )


        left_conf = (
            final_conf
        )

        right_conf = (
            final_conf
        )


    elif len(
        individual_results
    ) == 1:

        (
            final_shape,
            final_conf
        ) = individual_results[
            0
        ]


        # 片足写真1枚だけなら
        # その型を代表型として利用
        left_shape = (
            final_shape
        )

        right_shape = (
            final_shape
        )


        left_conf = (
            final_conf
        )

        right_conf = (
            final_conf
        )


    # =====================================================
    # 代表型
    # =====================================================
    if (
        left_shape
        not in [
            "未撮影",
            "判定困難"
        ]
    ):

        overall_shape = (
            left_shape
        )


    elif (
        right_shape
        not in [
            "未撮影",
            "判定困難"
        ]
    ):

        overall_shape = (
            right_shape
        )


    else:

        overall_shape = (
            "判定困難"
        )


    # =====================================================
    # 色・乾燥・角質用画像
    # =====================================================
    if both_image is not None:

        condition_rgb = pil_to_rgb(
            both_image
        )


    elif right_image is not None:

        condition_rgb = pil_to_rgb(
            right_image
        )


    else:

        condition_rgb = pil_to_rgb(
            left_image
        )


    (
        foot_color,
        color_info
    ) = color_analysis(
        condition_rgb
    )


    (
        dryness,
        callus
    ) = texture_and_callus(
        condition_rgb
    )


    return {
        "overall_shape":
            overall_shape,

        "left_shape":
            left_shape,

        "right_shape":
            right_shape,

        "left_shape_conf":
            left_conf,

        "right_shape_conf":
            right_conf,

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
# STEP 1
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
        "足が冷えやすいですか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )


    swelling = st.radio(
        "むくみを感じることがありますか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )


    tired = st.radio(
        "長時間歩いたり立っていると、足が疲れやすいですか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )


    standing = st.radio(
        "普段、立っている時間は長いですか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )


    shoes = st.selectbox(
        "普段よく履く靴は？",
        [
            "スニーカー",
            "革靴",
            "パンプス",
            "サンダル",
            "ブーツ",
            "その他"
        ]
    )


    foot_concern = st.selectbox(
        "足で一番気になることは？",
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


    # =====================================================
    # Select all / Choose options をなくす
    # =====================================================
    fatigue_area = st.pills(
        "今、疲れを感じる場所はありますか？",
        [
            "頭・目",
            "首",
            "肩",
            "背中",
            "腰",
            "胃まわり",
            "脚",
            "全身"
        ],
        selection_mode="multi"
    )


    if fatigue_area is None:

        fatigue_area = []


    sole_wear = st.selectbox(
        "靴底はどこが減りやすいですか？",
        [
            "分からない",
            "かかとの外側",
            "かかとの内側",
            "つま先側",
            "全体的に均等"
        ]
    )


    stumble = st.radio(
        "歩いている時につまずきやすいですか？",
        [
            "はい",
            "いいえ"
        ],
        horizontal=True
    )


    aroma_goal = st.selectbox(
        "今、一番求めているものは？",
        [
            "リラックス",
            "リフレッシュ",
            "集中",
            "睡眠",
            "気分転換"
        ]
    )


    if st.button(
        "次へ",
        type="primary"
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
            list(
                fatigue_area
            )
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
# STEP 2
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


    if both_feet:

        st.image(
            both_feet,
            caption="両足",
            use_container_width=True
        )


    if right_foot:

        st.image(
            right_foot,
            caption="右足",
            use_container_width=True
        )


    if left_foot:

        st.image(
            left_foot,
            caption="左足",
            use_container_width=True
        )


    has_photo = (
        both_feet is not None
        or
        right_foot is not None
        or
        left_foot is not None
    )


    # =====================================================
    # スマホでも横並び固定
    # =====================================================
    with st.container(
        key="nav_buttons"
    ):

        col1, col2 = st.columns(
            2,
            gap="small"
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

        with st.spinner(
            "足裏写真を解析しています..."
        ):

            both_image = (
                Image.open(
                    both_feet
                ).convert(
                    "RGB"
                )
                if both_feet
                else None
            )


            right_image = (
                Image.open(
                    right_foot
                ).convert(
                    "RGB"
                )
                if right_foot
                else None
            )


            left_image = (
                Image.open(
                    left_foot
                ).convert(
                    "RGB"
                )
                if left_foot
                else None
            )


            analysis = (
                analyze_uploaded_images(
                    both_image=both_image,
                    right_image=right_image,
                    left_image=left_image
                )
            )


            st.session_state.analysis = (
                analysis
            )


        st.session_state.step = 3

        st.rerun()


# =========================================================
# STEP 3
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
    # コンディションスコア
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


    # =====================================================
    # 1. 足の形
    # =====================================================
    shape = (
        analysis[
            "overall_shape"
        ]
    )


    shape_detail = (
        f"両足：{shape}"
    )


    result_card(
        "1. 足の形",
        (
            f"<span class='result-main'>"
            f"{shape}"
            f"</span>"
            "<br><br>"
            f"{shape_detail}"
        ),
        "card-beige"
    )


    # =====================================================
    # 2. 足の色
    # =====================================================
    color = (
        analysis[
            "foot_color"
        ]
    )


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
            "リフレクソロジーでは、疲れや気分転換を"
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
    # 3. 心身傾向
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
    # 4. 歩き方
    # =====================================================
    walk_points = []


    callus = (
        analysis[
            "callus"
        ]
    )


    if (
        sole_wear
        ==
        "かかとの外側"
    ):

        walk_points.append(
            "靴底の減り方から、足の外側へ"
            "荷重しやすい傾向が考えられます。"
        )


    elif (
        sole_wear
        ==
        "かかとの内側"
    ):

        walk_points.append(
            "靴底の減り方から、足の内側へ"
            "荷重しやすい傾向が考えられます。"
        )


    elif (
        sole_wear
        ==
        "つま先側"
    ):

        walk_points.append(
            "前足部へ負担が集まりやすい"
            "傾向が考えられます。"
        )


    elif (
        sole_wear
        ==
        "全体的に均等"
    ):

        walk_points.append(
            "靴底の減り方からは、"
            "大きな偏りは目立たない傾向です。"
        )


    if callus == "前足部":

        walk_points.append(
            "足裏写真でも前足部への負担が"
            "比較的大きい可能性があります。"
        )


    elif callus == "かかと":

        walk_points.append(
            "足裏写真では、かかと側への負担が"
            "比較的大きい可能性があります。"
        )


    elif callus in [
        "左側",
        "右側"
    ]:

        walk_points.append(
            f"写真上では足裏の{callus}に"
            "負担が偏っている可能性があります。"
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
    # 5. おすすめの靴
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
            "つま先方向に余裕のある靴がおすすめです。"
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
    # 6. 性格
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
    # 7. 反射区
    # =====================================================
    reflex_map = {

        "頭・目": (
            "足の親指周辺",
            "リフレクソロジーでは、"
            "親指周辺を頭部や目に対応する"
            "反射区として扱います。"
        ),

        "首": (
            "親指の付け根周辺",
            "リフレクソロジーでは、"
            "親指の付け根周辺を首まわりに対応する"
            "反射区として扱います。"
        ),

        "肩": (
            "足指の付け根から小指側",
            "リフレクソロジーでは、"
            "足指の付け根付近を肩まわりに対応する"
            "反射区として扱います。"
        ),

        "背中": (
            "足裏の内側ライン",
            "リフレクソロジーでは、"
            "足裏の内側を背中や背骨に対応する"
            "ラインとして扱います。"
        ),

        "腰": (
            "土踏まずの内側からかかと寄り",
            "リフレクソロジーでは、"
            "この周辺を腰まわりに対応する"
            "反射区として扱います。"
        ),

        "胃まわり": (
            "土踏まずの上部周辺",
            "リフレクソロジーでは、"
            "土踏まず上部を胃まわりに対応する"
            "反射区として扱います。"
        ),

        "脚": (
            "かかと周辺",
            "リフレクソロジーでは、"
            "かかと周辺を下半身のケアに"
            "用いる考え方があります。"
        ),

        "全身": (
            "足裏全体",
            "足裏全体を心地よい強さで"
            "ゆっくりほぐすのがおすすめです。"
        )
    }


    if fatigue_area:

        reflex_blocks = []


        for area in fatigue_area:

            zone, description = (
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
                f"{description}"
                "<br>"
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
            "現在、特に疲労箇所は選択されていません。"
            "足裏全体を心地よい強さで"
            "ゆっくりほぐすセルフケアがおすすめです。"
        )


    result_card(
        "7. 疲労箇所・反射区",
        reflex_text,
        "card-rose"
    )


    # =====================================================
    # 8. アロマ
    # =====================================================
    aroma_map = {

        "リラックス": (
            "ラベンダー",
            "ゆっくり過ごしたい時間や、"
            "気持ちを落ち着けたい時に"
            "取り入れやすい香りです。"
        ),

        "リフレッシュ": (
            "レモン",
            "気持ちを切り替えたい時や、"
            "すっきりした気分で過ごしたい時に"
            "取り入れやすい香りです。"
        ),

        "集中": (
            "ローズマリー",
            "仕事や勉強など、"
            "集中したい時間に取り入れやすい香りです。"
        ),

        "睡眠": (
            "ラベンダー",
            "就寝前など、"
            "落ち着いて過ごしたい時間に"
            "取り入れやすい香りです。"
        ),

        "気分転換": (
            "スイートオレンジ",
            "気分を切り替えたい時に"
            "取り入れやすい、やわらかな柑橘系の香りです。"
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
    # 9. セルフケア
    # =====================================================
    care_blocks = []


    if swelling == "はい":

        care_blocks.append(
            "<span class='care-title'>"
            "むくみケアのため"
            "</span>"
            "<br>"
            "足首をゆっくり回したり、"
            "ふくらはぎを無理のない範囲で"
            "軽く動かしてみましょう。"
        )


    if cold == "はい":

        care_blocks.append(
            "<span class='care-title'>"
            "冷え対策のため"
            "</span>"
            "<br>"
            "足湯や靴下などを活用し、"
            "足元を心地よく温める時間を"
            "つくるのがおすすめです。"
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


    if (
        analysis[
            "callus"
        ]
        not in [
            "なし",
            "判定困難"
        ]
    ):

        care_blocks.append(
            "<span class='care-title'>"
            "足裏への負担を減らすため"
            "</span>"
            "<br>"
            "角質が目立つ部分に負担が集中していないか、"
            "靴のサイズや履き心地を確認してみましょう。"
        )


    if stumble == "はい":

        care_blocks.append(
            "<span class='care-title'>"
            "歩行時の安定を意識するため"
            "</span>"
            "<br>"
            "無理のない範囲で足首を動かし、"
            "歩く時には足先を少し上げることを"
            "意識してみましょう。"
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
        "最初から診断する"
    ):

        st.session_state.step = 1

        st.rerun()