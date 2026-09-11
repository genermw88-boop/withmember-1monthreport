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

# --- [1] 순위 분석 및 동적 문구 생성 유틸리티] ---
def format_rank_input(rank_str):
    """숫자 입력 시 '위' 문구 정렬"""
    rank_str = str(rank_str).strip()
    if not rank_str or rank_str == "-":
        return "-"
    if not rank_str.endswith("위"):
        return f"{rank_str}위"
    return rank_str

def calculate_rank_diff(prev_str, curr_str):
    """상승/하락 순위 계산 및 화살표 텍스트 반환"""
    p_nums = re.findall(r'\d+', str(prev_str))
    c_nums = re.findall(r'\d+', str(curr_str))
    
    if p_nums and c_nums:
        p = int(p_nums[0])
        c = int(c_nums[0])
        diff = p - c
        if diff > 0:
            return f"▲ {diff}계단 상승", f"{p}위 ➔ {c}위 (▲ {diff}계단 상승)"
        elif diff < 0:
            return f"▼ {abs(diff)}계단 하락", f"{p}위 ➔ {c}위 (▼ {abs(diff)}계단 하락)"
        else:
            return "➖ 순위 유지", f"{p}위 ➔ {c}위 (순위 유지)"
    return "변동없음", f"{prev_str} ➔ {curr_str}"

def generate_dynamic_report(data_dict):
    """입력 데이터 성과에 맞춰 다채롭고 전문적인 보고 문구 자동 생성"""
    p_rank = data_dict.get('전월 순위', '-')
    c_rank = data_dict.get('당월 순위', '-')
    badge_text, rank_full_text = calculate_rank_diff(p_rank, c_rank)
    
    lines = []
    
    # 1. 순위 성과 문구 가변화
    if "상승" in badge_text:
        lines.append(f"• [플레이스 순위] {rank_full_text} - 타겟 키워드 최적화 작업으로 노출도가 대폭 향상되었습니다.")
    elif "유지" in badge_text:
        lines.append(f"• [플레이스 순위] {rank_full_text} - 상위권 순위를 안정적으로 유지하며 트래픽을 방어하고 있습니다.")
    elif "하락" in badge_text:
        lines.append(f"• [플레이스 순위] {rank_full_text} - 최신 네이버 로직 변화에 맞춰 리뉴얼 세팅 및 보강 작업을 진행 중입니다.")
    else:
        lines.append(f"• [플레이스 순위] {rank_full_text} - 플레이스 기본 SEO 세팅 및 트래픽 유입 작업을 순항 진행 중입니다.")
        
    # 2. 리뷰/답글 문구 가변화
    v_review = data_dict.get('방문자 리뷰 수', 0)
    r_count = data_dict.get('답글 수', 0)
    if v_review > 0 and r_count > 0:
        lines.append(f"• [리뷰 관리] 신규 방문자 리뷰 {v_review}건 유입 및 {r_count}건의 친절 답글 작성으로 고객 소통 지수를 강화했습니다.")
    elif v_review > 0:
        lines.append(f"• [리뷰 관리] 실방문자 리뷰 {v_review}건을 확보하여 매장 신뢰도를 높였습니다.")
    else:
        lines.append("• [리뷰 관리] 매장 플레이스 영수증/방문자 리뷰 지속 유도 및 모니터링을 진행했습니다.")
        
    # 3. 키워드 문구
    keywords = data_dict.get('대표키워드', [])
    if keywords:
        lines.append(f"• [키워드 최적화] {', '.join(keywords)} 대표 키워드를 중심으로 검색 엔진 노출 작업을 완료했습니다.")
        
    # 4. 리뷰 링크 문구
    links = data_dict.get('리뷰링크', [])
    if links:
        lines.append(f"• [콘텐츠 배포] 블로그 체험단/기자단 고품질 포스팅 {len(links)}건을 배포하여 브랜드 인지도를 확장했습니다.")
        
    lines.append("• [향후 계획] 지속적인 실시간 트래픽 분석을 통해 최상위 노출 유지 및 매출 증대에 집중하겠습니다.")
    return "\n".join(lines)

# --- [메인 헤더] ---
st.title("📊 위드멤버(WithMember) 프리미엄 월간 보고서")
st.markdown("데이터를 입력하면 **상승 순위 계산, ➔ 화살표 추가, 고급 디자인 테마**가 적용된 보고서가 자동 생성됩니다.")

