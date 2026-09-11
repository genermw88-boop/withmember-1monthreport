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

if "report_data" not in st.session_state:
    st.session_state.report_data = []

# --- [유틸리티 & 분석 로직] ---
def format_rank(rank_str):
    """숫자 뒤에 '위' 문구를 자동 부착"""
    rank_str = str(rank_str).strip()
    if not rank_str or rank_str == "-":
        return "-"
    if not rank_str.endswith("위"):
        return f"{rank_str}위"
    return rank_str

def calculate_rank_diff(prev_str, curr_str):
    """순위 상승/하락 계단 수 자동 계산 및 안전한 화살표 반환"""
    p_nums = re.findall(r'\d+', str(prev_str))
    c_nums = re.findall(r'\d+', str(curr_str))
    
    if p_nums and c_nums:
        p_val, c_val = int(p_nums[0]), int(c_nums[0])
        diff = p_val - c_val
        if diff > 0:
            return f"{p_val}위 -> {c_val}위 (▲ {diff}계단 상승)"
        elif diff < 0:
            return f"{p_val}위 -> {c_val}위 (▼ {abs(diff)}계단 하락)"
        else:
            return f"{c_val}위 (보류 및 순위 유지)"
    return f"{prev_str} -> {curr_str}"

def generate_dynamic_report(data_dict):
    """보고서 출력 시마다 문구가 다채롭게 바뀌는 다이나믹 엔진"""
    p_rank = data_dict.get('전월 순위', '-')
    c_rank = data_dict.get('당월 순위', '-')
    rank_summary = calculate_rank_diff(p_rank, c_rank)
    
    v_review = data_dict.get('방문자 리뷰 수', 0)
    r_count = data_dict.get('답글 수', 0)
    keywords = data_dict.get('대표키워드', [])
    links = data_dict.get('리뷰링크', [])
    
    # 어투 및 문장 바리에이션 패턴
    rank_templates = [
        f"• [플레이스 순위 분석] {rank_summary} 성과를 달성하며 플레이스 가시성이 대폭 개선되었습니다.",
        f"• [플레이스 순위 동향] 전월 대비 {rank_summary} 변동을 기록하며 타겟 노출을 성공적으로 확보했습니다.",
        f"• [순위 최적화 현황] 플레이스 알고리즘 적용을 통해 {rank_summary} 트래픽 우위를 확보하였습니다."
    ]
    
    review_templates = [
        f"• [리뷰 및 반응 관리] 신규 방문자 리뷰 {v_review}건 유입과 피드백 답글 {r_count}건을 신속히 완료하여 고객 신뢰도를 강화했습니다.",
        f"• [고객 소통 지수] 이번 달 실방문 리뷰 {v_review}개 획득 및 답글 {r_count}개를 등록하며 매장 평판 지수를 끌어올렸습니다.",
        f"• [선순환 선옥션] 신규 리뷰 {v_review}건 세팅과 답글 {r_count}건 밀착 케어로 지수 상승 기반을 마련했습니다."
    ]
    
    kw_templates = [
        f"• [핵심 키워드 작업] [{', '.join(keywords) if keywords else '주요 타겟 키워드'}] 중심의 플레이스 SEO 최적화를 집중 수행했습니다.",
        f"• [타겟 노출 강화] 대표키워드({', '.join(keywords) if keywords else '선정 키워드'}) 매칭도를 극대화하여 검색 유입을 유도했습니다."
    ]
    
    content_templates = [
        f"• [콘텐츠 마케팅] 고품질 체험단/기자단 리뷰 총 {len(links)}건을 배포하여 온라인 바이럴 영향력을 확대했습니다.",
        f"• [외부 트래픽 확보] 전문 블로거 콘텐츠 {len(links)}건 발행을 통해 브랜드 인지도와 신뢰도를 한층 높였습니다."
    ]
    
    future_templates = [
        "• [다음 달 전략] 현재 노출 순위 유지를 위한 지속적인 트래픽 모니터링과 2차 바이럴 작업을 병행할 예정입니다.",
        "• [향후 케어 플랜] 신규 알고리즘 변화에 맞춰 실시간 순위 방어 및 추가 키워드 확장을 추진하겠습니다."
    ]

    report_lines = [
        random.choice(rank_templates),
        random.choice(review_templates),
        random.choice(kw_templates),
        random.choice(content_templates) if links else "• [콘텐츠 마케팅] 차월 배포 일정에 맞춰 블로그 바이럴 세팅 진행 예정입니다.",
        random.choice(future_templates)
    ]
    
    return "\n".join(report_lines)

