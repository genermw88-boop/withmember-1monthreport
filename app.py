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
    page_title="위드멤버 익세큐티브 월간 보고서", 
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
    rank_str = str(rank_str).strip()
    if not rank_str:
        return "-"
    if not rank_str.endswith("위"):
        return f"{rank_str}위"
    return rank_str

def parse_rank_num(rank_str):
    nums = re.findall(r'\d+', str(rank_str))
    return int(nums[0]) if nums else None

def generate_itemized_reports(data_dict):
    """항목별 전문 분석 및 보고 문구 개별 생성 엔진"""
    reports = {}
    p_rank = parse_rank_num(data_dict.get('전월 순위', ''))
    c_rank = parse_rank_num(data_dict.get('당월 순위', ''))
    
    # 1. 플레이스 순위 보고 문구
    if p_rank is not None and c_rank is not None:
        if c_rank > p_rank: # 하락
            reports['rank_report'] = (
                f"• [현황 분석] 당월 플레이스 순위가 {p_rank}위에서 {c_rank}위로 조정됨에 따라 알고리즘 변동 정밀 점검 진행\n"
                f"• [긴급 반등 플랜] 대표키워드 연관도 재정비, 유효 트래픽 유입 상향, 영수증/블로그 리뷰 집중 투입으로 1~2주 내 순위 반등 실행"
            )
        elif c_rank < p_rank: # 상승
            reports['rank_report'] = (
                f"• [현황 분석] 순위가 {p_rank}위에서 {c_rank}위로 대폭 상승하여 최상위 노출권 진입 성공\n"
                f"• [유지 플랜] 실시간 모니터링 및 트래픽 유입 비율 관리를 통해 상위 노출 순위 방어 조치 진행"
            )
        else: # 유지
            reports['rank_report'] = (
                f"• [현황 분석] 순위가 {c_rank}위로 안정적으로 유지가 지속되고 있습니다.\n"
                f"• [확장 플랜] 세부 롱테일 키워드 노출 확대를 통한 추가 잠재고객 유입 강화"
            )
    else:
        reports['rank_report'] = f"• [플레이스 순위] (전월) {data_dict.get('전월 순위', '-')} ➔ (당월) {data_dict.get('당월 순위', '-')}"

    # 2. 대표키워드 세팅 보고 문구 (전문성 강화)
    keywords = data_dict.get('대표키워드', [])
    if keywords:
        kw_str = ", ".join(keywords)
        reports['keyword_report'] = (
            f"• [키워드 추출] 상권 검색량 및 전환율 데이터 기반 핵심 키워드 ({kw_str}) 도출\n"
            f"• [SEO 최적화 세팅] 스마트블록 연관도 강화, 플레이스 대표설명 문구 및 검색 태그 구조화 완료"
        )
    else:
        reports['keyword_report'] = "• [SEO 세팅] 대표키워드 미지정 상태 (다음 달 전용 핵심 키워드 분석 후 반영 예정)"

    # 3. 방문자 리뷰 및 답글 보고 문구
    v_review = data_dict.get('방문자 리뷰 수', 0)
    r_count = data_dict.get('답글 수', 0)
    reports['review_report'] = (
        f"• [리뷰 확보] 당월 신규 방문자 리뷰 {v_review}건 유입으로 매장 신뢰도 강화\n"
        f"• [고객 소통] 등록된 리뷰 100% 답글 완료 ({r_count}건)를 통한 플레이스 최적화 지수(SEO) 상승 반영"
    )

    # 4. 리뷰 링크 콘텐츠 보고 문구
    links = data_dict.get('리뷰링크', [])
    if links:
        reports['content_report'] = f"• [콘텐츠 배포] 고품질 체험단/기자단 리뷰 {len(links)}건 발행 완료 (브랜드 인지도 상승 및 외부 유입 트래픽 확보)"
    else:
        reports['content_report'] = "• [콘텐츠 배포] 당월 발행된 외부 리뷰 링크 없음"

    return reports

