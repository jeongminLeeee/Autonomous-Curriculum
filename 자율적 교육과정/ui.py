# ============================================================
# ui.py
#
# 재난 의료시설 최적화 시뮬레이션 UI
#
# Part 1 / 4
# ------------------------------------------------------------
# - Streamlit 기본 설정
# - 데이터 생성
# - 지도 및 재난 초기화
# - 병원 생성
# - p-Median 실행
# - Simulation 생성
# ============================================================


import streamlit as st
import random


# ------------------------------------------------------------
# 프로젝트 모듈
# ------------------------------------------------------------

from map_loader import MapLoader

from disaster import Disaster

from hospital import Hospital

from pmedian import solve_pmedian

from simulation import Simulation



# ============================================================
# Streamlit 설정
# ============================================================

st.set_page_config(

    page_title="재난 의료시설 최적화 시뮬레이션",

    layout="wide"

)



# ============================================================
# 제목
# ============================================================


st.title(
    "🚑 재난 의료시설 최적화 시뮬레이션"
)


st.markdown(
    """
    OpenStreetMap 기반 달서구 재난 상황에서
    
    p-Median 알고리즘을 이용하여 의료시설을 배치하고
    
    환자의 이동·대기·치료 과정을 시뮬레이션합니다.
    """
)



# ============================================================
# Sidebar
# ============================================================


st.sidebar.header(
    "⚙️ 시뮬레이션 설정"
)



# 환자 수

patient_count = st.sidebar.number_input(

    "환자 수",

    min_value=10,

    max_value=2000,

    value=200,

    step=10

)



# 후보 병원 수

candidate_count = st.sidebar.number_input(

    "후보 의료시설 수",

    min_value=2,

    max_value=50,

    value=15,

    step=1

)



# 선택 병원 수

selected_count = st.sidebar.number_input(

    "최종 선택 의료시설 수 (p)",

    min_value=1,

    max_value=20,

    value=5,

    step=1

)



# 시뮬레이션 시간

simulation_time = st.sidebar.number_input(

    "시뮬레이션 시간(초)",

    min_value=60,

    max_value=7200,

    value=3600,

    step=60

)



# 랜덤 seed

seed = st.sidebar.number_input(

    "Random Seed",

    value=42

)



# ============================================================
# Session State 초기화
# ============================================================


if "simulation" not in st.session_state:

    st.session_state.simulation = None


if "map_loader" not in st.session_state:

    st.session_state.map_loader = None


if "selected_hospitals" not in st.session_state:

    st.session_state.selected_hospitals = None


if "disaster" not in st.session_state:

    st.session_state.disaster = None



# ============================================================
# 시뮬레이션 생성 함수
# ============================================================


def create_simulation():


    random.seed(seed)



    # --------------------------------------------------------
    # 1. 지도 생성
    # --------------------------------------------------------

    loader = MapLoader()


    loader.load_map()



    # --------------------------------------------------------
    # 2. 재난 생성
    # --------------------------------------------------------

    disaster = Disaster(

        width=1000,

        height=1000,

        zone_count=3,

        seed=seed

    )



    # --------------------------------------------------------
    # 3. 환자 생성
    # --------------------------------------------------------

    patients = disaster.generate_patients(

        patient_count

    )



    # --------------------------------------------------------
    # 4. 후보 병원 생성
    #
    # 현재는 랜덤 생성
    # 추후 map_loader 기반 도로 노드로 개선 가능
    # --------------------------------------------------------


    candidates = []


    for i in range(candidate_count):


        x, y = loader.get_random_point()



        hospital = Hospital(

            hospital_id=i+1,

            x=x,

            y=y,

            capacity=5,

            max_queue=50

        )


        candidates.append(

            hospital

        )



    # --------------------------------------------------------
    # 5. p-Median 실행
    # --------------------------------------------------------


    selected = solve_pmedian(

        patients,

        candidates,

        selected_count

    )



    # --------------------------------------------------------
    # 6. Simulation 생성
    # --------------------------------------------------------


    sim = Simulation(

        patients,

        selected,

        duration=simulation_time,

        dt=1

    )



    return (

        loader,

        disaster,

        selected,

        sim

    )





