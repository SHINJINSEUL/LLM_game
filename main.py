import streamlit as st
import ollama
import random
import json

# --- 분야별 인물 후보 리스트 ---
CATEGORIES = {
    "아이돌": [
        "정국", "뷔", "지민", "RM", "진", "제이홉", "리사", "제니", "지수", "로제",
        "장원영", "안유진", "리즈", "이서", "가을", "유진", "유나", "예지", "리아", "류진",
        "채령", "카리나", "윈터", "닝닝", "지젤"
    ],
    "스포츠 선수": [
        "손흥민", "김연아", "이강인", "황선우", "류현진", "김민재", "박지성", "차범근", "윤성빈", "우상혁",
        "이승우", "정현", "서채현", "양학선", "최민정", "심석희", "황대헌", "조구함", "김소희", "오상욱",
        "김지연", "김우진", "안산", "장미란", "이용대"
    ],
    "방송인/배우": [
        "송강", "이정재", "유재석", "강호동", "박보검", "박서준", "정해인", "임시완", "전도연", "김혜수",
        "한지민", "이병헌", "남궁민", "조승우", "김태리", "신하균", "한석규", "서인국", "김선호", "정소민",
        "고아성", "이하늬", "공효진", "정유미", "박은빈"
    ],
    "애니/영화 캐릭터": [
        "엘사", "안나", "올라프", "피카츄", "도라에몽", "짱구", "이누야샤", "가오나시", "뽀로로", "헬로키티",
        "마리오", "루이지", "해리 포터", "스파이더맨", "아이언맨", "캡틴 아메리카", "토르", "배트맨",
        "슈퍼맨", "조커", "셜록 홈즈", "엘리자베스 여왕", "아인슈타인", "나루토", "사스케"
    ]
}

# --- 설명 JSON 불러오기 ---
with open("/workspace/LLM_game/data/full_100_descriptions.json", "r", encoding="utf-8") as f:
    DESCRIPTIONS = json.load(f)

# --- Streamlit 설정 ---
st.set_page_config(page_title="정체를 밝혀라!", page_icon="🕵️")
st.title("🕵️ 정체를 밝혀라! - AI 힌트 추리 게임")

# --- 세션 초기화 ---
if "character" not in st.session_state:
    st.session_state.category = st.selectbox("🎯 인물 분야를 선택하세요:", list(CATEGORIES.keys()))
    st.session_state.character = random.choice(CATEGORIES[st.session_state.category])
    st.session_state.character_name = st.session_state.character
    st.session_state.chat = []
    st.session_state.question_count = 0
    st.session_state.solved = False

    description_text = DESCRIPTIONS.get(st.session_state.character_name, "이 인물에 대한 설명은 없습니다.")

    st.session_state.system_prompt = f"""
    너는 지금 인물 추리 게임에 참여 중이야. 그리고 너는 지금부터 선택된 인물이 되어 플레이어의 질문에 직접 대답해야 해.

    🎭 역할:
    - 너는 이제 '{st.session_state.character_name}'이야.
    - {st.session_state.character_name}에 대한 정보는 다음과 같아:
      {description_text}

    🧠 게임 규칙:
    - 플레이어는 너에게 질문을 던지고, 너는 그 질문에 인물 입장에서 대답해야 해.
    - 다만, 너의 실명을 먼저 밝히거나 누군지 직접적으로 언급해서는 안 돼.
    - 질문이 "너 OOO이야?" 라는 식으로 정답을 시도하는 경우에는:
        - 정확히 이름이 일치하면 "정답이야!"
        - 틀리면 "아니야!" 라고만 말해.

    🙅‍♀️ 주의사항:
    - 설명 속 정보(소속, 활동, 특징, 유행어 등)를 자연스럽게 반영해.
    - 대답은 너무 길지 않게, 딱 핵심적인 힌트가 되도록 구성해.
    - 질문이 엉뚱하거나 잘못된 경우, 부드럽게 회피하거나 다른 방향으로 유도하지 말고 "질문과 관련된 내용으로 다시 물어봐 주세요."라고만 답변해.
    - 질문에 대한 답은 명확하고 단정적인 문장으로 대답하고, 그에 이어 JSON 설명 기반 힌트를 한 문장 추가해. 예: "네, 맞습니다. 저는 무대 위에서 에너지가 넘치는 퍼포먼스를 보여주는 것으로 유명하죠."

    - 너는 자연스럽고 친근한 말투를 사용해. 너무 딱딱하거나 기계적인 말투는 피하고, 마치 실제 인물처럼 말해.
    - 이전에 플레이어가 했던 질문과 힌트를 기억하고, 겹치거나 반복되는 질문에는 “그건 이미 말씀드렸어요”처럼 응답해.
    - 너는 선택된 인물의 분야(아이돌, 스포츠 선수 등)에 대해서만 대답하고, 그 외 분야에 대해서는 “그건 제 분야가 아니에요”라고 말해.

    - 이름의 일부라도 직접 언급하지 마. 이름을 유추할 수 있는 어떤 단어도 포함하지 마.
    - 정답을 유추할 수 있을 만큼 명확한 표현(예: 대표작 제목 전체, 그룹명 전체)은 피하고, 항상 간접적으로 표현해.
    - 어떤 경우에도 먼저 정답을 말하지 마. 오직 플레이어가 추측했을 때만 "정답이야!" 또는 "아니야!"로 대답해.

    자, 이제부터 너는 완전히 '{st.session_state.character_name}'가 되어 플레이어의 질문에 대답해!
    """

# --- Ollama 대화 함수 ---
def ask_eeve(user_prompt, system_prompt):
    response = ollama.chat(
        model="EEVE-Korean-10.8B",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response['message']['content']

st.markdown("AI가 한 인물을 정했어요. 질문을 통해 10번 안에 정체를 맞혀보세요!")

# --- 이전 대화 표시 ---
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 남은 질문 수 표시 ---
st.info(f"🧠 남은 질문 수: {10 - st.session_state.question_count} / 10")

# --- 채팅 입력 ---
if not st.session_state.solved and st.session_state.question_count < 10:
    user_input = st.chat_input("질문해보세요! 예: '사람이야?' 또는 '너 정국이야?'")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat.append({"role": "user", "content": user_input})
        st.session_state.question_count += 1

        input_clean = user_input.replace(" ", "").lower()
        name_clean = st.session_state.character_name.replace(" ", "").lower()

        is_guess_format = user_input.strip().startswith("너") and user_input.strip().endswith("야?")
        is_exact_match = name_clean in input_clean

        if is_guess_format and is_exact_match:
            st.session_state.solved = True
            st.balloons()
            st.success(f"🎉 정답! AI가 정한 인물은 **{st.session_state.character_name}**였어요!")
        elif is_guess_format:
            with st.chat_message("assistant"):
                st.markdown("아니야!")
            st.session_state.chat.append({"role": "assistant", "content": "아니야!"})
        else:
            response = ask_eeve(user_input, st.session_state.system_prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.chat.append({"role": "assistant", "content": response})

# --- 실패 시 정답 공개 ---
if not st.session_state.solved and st.session_state.question_count >= 10:
    st.session_state.solved = True
    st.error(f"❌ 10번 안에 못 맞췄어요! 정답은 **{st.session_state.character_name}**였습니다!")
