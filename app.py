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
    page_title="위드멤버 프리미엄 월간 보고서", 
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

def generate_smart_report(data_dict):
    """입력 데이터 및 순위 변동 상황 분석 기반 전문 보고 문구 생성"""
    report = []
    p_rank = parse_rank_num(data_dict.get('전월 순위', ''))
    c_rank = parse_rank_num(data_dict.get('당월 순위', ''))
    
    if p_rank is not None and c_rank is not None:
        if c_rank > p_rank: # 순위 하락
            report.append(f"⚠️ [플레이스 순위 변동 분석]\n"
                          f"당월 순위가 {p_rank}위에서 {c_rank}위로 조정됨에 따라 최신 네이버 알고리즘 업데이트 및 경쟁사 트래픽 변동을 정밀 분석했습니다.\n\n"
                          f"🛠️ [긴급 개선 및 반등 대응 방안]\n"
                          f"1) 대표 키워드 연관도 재설정 및 매장 정보 최적화 업데이트\n"
                          f"2) 타깃 유효 트래픽 유입 비율 상향 조정\n"
                          f"3) 고품질 블로그 리뷰 및 신규 영수증 리뷰 집중 배포를 통한 1-2주 내 순위 반등 실행")
        elif c_rank < p_rank: # 순위 상승
            report.append(f"📈 [플레이스 순위 상승 성과]\n"
                          f"순위가 {p_rank}위에서 {c_rank}위로 안정적으로 상승하여 가시성이 대폭 개선되었습니다. 현재 노출세를 유지하기 위해 실시간 트래픽 모니터링을 지속합니다.")
        else: # 순위 유지
            report.append(f"🛡️ [플레이스 순위 유지]\n"
                          f"순위가 {c_rank}위로 안정되게 유지가 지속되고 있습니다. 서브 키워드 유입 확장을 통해 최상위권 안착 작업을 병행합니다.")
    else:
        report.append(f"• [플레이스 순위] (전월) {data_dict.get('전월 순위', '-')} ➔ (당월) {data_dict.get('당월 순위', '-')}")

    v_review = data_dict.get('방문자 리뷰 수', 0)
    r_count = data_dict.get('답글 수', 0)
    report.append(f"💬 [고객 소통 지수]\n신규 방문자 리뷰 {v_review}건 유입 및 {r_count}건의 100% 답글 관리를 완료하여 매장 신뢰도를 강화했습니다.")

    links = data_dict.get('리뷰링크', [])
    if links:
        report.append(f"🔗 [마케팅 콘텐츠 발행]\n고품질 체험단/기자단 콘텐츠 총 {len(links)}건을 배포하여 브랜드 인지도를 확산했습니다.")

    return "\n\n".join(report)

