# ============================================================
# simulation.py
#
# 재난 의료 시뮬레이션 엔진
#
# Part 1 / 4
# ------------------------------------------------------------
# - Simulation 클래스
# - 초기화
# - 시간 관리
# - 기본 데이터 관리
# ============================================================


from patient import (
    PatientState,
    Severity
)



class Simulation:
    """
    재난 의료 시뮬레이션 관리자

    담당 기능
    ----------------------------
    - 전체 시간 흐름 관리
    - 환자 상태 관리
    - 병원 상태 관리
    - 결과 데이터 저장
    """



    # ========================================================
    # 생성자
    # ========================================================

    def __init__(
        self,
        patients,
        hospitals,
        map_loader,
        duration=3600,
        dt=1

    ):
        
        self.map_loader = map_loader


        # ----------------------------------------------------
        # 입력 데이터
        # ----------------------------------------------------

        # 환자 목록

        self.patients = patients


        # 의료시설 목록

        self.hospitals = hospitals



        # ----------------------------------------------------
        # 시간 설정
        # ----------------------------------------------------

        # 전체 시뮬레이션 시간(초)

        self.duration = duration


        # 시간 증가 단위(초)

        self.dt = dt


        # 현재 시간

        self.current_time = 0



        # ----------------------------------------------------
        # 결과 저장
        # ----------------------------------------------------


        # 사망 환자

        self.dead_patients = []


        # 치료 완료 환자

        self.finished_patients = []



        # ----------------------------------------------------
        # 애니메이션용 기록
        # ----------------------------------------------------

        # 시간별 환자 상태 저장

        self.history = []



        # ----------------------------------------------------
        # 통계 데이터
        # ----------------------------------------------------


        self.total_steps = 0


        self.total_moving = 0


        self.total_waiting = 0


        self.total_treating = 0




    # ========================================================
    # 초기 상태 설정
    # ========================================================

    def initialize(self):

        """
        시뮬레이션 시작 전 초기화

        """

        self.current_time = 0


        self.dead_patients.clear()


        self.finished_patients.clear()


        self.history.clear()



        # 병원 초기화

        for hospital in self.hospitals:

            hospital.reset()



        # 환자 상태 초기화

        for patient in self.patients:

            patient.state = (
                PatientState.MOVING
            )

            patient.dead = False



    # ========================================================
    # 현재 상태 기록
    # ========================================================

    def record_state(self):

        """
        animation.py에서 사용할
        시간별 상태 저장
        """

        snapshot = {


            "time":
                self.current_time,


            "patients":[],



            "hospitals":[]

        }



        # -------------------------
        # 환자 정보 저장
        # -------------------------

        for patient in self.patients:


            snapshot["patients"].append(

                {

                    "id":
                        patient.id,


                    "x":
                        patient.x,


                    "y":
                        patient.y,


                    "state":
                        patient.state.value,


                    "severity":
                        patient.severity.value

                }

            )



        # -------------------------
        # 병원 정보 저장
        # -------------------------

        for hospital in self.hospitals:


            snapshot["hospitals"].append(

                {

                    "id":
                        hospital.id,


                    "waiting":
                        hospital.waiting_count(),


                    "treating":
                        hospital.treating_count()

                }

            )



        self.history.append(
            snapshot
        )



    # ========================================================
    # 현재 환자 상태 계산
    # ========================================================

    def update_counter(self):


        self.total_moving = 0

        self.total_waiting = 0

        self.total_treating = 0



        for patient in self.patients:


            if patient.state == PatientState.MOVING:

                self.total_moving += 1



            elif patient.state == PatientState.WAITING:

                self.total_waiting += 1



            elif patient.state == PatientState.TREATING:

                self.total_treating += 1



    # ========================================================
    # 시간 증가
    # ========================================================

    def increase_time(self):


        self.current_time += self.dt


        self.total_steps += 1