# ============================================================
# 실행 버튼
# ============================================================


if st.sidebar.button(
    "🚀 시뮬레이션 준비"
):


    with st.spinner(
        "재난 환경 및 의료시설 배치 생성 중..."
    ):


        (

            loader,

            disaster,

            hospitals,

            simulation

        ) = create_simulation()



        st.session_state.map_loader = loader

        st.session_state.disaster = disaster

        st.session_state.selected_hospitals = hospitals

        st.session_state.simulation = simulation



    st.success(
        "시뮬레이션 준비 완료!"
    )



# ============================================================
# 현재 상태 확인
# ============================================================


if st.session_state.simulation is not None:


    st.info(
        "시뮬레이션 객체가 생성되었습니다. 다음 단계에서 지도와 결과 화면을 추가합니다."
    )



# ============================================================
# Part 2 / 4 시작
# ============================================================
# ============================================================
# Part 2 / 4
# ------------------------------------------------------------
# - Folium 지도 생성
# - OpenStreetMap 표시
# - 위험지역 표시
# - 환자 표시
# - 병원 표시
# ============================================================


import folium

from streamlit_folium import st_folium

from patient import Severity, PatientState



# ============================================================
# 지도 생성 함수
# ============================================================


def create_map():


    loader = st.session_state.map_loader

    disaster = st.session_state.disaster

    hospitals = st.session_state.selected_hospitals

    simulation = st.session_state.simulation



    if loader is None:

        return None



    # --------------------------------------------------------
    # 지도 중심 계산
    # --------------------------------------------------------


    boundary = loader.get_boundary()



    center_lat = (

        boundary["north"]

        +

        boundary["south"]

    ) / 2



    center_lon = (

        boundary["east"]

        +

        boundary["west"]

    ) / 2



    # --------------------------------------------------------
    # 기본 지도
    # --------------------------------------------------------


    m = folium.Map(

        location=[

            center_lat,

            center_lon

        ],

        zoom_start=13,

        tiles="OpenStreetMap"

    )



    # ========================================================
    # 위험지역 표시
    # ========================================================


    for zone in disaster.hazard_zones:


        folium.Circle(

            location=[

                zone.y,

                zone.x

            ],

            radius=zone.radius,

            color="red",

            fill=True,

            fill_opacity=0.2,

            popup=(

                f"위험지역 {zone.id}"

            )

        ).add_to(m)




    # ========================================================
    # 병원 표시
    # ========================================================


    for hospital in hospitals:


        congestion = hospital.congestion_ratio()



        if congestion >= 0.8:

            color = "red"


        elif congestion >= 0.5:

            color = "orange"


        else:

            color = "green"



        folium.Marker(

            location=[

                hospital.y,

                hospital.x

            ],


            popup=folium.Popup(

                f"""

                <b>Hospital {hospital.id}</b><br>

                치료중 :
                {hospital.treating_count()}명<br>

                대기 :
                {hospital.waiting_count()}명<br>

                병목률 :
                {congestion*100:.1f}%

                """,

                max_width=300

            ),


            icon=folium.Icon(

                color=color,

                icon="plus-sign"

            )


        ).add_to(m)





    # ========================================================
    # 환자 표시
    # ========================================================


    for patient in simulation.patients:



        # 위급도 색상


        if patient.severity == Severity.RED:

            color = "red"


        elif patient.severity == Severity.YELLOW:

            color = "orange"


        else:

            color = "green"




        # 상태별 투명도


        opacity = 1



        if patient.state == PatientState.FINISHED:

            opacity = 0.3



        elif patient.state == PatientState.DEAD:

            opacity = 0.5




        folium.CircleMarker(

            location=[

                patient.y,

                patient.x

            ],


            radius=4,


            color=color,


            fill=True,


            fill_opacity=opacity,


            popup=(

                f"""

                환자 ID : {patient.id}<br>

                위급도 :
                {patient.severity.value}<br>

                상태 :
                {patient.state.value}

                """

            )

        ).add_to(m)




    return m





