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
    page_title="위드멤버 월간 경영 성과 보고서", 
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
    if not rank_str.endswith("위"):
        return f"{rank_str}위"
    return rank_str

def parse_rank_num(rank_str):
    """순위 문자열에서 숫자만 추출"""
    nums = re.findall(r'\d+', str(rank_str))
    return int(nums[0]) if nums else None

def generate_structured_sections(data_dict):
    """카톡 및 이미지 보고서의 각 항목에 1:1로 일치할 항목별 분석 텍스트 생성"""
    p_rank = parse_rank_num(data_dict.get('전월 순위', ''))
    c_rank = parse_rank_num(data_dict.get('당월 순위', ''))
    
    # 1. 플레이스 순위 분석 및 대응 방안
    if p_rank is not None and c_rank is not None:
        if c_rank > p_rank: # 순위 하락
            rank_text = (
                f"• [현황 분석] 당월 플레이스 순위가 {p_rank}위에서 {c_rank}위로 조정됨에 따라 알고리즘 변동 정밀 점검 진행\n"
                f"• [긴급 반등 플랜] 대표키워드 연관도 재정비, 유효 트래픽 유입 상향, 영수증/블로그 리뷰 집중 투입으로 1-2주 내 순위 반등 실행"
            )
        elif c_rank < p_rank: # 순위 상승
            rank_text = (
                f"• [성과 분석] 당월 플레이스 순위가 {p_rank}위에서 {c_rank}위로 대폭 상승하여 가시성이 극대화되었습니다.\n"
                f"• [유지 플랜] 현재 최상위 노출세를 고착화하기 위해 유효 트래픽 유지 및 연관 키워드 지수 관리를 지속합니다."
            )
        else: # 순위 유지
            rank_text = (
                f"• [현황 분석] 당월 플레이스 순위가 {c_rank}위로 안정되게 유지되고 있습니다.\n"
                f"• [확장 플랜] 서브 키워드 순위 동반 상승 및 최상위권 안착을 위한 트래픽 최적화를 진행합니다."
            )
    else:
        rank_text = f"• [현황 분석] 당월 플레이스 순위: (전월) {data_dict.get('전월 순위', '-')} ➔ (당월) {data_dict.get('당월 순위', '-')}"

    # 2. 대표키워드 분석 및 SEO 세팅 보고
    keywords = data_dict.get('대표키워드', [])
    kw_str = ", ".join(keywords) if keywords else "주요 대표키워드"
    kw_text = (
        f"• [키워드 추출] 상권 검색량 및 전환율 데이터 기반 핵심 키워드 ({kw_str}) 도출\n"
        f"• [SEO 최적화 세팅] 스마트블록 연관도 강화, 플레이스 대표설명 문구 및 검색 태그 구조화 완료"
    )

    # 3. 방문자 리뷰 및 고객 답글 관리 보고
    v_review = data_dict.get('방문자 리뷰 수', 0)
    r_count = data_dict.get('답글 수', 0)
    review_text = (
        f"• [리뷰 확보] 당월 신규 방문자 리뷰 {v_review}건 유입으로 매장 신뢰도 강화\n"
        f"• [고객 소통] 등록된 리뷰 100% 답글 완료({r_count}건)를 통한 플레이스 최적화 지수(SEO) 상승 반영"
    )

    return {
        "rank_sec": rank_text,
        "kw_sec": kw_text,
        "review_sec": review_text
    }

