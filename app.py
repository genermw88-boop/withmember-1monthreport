import streamlit as st
import pandas as pd
import os
import urllib.request
import re
import random
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

# --- [다양한 보고서 문구 템플릿 풀(Pool)] ---
INCREASE_TEMPLATES = [
    "📈 [플레이스 순위 상승 성과]\n당월 플레이스 순위가 {p_rank}에서 {c_rank}로 올라섰습니다. 타깃 키워드 유효 트래픽과 체류 시간 증가가 주요 상승 요인으로 분석됩니다.\n\n🎯 [추후 관리 계획]\n상위권 안착을 위해 서브 키워드 최적화 작업을 병행하여 현 노출 지수를 단단히 유지하겠습니다.",
    "🚀 [노출 가시성 대폭 개선]\n매장 플레이스 순위가 {p_rank}에서 {c_rank}로 대폭 상승했습니다. 키워드 세팅 및 유입량 개선 작업이 즉각적인 성과로 이어졌습니다.\n\n🎯 [추후 관리 계획]\n주요 방문자 동선 분석을 통해 상위 노출을 고착화하고 신규 방문자 유입을 극대화하겠습니다.",
    "✨ [타깃 최적화 성공]\n{p_rank}에서 {c_rank}로 순위가 상승하며 플레이스 노출도가 크게 확대되었습니다. 최근 배포된 고품질 리뷰 콘텐츠와의 시너지 효과로 판단됩니다.\n\n🎯 [추후 관리 계획]\n상위 노출 유지 및 2차 타깃 키워드 도출을 통해 추가 유입 경로를 확장하겠습니다."
]

DECREASE_TEMPLATES = [
    "⚠️ [플레이스 순위 변동 분석]\n당월 순위가 {p_rank}에서 {c_rank}로 조정됨에 따라 최신 네이버 알고리즘 최신화 및 주변 경쟁 매장의 임시 트래픽 집중을 정밀 분석했습니다.\n\n🛠️ [긴급 개선 및 반등 대응 방안]\n1) 대표 키워드 연관도 재설정 및 매장 정보 최적화 업데이트\n2) 타깃 유효 트래픽 유입 비율 상향 조정\n3) 고품질 블로그 리뷰 및 신규 영수증 리뷰 집중 배포를 통한 1-2주 내 순위 반등 실행",
    "📉 [순위 변동 대응 리포트]\n순위가 {p_rank}에서 {c_rank}로 하락세를 보임에 따라 최신 로직에 맞춘 매장 지수 점검을 완료했습니다.\n\n🛠️ [개선 실행 계획]\n1) 플레이스 매장 정보 및 대표 키워드 재배치\n2) 신규 방문자 리뷰 및 답글 활성화를 통한 고객 소통 지수 보완\n3) 타깃 트래픽 집중 투입으로 빠르게 이전 상위 순위 회복 진행",
    "🔍 [알고리즘 대응 분석]\n경쟁 매장의 활성화 및 네이버 최적화 기준 변경으로 인해 순위가 {p_rank}에서 {c_rank}로 변동되었습니다.\n\n🛠️ [반등 솔루션 적용]\n1) 플레이스 세팅 값 정밀 교정 및 트래픽 재분배\n2) 고품질 블로그 리뷰 콘텐츠 추가 발행\n3) 리뷰 답글 및 소통 지수 극대화를 통한 순위 조속 반등 유도"
]

MAINTAIN_TEMPLATES = [
    "🛡️ [플레이스 순위 안정 유지]\n순위가 {c_rank}로 변동 없이 안정적으로 유지되고 있습니다. 상위권 경쟁이 치열한 상황에서도 방어 작업이 성공적으로 작용하고 있습니다.\n\n🎯 [향후 관리 계획]\n서브 타깃 키워드 노출을 확장하여 추가적인 유입 유입 경로를 확보하겠습니다.",
    "🔒 [상위 노출 유지 방어]\n당월 순위가 {c_rank}로 견고하게 유지 중입니다. 지속적인 모니터링을 통해 이탈을 방지하고 있습니다.\n\n🎯 [향후 관리 계획]\n신규 리뷰 유입 속도를 조절하여 최적 지수를 단단하게 유지하겠습니다."
]