# ============================================================
# 지도 출력
# ============================================================


if st.session_state.simulation is not None:


    st.subheader(
        "🗺️ 재난 상황 지도"
    )


    disaster_map = create_map()


    if disaster_map is not None:


        st_folium(

            disaster_map,

            width=1200,

            height=700

        )



# ============================================================
# Part 3 / 4 시작
# ============================================================
# ============================================================
# Part 3 / 4
# ------------------------------------------------------------
# - 시뮬레이션 실행
# - 현재 상태 Dashboard
# - 환자 상태 통계
# - 병원 상태 표시
# ============================================================


from patient import PatientState



# ============================================================
# 시뮬레이션 실행 함수
# ============================================================


def run_simulation():


    simulation = st.session_state.simulation


    if simulation is None:

        return



    progress = st.progress(0)


    status_text = st.empty()



    total_time = simulation.duration



    simulation.initialize()



    while not simulation.is_finished():


        simulation.step()



        progress.progress(

            min(

                simulation.current_time
                /
                total_time,

                1.0

            )

        )


        status_text.text(

            f"시뮬레이션 진행 중... "
            f"{simulation.current_time:.0f}s / "
            f"{total_time}s"

        )



    progress.progress(1.0)


    status_text.text(

        "시뮬레이션 완료!"

    )



    return simulation.get_result()





# ============================================================
# 실행 버튼
# ============================================================


if st.session_state.simulation is not None:


    st.divider()



    st.subheader(
        "🚀 시뮬레이션 실행"
    )


    if st.button(
        "▶ 재난 시뮬레이션 시작"
    ):


        with st.spinner(

            "환자 이동 및 병원 처리가 진행 중입니다..."

        ):


            result = run_simulation()



            st.session_state.result = result



        st.success(

            "시뮬레이션 완료"

        )





# ============================================================
# Dashboard
# ============================================================


if (

    "result" in st.session_state

    and

    st.session_state.result is not None

):


    simulation = st.session_state.simulation



    st.divider()


    st.subheader(

        "📊 현재 결과 Dashboard"

    )



    # --------------------------------------------------------
    # 환자 상태 계산
    # --------------------------------------------------------


    moving = 0

    waiting = 0

    treating = 0

    finished = 0

    dead = 0



    for patient in simulation.patients:



        if patient.state == PatientState.MOVING:

            moving += 1



        elif patient.state == PatientState.WAITING:

            waiting += 1



        elif patient.state == PatientState.TREATING:

            treating += 1



        elif patient.state == PatientState.FINISHED:

            finished += 1



        elif patient.state == PatientState.DEAD:

            dead += 1




    # --------------------------------------------------------
    # 상태 카드
    # --------------------------------------------------------


    col1, col2, col3, col4, col5 = st.columns(5)



    col1.metric(

        "🚶 이동중",

        moving

    )


    col2.metric(

        "⏳ 대기중",

        waiting

    )


    col3.metric(

        "🏥 치료중",

        treating

    )


    col4.metric(

        "✅ 치료완료",

        finished

    )


    col5.metric(

        "☠ 사망",

        dead

    )





    # ========================================================
    # 병원 현황
    # ========================================================


    st.subheader(

        "🏥 의료시설 현황"

    )



    hospitals = st.session_state.selected_hospitals



    for hospital in hospitals:



        stats = hospital.get_statistics()



        with st.expander(

            f"Hospital {hospital.id}"

        ):



            c1, c2, c3 = st.columns(3)



            c1.metric(

                "현재 대기",

                stats["waiting"]

            )


            c2.metric(

                "치료중",

                stats["treating"]

            )


            c3.metric(

                "완료",

                stats["completed"]

            )



            st.write(

                f"""
                평균 대기시간:
                {stats["average_waiting_time"]:.2f}초


                평균 치료시간:
                {stats["average_treatment_time"]:.2f}초


                최대 대기열:
                {stats["max_queue_length"]}명


                """

            )



            st.progress(

                min(

                    stats["congestion_ratio"],

                    1.0

                )

            )


            st.caption(

                f"병목률 : "
                f"{stats['congestion_ratio']*100:.1f}%"

            )



