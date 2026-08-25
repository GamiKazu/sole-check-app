import streamlit as st

st.set_page_config(
    page_title="足裏タイプ診断",
    layout="centered"
)

# セッション状態
if "step" not in st.session_state:
    st.session_state.step = 1

st.title("足裏タイプ診断")
st.write("簡単な質問と足裏写真から、あなたの足の傾向をチェックします。")

# STEP 1：質問
if st.session_state.step == 1:

    st.subheader("STEP 1　簡単な質問")

    cold = st.radio(
        "足が冷えやすいですか？",
        ["はい", "いいえ"]
    )

    swelling = st.radio(
        "むくみを感じることがありますか？",
        ["はい", "いいえ"]
    )

    tired = st.radio(
        "長時間歩くと足が疲れやすいですか？",
        ["はい", "いいえ"]
    )

    shoes = st.selectbox(
        "普段よく履く靴は？",
        ["スニーカー", "革靴", "パンプス", "サンダル", "その他"]
    )

    work = st.radio(
        "立っている時間が長いですか？",
        ["はい", "いいえ"]
    )

    aroma_goal = st.selectbox(
        "今、一番求めているものは？",
        ["リラックス", "リフレッシュ", "集中", "睡眠"]
    )

    if st.button("次へ", type="primary"):
        st.session_state.cold = cold
        st.session_state.swelling = swelling
        st.session_state.tired = tired
        st.session_state.shoes = shoes
        st.session_state.work = work
        st.session_state.aroma_goal = aroma_goal

        st.session_state.step = 2
        st.rerun()


# STEP 2：足裏写真
elif st.session_state.step == 2:

    st.subheader("STEP 2　足裏写真")

    st.write("右足と左足の足裏写真をアップロードしてください。")

    right_foot = st.file_uploader(
        "右足",
        type=["jpg", "jpeg", "png"],
        key="right"
    )

    left_foot = st.file_uploader(
        "左足",
        type=["jpg", "jpeg", "png"],
        key="left"
    )

    if right_foot:
        st.image(right_foot, caption="右足")

    if left_foot:
        st.image(left_foot, caption="左足")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("戻る"):
            st.session_state.step = 1
            st.rerun()

    with col2:
        if st.button(
            "診断する",
            type="primary",
            disabled=not (right_foot and left_foot)
        ):
            st.session_state.step = 3
            st.rerun()


# STEP 3：仮診断結果
elif st.session_state.step == 3:

    st.subheader("診断結果")

    st.write("足裏タイプ")
    st.info("バランス型")

    st.write("歩き方の傾向")
    st.write("現在は仮結果です。今後、足裏画像の分析結果を反映します。")

    st.write("おすすめの靴")
    st.write("クッション性と安定感のある靴がおすすめです。")

    st.write("おすすめのアロマ")

    if st.session_state.aroma_goal == "リラックス":
        aroma = "ラベンダー"
    elif st.session_state.aroma_goal == "リフレッシュ":
        aroma = "レモン"
    elif st.session_state.aroma_goal == "集中":
        aroma = "ローズマリー"
    else:
        aroma = "ラベンダー"

    st.success(aroma)

    if st.button("最初から診断する"):
        st.session_state.step = 1
        st.rerun()