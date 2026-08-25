import streamlit as st

st.title("足裏診断")

st.write("足裏写真を撮影して診断します")

photo = st.camera_input("足裏を撮影してください")

if photo:
    st.image(photo)
    st.success("撮影できました！")
    st.write("ここに診断結果を表示します。")