import streamlit as st
import pandas as pd
import os
import urllib.request
import re
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
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    urllib.request.urlretrieve(font_url, font_path)

# 세션 스테이트 초기화
if "report_data" not in st.session_state:
    st.session_state.report_data = []

st.title("📊 위드멤버 월간 마케팅 성과 보고서")
st.markdown("데이터를 입력하면 **AI가 관리 내용을 자동 분석 및 작성**합니다. 보고서 이미지와 함께 **클릭 가능한 링크**를 확인하세요.")

# --- 자동 보고서 작성 로직 ---
def generate_smart_report(data_dict):
    report = []
    
    # 1. 순위 분석
    prev_nums = re.findall(r'\d+', data_dict.get('전월 순위', ''))
    curr_nums = re.findall(r'\d+', data_dict.get('당월 순위', ''))
    
    if prev_nums and curr_nums:
        p_rank = int(prev_nums[0])
        c_rank = int(curr_nums[0])
        if c_rank < p_rank:
            report.append(f"✅ 플레이스 노출 순위가 {p_rank}위에서 {c_rank}위로 상승하여 가시성이 크게 개선되었습니다.")
        elif c_rank == p_rank:
            report.append(f"✅ 플레이스 노출 순위가 {c_rank}위로 안정적으로 유지되고 있습니다.")
        else:
            report.append(f"✅ 플레이스 노출 순위 방어 및 추가 상승을 위한 로직 분석과 최적화를 진행 중입니다.")
    
    # 2. 리뷰 및 답글 분석
    v_review = data_dict.get('방문자 리뷰 수', 0)
    r_count = data_dict.get('답글 수', 0)
    if v_review > 0 or r_count > 0:
        report.append(f"✅ 이번 달 신규 방문자 리뷰 {v_review}건 유입 및 {r_count}건의 답글 관리를 통해 고객 소통 지수(SEO)를 높였습니다.")
        
    # 3. 키워드 분석
    keywords = data_dict.get('대표키워드', [])
    if keywords:
        report.append(f"✅ [{', '.join(keywords)}] 핵심 키워드를 중심으로 타겟 고객 노출도 향상 작업을 진행했습니다.")
        
    # 4. 블로그/기자단 링크 분석
    links = data_dict.get('리뷰링크', [])
    if links:
        report.append(f"✅ 고품질 체험단 및 기자단 리뷰 총 {len(links)}건을 성공적으로 발행하여 브랜드 인지도를 확대했습니다.")
        
    report.append("✅ 다음 달에도 지속적인 모니터링과 트래픽 관리를 통해 꾸준한 매출 상승에 기여하겠습니다.")
    
    return "\n\n".join(report)

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명", placeholder="예: 강남 맛집")
        prev_rank = st.text_input("전월 플레이스 순위", placeholder="예: 15위")
        current_rank = st.text_input("당월 플레이스 순위", placeholder="예: 3위")
    with col2:
        visitor_review = st.number_input("이번 달 방문자 리뷰 수", min_value=0, step=1)
        reply_count = st.number_input("답글 수", min_value=0, step=1)

    st.markdown("---")
    
    with st.expander("📌 대표키워드 수정/추가 (최대 5개)", expanded=True):
        keywords = []
        k_cols = st.columns(5)
        for i in range(5):
            with k_cols[i]:
                kw = st.text_input(f"키워드 {i+1}", key=f"kw_{i}")
                keywords.append(kw)

    with st.expander("🔗 체험단 / 기자단 리뷰 링크 (최대 10개)"):
        links = []
        l_cols1, l_cols2 = st.columns(2)
        for i in range(10):
            col = l_cols1 if i < 5 else l_cols2
            with col:
                link = st.text_input(f"리뷰 링크 {i+1}", key=f"link_{i}")
                links.append(link)

    st.markdown("---")
    st.info("💡 '1달간 관리 내용'을 비워두시면 입력된 수치를 바탕으로 내용이 **자동 생성**됩니다.")
    management_report = st.text_area(
        "💡 1달간 관리 내용 보고 (직접 작성 시 이곳에 입력)", 
        placeholder="비워두시면 자동으로 분석 텍스트가 채워집니다.", 
        height=100
    )

    submitted = st.form_submit_button("➕ 분석 및 보고서 생성")

    if submitted:
        if store_name:
            valid_keywords = [k for k in keywords if k.strip()]
            valid_links = [l for l in links if l.strip()]

            # 데이터 딕셔너리 구성
            temp_data = {
                "매장명": store_name,
                "전월 순위": prev_rank,
                "당월 순위": current_rank,
                "방문자 리뷰 수": visitor_review,
                "답글 수": reply_count,
                "대표키워드": valid_keywords,
                "리뷰링크": valid_links,
            }
            
            # 관리 내용을 직접 안 적었다면 자동 생성
            if not management_report.strip():
                final_report = generate_smart_report(temp_data)
            else:
                final_report = management_report
                
            temp_data["관리내용"] = final_report

            st.session_state.report_data.append(temp_data)
            st.success(f"[{store_name}] 보고서가 성공적으로 생성되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 보고서 이미지 생성 로직 ---
def create_report_image(data):
    img_width = 800
    img_height = 1200
    img = Image.new("RGB", (img_width, img_height), color=(248, 249, 250))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(font_path, 36)
        sub_font = ImageFont.truetype(font_path, 24)
        body_font = ImageFont.truetype(font_path, 16)
    except:
        title_font = sub_font = body_font = ImageFont.load_default()

    y = 50
    margin = 50

    draw.text((margin, y), f"위드멤버 월간 마케팅 보고서", font=title_font, fill=(33, 37, 41))
    y += 60
    draw.text((margin, y), f"🏢 매장명 : {data['매장명']}", font=sub_font, fill=(0, 102, 204))
    y += 50
    draw.line([(margin, y), (img_width - margin, y)], fill=(200, 200, 200), width=2)
    y += 30

    draw.text((margin, y), "[ 성과 요약 ]", font=sub_font, fill=(33, 37, 41))
    y += 40
    summary_text = (
        f"- 플레이스 순위 : (전월) {data['전월 순위']} ➔ (당월) {data['당월 순위']}\n"
        f"- 이번 달 방문자 리뷰 수 : {data['방문자 리뷰 수']} 개\n"
        f"- 이번 달 답글 수 : {data['답글 수']} 개"
    )
    draw.text((margin + 10, y), summary_text, font=body_font, fill=(50, 50, 50), spacing=10)
    y += 90

    draw.text((margin, y), "[ 대표키워드 관리 현황 ]", font=sub_font, fill=(33, 37, 41))
    y += 40
    kw_text = ", ".join(data['대표키워드']) if data['대표키워드'] else "입력된 키워드 없음"
    draw.text((margin + 10, y), f"검색 타겟: {kw_text}", font=body_font, fill=(50, 50, 50))
    y += 60

    draw.text((margin, y), "[ 월간 관리 보고 내용 ]", font=sub_font, fill=(33, 37, 41))
    y += 40
    
    report_lines = []
    for line in data['관리내용'].split('\n'):
        if line.strip():
            report_lines.extend(textwrap.wrap(line, width=45))

    for line in report_lines:
        draw.text((margin + 10, y), line, font=body_font, fill=(50, 50, 50))
        y += 25

    y = img_height - 60
    draw.line([(margin, y), (img_width - margin, y)], fill=(200, 200, 200), width=2)
    draw.text((margin, y + 15), "WithMember Marketing Automation Report", font=body_font, fill=(150, 150, 150))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- [3] 결과 출력 및 클릭 가능한 공유 텍스트 제공 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📤 생성된 보고서 결과")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"### 🖼️ {data['매장명']} 보고서 이미지")
                img_bytes = create_report_image(data)
                
                st.image(img_bytes, use_container_width=True)
                st.download_button(
                    label="이미지(PNG) 다운로드",
                    data=img_bytes,
                    file_name=f"위드멤버_{data['매장명']}_보고서.png",
                    mime="image/png",
                    key=f"dl_img_{idx}"
                )
                
            with col2:
                st.markdown("### 💬 광고주 카톡 발송용 텍스트 (복사/붙여넣기)")
                st.caption("아래 내용을 복사해서 카카오톡으로 전송하시면 링크를 클릭할 수 있습니다.")
                
                # 카톡 공유용 포맷 생성
                share_text = f"안녕하세요 대표님! 위드멤버입니다.\n이번 달 [{data['매장명']}] 마케팅 관리 보고서 전달드립니다.\n\n"
                share_text += f"{data['관리내용']}\n\n"
                
                if data['리뷰링크']:
                    share_text += "🔗 [이번 달 체험단/기자단 발행 링크]\n"
                    for i, link in enumerate(data['리뷰링크']):
                        share_text += f"{i+1}. {link}\n"
                else:
                    share_text += "이번 달 발행된 리뷰 링크가 없습니다.\n"
                
                share_text += "\n상세 수치는 첨부해 드린 보고서 이미지를 확인해 주세요. 감사합니다!"
                
                # Streamlit UI에 마크다운으로 클릭 가능한 링크 렌더링
                st.text_area("복사 영역", value=share_text, height=350, key=f"txt_{idx}")
                
                # 화면에서 직접 클릭해 볼 수 있는 링크 리스트
                if data['리뷰링크']:
                    st.markdown("**👉 등록된 리뷰 바로가기 (클릭 테스트용)**")
                    for i, link in enumerate(data['리뷰링크']):
                        st.markdown(f"- [리뷰 {i+1} 보러가기]({link})")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
