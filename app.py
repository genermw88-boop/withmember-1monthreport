import streamlit as st
import pandas as pd
import os
import urllib.request
import re
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# 페이지 기본 설정
st.set_page_config(
    page_title="월간 마케팅 보고서 생성기", 
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

def generate_structured_sections(data_dict):
    p_rank = parse_rank_num(data_dict.get('전월 순위', ''))
    c_rank = parse_rank_num(data_dict.get('당월 순위', ''))
    
    # 1. 플레이스 순위 분석 문구 다변화 템플릿
    rise_templates = [
        f"• [성과 분석] 당월 플레이스 순위가 {p_rank}위에서 {c_rank}위로 대폭 상승하여 가시성이 극대화되었습니다.\n• [유지 플랜] 현재 최상위 노출세를 고착화하기 위해 유효 트래픽 유지 및 연관 키워드 지수 관리를 지속합니다.",
        f"• [상승 요인] 최적화 블로그 유입 및 영수증 리뷰 결합 효과로 순위가 {p_rank}위 ➔ {c_rank}위로 상승하였습니다.\n• [향후 계획] 상승세를 이어나가기 위해 대표 키워드 상단 고정 트래픽 및 소통 지수를 집중 유지합니다.",
        f"• [지표 개선] 연관 검색 태그 재정비와 유효 유입량 증가로 플레이스 순위가 {c_rank}위로 대폭 개선되었습니다.\n• [안착 전략] 현재 순위권 유지를 위해 주기적인 리뷰 반응 속도 관리와 연관 블로그 배포를 병행합니다."
    ]
    
    drop_templates = [
        f"• [현황 분석] 당월 플레이스 순위가 {p_rank}위에서 {c_rank}위로 조정됨에 따라 알고리즘 변동 정밀 점검 진행\n• [긴급 반등 플랜] 대표키워드 연관도 재정비, 유효 트래픽 유입 상향, 영수증/블로그 리뷰 집중 투입으로 1-2주 내 순위 반등 실행",
        f"• [원인 분석] 네이버 플레이스 로직 업데이트로 인해 순위가 {p_rank}위에서 {c_rank}위로 일시 변동되었습니다.\n• [대응 전략] 순위 복구를 위해 타겟 키워드 유효 트래픽 증대 및 신규 리뷰 배포 주기를 가속화합니다.",
        f"• [변동 점검] 경쟁업체 집계 지수 상승으로 인해 당월 순위가 {c_rank}위로 조정되었습니다.\n• [반등 실행] 최신 리뷰 세팅 및 검색 태그 최적화 수정을 거쳐 차주 내 이전 순위 회복을 목표로 집중 관리합니다."
    ]
    
    maintain_templates = [
        f"• [현황 분석] 당월 플레이스 순위가 {c_rank}위로 안정되게 유지되고 있습니다.\n• [확장 플랜] 서브 키워드 순위 동반 상승 및 최상위권 안착을 위한 트래픽 최적화를 진행합니다.",
        f"• [안정화 평가] 로직 변동 속에서도 {c_rank}위 자리를 확고하게 지키며 안정적인 노출세를 기록 중입니다.\n• [고착화 작업] 상위 지수 유지를 위해 신규 리뷰 유입 속도 조절 및 연관 키워드 작업을 지속 실행합니다.",
        f"• [지수 유지] 당월 순위 {c_rank}위를 유지하며 경쟁 매장 대비 안정적인 유입량을 확보하고 있습니다.\n• [점유율 확대] 메인 순위 유지와 동시에 방치된 서브 태그 키워드 검색 노출을 추가 확대합니다."
    ]

    if p_rank is not None and c_rank is not None:
        if c_rank > p_rank: # 하락
            rank_text = random.choice(drop_templates)
        elif c_rank < p_rank: # 상승
            rank_text = random.choice(rise_templates)
        else: # 유지
            rank_text = random.choice(maintain_templates)
    else:
        rank_text = f"• [현황 분석] 당월 플레이스 순위: (전월) {data_dict.get('전월 순위', '-')} = (당월) {data_dict.get('당월 순위', '-')}"

    # 2. 대표키워드 분석 (도출 -> 선정 완료)
    keywords = data_dict.get('대표키워드', [])
    kw_str = ", ".join(keywords) if keywords else "주요 대표키워드"
    kw_text = (
        f"• [키워드 추출] 상권 검색량 및 전환율 데이터 기반 핵심 키워드 ({kw_str}) 선정 완료\n"
        f"• [SEO 최적화 세팅] 스마트블록 연관도 강화, 플레이스 대표설명 문구 및 검색 태그 구조화 완료"
    )

    # 3. 방문자 리뷰 및 답글
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

# --- [메인 UI] ---
st.title("📊 월간 마케팅 보고서 생성기")

with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명 *", placeholder="예: ㅁㄴㅇ")
        prev_rank_input = st.text_input("전월 플레이스 순위", placeholder="예: 11")
        current_rank_input = st.text_input("당월 플레이스 순위", placeholder="예: 11")
    with col2:
        visitor_review = st.number_input("이번 달 방문자 리뷰 수", min_value=0, step=1)
        reply_count = st.number_input("답글 수", min_value=0, step=1)

    st.markdown("---")
    
    with st.expander("📌 대표키워드 설정 (최대 5개)", expanded=True):
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
    
    st.subheader("💬 항목별 상세 내용 직접 수정 (선택사항)")

    custom_rank_sec = st.text_area("1) 플레이스 순위 분석 내용", placeholder="비워두시면 유형별로 매번 다른 문구가 자동 적용됩니다.", height=70)
    custom_kw_sec = st.text_area("2) 대표키워드 분석 내용", placeholder="비워두시면 자동 생성됩니다.", height=70)
    custom_review_sec = st.text_area("3) 방문자 리뷰/답글 내용", placeholder="비워두시면 자동 생성됩니다.", height=70)

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
            
            auto_secs = generate_structured_sections(temp_data)

            temp_data["rank_sec"] = custom_rank_sec.strip() if custom_rank_sec.strip() else auto_secs["rank_sec"]
            temp_data["kw_sec"] = custom_kw_sec.strip() if custom_kw_sec.strip() else auto_secs["kw_sec"]
            temp_data["review_sec"] = custom_review_sec.strip() if custom_review_sec.strip() else auto_secs["review_sec"]

            st.session_state.report_data.append(temp_data)
            st.success(f"[{store_name}] 보고서가 성공적으로 생성되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [이미지 생성 엔진] ---
def create_fitted_single_line_image(data):
    img_width = 1200
    margin = 40

    try:
        title_font = ImageFont.truetype(font_bold_path, 32)
        section_font = ImageFont.truetype(font_bold_path, 19)
        kpi_title_font = ImageFont.truetype(font_bold_path, 13)
        kpi_val_font = ImageFont.truetype(font_bold_path, 22)
        arrow_font = ImageFont.truetype(font_bold_path, 18)
        body_font = ImageFont.truetype(font_path, 14)
    except:
        title_font = section_font = kpi_title_font = kpi_val_font = arrow_font = body_font = ImageFont.load_default()

    img = Image.new("RGB", (img_width, 2000), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    # 1. 상단 헤더
    h_header = 90
    draw.rectangle([(0, 0), (img_width, h_header)], fill=(15, 23, 42))
    draw.text((margin, 28), f"{data['매장명']} 월간 보고서", font=title_font, fill=(255, 255, 255))

    y = h_header + 25

    def draw_card(x1, y1, x2, y2, bg=(255, 255, 255), border=(226, 232, 240), accent=None):
        draw.rectangle([(x1, y1), (x2, y2)], fill=bg, outline=border, width=1)
        if accent:
            draw.rectangle([(x1, y1), (x1 + 5, y2)], fill=accent)

    # 2. 핵심 성과 지표 요약 (KPI)
    draw.text((margin, y), "핵심 성과 지표 요약", font=section_font, fill=(15, 23, 42))
    y += 32

    card_w = (img_width - (margin * 2) - 24) // 3
    p_rank = parse_rank_num(data['전월 순위'])
    c_rank = parse_rank_num(data['당월 순위'])
    
    rank_accent = (59, 130, 246)
    arrow_sym = "="
    arrow_color = (100, 116, 139)
    status_tag = "유지"

    if p_rank is not None and c_rank is not None:
        if c_rank < p_rank:
            rank_accent = (16, 185, 129)
            arrow_sym = "▲"
            arrow_color = (16, 185, 129)
            status_tag = "상승"
        elif c_rank > p_rank:
            rank_accent = (225, 29, 72)
            arrow_sym = "▼"
            arrow_color = (225, 29, 72)
            status_tag = "대응"
        else:
            rank_accent = (59, 130, 246)
            arrow_sym = "="
            arrow_color = (100, 116, 139)
            status_tag = "유지"

    # KPI 1 (플레이스 순위)
    draw_card(margin, y, margin + card_w, y + 85, accent=rank_accent)
    draw.text((margin + 16, y + 14), f"플레이스 순위 [{status_tag}]", font=kpi_title_font, fill=(100, 116, 139))
    draw.text((margin + 16, y + 40), f"{data['전월 순위']}", font=kpi_val_font, fill=(30, 41, 59))
    draw.text((margin + 82, y + 40), f"{arrow_sym}", font=arrow_font, fill=arrow_color)
    draw.text((margin + 108, y + 40), f"{data['당월 순위']}", font=kpi_val_font, fill=rank_accent)

    # KPI 2
    c2_x = margin + card_w + 12
    draw_card(c2_x, y, c2_x + card_w, y + 85, accent=(15, 23, 42))
    draw.text((c2_x + 16, y + 14), "당월 방문자 리뷰", font=kpi_title_font, fill=(100, 116, 139))
    draw.text((c2_x + 16, y + 40), f"{data['방문자 리뷰 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    # KPI 3
    c3_x = c2_x + card_w + 12
    draw_card(c3_x, y, c3_x + card_w, y + 85, accent=(15, 23, 42))
    draw.text((c3_x + 16, y + 14), "고객 답글 관리", font=kpi_title_font, fill=(100, 116, 139))
    draw.text((c3_x + 16, y + 40), f"{data['답글 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    y += 85 + 28

    # 3. 본문 세부 섹션
    def render_single_line_section(title, raw_text, cur_y, accent_col=(15, 23, 42), bg_col=(255, 255, 255), border_col=(226, 232, 240)):
        draw.text((margin, cur_y), title, font=section_font, fill=(15, 23, 42))
        cur_y += 32
        
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        block_h = max(60, len(lines) * 26 + 18)
        
        draw_card(margin, cur_y, img_width - margin, cur_y + block_h, bg=bg_col, border=border_col, accent=accent_col)
        
        ly = cur_y + 14
        for line in lines:
            draw.text((margin + 18, ly), line, font=body_font, fill=(30, 41, 59))
            ly += 26
            
        return cur_y + block_h + 26

    # [섹션 1] 플레이스 순위 분석
    is_dropped = (p_rank and c_rank and c_rank > p_rank)
    s1_bg = (254, 242, 242) if is_dropped else (255, 255, 255)
    s1_border = (254, 202, 202) if is_dropped else (226, 232, 240)
    s1_accent = (225, 29, 72) if is_dropped else (16, 185, 129) if (p_rank and c_rank and c_rank < p_rank) else (59, 130, 246)
    
    y = render_single_line_section("플레이스 순위 분석 및 대응 방안", data['rank_sec'], y, accent_col=s1_accent, bg_col=s1_bg, border_col=s1_border)

    # [섹션 2] 대표키워드 분석
    y = render_single_line_section("대표키워드 분석 및 SEO 세팅 보고", data['kw_sec'], y, accent_col=(14, 165, 233))

    # [섹션 3] 리뷰 및 답글
    y = render_single_line_section("방문자 리뷰 및 고객 답글 관리 보고", data['review_sec'], y, accent_col=(15, 23, 42))

    # [섹션 4] 체험단 / 기자단 배포 보고 및 리스트
    draw.text((margin, y), "체험단 / 기자단 배포 보고 및 리스트", font=section_font, fill=(15, 23, 42))
    y += 32
    links = data['리뷰링크']
    link_h = max(60, len(links) * 24 + 18 if links else 55)
    draw_card(margin, y, img_width - margin, y + link_h, accent=(2, 132, 199))

    ly = y + 14
    if links:
        for i, link in enumerate(links):
            draw.text((margin + 18, ly), f"{i+1}. {link}", font=body_font, fill=(2, 132, 199))
            ly += 24
    else:
        draw.text((margin + 18, ly), "등록된 리뷰 링크가 없습니다.", font=body_font, fill=(148, 163, 184))

    # 하단 여백 완전 크롭
    final_y = y + link_h + 15
    cropped_img = img.crop((0, 0, img_width, final_y))

    buf = BytesIO()
    cropped_img.save(buf, format="PNG")
    return buf.getvalue()

# --- [3] 결과 출력 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📤 생성된 보고서 및 카톡 전달 문구")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            col1, col2 = st.columns([1.2, 1])
            
            with col1:
                st.markdown(f"### 🖼️ [{data['매장명']}] 월간 보고서 이미지")
                img_bytes = create_fitted_single_line_image(data)
                st.image(img_bytes, use_container_width=True)
                
                st.download_button(
                    label=f"📥 {data['매장명']} 보고서 이미지(PNG) 다운로드",
                    data=img_bytes,
                    file_name=f"월간보고서_{data['매장명']}.png",
                    mime="image/png",
                    key=f"dl_btn_{idx}"
                )
                
            with col2:
                st.markdown(f"### 📱 [{data['매장명']}] 카톡 발송용 통합 요약 리포트")
                
                p_rank = parse_rank_num(data['전월 순위'])
                c_rank = parse_rank_num(data['당월 순위'])
                arrow_sym = "="
                status_str = "유지"
                if p_rank and c_rank:
                    if c_rank < p_rank:
                        arrow_sym = "▲"
                        status_str = "상승"
                    elif c_rank > p_rank:
                        arrow_sym = "▼"
                        status_str = "대응/점검"
                    else:
                        arrow_sym = "="
                        status_str = "유지"

                # 💡 이미지 본문 반복이 아닌 깔끔한 통합 요약 형식으로 카톡 문구 전면 개편
                kw_str = ", ".join(data['대표키워드']) if data['대표키워드'] else "주요 키워드"
                link_count = len(data['리뷰링크'])

                kakao_text = (
                    f"안녕하세요 대표님! [{data['매장명']}] 월간 마케팅 통합 보고서 전달드립니다.\n\n"
                    f"📌 [월간 핵심 성과 요약]\n"
                    f"• 플레이스 순위: {data['전월 순위']} {arrow_sym} {data['당월 순위']} ({status_str})\n"
                    f"• 당월 방문자 리뷰: {data['방문자 리뷰 수']}건 유입\n"
                    f"• 고객 답글 관리: {data['답글 수']}건 (100% 완료)\n\n"
                    f"📌 [주요 마케팅 집행 현황]\n"
                    f"• 플레이스 관리: 당월 순위 분석 및 알고리즘 맞춤 트래픽/SEO 세팅 진행\n"
                    f"• 대표키워드 최적화: ({kw_str}) 상권 분석 기반 핵심 태그 구조화 완료\n"
                    f"• 블로그/기자단 배포: 당월 총 {link_count}건 콘텐츠 배포 진행 완료\n\n"
                    f"📄 세부 항목별 상세 리포트 및 리뷰 배포 링크는 함께 첨부해 드린 보고서 이미지를 확인해 주세요!\n"
                    f"궁금하신 사항은 언제든 편하게 말씀해 주세요. 감사합니다. :)"
                )

                st.text_area("카톡 전송 문구 전체 복사", value=kakao_text, height=420, key=f"kakao_txt_{idx}")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
