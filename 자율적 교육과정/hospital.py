# ============================================================
# hospital.py
#
# Part 1 / 4
# ------------------------------------------------------------
# Hospital 클래스 정의
# 생성자
# 기본 변수
# ============================================================

from collections import deque
from patient import PatientState, Severity


class Hospital:
    """
    의료시설 클래스

    기능
    --------------------
    - 환자 대기열 관리
    - 치료 관리
    - 병목 관리
    - 통계 관리
    """

    def __init__(
        self,
        hospital_id,
        x,
        y,
        capacity=5,
        max_queue=50
    ):

        # -------------------------
        # 기본 정보
        # -------------------------

        self.id = hospital_id

        self.x = x
        self.y = y

        # 동시에 치료 가능한 인원
        self.capacity = capacity

        # 최대 대기 가능 인원
        self.max_queue = max_queue

        # -------------------------
        # 환자 목록
        # -------------------------

        # 대기열
        self.waiting_queue = deque()

        # 치료중
        self.treating_patients = []

        # 치료 완료
        self.finished_patients = []

        # -------------------------
        # 통계
        # -------------------------

        self.total_patients = 0

        self.total_completed = 0

        self.total_waiting_time = 0

        self.total_treatment_time = 0

        # 최대 대기열 길이
        self.max_queue_length = 0

        # 현재 대기열 길이
        self.current_queue_length = 0

        # 병목 발생 여부
        self.is_congested = False

    # ==========================================================
    # 병원까지 거리 계산
    # ==========================================================

    def distance_to(self, patient):

        dx = self.x - patient.x
        dy = self.y - patient.y

        return (dx ** 2 + dy ** 2) ** 0.5

    # ==========================================================
    # 수용 가능 여부
    # ==========================================================

    def has_queue_space(self):

        return len(self.waiting_queue) < self.max_queue

    # ==========================================================
    # 병목 여부
    # ==========================================================

    def update_congestion(self):

        self.is_congested = (
            len(self.waiting_queue)
            >= self.max_queue
        )

    # ==========================================================
    # 예상 대기시간
    # ==========================================================

    def get_expected_waiting_time(self):
        """
        개선 알고리즘에서 사용하는 함수

        이동시간 + 예상대기시간

        Cost 계산에 사용된다.
        """

        waiting = 0

        # 현재 치료중인 환자들의
        # 남은 치료시간

        for patient in self.treating_patients:
            waiting += patient.treatment_time

        # 대기중인 환자들의
        # 치료시간

        for patient in self.waiting_queue:
            waiting += patient.treatment_time

        # 동시에 치료 가능하므로
        # capacity만큼 나눠준다.

        return waiting / max(1, self.capacity)

# ============================================================
# Part 2에서 계속
# ============================================================
# ============================================================
# Part 2 / 4
# ------------------------------------------------------------
# 환자 등록
# 우선순위 대기열
# 치료 시작
# ============================================================

    # ==========================================================
    # 환자 추가
    # ==========================================================

    def add_patient(self, patient):

        """
        환자를 병원 대기열에 추가

        return
        -----------------
        True  : 추가 성공
        False : 대기열 가득참
        """

        self.update_congestion()

        if not self.has_queue_space():
            return False

        # 병원 도착

        patient.arrival_time = patient.created_time + patient.waiting_time

        patient.state = PatientState.WAITING

        self.waiting_queue.append(patient)

        self.total_patients += 1

        self.current_queue_length = len(self.waiting_queue)

        self.max_queue_length = max(
            self.max_queue_length,
            self.current_queue_length
        )

        self.update_congestion()

        return True

    # ==========================================================
    # 우선순위 정렬
    # RED → YELLOW → GREEN
    # ==========================================================

    def sort_waiting_queue(self):

        if len(self.waiting_queue) <= 1:
            return

        priority = {
            Severity.RED: 0,
            Severity.YELLOW: 1,
            Severity.GREEN: 2
        }

        queue = sorted(
            self.waiting_queue,
            key=lambda p: (
                priority[p.severity],
                p.arrival_time
            )
        )

        self.waiting_queue = deque(queue)

    # ==========================================================
    # 치료 시작
    # ==========================================================

    def start_treatment(self, current_time):

        """
        가능한 만큼 환자를 치료 시작
        """

        self.sort_waiting_queue()

        while (
            len(self.treating_patients) < self.capacity
            and
            len(self.waiting_queue) > 0
        ):

            patient = self.waiting_queue.popleft()

            patient.waiting_time = (
                current_time -
                patient.arrival_time
            )

            patient.start_treatment(self)

            patient.start_treatment_time = current_time

            self.total_waiting_time += patient.waiting_time

            self.treating_patients.append(patient)

        self.current_queue_length = len(self.waiting_queue)

        self.update_congestion()

    # ==========================================================
    # 현재 치료중 환자 수
    # ==========================================================

    def treating_count(self):

        return len(self.treating_patients)

    # ==========================================================
    # 현재 대기 환자 수
    # ==========================================================

    def waiting_count(self):

        return len(self.waiting_queue)

    # ==========================================================
    # 현재 총 환자 수
    # ==========================================================

    def patient_count(self):

        return (
            len(self.waiting_queue)
            +
            len(self.treating_patients)
        )

