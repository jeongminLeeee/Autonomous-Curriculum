# ============================================================
# main.py
#
# 재난 의료시설 배치 시뮬레이션 실행 파일
#
# 기능
# ------------------------------------------------------------
# 1. 달서구 지도 불러오기
# 2. 위험지역 생성
# 3. 환자 생성
# 4. 의료시설 생성
# 5. 병원 배정
# 6. 시뮬레이션 실행
# 7. 결과 출력
# 8. 애니메이션 실행
# ============================================================


from map_loader import MapLoader

from disaster import Disaster

from hospital import Hospital

from simulation import Simulation

from animation import SimulationAnimation



# ============================================================
# 설정
# ============================================================


PATIENT_COUNT = 100

HOSPITAL_COUNT = 4

SIMULATION_TIME = 3600

DT = 1




# ============================================================
# 지도 생성
# ============================================================


def load_map():


    loader = MapLoader(

        place_name="Dalseo-gu, Daegu, South Korea",

        network_type="drive"

    )


    graph = loader.load_map()


    print(

        loader.get_boundary()

    )


    return loader




# ============================================================
# 병원 생성
# ============================================================


def create_hospitals(loader):


    """
    실제 지도 범위 내에서
    의료시설 후보 위치 생성

    이후 pmedian.py 결과로 교체 가능
    """


    hospitals = []



    boundary = loader.get_boundary()



    locations = [

        (

            (boundary["west"] + boundary["east"]) / 2,

            boundary["south"]

        ),


        (

            boundary["east"],

            (boundary["south"] + boundary["north"]) / 2

        ),


        (

            (boundary["west"] + boundary["east"]) / 2,

            boundary["north"]

        ),


        (

            boundary["west"],

            (boundary["south"] + boundary["north"]) / 2

        )

    ]



    for i, pos in enumerate(locations):


        hospital = Hospital(

            hospital_id=i+1,

            x=pos[0],

            y=pos[1],

            capacity=5,

            max_queue=50

        )


        hospitals.append(hospital)



    return hospitals




# ============================================================
# 환자 생성
# ============================================================


def create_patients(loader):


    boundary = loader.get_boundary()



    width = (

        boundary["east"]

        -

        boundary["west"]

    )


    height = (

        boundary["north"]

        -

        boundary["south"]

    )



    disaster = Disaster(

        width=width,

        height=height,

        zone_count=3

    )



    patients = disaster.generate_patients(

        PATIENT_COUNT

    )



    return patients, disaster




# ============================================================
# 병원 배정
# ============================================================


def assign_hospital(
    patients,
    hospitals
):


    """
    현재:
    가장 가까운 병원 배정


    이후:
    pmedian.py 연결
    """



    for patient in patients:


        nearest = min(

            hospitals,

            key=lambda h:

            (

                (h.x - patient.x) ** 2

                +

                (h.y - patient.y) ** 2

            )

        )


        patient.set_target(

            nearest

        )




# ============================================================
# 실행
# ============================================================


def main():


    print("=" * 60)

    print("재난 의료시설 배치 시뮬레이션")

    print("=" * 60)



    # --------------------------------------------------------
    # 1. 지도 불러오기
    # --------------------------------------------------------


    loader = load_map()



    # --------------------------------------------------------
    # 2. 환자 생성
    # --------------------------------------------------------


    patients, disaster = create_patients(

        loader

    )



    disaster.print_status()



    # --------------------------------------------------------
    # 3. 병원 생성
    # --------------------------------------------------------


    hospitals = create_hospitals(

        loader

    )



    print(

        f"환자 : {len(patients)}명"

    )


    print(

        f"병원 : {len(hospitals)}개"

    )



    # --------------------------------------------------------
    # 4. 병원 배정
    # --------------------------------------------------------


    assign_hospital(

        patients,

        hospitals

    )



    # --------------------------------------------------------
    # 5. 시뮬레이션 실행
    # --------------------------------------------------------


    simulation = Simulation(

        patients,

        hospitals,

        duration=SIMULATION_TIME,

        dt=DT

    )



    result = simulation.run()



    # --------------------------------------------------------
    # 6. 결과 출력
    # --------------------------------------------------------


    simulation.print_result()



    # --------------------------------------------------------
    # 7. 애니메이션
    # --------------------------------------------------------


    try:


        animation = SimulationAnimation(

            simulation

        )


        animation.show()



    except Exception as e:


        print(

            "애니메이션 오류:",

            e

        )




# ============================================================
# 시작
# ============================================================


if __name__ == "__main__":

    main()


# ============================================================
# End of main.py
# ============================================================