# --- [메인 헤더] ---
st.title("📊 위드멤버(WithMember) 프리미엄 월간 보고서")
st.markdown("데이터를 입력하면 **상승 순위 계산, 전문 디자인 레이아웃, 다이나믹 보고 문구**가 자동 적용됩니다.")

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)
    with col1:
        store_name = st.text_input("매장명 *", placeholder="예: 위드식당")
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
    
    kakao_msg_input = st.text_area(
        "💬 보고 내용 직접 작성 (비워둘 경우 매번 새로운 다이나믹 문구 자동 생성)", 
        placeholder="비워두시면 매번 다채롭고 전문적인 AI 마케팅 분석 문구가 자동 세팅됩니다.", 
        height=100
    )

    submitted = st.form_submit_button("🚀 고품격 보고서 및 이미지 생성")

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
                final_msg = generate_dynamic_report(temp_data)
            else:
                final_msg = kakao_msg_input
                
            temp_data["관리내용"] = final_msg
            st.session_state.report_data.append(temp_data)
            st.success(f"[{store_name}] 보고서 생성이 완료되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 전문 체계화 이미지 생성 엔진 ---
def create_professional_image(data):
    img_width = 850
    img_height = 1320
    # 모던 쿨그레이 배경 (#F8FAFC)
    img = Image.new("RGB", (img_width, img_height), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(font_bold_path, 30)
        header_font = ImageFont.truetype(font_bold_path, 19)
        sub_bold_font = ImageFont.truetype(font_bold_path, 15)
        body_font = ImageFont.truetype(font_path, 14)
        small_font = ImageFont.truetype(font_path, 12)
    except:
        title_font = header_font = sub_bold_font = body_font = small_font = ImageFont.load_default()

    margin = 45

    # 1. 상단 프레임 배너 (#0F172A)
    draw.rectangle([(0, 0), (img_width, 135)], fill=(15, 23, 42))
    draw.text((margin, 32), "MONTHLY PERFORMANCE REPORT", font=small_font, fill=(56, 189, 248))
    draw.text((margin, 54), f"{data['매장명']} 월간 마케팅 성과 보고서", font=title_font, fill=(255, 255, 255))
    draw.text((img_width - 170, 38), "WITHMEMBER", font=header_font, fill=(226, 232, 240))

    y = 160

    # 서브 섹션 타이틀 포인트 바 그리기
    def draw_section_title(y_pos, title_text):
        draw.rectangle([(margin, y_pos + 2), (margin + 4, y_pos + 20)], fill=(2, 132, 199))
        draw.text((margin + 12, y_pos), title_text, font=header_font, fill=(15, 23, 42))

    # 2. 핵심 성과 요약 (상승 순위 계산 반영)
    draw_section_title(y, "핵심 성과 요약")
    y += 35

    card_w = (img_width - (margin * 2) - 30) // 3
    
    # 카드 1: 순위
    draw.rectangle([(margin, y), (margin + card_w, y + 95)], fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.text((margin + 15, y + 12), "플레이스 순위", font=small_font, fill=(100, 116, 139))
    rank_change_text = calculate_rank_diff(data['전월 순위'], data['당월 순위'])
    draw.text((margin + 15, y + 36), f"{data['전월 순위']} -> {data['당월 순위']}", font=header_font, fill=(2, 132, 199))
    
    # 상승 표기 배지
    p_nums = re.findall(r'\d+', str(data['전월 순위']))
    c_nums = re.findall(r'\d+', str(data['당월 순위']))
    if p_nums and c_nums and int(p_nums[0]) > int(c_nums[0]):
        diff_val = int(p_nums[0]) - int(c_nums[0])
        draw.text((margin + 15, y + 66), f"▲ {diff_val}계단 상승 완료", font=small_font, fill=(220, 38, 38))
    else:
        draw.text((margin + 15, y + 66), "안정적 순위 유지 중", font=small_font, fill=(71, 85, 105))

    # 카드 2: 방문자 리뷰
    c2_x = margin + card_w + 15
    draw.rectangle([(c2_x, y), (c2_x + card_w, y + 95)], fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.text((c2_x + 15, y + 12), "당월 방문자 리뷰", font=small_font, fill=(100, 116, 139))
    draw.text((c2_x + 15, y + 38), f"{data['방문자 리뷰 수']} 개", font=header_font, fill=(15, 23, 42))

    # 카드 3: 답글 수
    c3_x = c2_x + card_w + 15
    draw.rectangle([(c3_x, y), (c3_x + card_w, y + 95)], fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    draw.text((c3_x + 15, y + 12), "당월 답글 수", font=small_font, fill=(100, 116, 139))
    draw.text((c3_x + 15, y + 38), f"{data['답글 수']} 개", font=header_font, fill=(15, 23, 42))

    y += 125

    # 3. 대표키워드 현황
    draw_section_title(y, "대표키워드 세팅 및 관리")
    y += 35
    draw.rectangle([(margin, y), (img_width - margin, y + 60)], fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    kw_str = "   |   ".join(data['대표키워드']) if data['대표키워드'] else "설정된 대표키워드가 없습니다."
    draw.text((margin + 20, y + 20), kw_str, font=sub_bold_font, fill=(30, 41, 59))
    y += 90

    # 4. 월간 관리 보고 영역
    draw_section_title(y, "월간 관리 보고 및 세부 성과")
    y += 35
    
    report_lines = []
    for line in data['관리내용'].split('\n'):
        if line.strip():
            report_lines.extend(textwrap.wrap(line, width=54))
        
    card_h = max(130, len(report_lines) * 26 + 30)
    draw.rectangle([(margin, y), (img_width - margin, y + card_h)], fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    
    ry = y + 18
    for line in report_lines:
        draw.text((margin + 20, ry), line, font=body_font, fill=(51, 65, 85))
        ry += 26
        
    y += card_h + 30

    # 5. 체험단/기자단 배포 리스트
    draw_section_title(y, "체험단 / 기자단 배포 리스트")
    y += 35
    
    links = data['리뷰링크']
    link_card_h = max(80, len(links) * 25 + 25) if links else 65
    draw.rectangle([(margin, y), (img_width - margin, y + link_card_h)], fill=(255, 255, 255), outline=(226, 232, 240), width=1)
    
    ly = y + 16
    if links:
        for i, link in enumerate(links):
            link_display = link if len(link) < 68 else link[:65] + "..."
            draw.text((margin + 20, ly), f"{i+1}. {link_display}", font=body_font, fill=(2, 132, 199))
            ly += 25
    else:
        draw.text((margin + 20, ly), "등록된 리뷰 링크가 없습니다.", font=body_font, fill=(148, 163, 184))

    # 하단 푸터
    y = img_height - 45
    draw.line([(margin, y), (img_width - margin, y)], fill=(226, 232, 240), width=1)
    draw.text((margin, y + 12), "WithMember Marketing Automation System", font=small_font, fill=(148, 163, 184))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- [3] 결과 출력 및 카톡 발송 리포트 ---
if st.session_state.report_data:
    st.divider()
    st.subheader("📤 생성된 보고서 결과")
    
    for idx, data in enumerate(st.session_state.report_data):
        with st.container():
            col1, col2 = st.columns([1, 1.1])
            
            with col1:
                st.markdown(f"### 🖼️ [{data['매장명']}] 고급 이미지 보고서")
                img_bytes = create_professional_image(data)
                st.image(img_bytes, use_container_width=True)
                
                st.download_button(
                    label=f"📥 {data['매장명']} 보고서 다운로드 (PNG)",
                    data=img_bytes,
                    file_name=f"위드멤버_월간보고서_{data['매장명']}.png",
                    mime="image/png",
                    key=f"dl_btn_{idx}"
                )
                
            with col2:
                st.markdown(f"### 📱 [{data['매장명']}] 카톡 발송용 스마트 문구")
                st.caption("아래 텍스트를 복사해서 전송하시면 고객이 링크를 원클릭하여 바로 접속할 수 있습니다.")
                
                rank_diff_text = calculate_rank_diff(data['전월 순위'], data['당월 순위'])
                
                kakao_text = f"안녕하세요 대표님! 위드멤버입니다.\n[{data['매장명']}] 월간 마케팅 성과 보고서 전달드립니다.\n\n"
                kakao_text += f"📊 [핵심 성과 요약]\n"
                kakao_text += f"• 플레이스 순위: {rank_diff_text}\n"
                kakao_text += f"• 이번 달 방문자 리뷰: {data['방문자 리뷰 수']}개\n"
                kakao_text += f"• 답글 케어: {data['답글 수']}개\n\n"
                
                if data['대표키워드']:
                    kakao_text += f"📌 [대표키워드]: {', '.join(data['대표키워드'])}\n\n"
                    
                kakao_text += f"💡 [월간 관리 보고]\n{data['관리내용']}\n\n"
                
                if data['리뷰링크']:
                    kakao_text += "🔗 [체험단/기자단 리뷰 배포 링크]\n"
                    for i, link in enumerate(data['리뷰링크']):
                        kakao_text += f"{i+1}. {link}\n"
                
                kakao_text += "\n상세 보고서는 첨부해 드린 이미지를 확인해 주세요. 감사합니다!"

                st.text_area("카톡 전송용 텍스트 (Ctrl+A ➔ Ctrl+C)", value=kakao_text, height=330, key=f"kakao_txt_{idx}")
                
                if data['리뷰링크']:
                    st.markdown("#### 🔗 리뷰 바로가기 (클릭 테스트)")
                    for i, link in enumerate(data['리뷰링크']):
                        st.markdown(f"- [{i+1}번 리뷰 바로가기]({link})")

            st.markdown("---")

    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = []
        st.rerun()
