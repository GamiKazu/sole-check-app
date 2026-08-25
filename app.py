import streamlit as st

st.set_page_config(
    page_title="足裏タイプ診断",
    layout="centered"
)

# -----------------------------
# セッション状態
# -----------------------------
if "step" not in st.session_state:
    st.session_state.step = 1


# -----------------------------
# デザイン
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background-color: white;
        color: black;
    }

    [data-testid="stAppViewContainer"] {
        background-color: white;
    }

    [data-testid="stHeader"] {
        background-color: white;
    }

    .block-container {
        max-width: 720px;
        padding-top: 3.8rem;
        padding-bottom: 3rem;
    }

    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.45;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
        padding-top: 0.4rem;
        color: #222;
    }

    .sub-title {
        text-align: center;
        color: #777;
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    .result-card {
        padding: 18px 20px;
        border-radius: 12px;
        background-color: #f5f5f5;
        margin-bottom: 18px;
        color: #222;
    }

    div.stButton > button {
        width: 100%;
        height: 50px;
        font-size: 17px;
        font-weight: bold;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# タイトル
# -----------------------------
st.markdown(
    '<div class="main-title">足裏タイプ診断</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">簡単な質問と足裏写真から、あなたの足の傾向をチェックします</div>',
    unsafe_allow_html=True
)


# =========================================================
# STEP 1
# 質問
# =========================================================
if st.session_state.step == 1:

    st.subheader("STEP 1　簡単な質問")

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

    if st.button("次へ", type="primary"):

        st.session_state.cold = cold
        st.session_state.swelling = swelling
        st.session_state.tired = tired
        st.session_state.standing = standing
        st.session_state.shoes = shoes
        st.session_state.foot_concern = foot_concern
        st.session_state.aroma_goal = aroma_goal

        st.session_state.step = 2
        st.rerun()


# =========================================================
# STEP 2
# 足裏写真
# =========================================================
elif st.session_state.step == 2:

    st.subheader("STEP 2　足裏写真")

    st.write(
        "まず、両足の足裏が確認できる写真をアップロードしてください。"
    )

    both_feet = st.file_uploader(
        "両足の写真（必須）",
        type=["jpg", "jpeg", "png"],
        key="both_feet"
    )

    st.caption(
        "両足全体ができるだけ正面から写っている写真がおすすめです。"
    )

    st.write("")

    st.write(
        "細かい部分が分かりにくい場合は、"
        "右足・左足のアップ写真も追加できます。"
    )

    right_foot = st.file_uploader(
        "右足の写真（任意）",
        type=["jpg", "jpeg", "png"],
        key="right_foot"
    )

    left_foot = st.file_uploader(
        "左足の写真（任意）",
        type=["jpg", "jpeg", "png"],
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
        if st.button(
            "診断する",
            type="primary",
            disabled=not both_feet
        ):

            # -------------------------------------------------
            # 今は仮の画像診断値
            # 後でAI画像解析の結果に置き換える
            # -------------------------------------------------
            st.session_state.toe_type = "ギリシャ型"
            st.session_state.foot_color = "赤み強め"
            st.session_state.arch = "標準"
            st.session_state.callus = "前足部"
            st.session_state.dryness = "やや乾燥"
            st.session_state.left_right_diff = "小さい"

            st.session_state.step = 3
            st.rerun()


# =========================================================
# STEP 3
# 診断結果
# =========================================================
elif st.session_state.step == 3:

    toe_type = st.session_state.toe_type
    foot_color = st.session_state.foot_color
    arch = st.session_state.arch
    callus = st.session_state.callus
    dryness = st.session_state.dryness
    left_right_diff = st.session_state.left_right_diff

    cold = st.session_state.cold
    swelling = st.session_state.swelling
    tired = st.session_state.tired
    standing = st.session_state.standing
    shoes = st.session_state.shoes
    foot_concern = st.session_state.foot_concern
    aroma_goal = st.session_state.aroma_goal

    st.subheader("診断結果")

    st.caption(
        "現在は画像判定部分のみ仮データです。"
        "今後、足裏写真から自動判定するように変更します。"
    )

    st.divider()

    # =====================================================
    # 1. 足指タイプ
    # =====================================================
    if toe_type == "エジプト型":
        toe_text = (
            "親指が最も長く、小指に向かって順番に短くなるタイプです。"
            "リフレクソロジー的な性格傾向では、"
            "安定感や現実性を重視するタイプとして紹介されることがあります。"
        )

    elif toe_type == "ギリシャ型":
        toe_text = (
            "第2趾が親指より長いタイプです。"
            "リフレクソロジー的な性格傾向では、"
            "行動力や感性が強いタイプとして紹介されることがあります。"
        )

    else:
        toe_text = (
            "親指から中指付近までの長さが比較的そろっているタイプです。"
            "リフレクソロジー的な性格傾向では、"
            "バランスや慎重さを大切にするタイプとして紹介されることがあります。"
        )

    st.markdown("### 1. 足指タイプ")
    st.markdown(
        f"""
        <div class="result-card">
            <strong>{toe_type}</strong><br><br>
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
            "写真上では足裏に赤みがやや強く見られます。"
            "リフレクソロジー的には、活動量や緊張感が高い時、"
            "疲れがたまっている時の傾向として捉えることがあります。"
        )

    elif foot_color == "黄み強め":
        color_text = (
            "写真上では黄みがやや強く見られます。"
            "リフレクソロジー的には、疲れの蓄積や"
            "気分転換を求めている時の傾向として捉えることがあります。"
        )

    elif foot_color == "白っぽい":
        color_text = (
            "写真上では足裏がやや白っぽく見られます。"
            "リフレクソロジー的には、休息を求めている時や"
            "活力を温存したい時の傾向として捉えることがあります。"
        )

    else:
        color_text = (
            "写真上では、大きな色味の偏りは目立ちません。"
        )

    st.markdown("### 2. 足裏カラー")
    st.markdown(
        f"""
        <div class="result-card">
            <strong>{foot_color}</strong><br><br>
            {color_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # 3. 現在の心身傾向
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
            "現在は心身ともに休息を意識したい傾向です。"
            "無理に活動量を増やすより、ゆっくり休む時間を確保するのがおすすめです。"
        )
    elif rest_score >= 3:
        mind_body = (
            "少し疲れがたまりやすい傾向が見られます。"
            "短時間でも休息や気分転換を取り入れるのがおすすめです。"
        )
    else:
        mind_body = (
            "質問回答上では、大きな疲労傾向は目立ちません。"
            "現在の状態を維持しつつ、定期的なセルフケアがおすすめです。"
        )

    st.markdown("### 3. 現在の心身傾向")
    st.markdown(
        f"""
        <div class="result-card">
            {mind_body}
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # 4. 歩き方の傾向
    # =====================================================
    if callus == "前足部":
        walk_text = (
            "前足部に負担がかかりやすい傾向として考えられます。"
            "長時間歩いた時に足の前側が疲れやすい場合は、"
            "歩幅や靴のクッション性を見直すのもおすすめです。"
        )

    elif callus == "かかと":
        walk_text = (
            "かかと側への負担がやや強い傾向として考えられます。"
            "着地時の衝撃を和らげるクッション性のある靴がおすすめです。"
        )

    elif callus == "親指側":
        walk_text = (
            "足の内側に負担がかかりやすい傾向として考えられます。"
        )

    elif callus == "小指側":
        walk_text = (
            "足の外側に負担がかかりやすい傾向として考えられます。"
        )

    else:
        walk_text = (
            "足裏全体に大きな偏りは目立たない傾向です。"
        )

    st.markdown("### 4. 歩き方の傾向")
    st.markdown(
        f"""
        <div class="result-card">
            {walk_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # 5. おすすめの靴
    # =====================================================
    shoe_recommendations = []

    if tired == "はい":
        shoe_recommendations.append("クッション性が高い")

    if standing == "はい":
        shoe_recommendations.append("安定感がある")

    if arch == "低め":
        shoe_recommendations.append("適度なアーチサポートがある")

    if callus == "前足部":
        shoe_recommendations.append("つま先・前足部にゆとりがある")

    if callus == "小指側":
        shoe_recommendations.append("足幅に余裕がある")

    if not shoe_recommendations:
        shoe_recommendations.append("足幅と足長に合ったフィット感のある")

    shoe_text = "、".join(shoe_recommendations) + "靴がおすすめです。"

    st.markdown("### 5. おすすめの靴")
    st.markdown(
        f"""
        <div class="result-card">
            {shoe_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # 6. おすすめアロマ
    # =====================================================
    if aroma_goal == "リラックス":
        aroma = "ラベンダー"
        aroma_text = "ゆったりと過ごしたい時間におすすめです。"

    elif aroma_goal == "リフレッシュ":
        aroma = "レモン"
        aroma_text = "気持ちを切り替えたい時におすすめです。"

    elif aroma_goal == "集中":
        aroma = "ローズマリー"
        aroma_text = "集中したい時間におすすめです。"

    elif aroma_goal == "睡眠":
        aroma = "ラベンダー"
        aroma_text = "就寝前など落ち着きたい時間におすすめです。"

    else:
        aroma = "スイートオレンジ"
        aroma_text = "気分転換したい時におすすめです。"

    st.markdown("### 6. おすすめアロマ")
    st.markdown(
        f"""
        <div class="result-card">
            <strong>{aroma}</strong><br><br>
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
        care_list.append("足元を温める")

    if swelling == "はい":
        care_list.append("軽いストレッチや足首運動")

    if tired == "はい":
        care_list.append("足を休ませる時間をつくる")

    if dryness == "やや乾燥":
        care_list.append("入浴後の保湿")

    if callus != "なし":
        care_list.append("角質部分に過度な負担をかけない")

    if not care_list:
        care_list.append("定期的な保湿と足裏ストレッチ")

    care_text = "・".join(care_list)

    st.markdown("### 7. セルフケア")
    st.markdown(
        f"""
        <div class="result-card">
            {care_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.caption(
        "この診断は医療行為・医学的診断を目的としたものではありません。"
        "足裏カラーや性格傾向は、リフレクソロジー上の考え方をもとにした"
        "ウェルネス・エンタメ要素を含みます。"
    )

    st.write("")

    if st.button("最初から診断する"):
        st.session_state.step = 1
        st.rerun()