REVIEW_TEMPLATES = [
    "💬 [고객 소통 지수]\n신규 방문자 리뷰 {v_review}건 유입 및 {r_count}건의 답글 관리를 완료하여 매장 신뢰도를 강화했습니다.",
    "💬 [리뷰 활성화 성과]\n이번 달 방문자 리뷰 {v_review}건 유입 및 {r_count}건의 100% 답글 대응을 진행하여 순위 반영 지수를 높였습니다."
]

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

def generate_smart_report(data_dict):
    """입력 데이터 및 순위 변동 상황 분석 기반 무작위 전문 보고 문구 생성"""
    report = []
    p_rank_num = parse_rank_num(data_dict.get('전월 순위', ''))
    c_rank_num = parse_rank_num(data_dict.get('당월 순위', ''))
    
    p_rank_str = data_dict.get('전월 순위', '-')
    c_rank_str = data_dict.get('당월 순위', '-')
    
    # 순위 분석 무작위 선택
    if p_rank_num is not None and c_rank_num is not None:
        if c_rank_num > p_rank_num: # 하락 (숫자가 커짐)
            template = random.choice(DECREASE_TEMPLATES)
            report.append(template.format(p_rank=p_rank_str, c_rank=c_rank_str))
        elif c_rank_num < p_rank_num: # 상승 (숫자가 작아짐)
            template = random.choice(INCREASE_TEMPLATES)
            report.append(template.format(p_rank=p_rank_str, c_rank=c_rank_str))
        else: # 유지
            template = random.choice(MAINTAIN_TEMPLATES)
            report.append(template.format(c_rank=c_rank_str))
    else:
        report.append(f"• [플레이스 순위] (전월) {p_rank_str} ➔ (당월) {c_rank_str}")

    # 리뷰 분석 무작위 선택
    v_review = data_dict.get('방문자 리뷰 수', 0)
    r_count = data_dict.get('답글 수', 0)
    rev_temp = random.choice(REVIEW_TEMPLATES)
    report.append(rev_temp.format(v_review=v_review, r_count=r_count))

    # 콘텐츠 배포
    links = data_dict.get('리뷰링크', [])
    if links:
        report.append(f"🔗 [마케팅 콘텐츠 발행]\n고품질 체험단/기자단 콘텐츠 총 {len(links)}건을 배포하여 브랜드 인지도를 확산했습니다.")

    return "\n\n".join(report)

