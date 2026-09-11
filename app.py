import streamlit as st
import pandas as pd
import os
import urllib.request
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 페이지 기본 설정
st.set_page_config(
    page_title="위드멤버 월간 마케팅 보고서", page_icon="📊", layout="wide"
)

# --- [한글 폰트 자동 설정 (이미지 생성용)] ---
font_path = "NanumGothic.ttf"
if not os.path.exists(font_path):
    # 나눔고딕 폰트가 로컬(또는 클라우드)에 없으면 자동 다운로드
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    urllib.request.urlretrieve(font_url, font_path)

# 세션 스테이트 초기화
if "report_data" not in st.session_state:
    st.session_state.report_data = []

st.title("📊 위드멤버 월간 마케팅 성과 보고서")
st.markdown("매장별 마케팅 데이터와 관리 내용을 입력하고 **이미지 파일로 보고서를 다운로드**하세요.")

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 및 관리 내용 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명", placeholder="예: 강남 맛집")
        prev_rank = st.text_input("전월 플레이스 순위", placeholder="예: 15위")
        current_rank = st.text_input("당월 플레이스 순위", placeholder="예: 3위")
    with col2:
        visitor_review = st.number_input("이번 달 방문자 리뷰 수", min_value=0, step=1)
        reply_count = st.number_input("답글 수", min_value=0, step=1)

    st.markdown("---")
    
    # 대표키워드 5칸
    with st.expander("📌 대표키워드 수정/추가 (최대 5개)", expanded=True):
        keywords = []
        k_cols = st.columns(5)
        for i in range(5):
            with k_cols[i]:
                kw = st.text_input(f"키워드 {i+1}", key=f"kw_{i}")
                keywords.append(kw)

    # 리뷰 링크 10칸
    with st.expander("🔗 체험단 / 기자단 리뷰 링크 (최대 10개)"):
        links = []
        l_cols1, l_cols2 = st.columns(2)
        for i in range(10):
            col = l_cols1 if i < 5 else l_cols2
            with col:
                link = st.text_input(f"리뷰 링크 {i+1}", key=f"link_{i}")
                links.append(link)

    st.markdown("---")
    
    # 1달간 관리 내용
    management_report = st.text_area(
        "💡 1달간 관리 내용 보고", 
        placeholder="이번 달 진행한 SEO 최적화 작업, 리뷰 관리 내역, 영상 콘텐츠 제작 및 배포 현황 등을 상세히 적어주세요.", 
        height=150
    )

    submitted = st.form_submit_button("➕ 보고서 데이터 추가")

    if submitted:
        if store_name:
            # 빈칸 제외하고 리스트 정리
            valid_keywords = [k for k in keywords if k.strip()]
            valid_links = [l for l in links if l.strip()]

            new_data = {
                "매장명": store_name,
                "전월 순위": prev_rank,
                "당월 순위": current_rank,
                "방문자 리뷰 수": visitor_review,
                "답글 수": reply_count,
                "대표키워드": valid_keywords,
                "리뷰링크": valid_links,
                "관리내용": management_report
            }
            st.session_state.report_data.append(new_data)
            st.success(f"[{store_name}] 데이터가 추가되었습니다! 아래에서 이미지를 생성하세요.")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 보고서 이미지 생성 및 다운로드 로직 ---
def create_report_image(data):
    # 이미지 사이즈 및 배경 설정
    img_width = 800
    img_height = 1200
    img = Image.new("RGB", (img_width, img_height), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    # 폰트 설정
    try:
        title_font = ImageFont.truetype(font_path, 36)
        sub_font = ImageFont.truetype(font_path, 24)
        body_font = ImageFont.truetype(font_path, 16)
        bold_font = ImageFont.truetype(font_path, 18) # 굵게 표현할 때 대체 사용
    except:
        title_font = sub_font = body_font = bold_font = ImageFont.load_default()

    y = 50
    margin = 50

    # 1. 타이틀
    draw.text((margin, y), f"위드멤버 월간 마케팅 보고서", font=title_font, fill=(33, 37, 41))
    y += 60
    draw.text((margin, y), f"🏢 매장명 : {data['매장명']}", font=sub_font, fill=(0, 102, 204))
    y += 50
    draw.line([(margin, y), (img_width - margin, y)], fill=(200, 200, 200), width=2)
    y += 30

    # 2. 성과 요약
    draw.text((margin, y), "[ 성과 요약 ]", font=sub_font, fill=(33, 37, 41))
    y += 40
    summary_text = (
        f"- 플레이스 순위 : (전월) {data['전월 순위']} ➔ (당월) {data['당월 순위']}\n"
        f"- 이번 달 방문자 리뷰 수 : {data['방문자 리뷰 수']} 개\n"
        f"- 이번 달 답글 수 : {data['답글 수']} 개"
    )
    draw.text((margin + 10, y), summary_text, font=body_font, fill=(50, 50, 50), spacing=10)
    y += 90

    # 3. 대표 키워드
    draw.text((margin, y), "[ 대표키워드 관리 현황 ]", font=sub_font, fill=(33, 37, 41))
    y += 40
    kw_text = ", ".join(data['대표키워드']) if data['대표키워드'] else "입력된 키워드 없음"
    draw.text((margin + 10, y), f"검색 키워드: {kw_text}", font=body_font, fill=(50, 50, 50))
    y += 50

    # 4. 리뷰 진행 현황 (링크)
    draw.text((margin, y), "[ 체험단 / 기자단 배포 링크 ]", font=sub_font, fill=(33, 37, 41))
    y += 40
    if data['리뷰링크']:
        for i, link in enumerate(data['리뷰링크']):
            draw.text((margin + 10, y), f"{i+1}. {link}", font=body_font, fill=(0, 86, 179))
            y += 25
    else:
        draw.text((margin + 10, y), "입력된 리뷰 링크 없음", font=body_font, fill=(100, 100, 100))
        y += 25
    y += 20

    # 5. 월간 관리 보고 내용
    draw.text((margin, y), "[ 월간 관리 보고 내용 ]", font=sub_font, fill=(33, 37, 41))
    y += 40
    
    # 텍스트 줄바꿈 처리 (가로폭에 맞게)
    report_lines = []
    for line in data['관리내용'].split('\n'):
        report_lines.extend(textwrap.wrap(line, width=45)) # width 조정으로 여백 맞춤

    if not report_lines:
        report_lines = ["입력된 내용 없음"]

    for line in report_lines:
        draw.text((margin + 10, y), line, font=body_font, fill=(50, 50, 50))
        y += 25

    # 여백 및 하단 워터마크
    y = img_height - 60
    draw.line([(margin, y), (img_width - margin, y)], fill=(200, 200, 200), width=2)
    draw.text((margin, y + 15), "WithMember Marketing Automation Report", font=body_font, fill=(150, 150, 150))

    # 이미지를 바이트로 변환
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

# --- [3] 입력된 데이터 확인 및 이미지 다운로드 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📥 작성된 보고서 이미지 다운로드")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            st.markdown(f"### {idx+1}. {data['매장명']} 보고서")
            
            # 이미지 생성
            img_bytes = create_report_image(data)
            
            # 다운로드 버튼
            st.download_button(
                label=f"🖼️ [{data['매장명']}] 보고서 이미지(PNG) 다운로드",
                data=img_bytes,
                file_name=f"위드멤버_월간보고서_{data['매장명']}.png",
                mime="image/png",
                key=f"download_{idx}"
            )
            
            # 미리보기 토글
            with st.expander("미리보기 보기"):
                st.image(img_bytes, width=500)
            st.markdown("---")

    # 전체 데이터 초기화 버튼
    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
