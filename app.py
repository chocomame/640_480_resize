import streamlit as st
from PIL import Image, UnidentifiedImageError
import io
from concurrent.futures import ThreadPoolExecutor
import time

def resize_image(image, target_size=(640, 480)):
    # アスペクト比を計算
    aspect_ratio = image.width / image.height
    target_ratio = target_size[0] / target_size[1]

    if aspect_ratio > target_ratio:
        # 横長の画像
        new_height = target_size[1]
        new_width = int(new_height * aspect_ratio)
    else:
        # 縦長または正方形の画像
        new_width = target_size[0]
        new_height = int(new_width / aspect_ratio)

    # 画像をリサイズ
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # 中央部分を切り取る
    left = (resized_image.width - target_size[0]) // 2
    top = (resized_image.height - target_size[1]) // 2
    right = left + target_size[0]
    bottom = top + target_size[1]

    return resized_image.crop((left, top, right, bottom))

@st.cache_data
def process_image(uploaded_file):
    try:
        start_time = time.time()
        image = Image.open(uploaded_file)
        resized_image = resize_image(image)
        
        buffered = io.BytesIO()
        resized_image.save(buffered, format="PNG")
        
        processing_time = time.time() - start_time
        
        return {
            "original": image,
            "resized": resized_image,
            "download_data": buffered.getvalue(),
            "filename": uploaded_file.name,
            "processing_time": processing_time,
            "error": None
        }
    except UnidentifiedImageError:
        return {"error": "無効な画像ファイルです。", "filename": uploaded_file.name}
    except Exception as e:
        return {"error": f"エラーが発生しました: {str(e)}", "filename": uploaded_file.name}

st.set_page_config(page_title="画像リサイズアプリ", layout="wide")

st.title("複数画像リサイズアプリ")

st.info("このアプリは、アップロードされた画像を640x480ピクセルにリサイズします。余白は作成されません。")

uploaded_files = st.file_uploader("画像をアップロードしてください（複数可）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner('画像を処理中...'):
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_image, uploaded_files))

    for result in results:
        if result.get("error"):
            st.error(f"エラー: {result['filename']} - {result['error']}")
        else:
            st.subheader(f"画像: {result['filename']}")
            col1, col2 = st.columns(2)
            with col1:
                st.image(result["original"], caption="元の画像", use_column_width=True)
            with col2:
                st.image(result["resized"], caption="リサイズ後の画像 (640x480)", use_column_width=True)

            st.download_button(
                label=f"リサイズした画像をダウンロード: {result['filename']}",
                data=result["download_data"],
                file_name=f"resized_{result['filename']}",
                mime="image/png"
            )
            
            st.text(f"処理時間: {result['processing_time']:.2f} 秒")
            st.divider()

st.sidebar.header("アプリについて")
st.sidebar.info("""
このアプリは以下の機能を提供します：
- 複数画像の一括アップロードとリサイズ
- すべての画像を640x480ピクセルに変換（余白なし）
- リサイズ前後の画像プレビュー
- リサイズ済み画像のダウンロード
- エラーハンドリングと処理時間の表示
""")