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
    page_title="위드멤버 프리미엄 월간 마케팅 보고서", 
    page_icon="📊", 
    layout="wide"
)

# --- [한글 폰트 자동 다운로드 및 설정] ---
font_path = "NanumGothic.ttf"
font_bold_path = "NanumGothicBold.ttf"

if not os.path.exists(font_path):
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    urllib.request.urlretrieve(font_url, font_path)

if not os.path.exists(font_bold_path):
    font_bold_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
    urllib.request.urlretrieve(font_bold_url, font_bold_path)

# 세션 스테이트 초기화
if "report_data" not in st.session_state:
    st.session_state.report_data = []

# --- [유틸리티 함수] ---
def format_rank(rank_str):
    """숫자 뒤에 '위' 문구를 자동으로 부착하는 함수"""
    rank_str = str(rank_str).strip()
    if not rank_str:
        return "-"
    # 이미 '위'가 붙어있지 않다면 숫자에 '위' 붙이기
    if not rank_str.endswith("위"):
        return f"{rank_str}위"
    return rank_str

def generate_smart_report(data_dict):
    """입력 데이터를 바탕으로 전문적인 마케팅 요약문 생성"""
    report = []
    p_rank = data_dict.get('전월 순위', '-')
    c_rank = data_dict.get('당월 순위', '-')
    
    report.append(f"• [플레이스 순위] {p_rank} ➔ {c_rank} (노출 최적화 진행 중)")
    
    v_review = data_dict.get('방문자 리뷰 수', 0)
    r_count = data_dict.get('답글 수', 0)
    report.append(f"• [리뷰 관리] 신규 방문자 리뷰 {v_review}건 유입 및 답글 {r_count}건 등록 완료")
    
    keywords = data_dict.get('대표키워드', [])
    if keywords:
        report.append(f"• [키워드 작업] {', '.join(keywords)} 타겟 순위 상승 작업 수행")
        
    links = data_dict.get('리뷰링크', [])
    if links:
        report.append(f"• [콘텐츠 배포] 체험단/기자단 고품질 리뷰 총 {len(links)}건 발행 완료")
        
    report.append("• [향후 계획] 지속적인 트래픽 모니터링 및 상위 노출 유지를 위한 로직 적용 예정")
    return "\n".join(report)

