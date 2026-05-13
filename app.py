import os
import requests
import streamlit as st
from pathlib import Path

API_BASE_URL = os.environ.get("DSU_API_URL", "http://localhost:8000")
ASK_ENDPOINT = f"{API_BASE_URL}/api/ask"
API_TIMEOUT = 120   # 초 (LLM 추론 시간을 고려해 충분히 여유를 줍니다)

st.set_page_config(
    page_title="동서대학교 학칙 챗봇",
    page_icon="📘",
    layout="centered",
)

PAGE_IMAGE_DIR = Path("data/page_images")   # 프론트엔드 서버에 이미지가 없으면 표시 생략

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --dsu-red-dark: #C20324;
  --dsu-red: #A32D2D;
  --dsu-red-light: #C0392B;
  --bg: #F7F4F4;
  --surface: #FFFFFF;
  --border: #E8DEDE;
  --text-primary: #1A1A1A;
  --text-secondary: #4A4040;
  --text-muted: #9A8A8A;
  --shadow-card: 0 2px 12px rgba(123,28,28,0.08);
  --shadow-hover: 0 6px 24px rgba(123,28,28,0.14);
  --radius: 16px;
}

html, body, [class*="css"] {
  font-family: 'Noto Sans KR', sans-serif !important;
  background: var(--bg) !important;
}

.block-container {
  max-width: 860px !important;
  padding-top: 60px !important;
  padding-bottom: 120px !important;
}

/* 헤더 */
.dsu-header {
  background: var(--dsu-red-dark);
  border-radius: 0 0 20px 20px;
  padding: 10px 20px;
  margin-bottom: 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 16px rgba(123,28,28,0.22);
}
.dsu-header-left { display: flex; align-items: center; gap: 14px; }
.dsu-logo-icon {
  width: 42px; height: 42px;
  background: white;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}
.dsu-logo-title { color: white; font-size: 1.1rem; font-weight: 800; letter-spacing: -0.3px; }
.dsu-logo-sub { color: rgba(255,255,255,0.6); font-size: 0.72rem; font-weight: 400; margin-top: 2px; }
.dsu-header-badge {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.22);
  color: rgba(255,255,255,0.88);
  padding: 5px 13px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* 날짜 구분선 */
.dsu-divider {
  display: flex; align-items: center; gap: 10px;
  color: var(--text-muted); font-size: 0.75rem;
  margin: 16px 0;
}
.dsu-divider::before, .dsu-divider::after {
  content: ''; flex: 1; height: 1px; background: var(--border);
}

/* 섹션 레이블 */
.dsu-section-label {
  font-size: 0.75rem; font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 1px;
  margin: 20px 0 10px 0;
}

/* 자주 묻는 질문 버튼 */
.stButton > button {
  background: white !important;
  border: 1.5px solid var(--border) !important;
  color: var(--dsu-red) !important;
  border-radius: 999px !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  font-family: 'Noto Sans KR', sans-serif !important;
  padding: 8px 16px !important;
  transition: all 0.18s ease !important;
  box-shadow: none !important;
}
.stButton > button:hover {
  background: var(--dsu-red-dark) !important;
  color: white !important;
  border-color: var(--dsu-red-dark) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(123,28,28,0.2) !important;
}

/* 사용자 말풍선 */
.user-row { display: flex; justify-content: flex-end; align-items: flex-end; gap: 10px; margin: 12px 0 8px; }
.user-avatar {
  width: 30px; height: 30px; background: var(--dsu-red);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  color: white; font-size: 13px; flex-shrink: 0;
}
.user-bubble {
  max-width: 68%;
  background: var(--dsu-red-dark);
  color: white; padding: 13px 18px;
  border-radius: 18px 18px 4px 18px;
  font-size: 0.93rem; font-weight: 500; line-height: 1.65;
  box-shadow: 0 4px 16px rgba(123,28,28,0.22);
  word-break: keep-all;
}

/* 봇 말풍선 */
.bot-row { display: flex; justify-content: flex-start; align-items: flex-end; gap: 10px; margin: 8px 0 12px; }
.bot-avatar {
  width: 30px; height: 30px; background: var(--dsu-red-dark);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  color: white; font-size: 13px; flex-shrink: 0;
}
.bot-bubble {
  max-width: 80%;
  background: var(--surface); color: var(--text-primary);
  padding: 15px 20px;
  border-radius: 18px 18px 18px 4px;
  font-size: 0.93rem; line-height: 1.8;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--border);
  word-break: keep-all;
}