# --- [메인 헤더] ---
st.title("🏛️ 위드멤버(WithMember) 익세큐티브 월간 리포터")
st.markdown("항목별 **전문 마케팅 분석 보고서 이미지**와 **카톡 전달용 스마트 리포트**를 동시에 생성합니다.")

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명 *", placeholder="예: 강남 맛집")
        prev_rank_input = st.text_input("전월 플레이스 순위", placeholder="예: 3 (자동으로 '3위' 변환)")
        current_rank_input = st.text_input("당월 플레이스 순위", placeholder="예: 8 (자동으로 '8위' 변환)")
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
    
    st.subheader("💬 종합 관리 추가 의견 (선택 사항)")
    custom_report_input = st.text_area(
        "추가 전달 문구 (비워둘 경우 항목별 전문 보고 내용이 자동으로 완전하게 구성됩니다)", 
        placeholder="특이사항이나 광고주 전달용 메모가 있다면 입력해 주세요.", 
        height=80
    )

    submitted = st.form_submit_button("🚀 항목별 정밀 보고서 생성")

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
                "추가의견": custom_report_input
            }
            
            # 항목별 스마트 보고서 자동 생성
            temp_data["item_reports"] = generate_itemized_reports(temp_data)

            st.session_state.report_data.append(temp_data)
            st.success(f"[{store_name}] 항목별 정밀 보고서가 성공적으로 생성되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 대기업 스타일 항목별 정밀 보고서 이미지 생성 엔진 ---
def create_itemized_enterprise_image(data):
    img_width = 900
    img_height = 1450
    img = Image.new("RGB", (img_width, img_height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(font_bold_path, 34)
        section_font = ImageFont.truetype(font_bold_path, 17)
        kpi_val_font = ImageFont.truetype(font_bold_path, 22)
        body_font = ImageFont.truetype(font_path, 14)
        small_font = ImageFont.truetype(font_path, 12)
    except:
        title_font = section_font = kpi_val_font = body_font = small_font = ImageFont.load_default()

    margin = 50
    y = 0

    # 1. 헤더 다크 네이비 배너 (#0B192C) & 골드 바
    draw.rectangle([(0, 0), (img_width, 145)], fill=(11, 25, 44))
    draw.rectangle([(0, 0), (img_width, 6)], fill=(212, 175, 55))
    
    draw.text((margin, 32), "WITHMEMBER MARKETING PERFORMANCE REPORT", font=small_font, fill=(56, 189, 248))
    draw.text((margin, 54), f"{data['매장명']} 월간 경영 성과 보고서", font=title_font, fill=(255, 255, 255))
    draw.text((margin, 102), "CONFIDENTIAL  |  소상공인 맞춤 마케팅 최적화 성과 보고", font=small_font, fill=(148, 163, 184))

    y = 170

    def draw_panel(x1, y1, x2, y2, bg=(255, 255, 255), border=(226, 232, 240), accent_color=None):
        draw.rectangle([(x1, y1), (x2, y2)], fill=bg, outline=border, width=1)
        if accent_color:
            draw.rectangle([(x1, y1), (x1 + 6, y2)], fill=accent_color)

    item_rep = data["item_reports"]

    # 2. KPI 수치 대시보드 (3열)
    draw.text((margin, y), "KEY PERFORMANCE INDICATORS", font=small_font, fill=(100, 116, 139))
    draw.text((margin, y + 15), "📌 핵심 성과 지표 요약", font=section_font, fill=(15, 23, 42))
    y += 45

    card_w = (img_width - (margin * 2) - 24) // 3
    p_rank = parse_rank_num(data['전월 순위'])
    c_rank = parse_rank_num(data['당월 순위'])
    
    rank_accent = (2, 132, 199)
    rank_status = "측정"
    if p_rank and c_rank:
        if c_rank < p_rank:
            rank_accent = (16, 185, 129)
            rank_status = "상승 🔼"
        elif c_rank > p_rank:
            rank_accent = (225, 29, 72)
            rank_status = "대응 ⚠️"
        else:
            rank_status = "유지 🛡️"

    draw_panel(margin, y, margin + card_w, y + 85, accent_color=rank_accent)
    draw.text((margin + 18, y + 14), f"플레이스 순위 [{rank_status}]", font=small_font, fill=(100, 116, 139))
    draw.text((margin + 18, y + 38), f"{data['전월 순위']} ➔ {data['당월 순위']}", font=kpi_val_font, fill=rank_accent)

    c2_x = margin + card_w + 12
    draw_panel(c2_x, y, c2_x + card_w, y + 85, accent_color=(15, 23, 42))
    draw.text((c2_x + 18, y + 14), "당월 방문자 리뷰", font=small_font, fill=(100, 116, 139))
    draw.text((c2_x + 18, y + 38), f"{data['방문자 리뷰 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    c3_x = c2_x + card_w + 12
    draw_panel(c3_x, y, c3_x + card_w, y + 85, accent_color=(15, 23, 42))
    draw.text((c3_x + 18, y + 14), "고객 답글 관리", font=small_font, fill=(100, 116, 139))
    draw.text((c3_x + 18, y + 38), f"{data['답글 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    y += 110

    # 3. [항목 1] 순위 분석 및 대응 보고
    draw.text((margin, y), "1. PLACE RANKING & STRATEGY", font=small_font, fill=(100, 116, 139))
    draw.text((margin, y + 15), "📊 플레이스 순위 분석 및 대응 방안", font=section_font, fill=(15, 23, 42))
    y += 45

    rank_lines = []
    for line in item_rep['rank_report'].split('\n'):
        rank_lines.extend(textwrap.wrap(line, width=56))

    panel_h = max(70, len(rank_lines) * 23 + 24)
    bg_col = (254, 242, 242) if (p_rank and c_rank and c_rank > p_rank) else (255, 255, 255)
    border_col = (254, 202, 202) if (p_rank and c_rank and c_rank > p_rank) else (226, 232, 240)
    
    draw_panel(margin, y, img_width - margin, y + panel_h, bg=bg_col, border=border_col, accent_color=rank_accent)
    ly = y + 15
    for line in rank_lines:
        draw.text((margin + 18, ly), line, font=body_font, fill=(30, 41, 59))
        ly += 23
    y += panel_h + 25

    # 4. [항목 2] 대표키워드 세팅 보고 (요청사항 반영!)
    draw.text((margin, y), "2. SEARCH ENGINE OPTIMIZATION", font=small_font, fill=(100, 116, 139))
    draw.text((margin, y + 15), "🎯 대표키워드 분석 및 SEO 세팅 보고", font=section_font, fill=(15, 23, 42))
    y += 45

    kw_lines = []
    for line in item_rep['keyword_report'].split('\n'):
        kw_lines.extend(textwrap.wrap(line, width=56))

    panel_h = max(70, len(kw_lines) * 23 + 24)
    draw_panel(margin, y, img_width - margin, y + panel_h, accent_color=(56, 189, 248))
    ly = y + 15
    for line in kw_lines:
        draw.text((margin + 18, ly), line, font=body_font, fill=(30, 41, 59))
        ly += 23
    y += panel_h + 25

    # 5. [항목 3] 리뷰 및 고객 소통 보고
    draw.text((margin, y), "3. REVIEWS & CUSTOMER ENGAGEMENT", font=small_font, fill=(100, 116, 139))
    draw.text((margin, y + 15), "💬 방문자 리뷰 및 고객 답글 관리 보고", font=section_font, fill=(15, 23, 42))
    y += 45

    rev_lines = []
    for line in item_rep['review_report'].split('\n'):
        rev_lines.extend(textwrap.wrap(line, width=56))

    panel_h = max(70, len(rev_lines) * 23 + 24)
    draw_panel(margin, y, img_width - margin, y + panel_h, accent_color=(15, 23, 42))
    ly = y + 15
    for line in rev_lines:
        draw.text((margin + 18, ly), line, font=body_font, fill=(30, 41, 59))
        ly += 23
    y += panel_h + 25

    # 6. [항목 4] 마케팅 콘텐츠 배포 링크 보고
    draw.text((margin, y), "4. CONTENT MARKETING", font=small_font, fill=(100, 116, 139))
    draw.text((margin, y + 15), "🔗 체험단 / 기자단 배포 리스트", font=section_font, fill=(15, 23, 42))
    y += 45

    links = data['리뷰링크']
    link_panel_h = max(70, len(links) * 24 + 30) if links else 60
    draw_panel(margin, y, img_width - margin, y + link_panel_h, accent_color=(2, 132, 199))

    ly = y + 15
    if links:
        for i, link in enumerate(links):
            link_display = link if len(link) < 68 else link[:65] + "..."
            draw.text((margin + 18, ly), f"{i+1}. {link_display}", font=body_font, fill=(2, 132, 199))
            ly += 24
    else:
        draw.text((margin + 18, ly), "등록된 리뷰 링크가 없습니다.", font=body_font, fill=(148, 163, 184))

    # 하단 푸터
    y = img_height - 45
    draw.line([(margin, y), (img_width - margin, y)], fill=(203, 213, 225), width=1)
    draw.text((margin, y + 12), "WITHMEMBER MARKETING AUTOMATION SYSTEM  |  CONFIDENTIAL REPORT", font=small_font, fill=(148, 163, 184))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- [3] 결과 출력 및 카톡 발송용 리포트 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📤 생성된 월간 보고서 결과")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            col1, col2 = st.columns([1, 1.1])
            item_rep = data["item_reports"]
            
            with col1:
                st.markdown(f"### 🖼️ [{data['매장명']}] 항목별 이미지 보고서")
                img_bytes = create_itemized_enterprise_image(data)
                st.image(img_bytes, use_container_width=True)
                
                st.download_button(
                    label=f"📥 {data['매장명']} 고화질 PNG 다운로드",
                    data=img_bytes,
                    file_name=f"위드멤버_월간보고서_{data['매장명']}.png",
                    mime="image/png",
                    key=f"dl_btn_{idx}"
                )
                
            with col2:
                st.markdown(f"### 📱 [{data['매장명']}] 카톡 발송용 스마트 리포트")
                st.caption("아래 텍스트를 복사하여 카카오톡으로 전달하시면 링크를 원클릭 접속할 수 있습니다.")
                
                kakao_text = f"안녕하세요 대표님! 위드멤버입니다.\n[{data['매장명']}] 월간 마케팅 성과 보고서 전달드립니다.\n\n"
                
                kakao_text += f"1️⃣ [플레이스 순위 분석]\n{item_rep['rank_report']}\n\n"
                kakao_text += f"2️⃣ [대표키워드 SEO 세팅]\n{item_rep['keyword_report']}\n\n"
                kakao_text += f"3️⃣ [리뷰 및 고객 소통 관리]\n{item_rep['review_report']}\n\n"
                kakao_text += f"4️⃣ [체험단/기자단 배포 현황]\n{item_rep['content_report']}\n"
                
                if data['리뷰링크']:
                    for i, link in enumerate(data['리뷰링크']):
                        kakao_text += f"  - 리뷰 {i+1}: {link}\n"
                
                if data.get("추가의견"):
                    kakao_text += f"\n💡 [추가 안내 사항]\n{data['추가의견']}\n"
                
                kakao_text += "\n상세 내용은 첨부해 드린 보고서 이미지를 확인해 주세요. 감사합니다!"

                st.text_area("카톡 전송 문구 복사 (Ctrl+A ➔ Ctrl+C)", value=kakao_text, height=360, key=f"kakao_txt_{idx}")
                
                if data['리뷰링크']:
                    st.markdown("#### 🔗 리뷰 링크 원클릭 접속 테스트")
                    for i, link in enumerate(data['리뷰링크']):
                        st.markdown(f"- [{i+1}번 리뷰 보러가기 ({link[:35]}...)]({link})")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
