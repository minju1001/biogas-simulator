import streamlit as st

# 대표값 예시
def get_cn_and_ph(material):
    cn_map = {
        "음식물 폐기물": 14.81,
        "하수슬러지": 6.1,
        "돈분": 16.0,
        "우분": 20.0
    }
    ph_map = {
        "음식물 폐기물": 4.2,
        "하수슬러지": 7.63,
        "돈분": 7.25,
        "우분": 7.25
    }
    return cn_map[material], ph_map[material]

st.markdown("<h2 style='font-size:1.4em;'>바이오가스화 최적혼합비율 설계 시뮬레이터</h2>", unsafe_allow_html=True)

# 도/시군 선택
do_options = [
    "서울특별시", "부산광역시", "인천광역시", "대구광역시", "대전광역시", "광주광역시",
    "울산광역시", "세종특별자치시", "경기도", "충청북도", "충청남도", "전라남도",
    "경상북도", "경상남도", "강원특별자치도", "전북특별자치도", "제주특별자치도"
]
si_gun_options = [
    "춘천시", "청주시", "천안시", "전주시", "목포시", "수원시", "성남시", "제주시",
    "서귀포시", "부산진구", "동래구", "중구", "의정부시", "포항시", "안동시",
    "광주시", "강릉시", "원주시", "군산시", "여수시", "순천시", "김해시"
]

do = st.selectbox("1차: 도 단위 선택 (필수)", do_options)
si_gun = st.selectbox("2차: 시/군 단위 선택 (선택)", ["(선택 안 함)"] + si_gun_options)

season = st.selectbox("계절 선택", ["봄", "여름", "가을", "겨울"])
materials = st.multiselect("혼합 기질 선택", ["음식물 폐기물", "하수슬러지", "돈분", "우분"])
custom_ratio = st.text_input("혼합 비율 입력 (예: 음식물 60, 슬러지 40) / 미입력 시 자동 계산")

if st.button("시뮬레이션 실행"):
    st.subheader("혼합 비율 및 결과 예측")
    if len(materials) < 2:
        st.warning("기질을 최소 2개 이상 선택해주세요!")
    else:
        if custom_ratio:
            try:
                parts = [float(x.strip()) for x in custom_ratio.split(",")]
                if len(parts) != len(materials):
                    st.error("혼합비 개수가 기질 수와 맞지 않습니다!")
                    parts = None
                else:
                    total = sum(parts)
                    ratios = [x / total for x in parts]
            except:
                st.error("혼합비 입력 형식 오류. 예: 60, 40")
                ratios = None
        else:
            # 자동 혼합비 계산 - C/N = 22, pH = 7 기준으로 가중치 조절
            cn_targets = [get_cn_and_ph(m)[0] for m in materials]
            ph_targets = [get_cn_and_ph(m)[1] for m in materials]
            weights = [1 / (abs(22 - cn) + abs(7 - ph)) for cn, ph in zip(cn_targets, ph_targets)]
            total = sum(weights)
            ratios = [w / total for w in weights]
            st.info("혼합비 미입력: 자동 제안 혼합비 적용")
            st.write("**제안 혼합비:**")
            for i in range(len(materials)):
                st.write(f"{materials[i]}: {ratios[i]*100:.1f}%")

        if ratios:
            mix_cn = sum([ratios[i] * get_cn_and_ph(materials[i])[0] for i in range(len(materials))])
            mix_pH = sum([ratios[i] * get_cn_and_ph(materials[i])[1] for i in range(len(materials))])

            st.write(f"\n**혼합 C/N 비율:** {mix_cn:.2f}")
            st.write(f"**혼합 pH:** {mix_pH:.2f}")

            if custom_ratio:
                if mix_cn < 15:
                    st.warning(f"C/N 비가 낮습니다 → 탄소원 보완 필요 (예: 곡류류). 목표: 20~25")
                elif mix_cn > 30:
                    st.warning(f"C/N 비가 높습니다 → 질소원 보완 필요 (예: 슬러지). 목표: 20~25")
                else:
                    st.success("C/N 비 적정 범위입니다 (15~30)")

                if mix_pH < 6.5:
                    st.warning(f"pH가 낮습니다 → 알칼리성 기질 추가 필요 (예: 슬러지). 목표 pH: 6.5~8.5")
                elif mix_pH > 8.5:
                    st.warning(f"pH가 높습니다 → 산성 보조기질 필요. 목표 pH: 6.5~8.5")
                else:
                    st.success("pH 안정 범위입니다 (6.5~8.5)")
            else:
                st.success("자동 제안 혼합비로 안정 조건 충족 ✔\n(C/N ≒ 22, pH ≒ 7)")
