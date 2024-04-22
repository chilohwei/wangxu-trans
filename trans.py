import streamlit as st
from openai import OpenAI

def init_moonshot_client(api_key):
    return OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1",
    )

def translate_text(api_key, target_lang, text, file_type, progress_callback):
    client = init_moonshot_client(api_key)
    system_prompt = f"你是网旭翻译家,擅长将各种文本,分别翻译为:{target_lang}。你的翻译风格简洁、优雅,符合语言文化背景习惯。"
    
    try:
        # 将文本分成多个部分进行翻译,每部分不超过5000个字符
        chunk_size = 5000 
        parts = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        num_parts = len(parts)
        translated_parts = []
        for i, part in enumerate(parts):
            progress_callback(i / num_parts, f"正在翻译部分 {i+1} / {num_parts}...")
            completion = client.chat.completions.create(
                model="moonshot-v1-128k",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": part}
                ],
                temperature=0.3,
            )
            translated_parts.append(completion.choices[0].message.content)
        
        # 更新进度到100%
        progress_callback(1, "翻译完成。")
        return "".join(translated_parts)
    except Exception as e:
        st.error(f"请求Moonshot API失败: {str(e)}")
        return None

def parse_file(uploaded_file):
    file_content = uploaded_file.getvalue().decode("utf-8")
    return file_content, uploaded_file.type

def format_download_filename(original_filename, target_lang):
    lang_suffix_map = {
        "简体中文": "zh-Hans", "繁体中文": "zh-Hant", "英语": "en",
        "日语": "ja", "法语": "fr", "德语": "de", "西班牙语": "es",
        "葡萄牙语": "pt", "意大利语": "it", "阿拉伯语": "ar", "韩语": "ko"  
    }
    lang_suffix = lang_suffix_map.get(target_lang, "")
    name_part, extension_part = original_filename.rsplit('.', 1)
    return f"{name_part}-translated-{lang_suffix}.{extension_part}"

def main():
    st.set_page_config(page_title="多语言翻译工具", layout="wide")
    st.sidebar.title("上传文件和设置")
    uploaded_file = st.sidebar.file_uploader("选择一个文本文件", type=["txt", "xml", "json"])
    api_key = st.sidebar.text_input("输入Moonshot API Key", value="", type="password")
    translate_button = st.sidebar.button("翻译")

    st.title("多语言翻译预览")

    if uploaded_file is not None:
        original_text, file_type = parse_file(uploaded_file)
        st.text_area("原文预览", original_text, height=200)

        lang_mapping = {
            "简体中文": "简体中文", "繁体中文": "繁体中文", "英语": "英语",  
            "日语": "日语", "法语": "法语", "德语": "德语", "西班牙语": "西班牙语",
            "葡萄牙语": "葡萄牙语", "意大利语": "意大利语", "阿拉伯语": "阿拉伯语", "韩语": "韩语"
        }
        target_lang = st.selectbox("选择目标语言", list(lang_mapping.keys()))
        
        if translate_button and original_text:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(progress, message):
                progress_bar.progress(progress)
                status_text.text(message)
            
            translated_text = translate_text(api_key, lang_mapping[target_lang], original_text, file_type, progress_callback)
            
            if translated_text:
                st.text_area("翻译结果", translated_text, height=200)
                download_filename = format_download_filename(uploaded_file.name, lang_mapping[target_lang]) 
                st.download_button(label="下载翻译文本", data=translated_text.encode("utf-8"),
                                   file_name=download_filename,
                                   mime=file_type)
            progress_bar.empty()
            status_text.empty()
    else:
        st.info("请在左侧上传要翻译的文本文件")

if __name__ == "__main__":
    main()