# --- [메인 헤더] ---
st.title("📊 위드멤버(WithMember) 프리미엄 월간 보고서")
st.markdown("매장 성과를 입력하면 **고급스러운 이미지 보고서**와 **카톡 발송용 클릭 가능한 리포트**를 동시에 생성합니다.")

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명 *", placeholder="예: 강남 맛집")
        prev_rank_input = st.text_input("전월 플레이스 순위", placeholder="예: 15 (자동으로 '15위' 입력됨)")
        current_rank_input = st.text_input("당월 플레이스 순위", placeholder="예: 3 (자동으로 '3위' 입력됨)")
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
                link = st.text_input(f"리뷰 링크 {i+1}", key=f"link_{i}", placeholder="https://...")
                links.append(link)

    st.markdown("---")
    
    # 카톡 발송용 메시지 및 관리 보고 내용
    st.subheader("💬 카톡 발송 및 보고 내용")
    kakao_msg_input = st.text_area(
        "카톡 전달 문구 / 월간 관리 보고 내용 (비워두시면 데이터 기반 자동 생성)", 
        placeholder="비워둘 경우 작성되는 예시:\n안녕하세요 대표님! 위드멤버입니다. 이번 달 플레이스 순위가 15위에서 3위로 상승했습니다...", 
        height=120
    )

    submitted = st.form_submit_button("🚀 고급 보고서 및 카톡 메시지 생성")

    if submitted:
        if store_name:
            valid_keywords = [k for k in keywords if k.strip()]
            valid_links = [l for l in links if l.strip()]

            # 순위 뒤에 '위' 붙이기 처리
            formatted_prev_rank = format_rank(prev_rank_input) if prev_rank_input else "-"
            formatted_curr_rank = format_rank(current_rank_input) if current_rank_input else "-"

            temp_data = {
                "매장명": store_name,
                "전월 순위": formatted_prev_rank,
                "당월 순위": formatted_curr_rank,
                "방문자 리뷰 수": visitor_review,
                "답글 수": reply_count,
                "대표키워드": valid_keywords,
                "리뷰링크": valid_links,
            }
            
            # 카톡/보고 문구 자동생성 또는 사용자 입력값 적용
            if not kakao_msg_input.strip():
                final_msg = generate_smart_report(temp_data)
            else:
                final_msg = kakao_msg_input
                
            temp_data["관리내용"] = final_msg

            st.session_state.report_data.append(temp_data)
            st.success(f"[{store_name}] 프리미엄 보고서가 생성되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 고급 보고서 이미지 생성 엔진 ---
def create_professional_image(data):
    img_width = 850
    img_height = 1300
    # 고급스러운 연한 회색 배경 (#F8FAFC)
    img = Image.new("RGB", (img_width, img_height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    # 폰트 불러오기
    try:
        title_font = ImageFont.truetype(font_bold_path, 32)
        header_font = ImageFont.truetype(font_bold_path, 20)
        sub_bold_font = ImageFont.truetype(font_bold_path, 16)
        body_font = ImageFont.truetype(font_path, 15)
        small_font = ImageFont.truetype(font_path, 13)
    except:
        title_font = header_font = sub_bold_font = body_font = small_font = ImageFont.load_default()

    margin = 45
    y = 0

    # 1. 상단 다크블루 헤더 배너 (#0F172A)
    draw.rectangle([(0, 0), (img_width, 140)], fill=(15, 23, 42))
    draw.text((margin, 35), "MONTHLY MARKETING REPORT", font=small_font, fill=(56, 189, 248))
    draw.text((margin, 58), f"{data['매장명']} 월간 마케팅 성과 보고서", font=title_font, fill=(255, 255, 255))
    draw.text((img_width - 180, 40), "WITHMEMBER", font=header_font, fill=(226, 232, 240))

    y = 170

    # 카드 그리기 유틸리티 함수
    def draw_card(x1, y1, x2, y2, bg_color=(255, 255, 255), border_color=(226, 232, 240)):
        draw.rectangle([(x1, y1), (x2, y2)], fill=bg_color, outline=border_color, width=1)

    # 2. 주요 성과 대시보드 카드 (3열)
    draw.text((margin, y), "📊 핵심 성과 요약", font=header_font, fill=(15, 23, 42))
    y += 35

    card_w = (img_width - (margin * 2) - 30) // 3
    
    # 카드 1: 순위
    draw_card(margin, y, margin + card_w, y + 90)
    draw.text((margin + 15, y + 15), "플레이스 순위", font=small_font, fill=(100, 116, 139))
    rank_text = f"{data['전월 순위']} ➔ {data['당월 순위']}"
    draw.text((margin + 15, y + 42), rank_text, font=header_font, fill=(2, 132, 199))

    # 카드 2: 방문자 리뷰
    c2_x = margin + card_w + 15
    draw_card(c2_x, y, c2_x + card_w, y + 90)
    draw.text((c2_x + 15, y + 15), "당월 방문자 리뷰", font=small_font, fill=(100, 116, 139))
    draw.text((c2_x + 15, y + 42), f"{data['방문자 리뷰 수']} 개", font=header_font, fill=(15, 23, 42))

    # 카드 3: 답글 수
    c3_x = c2_x + card_w + 15
    draw_card(c3_x, y, c3_x + card_w, y + 90)
    draw.text((c3_x + 15, y + 15), "당월 답글 수", font=small_font, fill=(100, 116, 139))
    draw.text((c3_x + 15, y + 42), f"{data['답글 수']} 개", font=header_font, fill=(15, 23, 42))

    y += 120

    # 3. 대표키워드 현황 영역
    draw.text((margin, y), "📌 대표키워드 세팅 및 관리", font=header_font, fill=(15, 23, 42))
    y += 35
    draw_card(margin, y, img_width - margin, y + 65)
    kw_str = "  |  ".join(data['대표키워드']) if data['대표키워드'] else "설정된 대표키워드가 없습니다."
    draw.text((margin + 20, y + 22), kw_str, font=sub_bold_font, fill=(30, 41, 59))
    y += 95

    # 4. 카톡 메시지 및 월간 관리 보고 영역
    draw.text((margin, y), "💬 월간 관리 보고 및 카톡 메시지 요약", font=header_font, fill=(15, 23, 42))
    y += 35
    
    report_lines = []
    for line in data['관리내용'].split('\n'):
        report_lines.extend(textwrap.wrap(line, width=52))
        
    card_h = max(120, len(report_lines) * 26 + 30)
    draw_card(margin, y, img_width - margin, y + card_h, bg_color=(255, 255, 255))
    
    ry = y + 20
    for line in report_lines:
        draw.text((margin + 20, ry), line, font=body_font, fill=(51, 65, 85))
        ry += 26
        
    y += card_h + 30

    # 5. 체험단/기자단 배포 링크 영역
    draw.text((margin, y), "🔗 체험단 / 기자단 배포 리스트", font=header_font, fill=(15, 23, 42))
    y += 35
    
    links = data['리뷰링크']
    link_card_h = max(80, len(links) * 25 + 30) if links else 70
    draw_card(margin, y, img_width - margin, y + link_card_h)
    
    ly = y + 18
    if links:
        for i, link in enumerate(links):
            link_display = link if len(link) < 65 else link[:62] + "..."
            draw.text((margin + 20, ly), f"{i+1}. {link_display}", font=body_font, fill=(2, 132, 199))
            ly += 25
    else:
        draw.text((margin + 20, ly), "등록된 리뷰 링크가 없습니다.", font=body_font, fill=(148, 163, 184))

    # 하단 푸터
    y = img_height - 50
    draw.line([(margin, y), (img_width - margin, y)], fill=(203, 213, 225), width=1)
    draw.text((margin, y + 15), "WithMember Marketing Automation System", font=small_font, fill=(148, 163, 184))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- [3] 결과 출력 및 클릭 가능한 카톡 리포트 화면 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📤 생성된 월간 보고서 결과")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            col1, col2 = st.columns([1, 1.1])
            
            with col1:
                st.markdown(f"### 🖼️ [{data['매장명']}] 이미지 보고서")
                img_bytes = create_professional_image(data)
                st.image(img_bytes, use_container_width=True)
                
                st.download_button(
                    label=f"📥 {data['매장명']} 보고서 이미지(PNG) 다운로드",
                    data=img_bytes,
                    file_name=f"위드멤버_월간보고서_{data['매장명']}.png",
                    mime="image/png",
                    key=f"dl_btn_{idx}"
                )
                
            with col2:
                st.markdown(f"### 📱 [{data['매장명']}] 카톡 발송용 스마트 리포트")
                st.caption("아래 텍스트를 복사하여 카카오톡으로 전달하시면 링크를 원클릭하여 접속할 수 있습니다.")
                
                # 카톡 전송용 포맷 조합
                kakao_text = f"안녕하세요 대표님! 위드멤버입니다.\n[{data['매장명']}] 월간 마케팅 관리 보고서 전달드립니다.\n\n"
                kakao_text += f"📊 [성과 요약]\n"
                kakao_text += f"• 플레이스 순위: {data['전월 순위']} ➔ {data['당월 순위']}\n"
                kakao_text += f"• 이번 달 방문자 리뷰: {data['방문자 리뷰 수']}개\n"
                kakao_text += f"• 답글 관리: {data['답글 수']}개\n\n"
                
                if data['대표키워드']:
                    kakao_text += f"📌 [대표키워드]: {', '.join(data['대표키워드'])}\n\n"
                    
                kakao_text += f"💡 [월간 관리 보고]\n{data['관리내용']}\n\n"
                
                if data['리뷰링크']:
                    kakao_text += "🔗 [체험단/기자단 리뷰 링크]\n"
                    for i, link in enumerate(data['리뷰링크']):
                        kakao_text += f"{i+1}. {link}\n"
                
                kakao_text += "\n상세 내용은 첨부된 이미지를 참고해 주세요. 감사합니다!"

                # 복사 가능한 텍스트 영역
                st.text_area("카톡 전송 문구 복사 (Ctrl+A ➔ Ctrl+C)", value=kakao_text, height=320, key=f"kakao_txt_{idx}")
                
                # 클릭 가능한 링크 바로가기 리스트 (웹 화면용)
                if data['리뷰링크']:
                    st.markdown("#### 🔗 리뷰 링크 바로가기 (원클릭 접속)")
                    for i, link in enumerate(data['리뷰링크']):
                        st.markdown(f"- [{i+1}번 리뷰 보러가기 ({link[:35]}...)]({link})")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
