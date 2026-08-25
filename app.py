import streamlit as st

st.set_page_config(
    page_title="顔タイプ診断",
    layout="centered"
)

st.markdown("""
<style>
    .block-container {
        max-width: 650px;
        padding-top: 2rem;
    }

    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .sub-title {
        text-align: center;
        color: #777;
        margin-bottom: 2rem;
    }

    .result-box {
        padding: 20px;
        border-radius: 12px;
        background-color: #f5f5f5;
        margin-top: 20px;
    }

    div.stButton > button {
        width: 100%;
        height: 52px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">顔タイプ診断</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">写真からあなたの印象タイプを診断します</div>',
    unsafe_allow_html=True
)

photo = st.file_uploader(
    "顔写真をアップロード",
    type=["jpg", "jpeg", "png"]
)

if photo:
    st.image(
        photo,
        caption="選択した写真",
        use_container_width=True
    )

    if st.button("診断する", type="primary"):
        with st.spinner("診断中です..."):

            # 仮の診断結果
            result_type = "ムードメーカータイプ"
            social = 82
            calm = 64
            curiosity = 91

        st.markdown("## 診断結果")

        st.markdown(
            f"""
            <div class="result-box">
                <h2>{result_type}</h2>
                <p>
                    明るく親しみやすい印象を与えやすく、
                    周囲を自然に盛り上げるタイプです。
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("### 印象スコア")

        st.write(f"社交性　{social}%")
        st.progress(social)

        st.write(f"落ち着き　{calm}%")
        st.progress(calm)

        st.write(f"好奇心　{curiosity}%")
        st.progress(curiosity)

else:
    st.info("顔写真を選択してください")