# --- [메인 헤더] ---
st.title("📊 위드멤버(WithMember) 월간 경영 성과 보고서")
st.markdown("데이터를 입력하시면 영문 표기 없는 **깔끔한 한글 보고서 이미지**와 **항목별 1:1 매칭 카톡 리포트**가 완성됩니다.")

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명 *", placeholder="예: 강남 맛집")
        prev_rank_input = st.text_input("전월 플레이스 순위", placeholder="예: 11 (자동으로 '11위' 변환)")
        current_rank_input = st.text_input("당월 플레이스 순위", placeholder="예: 22 (자동으로 '22위' 변환)")
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
                link = st.text_input(f"리뷰 링크 {i+1}", key=f"link_{i}", placeholder="https://...")
                links.append(link)

    st.markdown("---")
    
    st.subheader("💬 항목별 직접 수정 (선택사항)")
    st.caption("비워둘 경우, 데이터에 따라 정밀 분석 문구가 자동으로 항목별에 맞게 생성됩니다.")

    custom_rank_sec = st.text_area("1) 플레이스 순위 분석 내용 직접 수정", placeholder="비워두시면 자동 생성됩니다.", height=70)
    custom_kw_sec = st.text_area("2) 대표키워드 분석 내용 직접 수정", placeholder="비워두시면 자동 생성됩니다.", height=70)
    custom_review_sec = st.text_area("3) 방문자 리뷰/답글 내용 직접 수정", placeholder="비워두시면 자동 생성됩니다.", height=70)

    submitted = st.form_submit_button("🚀 보고서 생성")

    if submitted:
        if store_name:
            valid_keywords = [k for k in keywords if k.strip()]
            valid_links = [l for l in links if l.strip()]

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
            
            # 자동 항목 생성
            auto_secs = generate_structured_sections(temp_data)

            # 직접 입력값이 있으면 우선 적용
            temp_data["rank_sec"] = custom_rank_sec.strip() if custom_rank_sec.strip() else auto_secs["rank_sec"]
            temp_data["kw_sec"] = custom_kw_sec.strip() if custom_kw_sec.strip() else auto_secs["kw_sec"]
            temp_data["review_sec"] = custom_review_sec.strip() if custom_review_sec.strip() else auto_secs["review_sec"]

            st.session_state.report_data.append(temp_data)
            st.success(f"[{store_name}] 완벽 일치 월간 보고서가 생성되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 깔끔한 한글 전용 보고서 이미지 생성 엔진 ---
def create_clean_korean_image(data):
    img_width = 900
    img_height = 1380
    img = Image.new("RGB", (img_width, img_height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(font_bold_path, 34)
        section_font = ImageFont.truetype(font_bold_path, 20)
        kpi_val_font = ImageFont.truetype(font_bold_path, 22)
        body_font = ImageFont.truetype(font_path, 15)
        small_font = ImageFont.truetype(font_path, 13)
    except:
        title_font = section_font = kpi_val_font = body_font = small_font = ImageFont.load_default()

    margin = 50

    # 1. 상단 헤더 배너 (영문 제거)
    draw.rectangle([(0, 0), (img_width, 140)], fill=(11, 25, 44))
    draw.text((margin, 35), f"{data['매장명']} 월간 경영 성과 보고서", font=title_font, fill=(255, 255, 255))
    draw.text((margin, 85), "소상공인 맞춤 마케팅 최적화 성과 보고서", font=small_font, fill=(148, 163, 184))

    y = 170

    # 카드 그리기 유틸리티
    def draw_section_card(x1, y1, x2, y2, bg=(255, 255, 255), border=(226, 232, 240), accent_color=(15, 23, 42)):
        draw.rectangle([(x1, y1), (x2, y2)], fill=bg, outline=border, width=1)
        if accent_color:
            draw.rectangle([(x1, y1), (x1 + 6, y2)], fill=accent_color)

    # 2. 핵심 성과 지표 요약 (KPI 3열 카드)
    draw.text((margin, y), "핵심 성과 지표 요약", font=section_font, fill=(15, 23, 42))
    y += 40

    card_w = (img_width - (margin * 2) - 24) // 3
    p_rank = parse_rank_num(data['전월 순위'])
    c_rank = parse_rank_num(data['당월 순위'])
    
    rank_accent = (2, 132, 199)
    rank_tag = "유지"
    if p_rank and c_rank:
        if c_rank < p_rank:
            rank_accent = (16, 185, 129) # 상승 (그린)
            rank_tag = "상승"
        elif c_rank > p_rank:
            rank_accent = (225, 29, 72) # 하락/대응 (레드)
            rank_tag = "대응"

    # KPI 카드 1
    draw_section_card(margin, y, margin + card_w, y + 90, accent_color=rank_accent)
    draw.text((margin + 18, y + 15), f"플레이스 순위 [{rank_tag}]", font=small_font, fill=(100, 116, 139))
    draw.text((margin + 18, y + 42), f"{data['전월 순위']}   {data['당월 순위']}", font=kpi_val_font, fill=rank_accent)

    # KPI 카드 2
    c2_x = margin + card_w + 12
    draw_section_card(c2_x, y, c2_x + card_w, y + 90, accent_color=(15, 23, 42))
    draw.text((c2_x + 18, y + 15), "당월 방문자 리뷰", font=small_font, fill=(100, 116, 139))
    draw.text((c2_x + 18, y + 42), f"{data['방문자 리뷰 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    # KPI 카드 3
    c3_x = c2_x + card_w + 12
    draw_section_card(c3_x, y, c3_x + card_w, y + 90, accent_color=(15, 23, 42))
    draw.text((c3_x + 18, y + 15), "고객 답글 관리", font=small_font, fill=(100, 116, 139))
    draw.text((c3_x + 18, y + 42), f"{data['답글 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    y += 120

    # 3. 항목별 섹션 렌더링 유틸리티
    def render_text_block(title, content_text, current_y, accent_col=(15, 23, 42), bg_col=(255, 255, 255), border_col=(226, 232, 240)):
        draw.text((margin, current_y), title, font=section_font, fill=(15, 23, 42))
        current_y += 35
        
        lines = []
        for line in content_text.split('\n'):
            if line.strip():
                lines.extend(textwrap.wrap(line, width=54))
            else:
                lines.append("")
                
        block_h = max(70, len(lines) * 25 + 25)
        draw_section_card(margin, current_y, img_width - margin, current_y + block_h, bg=bg_col, border=border_col, accent_color=accent_col)
        
        ly = current_y + 15
        for line in lines:
            draw.text((margin + 20, ly), line, font=body_font, fill=(30, 41, 59))
            ly += 25
            
        return current_y + block_h + 30

    # [항목 1] 플레이스 순위 분석 및 대응 방안
    is_dropped = (p_rank and c_rank and c_rank > p_rank)
    sec1_bg = (254, 242, 242) if is_dropped else (255, 255, 255)
    sec1_border = (254, 202, 202) if is_dropped else (226, 232, 240)
    sec1_accent = (225, 29, 72) if is_dropped else (16, 185, 129)
    y = render_text_block("플레이스 순위 분석 및 대응 방안", data['rank_sec'], y, accent_col=sec1_accent, bg_col=sec1_bg, border_col=sec1_border)

    # [항목 2] 대표키워드 분석 및 SEO 세팅 보고
    y = render_text_block("대표키워드 분석 및 SEO 세팅 보고", data['kw_sec'], y, accent_col=(56, 189, 248))

    # [항목 3] 방문자 리뷰 및 고객 답글 관리 보고
    y = render_text_block("방문자 리뷰 및 고객 답글 관리 보고", data['review_sec'], y, accent_col=(15, 23, 42))

    # [항목 4] 체험단 / 기자단 배포 리스트
    draw.text((margin, y), "체험단 / 기자단 배포 리스트", font=section_font, fill=(15, 23, 42))
    y += 35
    links = data['리뷰링크']
    link_h = max(80, len(links) * 25 + 25) if links else 65
    draw_section_card(margin, y, img_width - margin, y + link_h, accent_color=(2, 132, 199))

    ly = y + 15
    if links:
        for i, link in enumerate(links):
            link_disp = link if len(link) < 68 else link[:65] + "..."
            draw.text((margin + 20, ly), f"{i+1}. {link_disp}", font=body_font, fill=(2, 132, 199))
            ly += 25
    else:
        draw.text((margin + 20, ly), "등록된 리뷰 링크가 없습니다.", font=body_font, fill=(148, 163, 184))

    # 푸터 (영문 제거)
    y = img_height - 45
    draw.line([(margin, y), (img_width - margin, y)], fill=(203, 213, 225), width=1)
    draw.text((margin, y + 12), "위드멤버 마케팅 자동화 시스템", font=small_font, fill=(148, 163, 184))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- [3] 결과 출력 및 1:1 매칭 카톡 메시지 제공 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📤 생성된 보고서 및 카톡 전달 문구")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            col1, col2 = st.columns([1, 1.1])
            
            with col1:
                st.markdown(f"### 🖼️ [{data['매장명']}] 성과 보고서 이미지")
                img_bytes = create_clean_korean_image(data)
                st.image(img_bytes, use_container_width=True)
                
                st.download_button(
                    label=f"📥 {data['매장명']} 보고서 이미지(PNG) 다운로드",
                    data=img_bytes,
                    file_name=f"위드멤버_월간보고서_{data['매장명']}.png",
                    mime="image/png",
                    key=f"dl_btn_{idx}"
                )
                
            with col2:
                st.markdown(f"### 📱 [{data['매장명']}] 카톡 발송용 1:1 매칭 리포트")
                st.caption("보고서 이미지의 항목 순서 및 내용과 100% 동일하게 구성된 카톡 문구입니다.")
                
                # 이미지 보고서 항목과 1:1 대응되는 카톡 포맷
                kakao_text = f"안녕하세요 대표님! 위드멤버입니다.\n[{data['매장명']}] 월간 마케팅 경영 성과 보고서 전달드립니다.\n\n"
                
                kakao_text += f"📊 [핵심 성과 지표 요약]\n"
                kakao_text += f"• 플레이스 순위: {data['전월 순위']} ➔ {data['당월 순위']}\n"
                kakao_text += f"• 당월 방문자 리뷰: {data['방문자 리뷰 수']}건\n"
                kakao_text += f"• 고객 답글 관리: {data['답글 수']}건\n\n"
                
                kakao_text += f"🚨 [플레이스 순위 분석 및 대응 방안]\n{data['rank_sec']}\n\n"
                
                kakao_text += f"🎯 [대표키워드 분석 및 SEO 세팅 보고]\n{data['kw_sec']}\n\n"
                
                kakao_text += f"💬 [방문자 리뷰 및 고객 답글 관리 보고]\n{data['review_sec']}\n\n"
                
                if data['리뷰링크']:
                    kakao_text += "🔗 [체험단 / 기자단 배포 리스트]\n"
                    for i, link in enumerate(data['리뷰링크']):
                        kakao_text += f"{i+1}. {link}\n"
                
                kakao_text += "\n상세 내용은 첨부해 드린 보고서 이미지를 함께 확인해 주세요. 감사합니다!"

                st.text_area("카톡 전송 문구 전체 복사 (Ctrl+A ➔ Ctrl+C)", value=kakao_text, height=380, key=f"kakao_txt_{idx}")
                
                if data['리뷰링크']:
                    st.markdown("#### 🔗 리뷰 링크 원클릭 접속 테스트")
                    for i, link in enumerate(data['리뷰링크']):
                        st.markdown(f"- [{i+1}번 리뷰 바로가기]({link})")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