# --- [2] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명 *", placeholder="예: 강남 맛집")
        prev_rank_input = st.text_input("전월 플레이스 순위", placeholder="예: 11")
        current_rank_input = st.text_input("당월 플레이스 순위", placeholder="예: 1")
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
    
    st.subheader("💬 월간 보고 및 카톡 발송 문구")
    kakao_msg_input = st.text_area(
        "보고 내용 직접 작성 (비워둘 경우 성과 수치에 따라 맞춤형 자동 작성)", 
        placeholder="비워둘 경우 상승/하락 폭 및 성과에 맞춰 전문적인 문구가 자동으로 다르게 채워집니다.", 
        height=120
    )

    submitted = st.form_submit_button("🚀 프리미엄 보고서 생성")

    if submitted:
        if store_name:
            valid_keywords = [k for k in keywords if k.strip()]
            valid_links = [l for l in links if l.strip()]

            formatted_prev_rank = format_rank_input(prev_rank_input)
            formatted_curr_rank = format_rank_input(current_rank_input)

            temp_data = {
                "매장명": store_name,
                "전월 순위": formatted_prev_rank,
                "당월 순위": formatted_curr_rank,
                "방문자 리뷰 수": visitor_review,
                "답글 수": reply_count,
                "대표키워드": valid_keywords,
                "리뷰링크": valid_links,
            }
            
            # 가변 보고서 문구 생성 또는 사용자 입력값 세팅
            if not kakao_msg_input.strip():
                final_msg = generate_dynamic_report(temp_data)
            else:
                final_msg = kakao_msg_input
                
            temp_data["관리내용"] = final_msg

            st.session_state.report_data.append(temp_data)
            st.success(f"[{store_name}] 프리미엄 보고서가 생성되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [3] 고급 디자인 보고서 이미지 생성 엔진 ---
def create_professional_image(data):
    img_width = 850
    img_height = 1250
    # 배경: 고급 쿨그레이 (#F1F5F9)
    img = Image.new("RGB", (img_width, img_height), color=(241, 245, 249))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(font_bold_path, 30)
        section_font = ImageFont.truetype(font_bold_path, 19)
        card_bold_font = ImageFont.truetype(font_bold_path, 16)
        body_font = ImageFont.truetype(font_path, 14)
        small_font = ImageFont.truetype(font_path, 12)
    except:
        title_font = section_font = card_bold_font = body_font = small_font = ImageFont.load_default()

    margin = 45
    
    # 1. 상단 블루 그래디언트 느낌의 헤더 (#0F172A)
    draw.rectangle([(0, 0), (img_width, 130)], fill=(15, 23, 42))
    draw.text((margin, 30), "MONTHLY PERFORMANCE REPORT", font=small_font, fill=(56, 189, 248))
    draw.text((margin, 52), f"{data['매장명']} 월간 마케팅 성과 보고서", font=title_font, fill=(255, 255, 255))
    draw.text((img_width - 170, 35), "WITHMEMBER", font=section_font, fill=(226, 232, 240))

    y = 160

    # 섹션 타이틀 가이드라인 그리기 (왼쪽 블루 액센트 바 포함)
    def draw_section_header(title, y_pos):
        draw.rectangle([(margin, y_pos), (margin + 4, y_pos + 20)], fill=(2, 132, 199))
        draw.text((margin + 12, y_pos), title, font=section_font, fill=(15, 23, 42))

    # 카드 그리기 함수
    def draw_card(x1, y1, x2, y2, bg_color=(255, 255, 255), border_color=(203, 213, 225)):
        draw.rectangle([(x1, y1), (x2, y2)], fill=bg_color, outline=border_color, width=1)

    # 2. 핵심 성과 요약 카드
    draw_section_header("핵심 성과 요약", y)
    y += 35

    card_w = (img_width - (margin * 2) - 30) // 3
    
    # 순위 계산 및 뱃지 문구
    rank_badge, rank_arrow_text = calculate_rank_diff(data['전월 순위'], data['당월 순위'])

    # 카드 1: 순위 (화살표 ➔ 포함)
    draw_card(margin, y, margin + card_w, y + 95)
    draw.text((margin + 15, y + 12), "플레이스 순위", font=small_font, fill=(100, 116, 139))
    
    # 전월 ➔ 당월 화살표 표시
    rank_disp = f"{data['전월 순위']}  ➔  {data['당월 순위']}"
    draw.text((margin + 15, y + 36), rank_disp, font=card_bold_font, fill=(2, 132, 199))
    # 상승/하락 뱃지 표기
    badge_color = (220, 38, 38) if "하락" in rank_badge else (16, 185, 129) if "상승" in rank_badge else (100, 116, 139)
    draw.text((margin + 15, y + 65), f"({rank_badge})", font=small_font, fill=badge_color)

    # 카드 2: 방문자 리뷰
    c2_x = margin + card_w + 15
    draw_card(c2_x, y, c2_x + card_w, y + 95)
    draw.text((c2_x + 15, y + 12), "당월 방문자 리뷰", font=small_font, fill=(100, 116, 139))
    draw.text((c2_x + 15, y + 38), f"{data['방문자 리뷰 수']} 개", font=section_font, fill=(15, 23, 42))

    # 카드 3: 답글 수
    c3_x = c2_x + card_w + 15
    draw_card(c3_x, y, c3_x + card_w, y + 95)
    draw.text((c3_x + 15, y + 12), "당월 답글 수", font=small_font, fill=(100, 116, 139))
    draw.text((c3_x + 15, y + 38), f"{data['답글 수']} 개", font=section_font, fill=(15, 23, 42))

    y += 125

    # 3. 대표키워드 세팅 현황
    draw_section_header("대표키워드 세팅 및 관리", y)
    y += 35
    draw_card(margin, y, img_width - margin, y + 60)
    kw_str = "   |   ".join(data['대표키워드']) if data['대표키워드'] else "설정된 대표키워드가 없습니다."
    draw.text((margin + 20, y + 20), kw_str, font=card_bold_font, fill=(30, 41, 59))
    y += 90

    # 4. 월간 관리 보고 및 카톡 메시지 요약 (요청하신 빨간색 부분 화살표 및 상승문구 수정 반영!)
    draw_section_header("월간 관리 보고 및 카톡 메시지 요약", y)
    y += 35
    
    report_lines = []
    for line in data['관리내용'].split('\n'):
        if line.strip():
            report_lines.extend(textwrap.wrap(line, width=54))

    card_h = max(110, len(report_lines) * 25 + 30)
    draw_card(margin, y, img_width - margin, y + card_h)
    
    ry = y + 18
    for line in report_lines:
        draw.text((margin + 20, ry), line, font=body_font, fill=(51, 65, 85))
        ry += 25
        
    y += card_h + 30

    # 5. 체험단 / 기자단 배포 리스트
    draw_section_header("체험단 / 기자단 배포 리스트", y)
    y += 35
    
    links = data['리뷰링크']
    link_card_h = max(75, len(links) * 24 + 25) if links else 65
    draw_card(margin, y, img_width - margin, y + link_card_h)
    
    ly = y + 16
    if links:
        for i, link in enumerate(links):
            link_display = link if len(link) < 65 else link[:62] + "..."
            draw.text((margin + 20, ly), f"{i+1}. {link_display}", font=body_font, fill=(2, 132, 199))
            ly += 24
    else:
        draw.text((margin + 20, ly), "등록된 리뷰 링크가 없습니다.", font=body_font, fill=(148, 163, 184))

    # 하단 푸터
    y = img_height - 45
    draw.line([(margin, y), (img_width - margin, y)], fill=(203, 213, 225), width=1)
    draw.text((margin, y + 12), "WithMember Marketing Automation System", font=small_font, fill=(148, 163, 184))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- [4] 결과 출력 및 카톡 발송 화면 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📤 생성된 월간 보고서 결과")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            col1, col2 = st.columns([1, 1.1])
            
            with col1:
                st.markdown(f"### 🖼️ [{data['매장명']}] 고급 이미지 보고서")
                img_bytes = create_professional_image(data)
                st.image(img_bytes, use_container_width=True)
                
                st.download_button(
                    label=f"📥 [{data['매장명']}] 보고서 이미지(PNG) 다운로드",
                    data=img_bytes,
                    file_name=f"위드멤버_월간보고서_{data['매장명']}.png",
                    mime="image/png",
                    key=f"dl_btn_{idx}"
                )
                
            with col2:
                st.markdown(f"### 📱 [{data['매장명']}] 카톡 발송용 맞춤 리포트")
                st.caption("아래 문구를 복사해서 전달하면 카카오톡에서 링크 클릭이 가능합니다.")
                
                rank_badge, rank_arrow_text = calculate_rank_diff(data['전월 순위'], data['당월 순위'])
                
                kakao_text = f"안녕하세요 대표님! 위드멤버입니다.\n[{data['매장명']}] 월간 마케팅 관리 보고서 전달드립니다.\n\n"
                kakao_text += f"📊 [핵심 성과 요약]\n"
                kakao_text += f"• 플레이스 순위: {rank_arrow_text}\n"
                kakao_text += f"• 이번 달 방문자 리뷰: {data['방문자 리뷰 수']}개\n"
                kakao_text += f"• 답글 관리: {data['답글 수']}개\n\n"
                
                if data['대표키워드']:
                    kakao_text += f"📌 [대표키워드]: {', '.join(data['대표키워드'])}\n\n"
                    
                kakao_text += f"💡 [월간 관리 보고 내용]\n{data['관리내용']}\n\n"
                
                if data['리뷰링크']:
                    kakao_text += "🔗 [체험단/기자단 리뷰 배포 링크]\n"
                    for i, link in enumerate(data['리뷰링크']):
                        kakao_text += f"{i+1}. {link}\n"
                
                kakao_text += "\n상세 내용은 첨부해 드린 보고서 이미지를 함께 참고해 주세요. 감사합니다!"

                st.text_area("카톡 전송 문구 복사", value=kakao_text, height=320, key=f"kakao_txt_{idx}")
                
                if data['리뷰링크']:
                    st.markdown("#### 🔗 리뷰 링크 바로가기 (원클릭 접속)")
                    for i, link in enumerate(data['리뷰링크']):
                        st.markdown(f"- [{i+1}번 리뷰 보러가기]({link})")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
