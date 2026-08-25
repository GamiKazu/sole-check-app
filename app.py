import streamlit as st

st.title("顔タイプ診断")

st.write("顔写真をアップロードして診断します")

photo = st.file_uploader(
    "顔写真を選んでください",
    type=["jpg", "jpeg", "png"]
)

if photo:
    st.image(photo)
    st.success("画像を読み込みました！")
    st.write("ここに診断結果を表示します。")