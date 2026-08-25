import cv2
import numpy as np
import streamlit as st
from PIL import Image


st.set_page_config(
    page_title="足裏タイプ診断",
    layout="centered"
)


# =========================================================
# セッション状態
# =========================================================
if "step" not in st.session_state:
    st.session_state.step = 1


# =========================================================
# デザイン
# =========================================================
st.markdown("""
<style>

.block-container {
    max-width: 720px;
    padding-top: 4.5rem;
    padding-bottom: 3rem;
}

.main-title {
    text-align: center;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.5;
    margin-top: 0.5rem;
    margin-bottom: 0.6rem;
}

.sub-title {
    text-align: center;
    opacity: 0.65;
    line-height: 1.7;
    margin-bottom: 2rem;
}

.result-card {
    padding: 18px 20px;
    border-radius: 12px;
    background-color: #f5f5f5;
    color: #222222;
    margin-bottom: 18px;
    line-height: 1.8;
}

.result-main {
    font-size: 1.08rem;
    font-weight: 700;
}

div.stButton > button {
    width: 100%;
    min-height: 50px;
    font-size: 17px;
    font-weight: bold;
    border-radius: 10px;
}

@media (max-width: 600px) {
    .block-container {
        padding-top: 4rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .main-title {
        font-size: 1.9rem;
    }

    .sub-title {
        font-size: 0.95rem;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 基本関数
# =========================================================
def pil_to_rgb(image):
    return np.array(image.convert("RGB"))


def largest_contour(mask):
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    return max(contours, key=cv2.contourArea)


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

    mask = np.zeros(
        (h, w),
        np.uint8
    )

    margin_x = max(2, int(w * 0.06))
    margin_y = max(2, int(h * 0.04))

    rect = (
        margin_x,
        margin_y,
        max(2, w - margin_x * 2),
        max(2, h - margin_y * 2)
    )

    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(
            bgr,
            mask,
            rect,
            bgd,
            fgd,
            4,
            cv2.GC_INIT_WITH_RECT
        )

        binary = np.where(
            (mask == cv2.GC_FGD)
            |
            (mask == cv2.GC_PR_FGD),
            255,
            0
        ).astype("uint8")

    except cv2.error:

        gray = cv2.cvtColor(
            bgr,
            cv2.COLOR_BGR2GRAY
        )

        _, binary = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

    kernel = np.ones(
        (7, 7),
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

    contour = largest_contour(binary)

    if contour is None:
        return None

    area_ratio = (
        cv2.contourArea(contour)
        /
        float(h * w)
    )

    if area_ratio < 0.08:
        return None

    clean = np.zeros_like(binary)

    cv2.drawContours(
        clean,
        [contour],
        -1,
        255,
        thickness=-1
    )

    return clean


def crop_to_mask(rgb, mask):

    ys, xs = np.where(mask > 0)

    if len(xs) == 0:
        return rgb, mask

    x1 = xs.min()
    x2 = xs.max()
    y1 = ys.min()
    y2 = ys.max()

    return (
        rgb[y1:y2 + 1, x1:x2 + 1],
        mask[y1:y2 + 1, x1:x2 + 1]
    )


def ensure_toes_top(rgb, mask):

    h, w = mask.shape

    band = max(
        5,
        int(h * 0.22)
    )

    top_width = (
        np.count_nonzero(mask[:band] > 0)
        /
        band
    )

    bottom_width = (
        np.count_nonzero(mask[-band:] > 0)
        /
        band
    )

    if bottom_width > top_width * 1.10:

        return (
            np.rot90(rgb, 2),
            np.rot90(mask, 2)
        )

    return rgb, mask


# =========================================================
# 足の形
# =========================================================
def classify_foot_shape(rgb, big_toe_side):

    mask = segment_foot(rgb)

    if mask is None:
        return "判定困難", 0.0

    rgb, mask = crop_to_mask(
        rgb,
        mask
    )

    rgb, mask = ensure_toes_top(
        rgb,
        mask
    )

    h, w = mask.shape

    if h < 80 or w < 50:
        return "判定困難", 0.0

    toe_h = int(h * 0.40)

    toe_mask = mask[:toe_h].copy()

    contours, _ = cv2.findContours(
        toe_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )

    if not contours:
        return "判定困難", 0.0

    contour = max(
        contours,
        key=cv2.contourArea
    )

    points = contour[:, 0, :]

    top_by_x = {}

    for x, y in points:

        if x not in top_by_x:
            top_by_x[x] = y

        else:
            top_by_x[x] = min(
                top_by_x[x],
                y
            )

    xs = sorted(
        top_by_x.keys()
    )

    if len(xs) < 20:
        return "判定困難", 0.0

    curve = np.array(
        [top_by_x[x] for x in xs],
        dtype=np.float32
    )

    kernel_size = 9

    if len(curve) >= kernel_size:

        curve = np.convolve(
            curve,
            np.ones(kernel_size) / kernel_size,
            mode="same"
        )

    inv = -curve

    candidate_indices = []

    min_distance = max(
        8,
        int(len(xs) * 0.08)
    )

    for i in range(
        2,
        len(inv) - 2
    ):

        if (
            inv[i] > inv[i - 1]
            and
            inv[i] >= inv[i + 1]
            and
            inv[i] > inv[i - 2]
            and
            inv[i] >= inv[i + 2]
        ):

            if all(
                abs(i - old) >= min_distance
                for old in candidate_indices
            ):

                candidate_indices.append(i)

    candidate_indices = sorted(
        candidate_indices,
        key=lambda i: curve[i]
    )

    candidate_indices = candidate_indices[:7]

    candidate_indices = sorted(
        candidate_indices
    )

    if len(candidate_indices) < 4:
        return "判定困難", 0.0

    candidates = []

    for idx in candidate_indices:

        x = xs[idx]
        y = float(curve[idx])

        nx = x / max(1, w)

        if 0.03 < nx < 0.97:
            candidates.append((x, y))

    if len(candidates) < 4:
        return "判定困難", 0.0

    if len(candidates) > 5:

        candidates = sorted(
            candidates,
            key=lambda p: p[1]
        )[:5]

        candidates = sorted(
            candidates,
            key=lambda p: p[0]
        )

    if len(candidates) != 5:
        return "判定困難", 0.0

    if big_toe_side == "right":
        ordered = list(
            reversed(candidates)
        )

    else:
        ordered = candidates

    big_y = ordered[0][1]
    second_y = ordered[1][1]
    third_y = ordered[2][1]

    norm = max(
        1.0,
        float(toe_h)
    )

    big_vs_second = (
        second_y - big_y
    ) / norm

    second_vs_third = (
        third_y - second_y
    ) / norm

    big_vs_third = (
        third_y - big_y
    ) / norm

    # ギリシャ型
    if big_vs_second < -0.045:

        confidence = min(
            0.95,
            0.65
            +
            abs(big_vs_second)
            *
            3.0
        )

        return "ギリシャ型", confidence

    # エジプト型
    if (
        big_vs_second > 0.045
        and
        big_vs_third > 0.04
    ):

        confidence = min(
            0.95,
            0.65
            +
            big_vs_second
            *
            3.0
        )

        return "エジプト型", confidence

    # スクエア型
    if (
        abs(big_vs_second) <= 0.04
        and
        abs(second_vs_third) <= 0.04
    ):

        return "スクエア型", 0.72

    return "判定困難", 0.40


# =========================================================
# 足の色
# =========================================================
def color_analysis(rgb):

    mask = segment_foot(rgb)

    if mask is None:
        return "判定困難", {}

    hsv = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2HSV
    )

    lab = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2LAB
    )

    valid = mask > 0

    brightness = hsv[:, :, 2]

    valid &= brightness > 45
    valid &= brightness < 248

    if valid.sum() < 200:
        valid = mask > 0

    H = float(
        np.median(hsv[:, :, 0][valid])
    )

    S = float(
        np.median(hsv[:, :, 1][valid])
    )

    V = float(
        np.median(hsv[:, :, 2][valid])
    )

    A = float(
        np.median(lab[:, :, 1][valid])
    )

    B = float(
        np.median(lab[:, :, 2][valid])
    )

    if S < 35 and V > 185:

        result = "白っぽい"

    elif (
        (H <= 5 or H >= 176)
        and
        S >= 55
        and
        A >= 135
    ):

        result = "赤み強め"

    elif (
        H > 5
        and
        H <= 17
        and
        S >= 45
    ):

        result = "オレンジ寄り"

    elif (
        H > 17
        and
        H <= 32
        and
        S >= 45
        and
        B >= 135
    ):

        result = "黄み強め"

    else:

        result = "標準的な色味"

    return result, {
        "H": round(H, 1),
        "S": round(S, 1),
        "V": round(V, 1),
        "a": round(A, 1),
        "b": round(B, 1)
    }


# =========================================================
# 乾燥・角質
# =========================================================
def texture_and_callus(rgb):

    mask = segment_foot(rgb)

    if mask is None:
        return "判定困難", "判定困難"

    gray = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2GRAY
    )

    lap = cv2.Laplacian(
        gray,
        cv2.CV_64F
    )

    texture = np.abs(lap)[mask > 0]

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
        dryness = "乾燥が目立つ"

    elif texture_score > 18:
        dryness = "やや乾燥"

    else:
        dryness = "乾燥は目立たない"

    lab = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2LAB
    )

    light = lab[:, :, 0]
    yellow = lab[:, :, 2]

    candidates = (
        (mask > 0)
        &
        (light > 145)
        &
        (yellow > 138)
    )

    ys, xs = np.where(candidates)

    if len(xs) < 100:
        callus = "なし"

    else:

        all_y, all_x = np.where(
            mask > 0
        )

        x1 = all_x.min()
        x2 = all_x.max()
        y1 = all_y.min()
        y2 = all_y.max()

        cx = float(xs.mean())
        cy = float(ys.mean())

        nx = (
            cx - x1
        ) / max(1, x2 - x1)

        ny = (
            cy - y1
        ) / max(1, y2 - y1)

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

    return dryness, callus


# =========================================================
# 両足分割
# =========================================================
def split_both_feet(image):

    rgb = pil_to_rgb(image)

    h, w = rgb.shape[:2]

    middle = w // 2
    overlap = int(w * 0.03)

    left = rgb[
        :,
        :min(w, middle + overlap)
    ]

    right = rgb[
        :,
        max(0, middle - overlap):
    ]

    return left, right


# =========================================================
# 両足解析
# =========================================================
def analyze_both_feet(image):

    left_rgb, right_rgb = split_both_feet(
        image
    )

    left_shape, left_conf = classify_foot_shape(
        left_rgb,
        big_toe_side="right"
    )

    right_shape, right_conf = classify_foot_shape(
        right_rgb,
        big_toe_side="left"
    )

    full_rgb = pil_to_rgb(image)

    color, color_info = color_analysis(
        full_rgb
    )

    dryness, callus = texture_and_callus(
        full_rgb
    )

    valid_shapes = [
        shape
        for shape in [
            left_shape,
            right_shape
        ]
        if shape != "判定困難"
    ]

    if (
        len(valid_shapes) == 2
        and
        valid_shapes[0] == valid_shapes[1]
    ):
        overall_shape = valid_shapes[0]

    elif len(valid_shapes) == 2:
        overall_shape = "左右で異なる"

    elif len(valid_shapes) == 1:
        overall_shape = valid_shapes[0]

    else:
        overall_shape = "判定困難"

    return {
        "overall_shape": overall_shape,
        "left_shape": left_shape,
        "right_shape": right_shape,
        "left_shape_conf": left_conf,
        "right_shape_conf": right_conf,
        "foot_color": color,
        "color_info": color_info,
        "dryness": dryness,
        "callus": callus
    }


# =========================================================
# 結果カード
# =========================================================
def result_card(title, body):

    st.markdown(
        f"### {title}"
    )

    st.markdown(
        f"""
        <div class="result-card">
        {body}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# タイトル
# =========================================================
st.markdown(
    '<div class="main-title">'
    '足裏タイプ診断'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '簡単な質問と足裏写真から、'
    '足の特徴とセルフケアのヒントを診断します'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# STEP 1
# =========================================================
if st.session_state.step == 1:

    st.subheader(
        "STEP 1　簡単な質問"
    )

    cold = st.radio(
        "足が冷えやすいですか？",
        ["はい", "いいえ"],
        horizontal=True
    )

    swelling = st.radio(
        "むくみを感じることがありますか？",
        ["はい", "いいえ"],
        horizontal=True
    )

    tired = st.radio(
        "長時間歩いたり立っていると、足が疲れやすいですか？",
        ["はい", "いいえ"],
        horizontal=True
    )

    standing = st.radio(
        "普段、立っている時間は長いですか？",
        ["はい", "いいえ"],
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
        ["はい", "いいえ"],
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

    st.subheader(
        "STEP 2　足裏写真"
    )

    st.write(
        "両足の足裏が確認できる写真をアップロードしてください。"
    )

    both_feet = st.file_uploader(
        "両足の写真（必須）",
        type=["jpg", "jpeg", "png"],
        key="both_feet"
    )

    st.caption(
        "両足を並べ、足指からかかとまで正面から写してください。"
        "明るい場所で、足指が重ならないように撮影すると判定しやすくなります。"
    )

    right_foot = st.file_uploader(
        "右足のアップ写真（任意）",
        type=["jpg", "jpeg", "png"],
        key="right_foot"
    )

    left_foot = st.file_uploader(
        "左足のアップ写真（任意）",
        type=["jpg", "jpeg", "png"],
        key="left_foot"
    )

    if both_feet:

        st.image(
            both_feet,
            caption="両足",
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    with col1:

        if st.button("戻る"):

            st.session_state.step = 1
            st.rerun()

    with col2:

        diagnose = st.button(
            "診断する",
            type="primary",
            disabled=not both_feet
        )

    if diagnose:

        with st.spinner(
            "足裏写真を解析しています..."
        ):

            image = Image.open(
                both_feet
            ).convert("RGB")

            analysis = analyze_both_feet(
                image
            )

            # 右足アップを優先
            if right_foot:

                right_image = pil_to_rgb(
                    Image.open(
                        right_foot
                    ).convert("RGB")
                )

                rshape, rconf = classify_foot_shape(
                    right_image,
                    big_toe_side="left"
                )

                if rshape != "判定困難":

                    analysis["right_shape"] = rshape
                    analysis["right_shape_conf"] = rconf

            # 左足アップを優先
            if left_foot:

                left_image = pil_to_rgb(
                    Image.open(
                        left_foot
                    ).convert("RGB")
                )

                lshape, lconf = classify_foot_shape(
                    left_image,
                    big_toe_side="right"
                )

                if lshape != "判定困難":

                    analysis["left_shape"] = lshape
                    analysis["left_shape_conf"] = lconf

            left_shape = analysis["left_shape"]
            right_shape = analysis["right_shape"]

            if (
                left_shape != "判定困難"
                and
                right_shape != "判定困難"
            ):

                if left_shape == right_shape:
                    analysis["overall_shape"] = left_shape

                else:
                    analysis["overall_shape"] = "左右で異なる"

            elif left_shape != "判定困難":

                analysis["overall_shape"] = left_shape

            elif right_shape != "判定困難":

                analysis["overall_shape"] = right_shape

            else:
                analysis["overall_shape"] = "判定困難"

            st.session_state.analysis = analysis

        st.session_state.step = 3
        st.rerun()


# =========================================================
# STEP 3
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

    st.subheader("診断結果")


    # =====================================================
    # 1. 足の形
    # =====================================================
    shape_body = (
        f"<span class='result-main'>{analysis['overall_shape']}</span>"
        "<br><br>"
        f"左足：{analysis['left_shape']}"
        f"（判定度 {analysis['left_shape_conf'] * 100:.0f}%）"
        "<br>"
        f"右足：{analysis['right_shape']}"
        f"（判定度 {analysis['right_shape_conf'] * 100:.0f}%）"
    )

    result_card(
        "1. 足の形",
        shape_body
    )


    # =====================================================
    # 2. 足の色
    # =====================================================
    color = analysis["foot_color"]

    if color == "赤み強め":

        color_text = (
            "写真上では赤みが比較的強く見られます。"
            "リフレクソロジーでは、活動量が多い時や"
            "緊張感が高まっている時の傾向として捉える考え方があります。"
        )

    elif color == "オレンジ寄り":

        color_text = (
            "写真上ではオレンジ寄りの色味が見られます。"
            "リフレクソロジーでは、活動性が高い一方で、"
            "疲れも蓄積しやすい状態として捉える考え方があります。"
        )

    elif color == "黄み強め":

        color_text = (
            "写真上では黄みが比較的強く見られます。"
            "リフレクソロジーでは、疲労や気分転換を"
            "意識したい時の傾向として捉える考え方があります。"
        )

    elif color == "白っぽい":

        color_text = (
            "写真上では白っぽい色味が見られます。"
            "リフレクソロジーでは、休息やリラックスを"
            "意識したい状態として捉える考え方があります。"
        )

    elif color == "判定困難":

        color_text = (
            "今回の写真では足の色を安定して判定できませんでした。"
        )

    else:

        color_text = (
            "写真上では大きな色味の偏りは目立ちません。"
        )

    result_card(
        "2. 足の色",
        (
            f"<span class='result-main'>{color}</span>"
            "<br><br>"
            f"{color_text}"
        )
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

    if len(fatigue_area) >= 2:
        rest_score += 2

    elif len(fatigue_area) == 1:
        rest_score += 1

    if rest_score >= 7:

        mind_body = (
            "診断結果より、現在は疲れが蓄積しやすく、"
            "心身ともに休息を意識したい傾向です。"
            "無理に活動量を増やすより、睡眠やリラックスする時間を"
            "しっかり確保するのがおすすめです。"
        )

    elif rest_score >= 4:

        mind_body = (
            "診断結果より、やや疲れがたまりやすい傾向です。"
            "普段の活動は維持しつつ、短時間でも身体を休める時間や"
            "気分転換を取り入れるとよいでしょう。"
        )

    else:

        mind_body = (
            "診断結果より、現在は比較的バランスが取れている傾向です。"
            "今の状態を保ちながら、疲れを感じる前に"
            "こまめなセルフケアを取り入れるのがおすすめです。"
        )

    result_card(
        "3. 心身傾向",
        mind_body
    )


    # =====================================================
    # 4. 歩き方の傾向
    # =====================================================
    walk_points = []

    callus = analysis["callus"]

    if sole_wear == "かかとの外側":

        walk_points.append(
            "歩行時に足の外側へ体重が乗りやすい傾向が考えられます。"
        )

    elif sole_wear == "かかとの内側":

        walk_points.append(
            "歩行時に足の内側へ体重が乗りやすい傾向が考えられます。"
        )

    elif sole_wear == "つま先側":

        walk_points.append(
            "歩行時に前足部への負担が比較的大きい傾向が考えられます。"
        )

    elif sole_wear == "全体的に均等":

        walk_points.append(
            "靴底の減り方からは、大きな左右偏りは目立たない傾向です。"
        )

    if callus == "前足部":

        walk_points.append(
            "足裏写真でも前足部に負担が集中している可能性があります。"
        )

    elif callus == "かかと":

        walk_points.append(
            "足裏写真ではかかと側への負担が比較的大きい可能性があります。"
        )

    elif callus in ["左側", "右側"]:

        walk_points.append(
            f"足裏の{callus}側に負担が偏っている可能性があります。"
        )

    if stumble == "はい":

        walk_points.append(
            "つまずきやすさがあるため、歩幅や足の上げ方を意識するとよいでしょう。"
        )

    if not walk_points:

        walk_points.append(
            "今回の診断では、歩き方に大きな偏りは明確には見られませんでした。"
        )

    walk_text = "<br><br>".join(
        walk_points
    )

    result_card(
        "4. 歩き方の傾向",
        walk_text
    )


    # =====================================================
    # 5. おすすめの靴
    # =====================================================
    shape = analysis["overall_shape"]

    if shape == "エジプト型":

        shoe_title = (
            "ラウンドトゥ系のスニーカー・ウォーキングシューズ"
        )

        shoe_detail = (
            "親指が長いエジプト型は、親指側を圧迫しにくく、"
            "つま先が自然に丸くなっている靴がおすすめです。"
            "細すぎるポインテッド形状より、"
            "親指の前に適度な余裕があるモデルが向いています。"
        )

    elif shape == "ギリシャ型":

        shoe_title = (
            "前足部にゆとりのあるスニーカー・ウォーキングシューズ"
        )

        shoe_detail = (
            "第2趾が長いギリシャ型は、第2趾の先端が靴に当たりやすいため、"
            "つま先方向に十分な長さがある靴がおすすめです。"
            "ランニング系やウォーキング系など、"
            "前足部に余裕のあるスニーカーと相性が良い傾向です。"
        )

    elif shape == "スクエア型":

        shoe_title = (
            "ワイドタイプのスニーカー・幅広ウォーキングシューズ"
        )

        shoe_detail = (
            "指の長さが比較的そろったスクエア型は、"
            "つま先部分が横に広い靴がおすすめです。"
            "ワイドトゥボックスや幅広設計など、"
            "指を自然に広げられるモデルが向いています。"
        )

    elif shape == "左右で異なる":

        shoe_title = (
            "つま先に余裕のあるスニーカー・ウォーキングシューズ"
        )

        shoe_detail = (
            "左右で足の形に違いが見られるため、"
            "左右どちらかに合わせて窮屈な靴を選ぶより、"
            "つま先に余裕があり、フィット感を調節しやすい"
            "スニーカータイプがおすすめです。"
        )

    else:

        shoe_title = (
            "足幅とつま先に余裕のあるスニーカー"
        )

        shoe_detail = (
            "足の形を明確に判定できなかったため、"
            "足幅と足長が合い、つま先に適度な余裕がある"
            "スニーカーやウォーキングシューズがおすすめです。"
        )

    if tired == "はい":

        shoe_detail += (
            "<br><br>足が疲れやすいため、クッション性の高い靴もおすすめです。"
        )

    if standing == "はい":

        shoe_detail += (
            "<br><br>立っている時間が長いため、かかと周りの安定感も重視しましょう。"
        )

    result_card(
        "5. おすすめの靴",
        (
            f"<span class='result-main'>{shoe_title}</span>"
            "<br><br>"
            f"{shoe_detail}"
        )
    )


    # =====================================================
    # 6. 足から見る性格傾向
    # =====================================================
    if shape == "エジプト型":

        personality = (
            "エンタメ診断では、落ち着きがあり、"
            "自分のペースを大切にするタイプとして捉えられることがあります。"
            "慎重に物事を考え、好きなことにはじっくり取り組む傾向とされています。"
        )

    elif shape == "ギリシャ型":

        personality = (
            "エンタメ診断では、行動力や好奇心が強く、"
            "新しいことに積極的なタイプとして捉えられることがあります。"
            "アイデアを思いついたら、まず動いてみる傾向とされています。"
        )

    elif shape == "スクエア型":

        personality = (
            "エンタメ診断では、安定感があり、"
            "周囲との協調を大切にするタイプとして捉えられることがあります。"
            "物事を着実に進める現実派の傾向とされています。"
        )

    elif shape == "左右で異なる":

        personality = (
            "左右で異なる特徴が見られるため、"
            "エンタメ診断では、状況によって慎重さと行動力を"
            "使い分けるタイプとして楽しむことができます。"
        )

    else:

        personality = (
            "今回は足の形を明確に判定できなかったため、"
            "性格傾向の表示は控えめにしています。"
        )

    result_card(
        "6. 足から見る性格傾向",
        (
            f"{personality}"
            "<br><br>"
            "※足の形から性格を科学的に判断できるものではなく、"
            "占い・エンタメとしての内容です。"
        )
    )


    # =====================================================
    # 7. 疲労箇所とおすすめ反射区
    # =====================================================
    reflex_map = {

        "頭・目": (
            "足の親指周辺",
            "リフレクソロジーでは、親指周辺が頭部や目に対応する反射区として扱われます。"
        ),

        "首": (
            "親指の付け根周辺",
            "リフレクソロジーでは、親指の付け根周辺が首まわりに対応するとされています。"
        ),

        "肩": (
            "足指の付け根から小指側",
            "リフレクソロジーでは、足指の付け根付近が肩まわりに対応する反射区として扱われます。"
        ),

        "背中": (
            "足裏の内側ライン",
            "リフレクソロジーでは、足裏の内側が背中や背骨に対応するラインとして扱われます。"
        ),

        "腰": (
            "土踏まずの内側からかかと寄り",
            "リフレクソロジーでは、土踏まずの内側からかかと寄りが腰まわりに対応するとされています。"
        ),

        "胃まわり": (
            "土踏まずの上部付近",
            "リフレクソロジーでは、土踏まずの上部周辺が胃まわりに対応する反射区として扱われます。"
        ),

        "脚": (
            "かかと周辺",
            "リフレクソロジーでは、かかと周辺を下半身のケアに用いる考え方があります。"
        ),

        "全身": (
            "足裏全体",
            "足裏全体を無理のない強さでゆっくりほぐすケアがおすすめです。"
        )
    }

    if fatigue_area:

        reflex_blocks = []

        for area in fatigue_area:

            zone, text = reflex_map[area]

            reflex_blocks.append(
                f"<strong>{area}</strong><br>"
                f"おすすめ部位：{zone}<br>"
                f"{text}<br>"
                "親指で心地よい程度の強さで、"
                "5〜10秒ほどゆっくり刺激してみてください。"
            )

        reflex_text = "<br><br>".join(
            reflex_blocks
        )

    else:

        reflex_text = (
            "現在、特に疲労箇所は選択されていません。"
            "足裏全体をやさしくほぐすセルフケアがおすすめです。"
        )

    result_card(
        "7. 疲労箇所とおすすめ反射区",
        reflex_text
    )


    # =====================================================
    # 8. おすすめアロマ
    # =====================================================
    aroma_map = {

        "リラックス": (
            "ラベンダー",
            "落ち着いて過ごしたい時間に取り入れやすい香りです。"
        ),

        "リフレッシュ": (
            "レモン",
            "気持ちを切り替えたい時に取り入れやすい香りです。"
        ),

        "集中": (
            "ローズマリー",
            "集中したい時間に取り入れやすい香りです。"
        ),

        "睡眠": (
            "ラベンダー",
            "就寝前など落ち着きたい時間に取り入れやすい香りです。"
        ),

        "気分転換": (
            "スイートオレンジ",
            "明るい気分に切り替えたい時に取り入れやすい香りです。"
        )
    }

    aroma, aroma_text = aroma_map[
        aroma_goal
    ]

    result_card(
        "8. おすすめアロマ",
        (
            f"<span class='result-main'>{aroma}</span>"
            "<br><br>"
            f"{aroma_text}"
        )
    )


    # =====================================================
    # 9. セルフケア
    # =====================================================
    care = []

    if cold == "はい":
        care.append(
            "足湯や靴下などで足元を温める"
        )

    if swelling == "はい":
        care.append(
            "足首をゆっくり回したり、ふくらはぎを軽く動かす"
        )

    if tired == "はい":
        care.append(
            "帰宅後に足を休ませる時間をつくる"
        )

    if analysis["dryness"] in [
        "やや乾燥",
        "乾燥が目立つ"
    ]:

        care.append(
            "入浴後などに足裏を保湿する"
        )

    if analysis["callus"] not in [
        "なし",
        "判定困難"
    ]:

        care.append(
            "角質が目立つ部分に負担が集中しないよう靴を見直す"
        )

    if stumble == "はい":

        care.append(
            "歩く時に足先を少し上げる意識を持ち、無理のない範囲で足首を動かす"
        )

    if not care:

        care.append(
            "足裏の保湿と軽いストレッチを習慣にする"
        )

    care_text = "・" + "<br>・".join(
        care
    )

    result_card(
        "9. セルフケア",
        care_text
    )


    st.divider()

    st.caption(
        "このサービスは医療行為・医学的診断を目的としたものではありません。"
        "足の色は照明やカメラ補正の影響を受けます。"
        "心身傾向・反射区・性格傾向には、"
        "リフレクソロジーやエンタメ的な考え方が含まれます。"
        "強い痛み、しびれ、傷、急な腫れなどがある場合は、"
        "セルフケアを続けず医療機関等への相談を検討してください。"
    )

    if st.button(
        "最初から診断する"
    ):

        st.session_state.step = 1
        st.rerun()