# ============================================================
# Part 4 / 4 시작
# ============================================================
# ============================================================
# Part 4 / 4
# ------------------------------------------------------------
# - 최종 결과 분석
# - 통계 Dashboard
# - 그래프 출력
# ============================================================


import pandas as pd

import plotly.express as px



# ============================================================
# 최종 결과 Dashboard
# ============================================================


if (

    "result" in st.session_state

    and

    st.session_state.result is not None

):


    result = st.session_state.result



    st.divider()



    st.header(

        "📈 최종 시뮬레이션 결과"

    )



    # ========================================================
    # 핵심 지표
    # ========================================================


    col1, col2, col3, col4 = st.columns(4)



    col1.metric(

        "전체 환자",

        f"{result['total_patients']}명"

    )


    col2.metric(

        "사망자",

        f"{result['dead_patients']}명"

    )


    col3.metric(

        "생존율",

        f"{result['survival_rate']*100:.2f}%"

    )


    col4.metric(

        "종료 시간",

        f"{result['simulation_time']}초"

    )





    st.divider()



    # ========================================================
    # 평균 시간 분석
    # ========================================================


    st.subheader(

        "⏱️ 시간 분석"

    )



    c1, c2, c3 = st.columns(3)



    c1.metric(

        "평균 이동시간",

        f"{result['average_moving_time']:.2f}초"

    )


    c2.metric(

        "평균 대기시간",

        f"{result['average_waiting_time']:.2f}초"

    )


    c3.metric(

        "평균 치료 시작시간",

        f"{result['average_start_time']:.2f}초"

    )





    # ========================================================
    # 병원 데이터 DataFrame
    # ========================================================


    hospital_data = pd.DataFrame(

        result["hospital_statistics"]

    )



    st.subheader(

        "🏥 병원별 통계"

    )



    st.dataframe(

        hospital_data,

        use_container_width=True

    )





    # ========================================================
    # 병목률 그래프
    # ========================================================


    st.subheader(

        "🚨 의료시설 병목 분석"

    )



    congestion_fig = px.bar(

        hospital_data,

        x="hospital_id",

        y="congestion_ratio",

        labels={

            "hospital_id":

                "병원",

            "congestion_ratio":

                "병목률"

        },

        title="병원별 대기열 병목률"

    )



    st.plotly_chart(

        congestion_fig,

        use_container_width=True

    )





    # ========================================================
    # 이용률 그래프
    # ========================================================


    st.subheader(

        "📊 의료시설 이용률"

    )



    utilization_fig = px.bar(

        hospital_data,

        x="hospital_id",

        y="utilization",

        labels={

            "hospital_id":

                "병원",

            "utilization":

                "이용률"

        },

        title="병원별 치료시설 이용률"

    )



    st.plotly_chart(

        utilization_fig,

        use_container_width=True

    )





    # ========================================================
    # 결과 해석
    # ========================================================


    st.subheader(

        "📝 분석 결과"

    )


    best_hospital = (

        hospital_data

        .sort_values(

            "congestion_ratio"

        )

        .iloc[0]

    )



    worst_hospital = (

        hospital_data

        .sort_values(

            "congestion_ratio",

            ascending=False

        )

        .iloc[0]

    )



    st.write(

        f"""

        - 가장 안정적인 의료시설:

        Hospital {best_hospital['hospital_id']}

        (병목률:

        {best_hospital['congestion_ratio']*100:.1f}%)



        - 가장 혼잡한 의료시설:

        Hospital {worst_hospital['hospital_id']}

        (병목률:

        {worst_hospital['congestion_ratio']*100:.1f}%)



        본 결과를 통해 단순 거리 최소화 방식의

        p-Median 배치가 재난 상황에서 발생시키는

        병목 현상을 분석할 수 있습니다.

        """

    )



# ============================================================
# End of ui.py
# ============================================================