/* 키워드 뱃지 */
.kw-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; margin-left: 40px; }
.kw-badge {
  background: #FCEBEB; color: #791F1F;
  border: 1px solid #F7C1C1;
  padding: 4px 10px; border-radius: 999px;
  font-size: 0.78rem; font-weight: 600;
}

/* 근거 문서 expander */
.stExpander {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow-card) !important;
  margin-bottom: 8px !important;
  overflow: hidden !important;
}
.stExpander:hover { box-shadow: var(--shadow-hover) !important; }
.stExpander > div:first-child { padding: 13px 16px !important; }
.stExpander summary {
  font-size: 0.88rem !important;
  font-weight: 600 !important;
  color: var(--text-primary) !important;
}

/* 근거 번호 뱃지 */
.src-header { display: flex; align-items: center; gap: 10px; }
.src-num {
  width: 22px; height: 22px; background: var(--dsu-red-dark);
  color: white; border-radius: 6px;
  font-size: 0.72rem; font-weight: 700;
  display: inline-flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.src-tag {
  background: #FCEBEB; color: #791F1F;
  border: 1px solid #F7C1C1;
  padding: 2px 8px; border-radius: 6px;
  font-size: 0.72rem; font-weight: 600;
}
.src-appendix-tag {
  background: #FFF7ED; color: #C2410C;
  border: 1px solid #FED7AA;
  padding: 2px 8px; border-radius: 6px;
  font-size: 0.72rem; font-weight: 600;
}
.evidence-img-note {
  color: var(--dsu-red); font-size: 0.85rem; font-weight: 600;
  margin-bottom: 8px; padding: 8px 12px;
  background: #FCEBEB; border-radius: 8px;
  border-left: 3px solid var(--dsu-red);
}

/* st.chat_input 스타일 */
[data-testid="stChatInput"] {
  border-radius: 999px !important;
  border: 1.5px solid var(--border) !important;
  font-family: 'Noto Sans KR', sans-serif !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--dsu-red) !important;
  box-shadow: 0 0 0 3px rgba(163,45,45,0.1) !important;
}
[data-testid="stChatInputSubmitButton"] > button {
  background: var(--dsu-red-dark) !important;
  border-radius: 999px !important;
}
</style>
""", unsafe_allow_html=True)


# ── 세션 상태 초기화 ──
for key in ["pending_query", "chat_history", "last_sources", "last_keywords"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key == "pending_query" else []


# ── 유틸 함수 ──
def get_page_image_path(page, source_pdf):
    """로컬 이미지 파일이 존재할 때만 경로를 반환합니다."""
    if not page or not source_pdf:
        return None
    try:
        page_num = int(page)
    except (ValueError, TypeError):
        return None
    image_path = PAGE_IMAGE_DIR / source_pdf / f"page_{page_num}.png"
    return image_path if image_path.exists() else None


def should_show_image_first(item: dict) -> bool:
    section_type = item.get("section_type", "")
    title = item.get("title", "") or ""
    content = item.get("content", "") or ""
    appendix_like = section_type == "appendix"
    form_like = any(kw in title for kw in ["별지", "서식", "수료증"])
    table_like = any(kw in title for kw in ["입학정원표", "학위수여표", "별표", "[별표]"])
    content_hint = any(kw in content for kw in ["입학정원", "모집단위", "학위명"])
    return appendix_like or form_like or table_like or content_hint


def get_section_tag(item: dict) -> str:
    section_type = item.get("section_type", "")
    if section_type == "appendix":
        return '<span class="src-appendix-tag">부록/서식</span>'
    elif section_type == "addendum":
        return '<span class="src-tag">부칙</span>'
    return '<span class="src-tag">조문</span>'


def call_api(query: str, top_k: int = 5) -> dict:
    """
    백엔드 API를 호출하고 파싱된 응답 dict를 반환합니다.
    오류 발생 시 예외를 raise합니다.
    """
    payload = {"query": query, "top_k": top_k}
    response = requests.post(ASK_ENDPOINT, json=payload, timeout=API_TIMEOUT)
    response.raise_for_status()     # 4xx / 5xx → HTTPError 발생
    return response.json()


def run_query(query: str):
    """API를 호출하고 세션 상태를 업데이트합니다."""
    with st.spinner("AI가 학칙을 분석하고 있습니다... (수 초~수십 초 소요)"):
        try:
            data = call_api(query)
        except requests.exceptions.ConnectionError:
            st.error(
                f"❌ **API 서버에 연결할 수 없습니다.**\n\n"
                f"로컬 PC에서 `api_server.py`가 실행 중인지, "
                f"그리고 주소(`{API_BASE_URL}`)가 올바른지 확인해 주세요."
            )
            return
        except requests.exceptions.Timeout:
            st.error(
                "⏱️ **요청 시간이 초과되었습니다.**\n\n"
                "LLM 추론이 길어지고 있습니다. 잠시 후 다시 시도해 주세요."
            )
            return
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            detail = ""
            try:
                detail = e.response.json().get("detail", "")
            except Exception:
                pass
            st.error(f"🚨 **서버 오류 ({status})**\n\n{detail or str(e)}")
            return
        except Exception as e:
            st.error(f"🚨 **예기치 못한 오류가 발생했습니다.**\n\n{e}")
            return

    # 세션 상태 업데이트
    st.session_state.chat_history.append({
        "question": query,
        "answer": data.get("answer", "(답변 없음)"),
    })
    st.session_state.last_sources = data.get("sources", [])
    st.session_state.last_keywords = data.get("keywords", [])


# ── 헤더 ──
st.markdown("""
<div class="dsu-header">
  <div class="dsu-header-left">
    <div class="dsu-logo-icon">📘</div>
    <div>
      <div class="dsu-logo-title">동서대학교 학칙 챗봇</div>
      <div class="dsu-logo-sub">Dongseo University Rule Assistant</div>
    </div>
  </div>
  <span class="dsu-header-badge">AI 답변 서비스</span>