# --- [메인 헤더] ---
st.title("🏛️ 위드멤버(WithMember) 월간 보고서 생성기")
st.markdown("매장 성과를 입력하면 **한 페이지에 깔끔하게 맞춘 보고서 이미지**와 **카톡 전달용 리포트**를 동시에 생성합니다.")

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명 *", placeholder="예: 강남 맛집")
        prev_rank_input = st.text_input("전월 플레이스 순위", placeholder="예: 11")
        current_rank_input = st.text_input("당월 플레이스 순위", placeholder="예: 2")
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
    
    st.subheader("💬 카톡 발송 및 보고 내용 입력")
    kakao_msg_input = st.text_area(
        "월간 보고 내용 (비워두시면 자동으로 성과 보고문이 작성됩니다)", 
        placeholder="비워둘 경우 자동 작성됩니다.", 
        height=120
    )

    submitted = st.form_submit_button("🚀 맞춤형 보고서 생성")

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
            
            if not kakao_msg_input.strip():
                final_msg = generate_smart_report(temp_data)
            else:
                final_msg = kakao_msg_input
                
            temp_data["관리내용"] = final_msg

            st.session_state.report_data.append(temp_data)
            st.success(f"[{store_name}] 1페이지 맞춤형 프리미엄 보고서가 생성되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 1페이지 피팅 프리미엄 보고서 이미지 생성 엔진 ---
def create_enterprise_image(data):
    # 텍스트 및 링크 개수에 따라 최적 높이 동적 연산 (불필요한 하단 여백 제거)
    report_lines = []
    for line in data['관리내용'].split('\n'):
        if line.strip():
            report_lines.extend(textwrap.wrap(line, width=54))
        else:
            report_lines.append("")

    links = data['리뷰링크']
    
    # 영역별 높이 계산
    header_h = 130
    kpi_section_h = 145
    kw_section_h = 100
    report_section_h = max(130, len(report_lines) * 26 + 65)
    link_section_h = max(80, len(links) * 28 + 65) if links else 100
    footer_h = 60

    # 이미지 전체 높이 정밀 산출 (하단 붕 뜨는 여백 완전 방지)
    img_width = 880
    img_height = header_h + kpi_section_h + kw_section_h + report_section_h + link_section_h + footer_h

    # 배경 생성
    img = Image.new("RGB", (img_width, img_height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    # 폰트 불러오기
    try:
        title_font = ImageFont.truetype(font_bold_path, 32)
        section_font = ImageFont.truetype(font_bold_path, 19)
        kpi_val_font = ImageFont.truetype(font_bold_path, 23)
        body_font = ImageFont.truetype(font_path, 15)
        small_font = ImageFont.truetype(font_path, 13)
    except:
        title_font = section_font = kpi_val_font = body_font = small_font = ImageFont.load_default()

    margin = 50

    # 1. 헤더 다크 네이비 배너 (#0B192C)
    draw.rectangle([(0, 0), (img_width, 130)], fill=(11, 25, 44))
    draw.rectangle([(0, 0), (img_width, 5)], fill=(212, 175, 55)) # 골드 상단 라인
    
    draw.text((margin, 35), f"{data['매장명']} 월간 경영 성과 보고서", font=title_font, fill=(255, 255, 255))
    draw.text((margin, 82), "소상공인 맞춤 마케팅 로직 성과 보고", font=small_font, fill=(148, 163, 184))

    y = 155

    # 카드 그리기 유틸리티
    def draw_panel(x1, y1, x2, y2, bg=(255, 255, 255), border=(226, 232, 240), accent_color=None):
        draw.rectangle([(x1, y1), (x2, y2)], fill=bg, outline=border, width=1)
        if accent_color:
            draw.rectangle([(x1, y1), (x1 + 6, y2)], fill=accent_color)

    # 2. KPI 대시보드 카드 (영문 제거)
    draw.text((margin, y), "핵심 성과 요약 대시보드", font=section_font, fill=(15, 23, 42))
    y += 35

    card_w = (img_width - (margin * 2) - 24) // 3
    p_rank = parse_rank_num(data['전월 순위'])
    c_rank = parse_rank_num(data['당월 순위'])
    
    rank_accent = (2, 132, 199)
    rank_status = "순위 측정"
    if p_rank and c_rank:
        if c_rank < p_rank:
            rank_accent = (16, 185, 129)
            rank_status = "상승 🔼"
        elif c_rank > p_rank:
            rank_accent = (225, 29, 72)
            rank_status = "개선대응 ⚠️"
        else:
            rank_accent = (2, 132, 199)
            rank_status = "안정유지 🛡️"

    # KPI 1: 순위
    draw_panel(margin, y, margin + card_w, y + 90, accent_color=rank_accent)
    draw.text((margin + 18, y + 14), f"플레이스 순위 [{rank_status}]", font=small_font, fill=(100, 116, 139))
    draw.text((margin + 18, y + 42), f"{data['전월 순위']}   {data['당월 순위']}", font=kpi_val_font, fill=rank_accent)

    # KPI 2: 방문자 리뷰
    c2_x = margin + card_w + 12
    draw_panel(c2_x, y, c2_x + card_w, y + 90, accent_color=(15, 23, 42))
    draw.text((c2_x + 18, y + 14), "당월 방문자 리뷰 유입", font=small_font, fill=(100, 116, 139))
    draw.text((c2_x + 18, y + 42), f"{data['방문자 리뷰 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    # KPI 3: 답글 관리
    c3_x = c2_x + card_w + 12
    draw_panel(c3_x, y, c3_x + card_w, y + 90, accent_color=(15, 23, 42))
    draw.text((c3_x + 18, y + 14), "고객 답글 관리 내역", font=small_font, fill=(100, 116, 139))
    draw.text((c3_x + 18, y + 42), f"{data['답글 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    y += 115

    # 3. 대표키워드 현황 (영문 제거)
    draw.text((margin, y), "타깃 대표키워드 세팅 현황", font=section_font, fill=(15, 23, 42))
    y += 35
    
    draw_panel(margin, y, img_width - margin, y + 55, accent_color=(56, 189, 248))
    kw_str = "   |   ".join(data['대표키워드']) if data['대표키워드'] else "설정된 대표키워드가 없습니다."
    draw.text((margin + 20, y + 17), kw_str, font=section_font, fill=(30, 41, 59))
    y += 80

    # 4. 월간 종합 관리 및 개선 실행 보고 (영문 제거)
    draw.text((margin, y), "월간 종합 관리 및 개선 실행 보고", font=section_font, fill=(15, 23, 42))
    y += 35

    card_h = len(report_lines) * 26 + 30
    bg_col = (254, 242, 242) if (p_rank and c_rank and c_rank > p_rank) else (255, 255, 255)
    border_col = (254, 202, 202) if (p_rank and c_rank and c_rank > p_rank) else (226, 232, 240)
    card_accent = (225, 29, 72) if (p_rank and c_rank and c_rank > p_rank) else (15, 23, 42)

    draw_panel(margin, y, img_width - margin, y + card_h, bg=bg_col, border=border_col, accent_color=card_accent)

    ry = y + 18
    for line in report_lines:
        draw.text((margin + 20, ry), line, font=body_font, fill=(30, 41, 59))
        ry += 26

    y += card_h + 25

    # 5. 체험단 / 기자단 배포 리스트 (영문 제거)
    draw.text((margin, y), "체험단 / 기자단 배포 리스트", font=section_font, fill=(15, 23, 42))
    y += 35

    link_card_h = len(links) * 28 + 25 if links else 55
    draw_panel(margin, y, img_width - margin, y + link_card_h, accent_color=(2, 132, 199))

    ly = y + 15
    if links:
        for i, link in enumerate(links):
            link_display = link if len(link) < 68 else link[:65] + "..."
            draw.text((margin + 20, ly), f"{i+1}. {link_display}", font=body_font, fill=(2, 132, 199))
            ly += 28
    else:
        draw.text((margin + 20, ly), "등록된 리뷰 링크가 없습니다.", font=body_font, fill=(148, 163, 184))

    # 하단 푸터 (영문 제거 및 깔끔한 한글 변경)
    y = img_height - 35
    draw.line([(margin, y), (img_width - margin, y)], fill=(203, 213, 225), width=1)
    draw.text((margin, y + 10), "위드멤버 마케팅 성과 보고 시스템", font=small_font, fill=(148, 163, 184))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- [3] 결과 출력 및 카톡 공유 화면 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📤 생성된 월간 보고서 결과")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            col1, col2 = st.columns([1, 1.1])
            
            with col1:
                st.markdown(f"### 🖼️ [{data['매장명']} 보고서 이미지]")
                img_bytes = create_enterprise_image(data)
                st.image(img_bytes, use_container_width=True)
                
                st.download_button(
                    label=f"📥 {data['매장명']} 보고서 이미지(PNG) 다운로드",
                    data=img_bytes,
                    file_name=f"위드멤버_월간보고서_{data['매장명']}.png",
                    mime="image/png",
                    key=f"dl_btn_{idx}"
                )
                
            with col2:
                st.markdown(f"### 📱 [{data['매장명']}] 카톡 발송용 리포트")
                st.caption("아래 텍스트를 복사하여 카카오톡으로 전달하시면 링크를 원클릭 접속할 수 있습니다.")
                
                kakao_text = f"안녕하세요 대표님! 위드멤버입니다.\n[{data['매장명']}] 월간 마케팅 관리 보고서 전달드립니다.\n\n"
                kakao_text += f"📊 [핵심 성과 요약]\n"
                kakao_text += f"• 플레이스 순위: {data['전월 순위']} ➔ {data['당월 순위']}\n"
                kakao_text += f"• 당월 방문자 리뷰: {data['방문자 리뷰 수']}개\n"
                kakao_text += f"• 답글 관리 내역: {data['답글 수']}개\n\n"
                
                if data['대표키워드']:
                    kakao_text += f"📌 [대표키워드]: {', '.join(data['대표키워드'])}\n\n"
                    
                kakao_text += f"💡 [월간 관리 및 개선 대응 보고]\n{data['관리내용']}\n\n"
                
                if data['리뷰링크']:
                    kakao_text += "🔗 [체험단/기자단 리뷰 링크]\n"
                    for i, link in enumerate(data['리뷰링크']):
                        kakao_text += f"{i+1}. {link}\n"
                
                kakao_text += "\n상세 내용은 첨부해 드린 보고서 이미지를 확인해 주세요. 감사합니다!"

                st.text_area("카톡 전송 문구 복사 (Ctrl+A ➔ Ctrl+C)", value=kakao_text, height=340, key=f"kakao_txt_{idx}")
                
                if data['리뷰링크']:
                    st.markdown("#### 🔗 리뷰 링크 바로가기 (원클릭 테스트)")
                    for i, link in enumerate(data['리뷰링크']):
                        st.markdown(f"- [{i+1}번 리뷰 보러가기 ({link[:35]}...)]({link})")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
