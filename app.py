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
    page_title="위드멤버 월간 보고서", 
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
    """카톡 및 이미지 보고서 항목별 자동 문구 생성"""
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

    # 4. 체험단 / 기자단 배포 보고 (신규 추가)
    links_count = len(data_dict.get('리뷰링크', []))
    content_text = (
        f"• [콘텐츠 배포] 당월 목표 블로그 체험단 및 기자단 원고 총 {links_count}건 배포 완료\n"
        f"• [노출 타겟팅] 핵심 타겟 키워드 연관 포스팅 집행을 통한 상권 영역 내 매장 브랜드 인지도 극대화"
    )

    return {
        "rank_sec": rank_text,
        "kw_sec": kw_text,
        "review_sec": review_text,
        "content_sec": content_text
    }

# --- [메인 UI 헤더] ---
st.title("📊 위드멤버(WithMember) 월간 보고서 생성기")

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명 *", placeholder="예: ㅁㄴㅇ")
        prev_rank_input = st.text_input("전월 플레이스 순위", placeholder="예: 11 (자동으로 '11위' 변환)")
        current_rank_input = st.text_input("당월 플레이스 순위", placeholder="예: 22 (자동으로 '22위' 변환)")
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
    st.caption("비워두시면 데이터에 맞춰 정밀 분석 문구가 한 줄 형태로 자동 작성됩니다.")

    custom_rank_sec = st.text_area("1) 플레이스 순위 분석 내용", placeholder="비워두시면 자동 생성됩니다.", height=70)
    custom_kw_sec = st.text_area("2) 대표키워드 분석 내용", placeholder="비워두시면 자동 생성됩니다.", height=70)
    custom_review_sec = st.text_area("3) 방문자 리뷰/답글 내용", placeholder="비워두시면 자동 생성됩니다.", height=70)
    custom_content_sec = st.text_area("4) 체험단/기자단 배포 보고 내용", placeholder="비워두시면 자동 생성됩니다.", height=70)

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
            temp_data["content_sec"] = custom_content_sec.strip() if custom_content_sec.strip() else auto_secs["content_sec"]

            st.session_state.report_data.append(temp_data)
            st.success(f"[{store_name}] 보고서가 성공적으로 생성되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 이미지 생성 엔진 (한 줄 완벽 보장 + 하단 영문 삭제) ---
def create_professional_image(data):
    # 가로 폭을 1200px로 넉넉하게 넓혀 강제 줄바꿈 완벽 차단
    img_width = 1200
    margin = 45

    try:
        title_font = ImageFont.truetype(font_bold_path, 32)
        section_font = ImageFont.truetype(font_bold_path, 19)
        kpi_title_font = ImageFont.truetype(font_bold_path, 14)
        kpi_val_font = ImageFont.truetype(font_bold_path, 23)
        arrow_font = ImageFont.truetype(font_bold_path, 18)
        body_font = ImageFont.truetype(font_path, 14)
        small_font = ImageFont.truetype(font_path, 12)
    except:
        title_font = section_font = kpi_title_font = kpi_val_font = arrow_font = body_font = small_font = ImageFont.load_default()

    # 줄바꿈 자릿수를 105자로 늘려서 한 줄 출력을 보장
    def wrap_lines(text):
        res = []
        for l in text.split('\n'):
            if l.strip():
                res.extend(textwrap.wrap(l, width=105))
            else:
                res.append("")
        return res

    lines_sec1 = wrap_lines(data['rank_sec'])
    lines_sec2 = wrap_lines(data['kw_sec'])
    lines_sec3 = wrap_lines(data['review_sec'])
    lines_sec4 = wrap_lines(data['content_sec'])
    links = data['리뷰링크']

    h_header = 110
    h_kpi = 130
    h_sec1 = 35 + max(65, len(lines_sec1) * 25 + 18)
    h_sec2 = 35 + max(65, len(lines_sec2) * 25 + 18)
    h_sec3 = 35 + max(65, len(lines_sec3) * 25 + 18)
    h_sec4_text = len(lines_sec4) * 25 + 10
    h_sec4_links = (len(links) * 24 + 15) if links else 35
    h_sec4 = 35 + max(80, h_sec4_text + h_sec4_links + 15)
    h_footer = 40

    total_calculated_height = 130 + h_header + h_kpi + h_sec1 + h_sec2 + h_sec3 + h_sec4 + h_footer
    img_height = max(1000, total_calculated_height)

    img = Image.new("RGB", (img_width, img_height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    # 1. 헤더
    draw.rectangle([(0, 0), (img_width, 110)], fill=(15, 23, 42))
    draw.rectangle([(margin, 25), (margin + 120, 47)], fill=(30, 41, 59), outline=(51, 65, 85), width=1)
    draw.text((margin + 12, 28), "WITHMEMBER", font=small_font, fill=(56, 189, 248))
    draw.text((margin, 55), f"{data['매장명']} 월간 보고서", font=title_font, fill=(255, 255, 255))

    y = 135

    def draw_card(x1, y1, x2, y2, bg=(255, 255, 255), border=(226, 232, 240), accent=None):
        draw.rectangle([(x1, y1), (x2, y2)], fill=bg, outline=border, width=1)
        if accent:
            draw.rectangle([(x1, y1), (x1 + 5, y2)], fill=accent)

    # 2. 핵심 성과 지표
    draw.text((margin, y), "핵심 성과 지표 요약", font=section_font, fill=(15, 23, 42))
    y += 32

    card_w = (img_width - (margin * 2) - 24) // 3
    p_rank = parse_rank_num(data['전월 순위'])
    c_rank = parse_rank_num(data['당월 순위'])
    
    rank_accent = (59, 130, 246)
    arrow_sym = "➔"
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

    draw_card(margin, y, margin + card_w, y + 85, accent=rank_accent)
    draw.text((margin + 16, y + 14), f"플레이스 순위 [{status_tag}]", font=kpi_title_font, fill=(100, 116, 139))
    draw.text((margin + 16, y + 40), f"{data['전월 순위']}", font=kpi_val_font, fill=(30, 41, 59))
    draw.text((margin + 80, y + 42), f"{arrow_sym}", font=arrow_font, fill=arrow_color)
    draw.text((margin + 112, y + 40), f"{data['당월 순위']}", font=kpi_val_font, fill=rank_accent)

    c2_x = margin + card_w + 12
    draw_card(c2_x, y, c2_x + card_w, y + 85, accent=(15, 23, 42))
    draw.text((c2_x + 16, y + 14), "당월 방문자 리뷰", font=kpi_title_font, fill=(100, 116, 139))
    draw.text((c2_x + 16, y + 40), f"{data['방문자 리뷰 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    c3_x = c2_x + card_w + 12
    draw_card(c3_x, y, c3_x + card_w, y + 85, accent=(15, 23, 42))
    draw.text((c3_x + 16, y + 14), "고객 답글 관리", font=kpi_title_font, fill=(100, 116, 139))
    draw.text((c3_x + 16, y + 40), f"{data['답글 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    y += 110

    # 3. 본문 세부 섹션 렌더링
    def render_section_block(title, line_list, cur_y, accent_col=(15, 23, 42), bg_col=(255, 255, 255), border_col=(226, 232, 240)):
        draw.text((margin, cur_y), title, font=section_font, fill=(15, 23, 42))
        cur_y += 30
        
        block_h = max(65, len(line_list) * 25 + 18)
        draw_card(margin, cur_y, img_width - margin, cur_y + block_h, bg=bg_col, border=border_col, accent=accent_col)
        
        ly = cur_y + 12
        for line in line_list:
            draw.text((margin + 18, ly), line, font=body_font, fill=(30, 41, 59))
            ly += 25
            
        return cur_y + block_h + 22

    # [섹션 1] 플레이스 순위 분석
    is_dropped = (p_rank and c_rank and c_rank > p_rank)
    s1_bg = (254, 242, 242) if is_dropped else (255, 255, 255)
    s1_border = (254, 202, 202) if is_dropped else (226, 232, 240)
    s1_accent = (225, 29, 72) if is_dropped else (16, 185, 129)
    y = render_section_block("플레이스 순위 분석 및 대응 방안", lines_sec1, y, accent_col=s1_accent, bg_col=s1_bg, border_col=s1_border)

    # [섹션 2] 대표키워드 분석
    y = render_section_block("대표키워드 분석 및 SEO 세팅 보고", lines_sec2, y, accent_col=(14, 165, 233))

    # [섹션 3] 리뷰 및 답글
    y = render_section_block("방문자 리뷰 및 고객 답글 관리 보고", lines_sec3, y, accent_col=(15, 23, 42))

    # [섹션 4] 체험단 / 기자단 배포 보고 및 리스트 (보고 문구 + 링크 함께 표시)
    draw.text((margin, y), "체험단 / 기자단 배포 보고 및 리스트", font=section_font, fill=(15, 23, 42))
    y += 30
    
    sec4_box_h = max(80, h_sec4_text + h_sec4_links + 15)
    draw_card(margin, y, img_width - margin, y + sec4_box_h, accent=(2, 132, 199))

    ly = y + 12
    # 보고 문구 출력
    for line in lines_sec4:
        draw.text((margin + 18, ly), line, font=body_font, fill=(30, 41, 59))
        ly += 25

    if lines_sec4 and links:
        draw.line([(margin + 18, ly + 2), (img_width - margin - 18, ly + 2)], fill=(226, 232, 240), width=1)
        ly += 10

    # 링크 출력
    if links:
        for i, link in enumerate(links):
            link_disp = link if len(link) < 100 else link[:97] + "..."
            draw.text((margin + 18, ly), f"{i+1}. {link_disp}", font=body_font, fill=(2, 132, 199))
            ly += 24
    else:
        draw.text((margin + 18, ly), "등록된 리뷰 링크가 없습니다.", font=body_font, fill=(148, 163, 184))

    y += sec4_box_h + 25

    # 하단 푸터 (영문 문구 전면 삭제 및 깔끔한 한국어 마무리)
    draw.line([(margin, y), (img_width - margin, y)], fill=(226, 232, 240), width=1)
    draw.text((margin, y + 8), "위드멤버 마케팅 자동화 시스템", font=small_font, fill=(148, 163, 184))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- [3] 결과 출력 및 1:1 매칭 카톡 메시지 제공 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📤 생성된 보고서 및 카톡 전달 문구")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            col1, col2 = st.columns([1.1, 1])
            
            with col1:
                st.markdown(f"### 🖼️ [{data['매장명']}] 월간 보고서 이미지")
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
                st.markdown(f"### 📱 [{data['매장명']}] 카톡 발송용 리포트 문구")
                
                p_rank = parse_rank_num(data['전월 순위'])
                c_rank = parse_rank_num(data['당월 순위'])
                arrow_sym = "➔"
                if p_rank and c_rank:
                    if c_rank < p_rank:
                        arrow_sym = "▲"
                    elif c_rank > p_rank:
                        arrow_sym = "▼"

                kakao_text = f"안녕하세요 대표님! 위드멤버입니다.\n[{data['매장명']}] 월간 마케팅 보고서 전달드립니다.\n\n"
                
                kakao_text += f"📊 [핵심 성과 지표 요약]\n"
                kakao_text += f"• 플레이스 순위: {data['전월 순위']} {arrow_sym} {data['당월 순위']}\n"
                kakao_text += f"• 당월 방문자 리뷰: {data['방문자 리뷰 수']}건\n"
                kakao_text += f"• 고객 답글 관리: {data['답글 수']}건\n\n"
                
                kakao_text += f"🚨 [플레이스 순위 분석 및 대응 방안]\n{data['rank_sec']}\n\n"
                kakao_text += f"🎯 [대표키워드 분석 및 SEO 세팅 보고]\n{data['kw_sec']}\n\n"
                kakao_text += f"💬 [방문자 리뷰 및 고객 답글 관리 보고]\n{data['review_sec']}\n\n"
                kakao_text += f"📢 [체험단 / 기자단 배포 보고]\n{data['content_sec']}\n\n"
                
                if data['리뷰링크']:
                    kakao_text += "🔗 [체험단 / 기자단 배포 리스트]\n"
                    for i, link in enumerate(data['리뷰링크']):
                        kakao_text += f"{i+1}. {link}\n"
                
                kakao_text += "\n상세 내용은 첨부해 드린 보고서 이미지를 확인해 주세요. 감사합니다!"

                st.text_area("카톡 전송 문구 전체 복사", value=kakao_text, height=450, key=f"kakao_txt_{idx}")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