</div>
""", unsafe_allow_html=True)

# ── 자주 묻는 질문 ──
st.markdown('<div class="dsu-section-label">자주 묻는 질문</div>', unsafe_allow_html=True)
q_list = [
    ("🎓 휴학",     "휴학은 몇 학기까지 가능한가요?"),
    ("📚 전공선택", "전공 선택 시기는 언제인가요?"),
    ("👥 교원양성", "교원양성 위원회 구성은?"),
    ("📄 연구서류", "연구 제출서류 안내"),
]
cols = st.columns(4)
for i, (btn_label, q_text) in enumerate(q_list):
    if cols[i].button(btn_label, use_container_width=True):
        st.session_state.pending_query = q_text
        st.rerun()

# ── 자주 묻는 질문 버튼으로 들어온 쿼리 처리 ──
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = ""
    run_query(query)

# ── 대화 내용 ──
if st.session_state.chat_history:
    st.markdown('<div class="dsu-divider">대화</div>', unsafe_allow_html=True)
    current = st.session_state.chat_history[-1]

    st.markdown(f"""
    <div class="user-row">
      <div class="user-bubble">{current["question"]}</div>
      <div class="user-avatar">👤</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="bot-row">
      <div class="bot-avatar">🎓</div>
      <div class="bot-bubble">{current["answer"].replace(chr(10), "<br>")}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.last_keywords:
        badges = "".join(
            [f'<span class="kw-badge"># {kw}</span>' for kw in st.session_state.last_keywords]
        )
        st.markdown(f'<div class="kw-wrap">{badges}</div>', unsafe_allow_html=True)

# ── 근거 문서 ──
if st.session_state.last_sources:
    st.markdown('<div class="dsu-section-label">근거 문서</div>', unsafe_allow_html=True)
    for idx, item in enumerate(st.session_state.last_sources, start=1):
        page       = item.get("page", "")
        source_pdf = item.get("source_pdf", "")
        title      = item.get("title", "")
        article_no = item.get("article_no") or "-"
        context_title = item.get("context_title", "")

        label = (
            f"{idx}. {article_no} | {title}"
            + (f" · 📁 {source_pdf}" if source_pdf else "")
            + (f" · 📁 {context_title}" if context_title else "")
        )

        with st.expander(label):
            image_path  = get_page_image_path(page, source_pdf)
            image_first = should_show_image_first(item)
            content     = item.get("content", "") or ""

            if image_path:
                if image_first:
                    st.markdown(
                        '<div class="evidence-img-note">💡 표/서식 형태의 내용이므로 원본 이미지를 먼저 표시합니다.</div>',
                        unsafe_allow_html=True,
                    )
                    st.image(str(image_path), caption=f"원본 페이지 ({source_pdf}, {page}p)", use_column_width=True)
                    if st.checkbox("텍스트로 내용 확인", key=f"txt_{idx}"):
                        st.markdown(content, unsafe_allow_html=True)
                else:
                    st.markdown(content, unsafe_allow_html=True)
                    with st.expander("📄 원본 페이지 이미지 보기"):
                        st.image(str(image_path), use_column_width=True)
            else:
                st.markdown(content, unsafe_allow_html=True)

# ── 하단 고정 입력창 ──
user_query = st.chat_input("메시지를 입력하세요…")
if user_query and user_query.strip():
    run_query(user_query)
    st.rerun()