# ============================================================
# Part 2 / 4 에서 계속
# ============================================================
# ============================================================
# simulation.py
#
# Part 2 / 4
# ------------------------------------------------------------
# - 환자 이동 처리
# - 병원 도착 처리
# - 대기열 등록
# - 병원 배정 관리
# ============================================================



    # ========================================================
    # 환자 이동 처리
    # ========================================================

    def update_patient_movement(self):

        """
        이동 중인 환자를 목표 병원 방향으로 이동

        처리
        ----------------------------
        MOVING 상태 환자 이동
        병원 도착 시 WAITING 변경
        """

        for patient in self.patients:


            # 이동 상태가 아니면 제외

            if patient.state != PatientState.MOVING:

                continue



            # 이동

            patient.move()



            # 도착 확인

            if patient.state == PatientState.WAITING:


                self.arrive_hospital(
                    patient
                )



    # ========================================================
    # 병원 도착 처리
    # ========================================================

    def arrive_hospital(
        self,
        patient
    ):

        """
        환자가 목표 병원에 도착했을 때 처리

        """

        hospital = (
            patient.target_hospital
        )



        # 목표 병원이 없는 경우

        if hospital is None:

            return



        # 병원 대기열 추가

        success = hospital.add_patient(
            patient
        )



        # -------------------------
        # 병원이 가득 찬 경우
        # -------------------------

        if not success:


            # 현재 구조에서는
            # 대기 상태 유지

            patient.state = (
                PatientState.WAITING
            )



    # ========================================================
    # 병원 배정
    # ========================================================

    def assign_hospitals(
        self,
        algorithm
    ):

        """
        환자에게 병원 지정

        Parameters
        ----------
        algorithm :
            p-Median 또는 개선 알고리즘 함수


        예:
        ----------------
        pmedian.solve_pmedian
        improved_algorithm.select_hospital

        """



        # -------------------------
        # 전체 병원 선택형 알고리즘
        # -------------------------

        if callable(algorithm):


            result = algorithm(
                self.patients,
                self.hospitals
            )


            return result



    # ========================================================
    # 목표 병원 없는 환자 확인
    # ========================================================

    def check_unassigned_patients(self):


        count = 0



        for patient in self.patients:


            if patient.target_hospital is None:

                count += 1



        return count



    # ========================================================
    # 이동 가능한 환자 수
    # ========================================================

    def moving_count(self):


        count = 0



        for patient in self.patients:


            if patient.state == PatientState.MOVING:

                count += 1



        return count



    # ========================================================
    # 대기 환자 수
    # ========================================================

    def waiting_count(self):


        count = 0



        for patient in self.patients:


            if patient.state == PatientState.WAITING:

                count += 1



        return count



    # ========================================================
    # 치료 중 환자 수
    # ========================================================

    def treating_count(self):


        count = 0



        for patient in self.patients:


            if patient.state == PatientState.TREATING:

                count += 1



        return count



# ============================================================
# Part 3 / 4 에서 계속
# ============================================================
# ============================================================
# simulation.py
#
# Part 3 / 4
# ------------------------------------------------------------
# - 병원 치료 진행
# - 생존시간 업데이트
# - 사망 처리
# - 시간 단위 진행(step)
# ============================================================



    # ========================================================
    # 병원 상태 업데이트
    # ========================================================

    def update_hospitals(self):

        """
        모든 의료시설 업데이트

        처리
        ----------------------------
        - 치료 진행
        - 치료 완료
        - 다음 환자 치료 시작
        """

        for hospital in self.hospitals:


            hospital.update(

                self.dt,

                self.current_time

            )



    # ========================================================
    # 환자 생존시간 업데이트
    # ========================================================

    def update_patient_survival(self):

        """
        환자 치료 제한시간 감소

        RED / YELLOW 환자의
        제한시간 초과 처리
        """

        for patient in self.patients:


            # 이미 종료된 환자 제외

            if patient.state in (

                PatientState.DEAD,

                PatientState.FINISHED

            ):

                continue



            before_state = (
                patient.state
            )



            patient.update_survival(

                self.dt

            )



            # 새롭게 사망한 환자 기록

            if (

                patient.state == PatientState.DEAD

                and

                before_state != PatientState.DEAD

            ):


                self.dead_patients.append(

                    patient

                )



    # ========================================================
    # 치료 완료 환자 기록
    # ========================================================

    def update_finished_patients(self):


        self.finished_patients.clear()



        for patient in self.patients:


            if (

                patient.state

                ==

                PatientState.FINISHED

            ):


                self.finished_patients.append(

                    patient

                )



    # ========================================================
    # 한 번의 시간 진행
    # ========================================================

    def step(self):

        """
        시뮬레이션 1초 진행


        순서
        ----------------------------
        1. 환자 이동
        2. 병원 처리
        3. 치료 진행
        4. 생존시간 감소
        5. 기록 저장
        6. 시간 증가

        """



        # 1.
        # 환자 이동

        self.update_patient_movement()



        # 2.
        # 병원 치료

        self.update_hospitals()



        # 3.
        # 사망 판단

        self.update_patient_survival()



        # 4.
        # 완료 환자 갱신

        self.update_finished_patients()



        # 5.
        # 상태 기록

        self.record_state()



        # 6.
        # 상태 카운트

        self.update_counter()



        # 7.
        # 시간 증가

        self.increase_time()



    # ========================================================
    # 종료 여부 확인
    # ========================================================

    def is_finished(self):


        # 시간이 끝난 경우

        if self.current_time >= self.duration:

            return True



        # 모든 환자가 종료된 경우

        active = 0



        for patient in self.patients:


            if patient.state not in (

                PatientState.DEAD,

                PatientState.FINISHED

            ):

                active += 1



        if active == 0:

            return True



        return False



