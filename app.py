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
    padding-top: 4.2rem;
    padding-bottom: 4rem;
}

.top-credit {
    text-align: right;
    font-size: 10px;
    color: #AAAAAA;
    opacity: 0.78;
    letter-spacing: 0.04em;
    margin-top: -28px;
    margin-bottom: 5px;
}

.main-title {
    text-align: center;

    font-family:
        "Yu Mincho",
        "Hiragino Mincho ProN",
        "YuMincho",
        serif;

    font-size: 2.5rem;
    font-weight: 600;

    letter-spacing: 0.08em;

    line-height: 1.5;

    color: #405348;

    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
}

.english-title {
    text-align: center;

    color: #9B806E;

    font-size: 0.76rem;

    letter-spacing: 0.20em;

    font-weight: 600;

    margin-bottom: 2.3rem;
}

.step-box {
    padding: 14px 19px;

    border-radius: 15px;

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

    margin-bottom: 1.5rem;
}

.guide-card {
    background: #FBF7F0;

    border: 1px solid #EDE2D5;

    border-radius: 16px;

    padding: 18px 20px;

    margin-top: 5px;
    margin-bottom: 20px;

    color: #4F4A45;

    line-height: 1.9;
}

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

@media (max-width: 600px) {

    .block-container {
        padding-top: 3.8rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .top-credit {
        font-size: 8px;
        margin-top: -22px;
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
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# 作成者
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
                grab_mask == cv2.GC_FGD
            )
            |
            (
                grab_mask == cv2.GC_PR_FGD
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
# 足だけ切り抜き
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
# 足の傾き補正
# =========================================================
def straighten_foot(
    rgb,
    mask
):

    ys, xs = np.where(
        mask > 0
    )

    if len(xs) < 100:
        return rgb, mask

    points = np.column_stack(
        (
            xs,
            ys
        )
    ).astype(
        np.float32
    )

    mean, eigenvectors = cv2.PCACompute(
        points,
        mean=None
    )

    if eigenvectors is None:
        return rgb, mask

    vx = float(
        eigenvectors[0][0]
    )

    vy = float(
        eigenvectors[0][1]
    )

    angle = np.degrees(
        np.arctan2(
            vy,
            vx
        )
    )

    rotation = (
        angle
        -
        90.0
    )

    h, w = mask.shape

    center = (
        w / 2,
        h / 2
    )

    matrix = cv2.getRotationMatrix2D(
        center,
        rotation,
        1.0
    )

    rotated_rgb = cv2.warpAffine(
        rgb,
        matrix,
        (
            w,
            h
        ),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(
            255,
            255,
            255
        )
    )

    rotated_mask = cv2.warpAffine(
        mask,
        matrix,
        (
            w,
            h
        ),
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0
    )

    return (
        rotated_rgb,
        rotated_mask
    )


# =========================================================
# 指先を上に補正
# =========================================================
def ensure_toes_top(
    rgb,
    mask
):

    h, w = mask.shape

    band = max(
        8,
        int(
            h * 0.20
        )
    )

    top = mask[
        :band
    ]

    bottom = mask[
        -band:
    ]

    top_width = (
        np.count_nonzero(
            top
        )
        /
        max(
            1,
            band
        )
    )

    bottom_width = (
        np.count_nonzero(
            bottom
        )
        /
        max(
            1,
            band
        )
    )

    if (
        bottom_width
        >
        top_width * 1.08
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
# 平滑化
# =========================================================
def smooth_curve(
    curve,
    window
):

    if len(curve) < 5:
        return curve

    window = max(
        5,
        window
    )

    if window % 2 == 0:
        window += 1

    if window >= len(curve):

        window = max(
            5,
            len(curve) // 3
        )

        if window % 2 == 0:
            window += 1

    kernel = np.ones(
        window,
        dtype=np.float32
    ) / float(
        window
    )

    return np.convolve(
        curve,
        kernel,
        mode="same"
    )


# =========================================================
# 指先候補
# =========================================================
def detect_toe_tips(mask):

    h, w = mask.shape

    toe_height = int(
        h * 0.45
    )

    toe_mask = mask[
        :toe_height
    ]

    top_curve = np.full(
        w,
        np.nan,
        dtype=np.float32
    )

    for x in range(w):

        ys = np.where(
            toe_mask[
                :,
                x
            ] > 0
        )[0]

        if len(ys) > 0:

            top_curve[x] = float(
                np.percentile(
                    ys,
                    5
                )
            )

    valid_x = np.where(
        ~np.isnan(
            top_curve
        )
    )[0]

    if len(valid_x) < 30:
        return None

    x1 = int(
        valid_x.min()
    )

    x2 = int(
        valid_x.max()
    )

    curve = top_curve[
        x1:x2 + 1
    ]

    nans = np.isnan(
        curve
    )

    if np.any(nans):

        valid = np.where(
            ~nans
        )[0]

        if len(valid) < 2:
            return None

        curve[nans] = np.interp(
            np.where(
                nans
            )[0],
            valid,
            curve[valid]
        )

    window = max(
        7,
        int(
            len(curve)
            *
            0.025
        )
    )

    curve = smooth_curve(
        curve,
        window
    )

    candidates = []

    min_distance = max(
        8,
        int(
            len(curve)
            *
            0.10
        )
    )

    search_radius = max(
        8,
        int(
            len(curve)
            *
            0.06
        )
    )

    for i in range(
        search_radius,
        len(curve)
        -
        search_radius
    ):

        local = curve[
            i - search_radius:
            i + search_radius + 1
        ]

        if (
            curve[i]
            >
            np.min(local) + 0.5
        ):

            continue

        left_level = float(
            np.percentile(
                local[
                    :search_radius
                ],
                65
            )
        )

        right_level = float(
            np.percentile(
                local[
                    search_radius + 1:
                ],
                65
            )
        )

        prominence = (
            (
                left_level
                +
                right_level
            )
            /
            2
            -
            curve[i]
        )

        if prominence < (
            h * 0.008
        ):
            continue

        candidate = {
            "index": i,
            "x": x1 + i,
            "y": float(
                curve[i]
            ),
            "prominence": float(
                prominence
            )
        }

        if not candidates:

            candidates.append(
                candidate
            )

        else:

            nearest = min(
                candidates,
                key=lambda c:
                    abs(
                        c["index"]
                        -
                        i
                    )
            )

            if (
                abs(
                    nearest["index"]
                    -
                    i
                )
                <
                min_distance
            ):

                if (
                    prominence
                    >
                    nearest[
                        "prominence"
                    ]
                ):

                    candidates.remove(
                        nearest
                    )

                    candidates.append(
                        candidate
                    )

            else:

                candidates.append(
                    candidate
                )

    candidates = sorted(
        candidates,
        key=lambda c:
            c["prominence"],
        reverse=True
    )[:7]

    if len(candidates) >= 5:

        candidates = sorted(
            candidates,
            key=lambda c:
                c["y"]
        )[:5]

        candidates = sorted(
            candidates,
            key=lambda c:
                c["x"]
        )

        return candidates

    # フォールバック
    toe_width = (
        x2
        -
        x1
        +
        1
    )

    fallback = []

    for i in range(5):

        sx = int(
            x1
            +
            toe_width
            *
            i
            /
            5
        )

        ex = int(
            x1
            +
            toe_width
            *
            (
                i
                +
                1
            )
            /
            5
        )

        zone = mask[
            :toe_height,
            sx:ex
        ]

        ys, xs = np.where(
            zone > 0
        )

        if len(ys) == 0:
            return None

        y = float(
            np.percentile(
                ys,
                3
            )
        )

        x = float(
            sx
            +
            np.median(
                xs
            )
        )

        fallback.append(
            {
                "x": x,
                "y": y,
                "prominence": 0
            }
        )

    return fallback


# =========================================================
# 足の形判定
# =========================================================
def classify_foot_shape(
    rgb,
    big_toe_side
):

    mask = segment_foot(
        rgb
    )

    if mask is None:
        return "判定困難", 0.0

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

    if h < 100 or w < 50:
        return "判定困難", 0.0

    tips = detect_toe_tips(
        mask
    )

    if (
        tips is None
        or
        len(tips) != 5
    ):

        return "判定困難", 0.25

    tips = sorted(
        tips,
        key=lambda p:
            p["x"]
    )

    if big_toe_side == "right":

        ordered = list(
            reversed(
                tips
            )
        )

    else:

        ordered = tips

    ys = [
        float(
            p["y"]
        )
        for p in ordered
    ]

    big = ys[0]
    second = ys[1]
    third = ys[2]
    fourth = ys[3]
    fifth = ys[4]

    foot_length = max(
        1.0,
        float(h)
    )

    second_big = (
        second
        -
        big
    ) / foot_length

    third_big = (
        third
        -
        big
    ) / foot_length

    third_second = (
        third
        -
        second
    ) / foot_length

    # ギリシャ型
    if second_big < -0.015:

        confidence = min(
            0.95,
            0.70
            +
            abs(
                second_big
            )
            *
            6
        )

        return (
            "ギリシャ型",
            confidence
        )

    # エジプト型
    descending_pattern = (
        big
        <
        second
        and
        second
        <=
        third
        +
        h * 0.008
        and
        third
        <=
        fourth
        +
        h * 0.010
        and
        fourth
        <=
        fifth
        +
        h * 0.015
    )

    if (
        second_big > 0.015
        and
        third_big > 0.020
        and
        descending_pattern
    ):

        confidence = min(
            0.95,
            0.70
            +
            second_big
            *
            6
        )

        return (
            "エジプト型",
            confidence
        )

    # スクエア型
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

    if (
        first_three_range <= 0.018
        and
        abs(
            third_second
        )
        <=
        0.018
    ):

        return (
            "スクエア型",
            0.76
        )

    return (
        "判定困難",
        0.45
    )


# =========================================================
# 足の色
# =========================================================
def color_analysis(rgb):

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
        brightness > 45
    )

    valid &= (
        brightness < 248
    )

    if valid.sum() < 200:

        valid = (
            mask > 0
        )

    H = float(
        np.median(
            hsv[:, :, 0][valid]
        )
    )

    S = float(
        np.median(
            hsv[:, :, 1][valid]
        )
    )

    V = float(
        np.median(
            hsv[:, :, 2][valid]
        )
    )

    A = float(
        np.median(
            lab[:, :, 1][valid]
        )
    )

    B = float(
        np.median(
            lab[:, :, 2][valid]
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
            "H": round(H, 1),
            "S": round(S, 1),
            "V": round(V, 1),
            "a": round(A, 1),
            "b": round(B, 1)
        }
    )


# =========================================================
# 乾燥・角質
# =========================================================
def texture_and_callus(rgb):

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

        score = float(
            np.percentile(
                texture,
                75
            )
        )

    else:

        score = 0

    if score > 28:

        dryness = (
            "乾燥が目立つ"
        )

    elif score > 18:

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
        x2 - x1
    )

    ny = (
        cy
        -
        y1
    ) / max(
        1,
        y2 - y1
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
# 両足分割
# =========================================================
def split_both_feet(image):

    rgb = pil_to_rgb(
        image
    )

    h, w = rgb.shape[:2]

    middle = (
        w // 2
    )

    overlap = int(
        w * 0.04
    )

    left = rgb[
        :,
        :min(
            w,
            middle + overlap
        )
    ]

    right = rgb[
        :,
        max(
            0,
            middle - overlap
        ):
    ]

    return (
        left,
        right
    )


# =========================================================
# 全写真解析
# =========================================================
def analyze_uploaded_images(
    both_image=None,
    right_image=None,
    left_image=None
):

    left_shape = "未撮影"
    right_shape = "未撮影"

    left_conf = 0.0
    right_conf = 0.0

    both_left = None
    both_right = None

    if both_image is not None:

        (
            both_left,
            both_right
        ) = split_both_feet(
            both_image
        )

    if left_image is not None:

        left_rgb = pil_to_rgb(
            left_image
        )

        (
            left_shape,
            left_conf
        ) = classify_foot_shape(
            left_rgb,
            big_toe_side="right"
        )

    elif both_left is not None:

        (
            left_shape,
            left_conf
        ) = classify_foot_shape(
            both_left,
            big_toe_side="right"
        )

    if right_image is not None:

        right_rgb = pil_to_rgb(
            right_image
        )

        (
            right_shape,
            right_conf
        ) = classify_foot_shape(
            right_rgb,
            big_toe_side="left"
        )

    elif both_right is not None:

        (
            right_shape,
            right_conf
        ) = classify_foot_shape(
            both_right,
            big_toe_side="left"
        )

    valid_shapes = [
        s
        for s
        in [
            left_shape,
            right_shape
        ]
        if s
        not in [
            "未撮影",
            "判定困難"
        ]
    ]

    if len(valid_shapes) == 2:

        if (
            valid_shapes[0]
            ==
            valid_shapes[1]
        ):

            overall_shape = (
                valid_shapes[0]
            )

        else:

            overall_shape = (
                "左右で異なる"
            )

    elif len(valid_shapes) == 1:

        overall_shape = (
            valid_shapes[0]
        )

    else:

        overall_shape = (
            "判定困難"
        )

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

    fatigue_area = st.multiselect(
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
        ]
    )

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

    # HTMLタグがそのまま表示されないよう、
    # 1行のHTMLとして出す
    st.markdown(
        """
<div class="guide-card">
下の3つのうち、どれか1枚以上アップロードしてください。<br><br>
足の形をより正確に判定するには、両足または右左の足どちらかを1枚ずつ真正面から撮影した写真がおすすめです。<br><br>
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

    col1, col2 = st.columns(
        2
    )

    with col1:

        if st.button(
            "戻る"
        ):

            st.session_state.step = 1

            st.rerun()

    with col2:

        diagnose = st.button(
            "診断する",
            type="primary",
            disabled=not has_photo
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
    # 総合スコア
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
<div style="font-size:13px; margin-top:5px; font-weight:500; opacity:0.75;">
{score_message}
</div>
</div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 1. 足の形
    # =====================================================
    shape_detail = ""

    if (
        analysis[
            "left_shape"
        ]
        !=
        "未撮影"
    ):

        shape_detail += (
            "左足："
            +
            analysis[
                "left_shape"
            ]
        )

        if (
            analysis[
                "left_shape"
            ]
            !=
            "判定困難"
        ):

            shape_detail += (
                f"（判定度 "
                f"{analysis['left_shape_conf'] * 100:.0f}%）"
            )

    if (
        analysis[
            "right_shape"
        ]
        !=
        "未撮影"
    ):

        if shape_detail:

            shape_detail += "<br>"

        shape_detail += (
            "右足："
            +
            analysis[
                "right_shape"
            ]
        )

        if (
            analysis[
                "right_shape"
            ]
            !=
            "判定困難"
        ):

            shape_detail += (
                f"（判定度 "
                f"{analysis['right_shape_conf'] * 100:.0f}%）"
            )

    result_card(
        "1. 足の形",
        (
            "<span class='result-main'>"
            +
            analysis[
                "overall_shape"
            ]
            +
            "</span>"
            +
            "<br><br>"
            +
            shape_detail
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
    shape = (
        analysis[
            "overall_shape"
        ]
    )

    if shape == "エジプト型":

        shoe_title = (
            "ラウンドトゥ系スニーカー・"
            "ウォーキングシューズ"
        )

        shoe_detail = (
            "親指が最も長い傾向があるため、"
            "親指側を圧迫しにくいラウンドトゥがおすすめです。"
            "親指の前に適度な余裕があるモデルを選びましょう。"
        )

    elif shape == "ギリシャ型":

        shoe_title = (
            "前足部に余裕のあるスニーカー・"
            "ウォーキングシューズ"
        )

        shoe_detail = (
            "第2趾が長い傾向があるため、"
            "第2趾が靴先に当たりにくいよう"
            "つま先方向に余裕がある靴がおすすめです。"
            "ランニング系スニーカーも選択肢になります。"
        )

    elif shape == "スクエア型":

        shoe_title = (
            "ワイドタイプのスニーカー・"
            "幅広ウォーキングシューズ"
        )

        shoe_detail = (
            "親指から第3趾あたりまでの長さが近いため、"
            "指先を横に広げやすいワイドトゥボックスが"
            "おすすめです。"
        )

    elif shape == "左右で異なる":

        shoe_title = (
            "フィット感を調整しやすいスニーカー"
        )

        shoe_detail = (
            "左右で足型の特徴が異なるため、"
            "靴紐などで左右それぞれのフィット感を"
            "調整しやすい靴がおすすめです。"
        )

    else:

        shoe_title = (
            "つま先に余裕のあるスニーカー"
        )

        shoe_detail = (
            "今回の写真では足型を明確に判定できなかったため、"
            "足幅と足長に合い、指先を圧迫しにくい"
            "スニーカーがおすすめです。"
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
    # 6. 性格傾向
    # =====================================================
    if shape == "エジプト型":

        personality = (
            "足型を使ったエンタメ診断では、"
            "落ち着きがあり、自分のペースを大切にする"
            "タイプとして捉えられることがあります。"
            "物事をじっくり考えてから行動する傾向とされています。"
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

    elif shape == "左右で異なる":

        personality = (
            "左右で異なる特徴があるため、"
            "慎重さと行動力を状況によって"
            "使い分けるタイプとして楽しむことができます。"
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
            "特定の場所だけでなく、"
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
                f"<span class='care-title'>{area}</span>"
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
        "7. 疲労箇所とおすすめ反射区",
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
            f"<span class='result-main'>{aroma}</span>"
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


    st.divider()

    st.caption(
        "このサービスは医療行為・医学的診断を"
        "目的としたものではありません。"
        "足の色は照明やカメラ補正などの影響を受けます。"
        "心身傾向・反射区・性格傾向には、"
        "リフレクソロジーやエンタメ的な考え方が含まれます。"
        "強い痛み、しびれ、傷、急な腫れ、"
        "色の大きな変化などがある場合は、"
        "必要に応じて医療機関等へ相談してください。"
    )


    if st.button(
        "最初から診断する"
    ):

        st.session_state.step = 1

        st.rerun()