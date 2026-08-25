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
    .block-container {
        max-width: 700px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .sub-title {
        text-align: center;
        color: #777;
        margin-bottom: 2rem;
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
# 簡単な質問
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

    standing = st.radio(
        "普段、立っている時間は長いですか？",
        ["はい", "いいえ"],
        horizontal=True
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
        st.session_state.shoes = shoes
        st.session_state.standing = standing
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
        "両足の写真だけでは細かい部分が分かりにくい場合は、"
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

    # -----------------------------
    # プレビュー
    # -----------------------------
    if both_feet:
        st.image(
            both_feet,
            caption="両足の写真",
            use_container_width=True
        )

    if right_foot:
        st.image(
            right_foot,
            caption="右足の写真",
            use_container_width=True
        )

    if left_foot:
        st.image(
            left_foot,
            caption="左足の写真",
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
            st.session_state.step = 3
            st.rerun()


# =========================================================
# STEP 3
# 仮の診断結果
# =========================================================
elif st.session_state.step == 3:

    st.subheader("診断結果")

    st.caption(
        "現在は画面確認用の仮診断です。"
        "今後、足裏写真の画像分析を組み込みます。"
    )

    st.divider()

    # -----------------------------
    # 足裏タイプ
    # -----------------------------
    st.markdown("### 足裏タイプ")

    st.info("バランス型")

    st.write(
        "全体的にバランスが取りやすいタイプとして表示しています。"
    )

    st.divider()

    # -----------------------------
    # 歩き方
    # -----------------------------
    st.markdown("### 歩き方の傾向")

    st.write(
        "現在は仮結果です。"
        "今後は足裏写真や質問内容から歩き方の傾向を表示します。"
    )

    st.divider()

    # -----------------------------
    # 靴
    # -----------------------------
    st.markdown("### おすすめの靴")

    if st.session_state.tired == "はい":
        st.write(
            "クッション性と安定感があり、"
            "足への負担を軽減しやすい靴がおすすめです。"
        )
    else:
        st.write(
            "足幅や足の形に合い、"
            "つま先に適度なゆとりがある靴がおすすめです。"
        )

    st.divider()

    # -----------------------------
    # 足裏コンディション
    # -----------------------------
    st.markdown("### 足裏コンディション")

    if st.session_state.cold == "はい":
        st.write(
            "冷えを感じやすい傾向があるようです。"
        )

    if st.session_state.swelling == "はい":
        st.write(
            "むくみを感じやすい傾向があるようです。"
        )

    if (
        st.session_state.cold == "いいえ"
        and st.session_state.swelling == "いいえ"
    ):
        st.write(
            "現時点の質問回答では、"
            "冷えやむくみの自覚は少ないようです。"
        )

    st.divider()

    # -----------------------------
    # 性格傾向
    # -----------------------------
    st.markdown("### 性格傾向")

    st.write(
        "今後、リフレクソロジーをベースにした"
        "エンタメ要素として表示します。"
    )

    st.divider()

    # -----------------------------
    # アロマ
    # -----------------------------
    st.markdown("### おすすめのアロマ")

    goal = st.session_state.aroma_goal

    if goal == "リラックス":
        aroma = "ラベンダー"
        aroma_text = "ゆったり過ごしたい時間におすすめです。"

    elif goal == "リフレッシュ":
        aroma = "レモン"
        aroma_text = "気持ちを切り替えたい時におすすめです。"

    elif goal == "集中":
        aroma = "ローズマリー"
        aroma_text = "集中したい時間におすすめです。"

    elif goal == "睡眠":
        aroma = "ラベンダー"
        aroma_text = "就寝前など落ち着きたい時間におすすめです。"

    else:
        aroma = "スイートオレンジ"
        aroma_text = "気分転換したい時におすすめです。"

    st.success(aroma)

    st.write(aroma_text)

    st.divider()

    st.caption(
        "この診断は医療行為・医学的診断を目的としたものではありません。"
    )

    st.write("")

    if st.button("最初から診断する"):
        st.session_state.step = 1
        st.rerun()