# ============================================================
# Part 4 / 4 에서 계속
# ============================================================
# ============================================================
# simulation.py
#
# Part 4 / 4
# ------------------------------------------------------------
# - 전체 실행
# - 결과 분석
# - 통계 반환
# - 출력
# ============================================================



    # ========================================================
    # 전체 시뮬레이션 실행
    # ========================================================

    def run(self):

        """
        시뮬레이션 전체 실행

        """

        print("=" * 60)

        print("재난 의료 시뮬레이션 시작")

        print("=" * 60)



        # 초기화

        self.initialize()



        # 반복 실행

        while not self.is_finished():


            self.step()



        # 마지막 결과 갱신

        self.update_finished_patients()



        result = self.get_result()



        print("=" * 60)

        print("재난 의료 시뮬레이션 종료")

        print("=" * 60)



        return result




    # ========================================================
    # 생존율 계산
    # ========================================================

    def survival_rate(self):


        total = len(
            self.patients
        )


        if total == 0:

            return 0



        alive = total - len(
            self.dead_patients
        )


        return alive / total




    # ========================================================
    # 평균 치료 시작 시간
    # ========================================================

    def average_start_time(self):


        total = 0

        count = 0



        for patient in self.patients:


            if patient.start_treatment_time is not None:


                total += (
                    patient.start_treatment_time
                    -
                    patient.created_time
                )


                count += 1



        if count == 0:

            return 0



        return total / count




    # ========================================================
    # 평균 이동시간
    # ========================================================

    def average_moving_time(self):


        total = 0

        count = 0



        for patient in self.patients:


            if patient.arrival_time is not None:


                total += (

                    patient.arrival_time

                    -

                    patient.created_time

                )


                count += 1



        if count == 0:

            return 0



        return total / count




    # ========================================================
    # 평균 대기시간
    # ========================================================

    def average_waiting_time(self):


        total = 0

        count = 0



        for hospital in self.hospitals:


            total += (
                hospital.total_waiting_time
            )


            count += (
                hospital.total_completed
            )



        if count == 0:

            return 0



        return total / count




    # ========================================================
    # 병원별 통계
    # ========================================================

    def hospital_statistics(self):


        result = []



        for hospital in self.hospitals:


            result.append(

                hospital.get_statistics()

            )



        return result




    # ========================================================
    # 최종 결과
    # ========================================================

    def get_result(self):


        return {


            # 전체 환자

            "total_patients":

                len(self.patients),



            # 사망자

            "dead_patients":

                len(self.dead_patients),



            # 치료 완료

            "finished_patients":

                len(self.finished_patients),



            # 생존율

            "survival_rate":

                self.survival_rate(),



            # 평균 이동시간

            "average_moving_time":

                self.average_moving_time(),



            # 평균 대기시간

            "average_waiting_time":

                self.average_waiting_time(),



            # 평균 치료 시작시간

            "average_start_time":

                self.average_start_time(),



            # 종료 시간

            "simulation_time":

                self.current_time,



            # 병원별 정보

            "hospital_statistics":

                self.hospital_statistics()

        }




    # ========================================================
    # 결과 출력
    # ========================================================

    def print_result(self):


        result = self.get_result()



        print("\n")

        print("=" * 60)

        print("시뮬레이션 결과")

        print("=" * 60)



        print(
            f"전체 환자 : "
            f"{result['total_patients']}명"
        )


        print(
            f"사망자 : "
            f"{result['dead_patients']}명"
        )


        print(
            f"치료 완료 : "
            f"{result['finished_patients']}명"
        )


        print(
            f"생존율 : "
            f"{result['survival_rate']*100:.2f}%"
        )


        print(
            f"평균 이동시간 : "
            f"{result['average_moving_time']:.2f}초"
        )


        print(
            f"평균 대기시간 : "
            f"{result['average_waiting_time']:.2f}초"
        )


        print(
            f"평균 치료 시작시간 : "
            f"{result['average_start_time']:.2f}초"
        )


        print("=" * 60)



        print("\n[병원별 통계]")


        for hospital in result["hospital_statistics"]:


            print(
                hospital
            )



# ============================================================
# 테스트 실행
# ============================================================

if __name__ == "__main__":


    print(
        "simulation.py module test"
    )



# ============================================================
# End of simulation.py
# ============================================================
