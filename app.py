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
    line-height: 1.7;
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
# 基本画像処理
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

    return max(
        contours,
        key=cv2.contourArea
    )


# =========================================================
# 足の領域抽出
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

    margin_x = max(
        2,
        int(w * 0.06)
    )

    margin_y = max(
        2,
        int(h * 0.04)
    )

    rect = (
        margin_x,
        margin_y,
        max(
            2,
            w - margin_x * 2
        ),
        max(
            2,
            h - margin_y * 2
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
            cv2.THRESH_BINARY
            +
            cv2.THRESH_OTSU
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


    contour = largest_contour(
        binary
    )

    if contour is None:
        return None


    area_ratio = (
        cv2.contourArea(contour)
        /
        float(h * w)
    )

    if area_ratio < 0.08:
        return None


    clean = np.zeros_like(
        binary
    )

    cv2.drawContours(
        clean,
        [contour],
        -1,
        255,
        thickness=-1
    )

    return clean


# =========================================================
# マスク部分だけ切り抜く
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


    x1 = xs.min()
    x2 = xs.max()

    y1 = ys.min()
    y2 = ys.max()


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
# 足指が上側になるように向きを補正
# =========================================================
def ensure_toes_top(
    rgb,
    mask
):

    h, w = mask.shape

    band = max(
        5,
        int(h * 0.22)
    )

    top_width = (
        np.count_nonzero(
            mask[:band] > 0
        )
        /
        band
    )

    bottom_width = (
        np.count_nonzero(
            mask[-band:] > 0
        )
        /
        band
    )


    if bottom_width > (
        top_width * 1.10
    ):

        return (
            np.rot90(
                rgb,
                2
            ),
            np.rot90(
                mask,
                2
            )
        )


    return rgb, mask


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

        return (
            "判定困難",
            0.0
        )


    rgb, mask = crop_to_mask(
        rgb,
        mask
    )

    rgb, mask = ensure_toes_top(
        rgb,
        mask
    )


    h, w = mask.shape

    if h < 60 or w < 40:

        return (
            "判定困難",
            0.0
        )


    toe_band_h = max(
        20,
        int(h * 0.38)
    )

    toe_mask = mask[
        :toe_band_h
    ]


    zone_edges = np.linspace(
        0,
        w,
        6
    ).astype(int)


    tips = []


    for i in range(5):

        x1 = zone_edges[i]
        x2 = zone_edges[i + 1]

        zone = toe_mask[
            :,
            x1:x2
        ]

        ys, xs = np.where(
            zone > 0
        )

        if len(ys) < max(
            10,
            (x2 - x1) * 2
        ):

            tips.append(
                None
            )

        else:

            tips.append(
                float(
                    np.percentile(
                        ys,
                        5
                    )
                )
            )


    # 左足は親指が中央側＝右
    if big_toe_side == "right":

        big_idx = 4
        second_idx = 3
        third_idx = 2

    else:

        big_idx = 0
        second_idx = 1
        third_idx = 2


    needed = [
        tips[big_idx],
        tips[second_idx],
        tips[third_idx]
    ]


    if any(
        value is None
        for value in needed
    ):

        return (
            "判定困難",
            0.0
        )


    big_y = needed[0]
    second_y = needed[1]
    third_y = needed[2]


    norm = max(
        1.0,
        float(toe_band_h)
    )


    # yが小さいほど
    # 上にある＝長い指
    d12 = (
        second_y - big_y
    ) / norm

    d23 = (
        third_y - second_y
    ) / norm


    # 第2趾が親指より長い
    if d12 < -0.035:

        result = "ギリシャ型"

        confidence = min(
            0.95,
            0.60
            +
            abs(d12) * 4.0
        )


    # 1～3趾の高さが近い
    elif (
        abs(d12) <= 0.03
        and
        abs(d23) <= 0.045
    ):

        result = "スクエア型"

        confidence = 0.70


    # 親指が第2趾より長い
    elif d12 > 0.025:

        result = "エジプト型"

        confidence = min(
            0.95,
            0.60
            +
            d12 * 4.0
        )


    else:

        result = "判定困難"

        confidence = 0.45


    return (
        result,
        confidence
    )


# =========================================================
# HSV + Labで足裏カラー判定
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


    valid = mask > 0


    # 影と白飛びを除外
    brightness = hsv[:, :, 2]

    valid &= (
        brightness > 45
    )

    valid &= (
        brightness < 248
    )


    if valid.sum() < 200:

        valid = mask > 0


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

    L = float(
        np.median(
            lab[:, :, 0][valid]
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


    # -----------------------------
    # 白
    # -----------------------------
    if (
        S < 35
        and
        V > 185
    ):

        result = "白っぽい"


    # -----------------------------
    # 赤
    # -----------------------------
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


    # -----------------------------
    # オレンジ
    # -----------------------------
    elif (
        H > 5
        and
        H <= 17
        and
        S >= 45
    ):

        result = "オレンジ寄り"


    # -----------------------------
    # 黄色
    # -----------------------------
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


    # -----------------------------
    # 標準
    # -----------------------------
    else:

        result = "標準的な色味"


    info = {

        "H": round(H, 1),
        "S": round(S, 1),
        "V": round(V, 1),

        "L": round(L, 1),
        "a": round(A, 1),
        "b": round(B, 1)

    }


    return (
        result,
        info
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
    )[mask > 0]


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


    light = lab[:, :, 0]
    yellow = lab[:, :, 2]


    candidates = (
        (mask > 0)
        &
        (light > 145)
        &
        (yellow > 138)
    )


    ys, xs = np.where(
        candidates
    )


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
# 両足画像を左右に分ける
# =========================================================
def split_both_feet(image):

    rgb = pil_to_rgb(
        image
    )

    h, w = rgb.shape[:2]


    middle = w // 2


    overlap = int(
        w * 0.03
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
# 両足を総合解析
# =========================================================
def analyze_both_feet(image):

    left_rgb, right_rgb = (
        split_both_feet(
            image
        )
    )


    left_shape, left_conf = (
        classify_foot_shape(
            left_rgb,
            big_toe_side="right"
        )
    )


    right_shape, right_conf = (
        classify_foot_shape(
            right_rgb,
            big_toe_side="left"
        )
    )


    full_rgb = pil_to_rgb(
        image
    )


    color, color_info = (
        color_analysis(
            full_rgb
        )
    )


    dryness, callus = (
        texture_and_callus(
            full_rgb
        )
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
        valid_shapes[0]
        ==
        valid_shapes[1]
    ):

        overall_shape = (
            valid_shapes[0]
        )


    elif len(valid_shapes) == 2:

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
def result_card(
    title,
    body
):

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
    'あなたの足の傾向をチェックします'
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
        "長時間歩いたり立っていると、"
        "足が疲れやすいですか？",
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

        st.session_state.foot_concern = (
            foot_concern
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

    st.subheader(
        "STEP 2　足裏写真"
    )


    st.write(
        "両足の足裏が確認できる写真を"
        "アップロードしてください。"
    )


    both_feet = st.file_uploader(
        "両足の写真（必須）",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key="both_feet"
    )


    st.caption(
        "両足を並べ、足指からかかとまで"
        "正面から写してください。"
        "背景と足の色ができるだけ"
        "区別しやすい写真がおすすめです。"
    )


    right_foot = st.file_uploader(
        "右足のアップ写真（任意）",
        type=[
            "jpg",
            "jpeg",
            "png"
        ],
        key="right_foot"
    )


    left_foot = st.file_uploader(
        "左足のアップ写真（任意）",
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
            disabled=not both_feet
        )


    if diagnose:

        with st.spinner(
            "足裏写真を解析しています..."
        ):

            image = Image.open(
                both_feet
            ).convert(
                "RGB"
            )


            analysis = (
                analyze_both_feet(
                    image
                )
            )


            # -----------------------------
            # 右足補助写真
            # -----------------------------
            if right_foot:

                right_image = pil_to_rgb(
                    Image.open(
                        right_foot
                    ).convert(
                        "RGB"
                    )
                )


                rshape, rconf = (
                    classify_foot_shape(
                        right_image,
                        big_toe_side="left"
                    )
                )


                if rshape != "判定困難":

                    analysis[
                        "right_shape"
                    ] = rshape

                    analysis[
                        "right_shape_conf"
                    ] = rconf


            # -----------------------------
            # 左足補助写真
            # -----------------------------
            if left_foot:

                left_image = pil_to_rgb(
                    Image.open(
                        left_foot
                    ).convert(
                        "RGB"
                    )
                )


                lshape, lconf = (
                    classify_foot_shape(
                        left_image,
                        big_toe_side="right"
                    )
                )


                if lshape != "判定困難":

                    analysis[
                        "left_shape"
                    ] = lshape

                    analysis[
                        "left_shape_conf"
                    ] = lconf


            left_shape = (
                analysis[
                    "left_shape"
                ]
            )

            right_shape = (
                analysis[
                    "right_shape"
                ]
            )


            if (
                left_shape
                !=
                "判定困難"
                and
                right_shape
                !=
                "判定困難"
            ):

                if (
                    left_shape
                    ==
                    right_shape
                ):

                    analysis[
                        "overall_shape"
                    ] = left_shape

                else:

                    analysis[
                        "overall_shape"
                    ] = "左右で異なる"


            elif (
                left_shape
                !=
                "判定困難"
            ):

                analysis[
                    "overall_shape"
                ] = left_shape


            elif (
                right_shape
                !=
                "判定困難"
            ):

                analysis[
                    "overall_shape"
                ] = right_shape


            else:

                analysis[
                    "overall_shape"
                ] = "判定困難"


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

    aroma_goal = (
        st.session_state.aroma_goal
    )


    st.subheader(
        "診断結果"
    )


    # =====================================================
    # 1 足の形
    # =====================================================
    shape_body = (
        f"<strong>{analysis['overall_shape']}</strong>"
        "<br><br>"
        f"左足：{analysis['left_shape']}"
        f"（判定度 "
        f"{analysis['left_shape_conf'] * 100:.0f}%）"
        "<br>"
        f"右足：{analysis['right_shape']}"
        f"（判定度 "
        f"{analysis['right_shape_conf'] * 100:.0f}%）"
    )


    result_card(
        "1. 足の形",
        shape_body
    )


    # =====================================================
    # 2 足裏カラー
    # =====================================================
    color = (
        analysis[
            "foot_color"
        ]
    )


    if color == "赤み強め":

        color_text = (
            "写真上では赤みが強く見られます。"
            "リフレクソロジー上では、"
            "活動量や緊張感が高まっている時の"
            "傾向として捉える考え方があります。"
        )


    elif color == "オレンジ寄り":

        color_text = (
            "写真上ではオレンジ寄りの"
            "色味が見られます。"
            "リフレクソロジー上では、"
            "活動性と疲労感の両方が"
            "表れやすい状態として"
            "捉える考え方があります。"
        )


    elif color == "黄み強め":

        color_text = (
            "写真上では黄みが強く見られます。"
            "リフレクソロジー上では、"
            "疲れや気分転換を求めている時の"
            "傾向として捉える考え方があります。"
        )


    elif color == "白っぽい":

        color_text = (
            "写真上では白っぽく見られます。"
            "リフレクソロジー上では、"
            "休息を必要としている時の"
            "傾向として捉える考え方があります。"
        )


    else:

        color_text = (
            "写真上では大きな色味の偏りは"
            "目立ちません。"
        )


    result_card(
        "2. 足裏カラー",
        (
            f"<strong>{color}</strong>"
            "<br><br>"
            f"{color_text}"
        )
    )


    # =====================================================
    # 3 心身傾向
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

    if aroma_goal == "睡眠":
        rest_score += 1


    if rest_score >= 6:

        mind_body = (
            "質問回答と足裏の見た目を合わせると、"
            "今は休息を意識したい傾向として"
            "捉えられます。"
        )


    elif rest_score >= 3:

        mind_body = (
            "少し疲れがたまりやすい"
            "傾向として捉えられます。"
            "短時間でも休息や気分転換を"
            "取り入れるのがおすすめです。"
        )


    else:

        mind_body = (
            "質問回答上では大きな疲労傾向は"
            "目立ちません。"
            "現在の状態を保ちながら"
            "定期的なセルフケアがおすすめです。"
        )


    result_card(
        "3. 現在の心身傾向",
        mind_body
    )


    # =====================================================
    # 4 歩き方
    # =====================================================
    callus = (
        analysis[
            "callus"
        ]
    )


    if callus == "前足部":

        walk_text = (
            "前足部に負担が集中している"
            "可能性があります。"
        )


    elif callus == "かかと":

        walk_text = (
            "かかと側への負担が"
            "比較的大きい可能性があります。"
        )


    elif callus in [
        "左側",
        "右側"
    ]:

        walk_text = (
            f"足裏の{callus}に"
            "角質傾向が見られます。"
            "荷重の偏りを考える際の"
            "参考になります。"
        )


    elif callus == "なし":

        walk_text = (
            "角質位置から見た大きな"
            "負担の偏りは明確ではありません。"
        )


    else:

        walk_text = (
            "今回の写真では負担位置を"
            "明確に判定できませんでした。"
        )


    result_card(
        "4. 歩き方の傾向",
        walk_text
    )


    # =====================================================
    # 5 靴
    # =====================================================
    shoe_list = []


    if tired == "はい":

        shoe_list.append(
            "クッション性が高い"
        )


    if standing == "はい":

        shoe_list.append(
            "安定感がある"
        )


    if callus == "前足部":

        shoe_list.append(
            "前足部にゆとりがある"
        )


    if callus in [
        "左側",
        "右側"
    ]:

        shoe_list.append(
            "足幅に無理のない"
        )


    if not shoe_list:

        shoe_list.append(
            "足幅と足長に合った"
        )


    shoe_text = (
        "、".join(
            shoe_list
        )
        +
        "靴がおすすめです。"
    )


    result_card(
        "5. おすすめの靴",
        shoe_text
    )


    # =====================================================
    # 6 アロマ
    # =====================================================
    aroma_map = {

        "リラックス": (
            "ラベンダー",
            "落ち着いて過ごしたい時間に"
            "取り入れやすい香りです。"
        ),

        "リフレッシュ": (
            "レモン",
            "気持ちを切り替えたい時に"
            "取り入れやすい香りです。"
        ),

        "集中": (
            "ローズマリー",
            "集中したい時間に"
            "取り入れやすい香りです。"
        ),

        "睡眠": (
            "ラベンダー",
            "就寝前など落ち着きたい時間に"
            "おすすめです。"
        ),

        "気分転換": (
            "スイートオレンジ",
            "気分転換したい時に"
            "取り入れやすい香りです。"
        )
    }


    aroma, aroma_text = (
        aroma_map[
            aroma_goal
        ]
    )


    result_card(
        "6. おすすめアロマ",
        (
            f"<strong>{aroma}</strong>"
            "<br><br>"
            f"{aroma_text}"
        )
    )


    # =====================================================
    # 7 セルフケア
    # =====================================================
    care = []


    if cold == "はい":

        care.append(
            "足元を温める"
        )


    if swelling == "はい":

        care.append(
            "軽い足首運動やストレッチ"
        )


    if tired == "はい":

        care.append(
            "足を休ませる時間をつくる"
        )


    if analysis[
        "dryness"
    ] in [
        "やや乾燥",
        "乾燥が目立つ"
    ]:

        care.append(
            "入浴後などに保湿する"
        )


    if callus not in [
        "なし",
        "判定困難"
    ]:

        care.append(
            "角質が目立つ部分に"
            "過度な負担をかけない"
        )


    if not care:

        care.append(
            "定期的な保湿と"
            "足裏ストレッチ"
        )


    result_card(
        "7. セルフケア",
        "・".join(
            care
        )
    )


    st.divider()


    st.caption(
        "このサービスは医療行為・医学的診断を"
        "目的としたものではありません。"
        "足裏カラーは照明やカメラ補正の"
        "影響を受けます。"
        "心身傾向にはリフレクソロジー上の"
        "考え方を参考にした"
        "ウェルネス・エンタメ要素が含まれます。"
    )


    if st.button(
        "最初から診断する"
    ):

        st.session_state.step = 1

        st.rerun()