# --- [메인 헤더] ---
st.title("🏛️ 위드멤버(WithMember) 익세큐티브 월간 리포터")
st.markdown("정교한 레이아웃과 **상황별 다양한 보고 문구**가 자동 적용된 최고급 보고서를 생성합니다.")

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명 *", placeholder="예: 강남 맛집")
        prev_rank_input = st.text_input("전월 플레이스 순위", placeholder="예: 22 (자동으로 '22위' 변환)")
        current_rank_input = st.text_input("당월 플레이스 순위", placeholder="예: 33 (자동으로 '33위' 변환)")
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
        "월간 보고 내용 (비워두시면 매번 새로운 스타일의 전문 보고 문구가 자동 생성됩니다)", 
        placeholder="비워두실 경우: 순위 상승/하락에 맞춘 다채로운 분석 및 대응 방안 문구가 무작위 추출 적용됩니다.", 
        height=100
    )

    submitted = st.form_submit_button("🚀 최고급 보고서 생성")

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
            st.success(f"[{store_name}] 보고서가 생성되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 완벽 정렬 이미지 생성 엔진 ---
def create_enterprise_image(data):
    # 여유 있는 높이 설정 (하단 Overlap 방지)
    img_width = 900
    img_height = 1480
    img = Image.new("RGB", (img_width, img_height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(font_bold_path, 32)
        subtitle_font = ImageFont.truetype(font_bold_path, 17)
        section_font = ImageFont.truetype(font_bold_path, 18)
        kpi_val_font = ImageFont.truetype(font_bold_path, 22)
        body_font = ImageFont.truetype(font_path, 15)
        small_font = ImageFont.truetype(font_path, 12)
    except:
        title_font = subtitle_font = section_font = kpi_val_font = body_font = small_font = ImageFont.load_default()

    margin = 50

    # 1. 헤더 다크 네이비 배너
    draw.rectangle([(0, 0), (img_width, 140)], fill=(11, 25, 44))
    draw.rectangle([(0, 0), (img_width, 6)], fill=(212, 175, 55)) # 골드 라인
    
    draw.text((margin, 30), "WITHMEMBER MARKETING PERFORMANCE REPORT", font=small_font, fill=(56, 189, 248))
    draw.text((margin, 52), f"{data['매장명']} 월간 경영 성과 보고서", font=title_font, fill=(255, 255, 255))
    draw.text((margin, 100), "소상공인 맞춤 마케팅 로직 성과 보고  |  CONFIDENTIAL", font=small_font, fill=(148, 163, 184))

    y = 170

    # 카드 패널 그리기 함수
    def draw_panel(x1, y1, x2, y2, bg=(255, 255, 255), border=(226, 232, 240), accent_color=None):
        draw.rectangle([(x1, y1), (x2, y2)], fill=bg, outline=border, width=1)
        if accent_color:
            draw.rectangle([(x1, y1), (x1 + 6, y2)], fill=accent_color)

    # 2. KPI 대시보드 카드
    draw.text((margin, y), "📌 핵심 성과 요약 대시보드", font=section_font, fill=(15, 23, 42))
    y += 38

    card_w = (img_width - (margin * 2) - 24) // 3
    
    p_rank = parse_rank_num(data['전월 순위'])
    c_rank = parse_rank_num(data['당월 순위'])
    
    rank_accent = (2, 132, 199)
    rank_status_tag = "측정"
    if p_rank and c_rank:
        if c_rank < p_rank:
            rank_accent = (16, 185, 129) # 그린
            rank_status_tag = "상승 🔼"
        elif c_rank > p_rank:
            rank_accent = (225, 29, 72) # 레드
            rank_status_tag = "개선대응 ⚠️"
        else:
            rank_accent = (2, 132, 199) # 블루
            rank_status_tag = "유지 🛡️"

    # KPI 1: 순위
    draw_panel(margin, y, margin + card_w, y + 95, accent_color=rank_accent)
    draw.text((margin + 18, y + 16), f"플레이스 순위 [{rank_status_tag}]", font=small_font, fill=(100, 116, 139))
    draw.text((margin + 18, y + 45), f"{data['전월 순위']}  →  {data['당월 순위']}", font=kpi_val_font, fill=rank_accent)

    # KPI 2: 방문자 리뷰
    c2_x = margin + card_w + 12
    draw_panel(c2_x, y, c2_x + card_w, y + 95, accent_color=(15, 23, 42))
    draw.text((c2_x + 18, y + 16), "당월 방문자 리뷰 유입", font=small_font, fill=(100, 116, 139))
    draw.text((c2_x + 18, y + 45), f"{data['방문자 리뷰 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    # KPI 3: 답글 관리
    c3_x = c2_x + card_w + 12
    draw_panel(c3_x, y, c3_x + card_w, y + 95, accent_color=(15, 23, 42))
    draw.text((c3_x + 18, y + 16), "고객 답글 관리 내역", font=small_font, fill=(100, 116, 139))
    draw.text((c3_x + 18, y + 45), f"{data['답글 수']} 건", font=kpi_val_font, fill=(15, 23, 42))

    y += 125

    # 3. 대표키워드 세팅 현황
    draw.text((margin, y), "🎯 타깃 대표키워드 세팅 현황", font=section_font, fill=(15, 23, 42))
    y += 38
    
    draw_panel(margin, y, img_width - margin, y + 60, accent_color=(56, 189, 248))
    kw_str = "   |   ".join(data['대표키워드']) if data['대표키워드'] else "설정된 대표키워드가 없습니다."
    draw.text((margin + 20, y + 20), kw_str, font=subtitle_font, fill=(30, 41, 59))
    y += 90

    # 4. 월간 종합 관리 및 개선 실행 보고 (텍스트 줄간격 정밀 정렬)
    draw.text((margin, y), "💡 월간 종합 관리 및 개선 실행 보고", font=section_font, fill=(15, 23, 42))
    y += 38

    report_lines = []
    for paragraph in data['관리내용'].split('\n'):
        if paragraph.strip():
            wrapped = textwrap.wrap(paragraph, width=54)
            report_lines.extend(wrapped)
        else:
            report_lines.append("") # 단락 분리용 빈 줄

    card_h = max(140, len(report_lines) * 24 + 40)
    
    bg_col = (254, 242, 242) if (p_rank and c_rank and c_rank > p_rank) else (255, 255, 255)
    border_col = (254, 202, 202) if (p_rank and c_rank and c_rank > p_rank) else (226, 232, 240)
    card_accent = (225, 29, 72) if (p_rank and c_rank and c_rank > p_rank) else (15, 23, 42)

    draw_panel(margin, y, img_width - margin, y + card_h, bg=bg_col, border=border_col, accent_color=card_accent)

    ry = y + 20
    for line in report_lines:
        if line == "":
            ry += 12 # 단락 간격
        else:
            draw.text((margin + 22, ry), line, font=body_font, fill=(30, 41, 59))
            ry += 24

    y += card_h + 35

    # 5. 체험단 / 기자단 배포 리스트
    draw.text((margin, y), "🔗 체험단 / 기자단 배포 리스트", font=section_font, fill=(15, 23, 42))
    y += 38

    links = data['리뷰링크']
    link_card_h = max(75, len(links) * 28 + 30) if links else 65
    draw_panel(margin, y, img_width - margin, y + link_card_h, accent_color=(2, 132, 199))

    ly = y + 18
    if links:
        for i, link in enumerate(links):
            link_display = link if len(link) < 68 else link[:65] + "..."
            draw.text((margin + 22, ly), f"{i+1}. {link_display}", font=body_font, fill=(2, 132, 199))
            ly += 26
    else:
        draw.text((margin + 22, ly), "등록된 리뷰 링크가 없습니다.", font=body_font, fill=(148, 163, 184))

    # 푸터 (충분한 하단 공간 확보)
    y = img_height - 50
    draw.line([(margin, y), (img_width - margin, y)], fill=(203, 213, 225), width=1)
    draw.text((margin, y + 15), "WITHMEMBER MARKETING AUTOMATION SYSTEM  |  CONFIDENTIAL REPORT", font=small_font, fill=(148, 163, 184))

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
                st.markdown(f"### 🖼️ [{data['매장명']}] 익세큐티브 보고서")
                img_bytes = create_enterprise_image(data)
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
                
                kakao_text = f"안녕하세요 대표님! 위드멤버입니다.\n[{data['매장명']}] 월간 마케팅 관리 보고서 전달드립니다.\n\n"
                kakao_text += f"📊 [핵심 성과 요약]\n"
                kakao_text += f"• 플레이스 순위: {data['전월 순위']} ➔ {data['당월 순위']}\n"
                kakao_text += f"• 당월 방문자 리뷰: {data['방문자 리뷰 수']}개\n"
                kakao_text += f"• 답글 관리 내역: {data['답글 수']}개\n\n"
                
                if data['대표키워드']:
                    kakao_text += f"📌 [대표키워드]: {', '.join(data['대표키워드'])}\n\n"
                    
                kakao_text += f"💡 [월간 관리 및 대응 보고]\n{data['관리내용']}\n\n"
                
                if data['리뷰링크']:
                    kakao_text += "🔗 [체험단/기자단 리뷰 링크]\n"
                    for i, link in enumerate(data['리뷰링크']):
                        kakao_text += f"{i+1}. {link}\n"
                
                kakao_text += "\n상세 내용은 첨부해 드린 보고서 이미지를 확인해 주세요. 감사합니다!"

                st.text_area("카톡 전송 문구 복사 (Ctrl+A ➔ Ctrl+C)", value=kakao_text, height=340, key=f"kakao_txt_{idx}")
                
                if data['리뷰링크']:
                    st.markdown("#### 🔗 리뷰 링크 원클릭 접속 테스트")
                    for i, link in enumerate(data['리뷰링크']):
                        st.markdown(f"- [{i+1}번 리뷰 보러가기 ({link[:35]}...)]({link})")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
