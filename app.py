import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="위드멤버 월간 마케팅 보고서", page_icon="📊", layout="wide"
)

st.title("📊 위드멤버 월간 마케팅 성과 보고서 생성기")
st.markdown(
    "매장별 마케팅 데이터를 입력하고 월간 보고서 내용을 간편하게 확인 및 저장하세요."
)

# 세션 스테이트 초기화 (데이터 임시 저장용)
if "report_data" not in st.session_state:
    st.session_state.report_data = pd.DataFrame(
        columns=[
            "매장명",
            "전월 순위",
            "당월 순위",
            "방문자 리뷰 수",
            "답글 수",
            "수정된 대표키워드",
            "체험단 리뷰 수",
            "기자단 리뷰 수",
            "비고",
        ]
    )

# --- [1] 데이터 입력 폼 ---
with st.form("report_form"):
    st.subheader("📝 마케팅 성과 데이터 입력")

    col1, col2 = st.columns(2)

    with col1:
        store_name = st.text_input("매장명", placeholder="예: 강남 맛집")
        prev_rank = st.text_input("전월 플레이스 순위", placeholder="예: 15위")
        current_rank = st.text_input("당월 플레이스 순위", placeholder="예: 3위")
        visitor_review = st.number_input(
            "이번 달 방문자 리뷰 수", min_value=0, step=1
        )
        reply_count = st.number_input("답글 수", min_value=0, step=1)

    with col2:
        target_keyword = st.text_input(
            "대표키워드 수정 / 추가", placeholder="예: 강남역 맛집, 강남 고기집"
        )
        experience_group = st.number_input(
            "체험단 리뷰 입력", min_value=0, step=1
        )
        journalist_group = st.number_input(
            "기자단 리뷰 입력", min_value=0, step=1
        )
        memo = st.text_area("특이사항 및 비고", placeholder="추가 전달 사항 등")

    submitted = st.form_submit_button("➕ 보고서 항목 추가")

    if submitted:
        if store_name:
            new_data = {
                "매장명": store_name,
                "전월 순위": prev_rank,
                "당월 순위": current_rank,
                "방문자 리뷰 수": visitor_review,
                "답글 수": reply_count,
                "수정된 대표키워드": target_keyword,
                "체험단 리뷰 수": experience_group,
                "기자단 리뷰 수": journalist_group,
                "비고": memo,
            }
            # 데이터프레임에 추가
            st.session_state.report_data = pd.concat(
                [
                    st.session_state.report_data,
                    pd.DataFrame([new_data]),
                ],
                ignore_index=True,
            )
            st.success(f"[{store_name}] 데이터가 성공적으로 추가되었습니다!")
        else:
            st.error("매장명은 필수 입력 사항입니다.")

# --- [2] 입력된 데이터 리스트 확인 및 편집 ---
if not st.session_state.report_data.empty:
    st.divider()
    st.subheader("📋 입력된 월간 보고서 데이터 목록")

    # 데이터 수정 기능 제공
    edited_df = st.data_editor(
        st.session_state.report_data, num_rows="dynamic", use_container_width=True
    )
    st.session_state.report_data = edited_df

    # 데이터 초기화 버튼
    if st.button("🗑️ 전체 데이터 초기화"):
        st.session_state.report_data = pd.DataFrame(columns=st.session_state.report_data.columns)
        st.rerun()

    # --- [3] 파일 다운로드 (Excel / CSV) ---
    st.divider()
    st.subheader("📥 보고서 파일 다운로드")

    # CSV 변환 함수
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8-sig")  # 한글 깨짐 방지 utf-8-sig

    csv_data = convert_df_to_csv(st.session_state.report_data)

    st.download_button(
        label="📄 CSV 파일로 다운로드",
        data=csv_data,
        file_name="monthly_marketing_report.csv",
        mime="text/csv",
    )
else:
    st.info("아직 입력된 데이터가 없습니다. 위의 폼을 이용해 데이터를 추가해 주세요.")