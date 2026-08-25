import io

import cv2
import numpy as np
import streamlit as st
import torch
from PIL import Image
from transformers import pipeline


# =========================================================
# ページ設定
# =========================================================
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

.analysis-card {
    padding: 14px 16px;
    border-radius: 10px;
    background-color: #f8f8f8;
    color: #222222;
    margin-bottom: 10px;
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
# 無料AIモデル
# 初回のみダウンロード
# =========================================================
@st.cache_resource(show_spinner=False)
def load_classifier():

    device = 0 if torch.cuda.is_available() else -1

    classifier = pipeline(
        task="zero-shot-image-classification",
        model="openai/clip-vit-base-patch32",
        device=device
    )

    return classifier


# =========================================================
# 画像読み込み
# =========================================================
def load_image(uploaded_file):

    uploaded_file.seek(0)

    image = Image.open(uploaded_file).convert("RGB")

    return image


# =========================================================
# CLIP分類
# =========================================================
def classify_image(image, labels):

    classifier = load_classifier()

    results = classifier(
        image,
        candidate_labels=labels
    )

    if not results:
        return None, 0.0

    best = results[0]

    return best["label"], float(best["score"])


# =========================================================
# 足指タイプ
# =========================================================
def analyze_toe_type(image):

    labels = [
        "Egyptian foot shape, big toe is the longest and toes gradually get shorter",
        "Greek foot shape, second toe is longer than the big toe",
        "square Roman foot shape, first three toes are similar in length",
        "unclear toe shape"
    ]

    label, confidence = classify_image(
        image,
        labels
    )

    mapping = {
        labels[0]: "エジプト型",
        labels[1]: "ギリシャ型",
        labels[2]: "スクエア型",
        labels[3]: "判定困難"
    }

    return mapping.get(label, "判定困難"), confidence


# =========================================================
# 乾燥
# =========================================================
def analyze_dryness(image):

    labels = [
        "smooth moisturized sole skin",
        "slightly dry sole skin",
        "very dry cracked sole skin"
    ]

    label, confidence = classify_image(
        image,
        labels
    )

    mapping = {
        labels[0]: "乾燥は目立たない",
        labels[1]: "やや乾燥",
        labels[2]: "乾燥が目立つ"
    }

    return mapping.get(
        label,
        "判定困難"
    ), confidence


# =========================================================
# 角質
# =========================================================
def analyze_callus(image):

    labels = [
        "no visible callus on the sole",
        "callus mainly on the heel",
        "callus mainly on the ball of the foot",
        "callus mainly near the big toe",
        "callus mainly near the little toe"
    ]

    label, confidence = classify_image(
        image,
        labels
    )

    mapping = {
        labels[0]: "なし",
        labels[1]: "かかと",
        labels[2]: "前足部",
        labels[3]: "親指側",
        labels[4]: "小指側"
    }

    return mapping.get(
        label,
        "判定困難"
    ), confidence


# =========================================================
# 足裏カラー解析
# OpenCVで写真上の色味を見る
# =========================================================
def analyze_foot_color(image):

    rgb = np.array(image)

    height, width, _ = rgb.shape

    # 背景の影響を少し減らすため
    # 中央80%を使用
    y1 = int(height * 0.10)
    y2 = int(height * 0.90)

    x1 = int(width * 0.10)
    x2 = int(width * 0.90)

    crop = rgb[y1:y2, x1:x2]

    # 極端に暗い / 明るい背景を多少除外
    gray = cv2.cvtColor(
        crop,
        cv2.COLOR_RGB2GRAY
    )

    mask = (
        (gray > 45)
        & (gray < 245)
    )

    pixels = crop[mask]

    if len(pixels) < 100:

        pixels = crop.reshape(-1, 3)

    mean_rgb = pixels.mean(axis=0)

    red = float(mean_rgb[0])
    green = float(mean_rgb[1])
    blue = float(mean_rgb[2])

    brightness = (
        red + green + blue
    ) / 3

    # -----------------------------
    # 簡易カラー分類
    # -----------------------------
    if (
        red > green * 1.10
        and red > blue * 1.15
    ):

        color = "赤み強め"

    elif (
        red > blue * 1.18
        and green > blue * 1.10
        and abs(red - green) < 50
    ):

        color = "黄み強め"

    elif (
        brightness > 195
        and abs(red - green) < 30
        and abs(green - blue) < 30
    ):

        color = "白っぽい"

    else:

        color = "標準的な色味"

    rgb_info = {
        "R": round(red, 1),
        "G": round(green, 1),
        "B": round(blue, 1)
    }

    return color, rgb_info


# =========================================================
# 画像1枚を総合解析
# =========================================================
def analyze_foot_image(image):

    toe_type, toe_confidence = (
        analyze_toe_type(image)
    )

    dryness, dryness_confidence = (
        analyze_dryness(image)
    )

    callus, callus_confidence = (
        analyze_callus(image)
    )

    foot_color, rgb_info = (
        analyze_foot_color(image)
    )

    return {

        "toe_type": toe_type,
        "toe_confidence": toe_confidence,

        "dryness": dryness,
        "dryness_confidence": dryness_confidence,

        "callus": callus,
        "callus_confidence": callus_confidence,

        "foot_color": foot_color,

        "rgb": rgb_info
    }


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
# 質問
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

    st.write("")

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
# 写真
# =========================================================
elif st.session_state.step == 2:

    st.subheader(
        "STEP 2　足裏写真"
    )

    st.write(
        "まず、両足の足裏が確認できる"
        "写真をアップロードしてください。"
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
        "足指からかかとまで、"
        "両足全体が正面から写るようにしてください。"
        "自然光または明るい白色照明で、"
        "画像加工なしの写真がおすすめです。"
    )

    st.write("")

    st.write(
        "細部が分かりにくい場合は、"
        "右足・左足のアップ写真も追加できます。"
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

    st.write("")

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
            "足裏写真を解析しています。"
            "初回はAIモデルの読み込みに"
            "少し時間がかかります。"
        ):

            both_image = load_image(
                both_feet
            )

            both_analysis = (
                analyze_foot_image(
                    both_image
                )
            )

            st.session_state.both_analysis = (
                both_analysis
            )

            # ---------------------------------
            # 右足追加画像
            # ---------------------------------
            if right_foot:

                right_image = load_image(
                    right_foot
                )

                st.session_state.right_analysis = (
                    analyze_foot_image(
                        right_image
                    )
                )

            else:

                st.session_state.right_analysis = (
                    None
                )

            # ---------------------------------
            # 左足追加画像
            # ---------------------------------
            if left_foot:

                left_image = load_image(
                    left_foot
                )

                st.session_state.left_analysis = (
                    analyze_foot_image(
                        left_image
                    )
                )

            else:

                st.session_state.left_analysis = (
                    None
                )

        st.session_state.step = 3

        st.rerun()


# =========================================================
# STEP 3
# 診断結果
# =========================================================
elif st.session_state.step == 3:

    analysis = (
        st.session_state.both_analysis
    )

    toe_type = analysis["toe_type"]
    foot_color = analysis["foot_color"]
    callus = analysis["callus"]
    dryness = analysis["dryness"]

    cold = st.session_state.cold
    swelling = st.session_state.swelling
    tired = st.session_state.tired
    standing = st.session_state.standing
    aroma_goal = (
        st.session_state.aroma_goal
    )

    st.subheader(
        "診断結果"
    )

    st.caption(
        "画像AIと写真上の色解析、"
        "質問回答を組み合わせた結果です。"
    )


    # =====================================================
    # AI画像解析結果
    # =====================================================
    st.markdown(
        "### 画像解析"
    )

    st.markdown(
        f"""
        <div class="analysis-card">

        <strong>足指タイプ</strong><br>
        {toe_type}
        （AI信頼度：
        {analysis["toe_confidence"] * 100:.0f}%）

        <br><br>

        <strong>足裏カラー</strong><br>
        {foot_color}

        <br><br>

        <strong>乾燥傾向</strong><br>
        {dryness}
        （AI信頼度：
        {analysis["dryness_confidence"] * 100:.0f}%）

        <br><br>

        <strong>角質が目立つ位置</strong><br>
        {callus}
        （AI信頼度：
        {analysis["callus_confidence"] * 100:.0f}%）

        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 1. 足指タイプ
    # =====================================================
    if toe_type == "エジプト型":

        toe_text = (
            "親指が最も長く、"
            "小指に向かって徐々に短くなる"
            "特徴が見られます。"
            "リフレクソロジー的な解釈では、"
            "安定感や現実性を重視する"
            "タイプとして紹介されることがあります。"
        )

    elif toe_type == "ギリシャ型":

        toe_text = (
            "第2趾が親指より長い特徴が"
            "見られます。"
            "リフレクソロジー的な解釈では、"
            "行動力や感性が強いタイプとして"
            "紹介されることがあります。"
        )

    elif toe_type == "スクエア型":

        toe_text = (
            "親指から中指付近の長さが"
            "比較的近い特徴が見られます。"
            "リフレクソロジー的な解釈では、"
            "慎重さやバランスを重視する"
            "タイプとして紹介されることがあります。"
        )

    else:

        toe_text = (
            "今回の写真では足指タイプを"
            "明確に分類できませんでした。"
            "足指が正面から見える写真を"
            "追加すると判定しやすくなります。"
        )

    st.markdown(
        "### 1. 足指タイプ"
    )

    st.markdown(
        f"""
        <div class="result-card">
        <strong>{toe_type}</strong>
        <br><br>
        {toe_text}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 2. 足裏カラー
    # =====================================================
    if foot_color == "赤み強め":

        color_text = (
            "写真上では足裏に赤みが"
            "比較的強く見られます。"
            "リフレクソロジー上では、"
            "活動量が多い時や、緊張感・疲れを"
            "感じている時の傾向として"
            "捉える考え方があります。"
        )

    elif foot_color == "黄み強め":

        color_text = (
            "写真上では黄みが比較的"
            "強く見られます。"
            "リフレクソロジー上では、"
            "疲れがたまった時や、"
            "気分転換を求める状態として"
            "捉える考え方があります。"
        )

    elif foot_color == "白っぽい":

        color_text = (
            "写真上では全体的に"
            "白っぽく見られます。"
            "リフレクソロジー上では、"
            "休息を求めている時や"
            "活力を温存したい時の傾向として"
            "捉える考え方があります。"
        )

    else:

        color_text = (
            "写真上では大きな色味の偏りは"
            "目立ちません。"
        )

    st.markdown(
        "### 2. 足裏カラー"
    )

    st.markdown(
        f"""
        <div class="result-card">
        <strong>{foot_color}</strong>
        <br><br>
        {color_text}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 3. 心身傾向
    # =====================================================
    rest_score = 0

    if foot_color == "赤み強め":
        rest_score += 2

    if foot_color == "白っぽい":
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
            "現在は休息を意識したい傾向です。"
            "質問回答でも疲れや冷えなどが"
            "重なっているため、"
            "無理をせずリラックスする時間を"
            "確保するのがおすすめです。"
        )

    elif rest_score >= 3:

        mind_body = (
            "少し疲れがたまりやすい"
            "傾向が見られます。"
            "短時間でも休息や気分転換を"
            "取り入れるのがおすすめです。"
        )

    else:

        mind_body = (
            "質問回答上では大きな疲労傾向は"
            "目立ちません。"
            "現在の状態を保ちながら、"
            "定期的なセルフケアを"
            "取り入れるのがおすすめです。"
        )

    st.markdown(
        "### 3. 現在の心身傾向"
    )

    st.markdown(
        f"""
        <div class="result-card">
        {mind_body}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 4. 歩き方
    # =====================================================
    if callus == "前足部":

        walk_text = (
            "前足部に負担が集中している"
            "可能性があります。"
            "長く歩いた時に足の前側が"
            "疲れやすくないか確認してみてください。"
        )

    elif callus == "かかと":

        walk_text = (
            "かかと側への負担が"
            "比較的大きい可能性があります。"
            "着地時の衝撃を受けやすい傾向として"
            "参考にしてください。"
        )

    elif callus == "親指側":

        walk_text = (
            "足の内側・親指側へ"
            "負担がかかりやすい可能性があります。"
        )

    elif callus == "小指側":

        walk_text = (
            "足の外側・小指側へ"
            "負担がかかりやすい可能性があります。"
        )

    else:

        walk_text = (
            "写真上では角質位置から見た"
            "大きな負担の偏りは"
            "明確ではありません。"
        )

    st.markdown(
        "### 4. 歩き方の傾向"
    )

    st.markdown(
        f"""
        <div class="result-card">
        {walk_text}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 5. 靴
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

    if callus == "小指側":

        shoe_list.append(
            "足幅に余裕がある"
        )

    if not shoe_list:

        shoe_list.append(
            "足幅と足長に合った"
            "フィット感のある"
        )

    shoe_text = (
        "、".join(shoe_list)
        + "靴がおすすめです。"
    )

    st.markdown(
        "### 5. おすすめの靴"
    )

    st.markdown(
        f"""
        <div class="result-card">
        {shoe_text}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 6. アロマ
    # =====================================================
    if aroma_goal == "リラックス":

        aroma = "ラベンダー"

        aroma_text = (
            "落ち着いて過ごしたい時間に"
            "取り入れやすい香りです。"
        )

    elif aroma_goal == "リフレッシュ":

        aroma = "レモン"

        aroma_text = (
            "気持ちを切り替えたい時に"
            "取り入れやすい香りです。"
        )

    elif aroma_goal == "集中":

        aroma = "ローズマリー"

        aroma_text = (
            "集中したい時間に"
            "取り入れやすい香りです。"
        )

    elif aroma_goal == "睡眠":

        aroma = "ラベンダー"

        aroma_text = (
            "就寝前など、"
            "落ち着きたい時間におすすめです。"
        )

    else:

        aroma = "スイートオレンジ"

        aroma_text = (
            "気分転換したい時に"
            "取り入れやすい香りです。"
        )

    st.markdown(
        "### 6. おすすめアロマ"
    )

    st.markdown(
        f"""
        <div class="result-card">
        <strong>{aroma}</strong>
        <br><br>
        {aroma_text}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 7. セルフケア
    # =====================================================
    care_list = []

    if cold == "はい":

        care_list.append(
            "足元を温める"
        )

    if swelling == "はい":

        care_list.append(
            "軽い足首運動やストレッチ"
        )

    if tired == "はい":

        care_list.append(
            "足を休ませる時間をつくる"
        )

    if dryness in [
        "やや乾燥",
        "乾燥が目立つ"
    ]:

        care_list.append(
            "入浴後などに保湿する"
        )

    if callus not in [
        "なし",
        "判定困難"
    ]:

        care_list.append(
            "角質が目立つ部分に"
            "過度な負担をかけない"
        )

    if not care_list:

        care_list.append(
            "定期的な保湿と"
            "足裏ストレッチ"
        )

    care_text = "・".join(
        care_list
    )

    st.markdown(
        "### 7. セルフケア"
    )

    st.markdown(
        f"""
        <div class="result-card">
        {care_text}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # 補助写真解析
    # =====================================================
    right_analysis = (
        st.session_state.get(
            "right_analysis"
        )
    )

    left_analysis = (
        st.session_state.get(
            "left_analysis"
        )
    )

    if (
        right_analysis
        or left_analysis
    ):

        st.divider()

        st.markdown(
            "### 補助写真の解析"
        )

        if right_analysis:

            st.write(
                "**右足**"
            )

            st.write(
                f"足指タイプ："
                f"{right_analysis['toe_type']}"
            )

            st.write(
                f"カラー："
                f"{right_analysis['foot_color']}"
            )

            st.write(
                f"乾燥："
                f"{right_analysis['dryness']}"
            )

            st.write(
                f"角質："
                f"{right_analysis['callus']}"
            )

        if left_analysis:

            st.write(
                "**左足**"
            )

            st.write(
                f"足指タイプ："
                f"{left_analysis['toe_type']}"
            )

            st.write(
                f"カラー："
                f"{left_analysis['foot_color']}"
            )

            st.write(
                f"乾燥："
                f"{left_analysis['dryness']}"
            )

            st.write(
                f"角質："
                f"{left_analysis['callus']}"
            )


    st.divider()

    st.caption(
        "このサービスは医療行為や"
        "医学的診断を目的としたものではありません。"
        "画像の色味は照明やカメラ補正の"
        "影響を受けます。"
        "足裏カラー・性格傾向・心身傾向には、"
        "リフレクソロジー上の考え方を"
        "参考にしたウェルネス・"
        "エンタメ要素が含まれます。"
    )

    st.write("")

    if st.button(
        "最初から診断する"
    ):

        st.session_state.step = 1

        st.rerun()