# ============================================================
# Part 3에서 계속
# ============================================================
# ============================================================
# Part 3 / 4
# ------------------------------------------------------------
# 치료 진행
# 치료 종료
# 통계 관리
# ============================================================

    # ==========================================================
    # 치료 진행
    # ==========================================================

    def update(self, dt, current_time):
        """
        병원의 상태를 dt(초)만큼 업데이트

        Parameters
        ----------
        dt : float
            경과 시간(초)

        current_time : float
            현재 시뮬레이션 시간
        """

        finished = []

        # -------------------------
        # 치료 진행
        # -------------------------

        for patient in self.treating_patients:

            patient.update_treatment(dt)

            if patient.state == PatientState.FINISHED:

                patient.finish_time = current_time

                self.total_treatment_time += (
                    patient.finish_time
                    - patient.start_treatment_time
                )

                finished.append(patient)

        # -------------------------
        # 완료 환자 제거
        # -------------------------

        for patient in finished:

            self.treating_patients.remove(patient)

            self.finished_patients.append(patient)

            self.total_completed += 1

        # -------------------------
        # 빈 자리가 생기면
        # 다음 환자 치료 시작
        # -------------------------

        self.start_treatment(current_time)

        self.update_congestion()

    # ==========================================================
    # 평균 대기시간
    # ==========================================================

    def average_waiting_time(self):

        if self.total_completed == 0:
            return 0

        return (
            self.total_waiting_time
            / self.total_completed
        )

    # ==========================================================
    # 평균 치료시간
    # ==========================================================

    def average_treatment_time(self):

        if self.total_completed == 0:
            return 0

        return (
            self.total_treatment_time
            / self.total_completed
        )

    # ==========================================================
    # 병원 이용률
    # ==========================================================

    def utilization(self):

        return (
            len(self.treating_patients)
            / self.capacity
        )

    # ==========================================================
    # 병목 정도
    # ==========================================================

    def congestion_ratio(self):

        return (
            len(self.waiting_queue)
            / self.max_queue
        )
# ============================================================
# Part 4 / 4
# ------------------------------------------------------------
# 초기화
# 통계
# 출력
# ============================================================

    # ==========================================================
    # 병원 초기화
    # ==========================================================

    def reset(self):
        """
        시뮬레이션을 다시 시작할 때 사용
        """

        self.waiting_queue.clear()

        self.treating_patients.clear()

        self.finished_patients.clear()

        self.total_patients = 0
        self.total_completed = 0

        self.total_waiting_time = 0
        self.total_treatment_time = 0

        self.max_queue_length = 0
        self.current_queue_length = 0

        self.is_congested = False

    # ==========================================================
    # 병원 통계
    # ==========================================================

    def get_statistics(self):

        return {

            "hospital_id": self.id,

            "total_patients": self.total_patients,

            "completed": self.total_completed,

            "waiting": len(self.waiting_queue),

            "treating": len(self.treating_patients),

            "finished": len(self.finished_patients),

            "average_waiting_time": self.average_waiting_time(),

            "average_treatment_time": self.average_treatment_time(),

            "utilization": self.utilization(),

            "congestion_ratio": self.congestion_ratio(),

            "max_queue_length": self.max_queue_length
        }

    # ==========================================================
    # 병원 상태 출력
    # ==========================================================

    def print_status(self):

        print("-" * 50)

        print(f"Hospital {self.id}")

        print(f"Location : ({self.x:.2f}, {self.y:.2f})")

        print(f"Waiting : {len(self.waiting_queue)}")

        print(f"Treating : {len(self.treating_patients)}")

        print(f"Finished : {len(self.finished_patients)}")

        print(f"Congested : {self.is_congested}")

        print("-" * 50)

    # ==========================================================
    # 문자열 출력
    # ==========================================================

    def __str__(self):

        return (
            f"Hospital("
            f"id={self.id}, "
            f"waiting={len(self.waiting_queue)}, "
            f"treating={len(self.treating_patients)}, "
            f"completed={self.total_completed})"
        )

    __repr__ = __str__

# ============================================================
# End of hospital.py
# ============================================================