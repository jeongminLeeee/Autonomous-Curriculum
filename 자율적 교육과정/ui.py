# ============================================================
# ui.py
#
# 재난 의료시설 최적화 시뮬레이터
#
# Part 1 / 4
# ------------------------------------------------------------
# - import
# - UI 생성
# - 입력창
# - 버튼 배치
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox

import random

from shapely.lib import boundary

from map_loader import MapLoader
from disaster import Disaster
from hospital import Hospital
from simulation import Simulation
from pmedian import solve_pmedian
from animation import SimulationAnimation


class SimulationUI:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title("재난 의료시설 배치 시뮬레이터")

        self.root.geometry("1000x700")

        self.root.resizable(False, False)

        # -----------------------------
        # 시뮬레이션 객체
        # -----------------------------

        self.map_loader = None
        self.disaster = None
        self.simulation = None

        self.candidate_hospitals = []
        self.selected_hospitals = []

        # -----------------------------
        # 변수
        # -----------------------------

        self.patient_var = tk.IntVar(value=200)

        self.candidate_var = tk.IntVar(value=15)

        self.selected_var = tk.IntVar(value=5)

        self.time_var = tk.IntVar(value=3600)

        self.seed_var = tk.IntVar(value=42)

        # -----------------------------
        # UI 생성
        # -----------------------------

        self.create_widgets()

    # =====================================================
    # 위젯 생성
    # =====================================================

    def create_widgets(self):

        title = tk.Label(

            self.root,

            text="재난 의료시설 최적화 시뮬레이터",

            font=("맑은 고딕", 20, "bold")

        )

        title.pack(pady=10)

        #####################################################

        setting = tk.LabelFrame(

            self.root,

            text="시뮬레이션 설정",

            padx=10,

            pady=10

        )

        setting.pack(fill="x", padx=10)

        #####################################################

        tk.Label(

            setting,

            text="환자 수"

        ).grid(row=0, column=0, sticky="w")

        tk.Entry(

            setting,

            textvariable=self.patient_var,

            width=10

        ).grid(row=0, column=1, padx=10)

        #####################################################

        tk.Label(

            setting,

            text="후보 병원 수"

        ).grid(row=1, column=0, sticky="w")

        tk.Entry(

            setting,

            textvariable=self.candidate_var,

            width=10

        ).grid(row=1, column=1, padx=10)

        #####################################################

        tk.Label(

            setting,

            text="선택 병원(p)"

        ).grid(row=2, column=0, sticky="w")

        tk.Entry(

            setting,

            textvariable=self.selected_var,

            width=10

        ).grid(row=2, column=1, padx=10)

        #####################################################

        tk.Label(

            setting,

            text="시뮬레이션 시간"

        ).grid(row=3, column=0, sticky="w")

        tk.Entry(

            setting,

            textvariable=self.time_var,

            width=10

        ).grid(row=3, column=1, padx=10)

        #####################################################

        tk.Label(

            setting,

            text="Random Seed"

        ).grid(row=4, column=0, sticky="w")

        tk.Entry(

            setting,

            textvariable=self.seed_var,

            width=10

        ).grid(row=4, column=1, padx=10)

        #####################################################

        button_frame = tk.Frame(self.root)

        button_frame.pack(pady=15)

        self.map_button = tk.Button(

            button_frame,

            text="지도 불러오기",

            width=18,

            command=self.load_map

        )

        self.map_button.grid(row=0, column=0, padx=5)

        self.prepare_button = tk.Button(

            button_frame,

            text="시뮬레이션 준비",

            width=18,

            command=self.prepare_simulation,

            state="disabled"

        )

        self.prepare_button.grid(row=0, column=1, padx=5)

        self.run_button = tk.Button(

            button_frame,

            text="시뮬레이션 실행",

            width=18,

            command=self.run_simulation,

            state="disabled"

        )

        self.run_button.grid(row=0, column=2, padx=5)

        self.animation_button = tk.Button(

            button_frame,

            text="애니메이션 보기",

            width=18,

            command=self.show_animation,

            state="disabled"

        )

        self.animation_button.grid(row=0, column=3, padx=5)

        self.result_button = tk.Button(

            button_frame,

            text="결과 보기",

            width=18,

            command=self.show_result,

            state="disabled"

        )

        self.result_button.grid(row=0, column=4, padx=5)

        #####################################################

        log_frame = tk.LabelFrame(

            self.root,

            text="상태"

        )

        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log = tk.Text(

            log_frame,

            height=20

        )

        self.log.pack(fill="both", expand=True)

    # =====================================================
    # 로그 출력
    # =====================================================

    def write_log(self, text):

        self.log.insert(tk.END, text + "\n")

        self.log.see(tk.END)
    # =====================================================
    # 지도 불러오기
    # =====================================================

    def load_map(self):

        try:

            self.write_log("OpenStreetMap 불러오는 중...")

            self.map_loader = MapLoader()

            self.map_loader.load_map()

            self.write_log("지도 불러오기 완료")

            self.prepare_button.config(state="normal")

            messagebox.showinfo(
                "완료",
                "달서구 지도를 불러왔습니다."
            )

        except Exception as e:

            messagebox.showerror(
                "오류",
                str(e)
            )



    # =====================================================
    # 시뮬레이션 준비
    # =====================================================

    def prepare_simulation(self):

        if self.map_loader is None:

            messagebox.showwarning(
                "경고",
                "먼저 지도를 불러오세요."
            )

            return

        self.write_log("")

        self.write_log("===== 시뮬레이션 준비 =====")

        random.seed(
            self.seed_var.get()
        )

        # ----------------------------------------
        # 재난 생성
        # ----------------------------------------

        boundary = self.map_loader.get_boundary()
        print(boundary)

        self.disaster = Disaster(
            west=boundary["west"],
            east=boundary["east"],
            south=boundary["south"],
            north=boundary["north"],
            zone_count=3,
            seed=self.seed_var.get()
        )

        self.write_log("위험지역 생성 완료")

        # ----------------------------------------
        # 환자 생성
        # ----------------------------------------

        patients = self.disaster.generate_patients(

            self.patient_var.get()

        )

        self.write_log(
            f"환자 {len(patients)}명 생성"
        )

        # ----------------------------------------
        # 후보 병원 생성
        # ----------------------------------------

        self.candidate_hospitals = []

        for i in range(

            self.candidate_var.get()

        ):

            x, y = self.map_loader.get_random_point()

            hospital = Hospital(

                hospital_id=i + 1,

                x=x,

                y=y,

                capacity=5,

                max_queue=50

            )

            self.candidate_hospitals.append(

                hospital

            )

        self.write_log(

            f"후보 병원 {len(self.candidate_hospitals)}개 생성"

        )

        # ----------------------------------------
        # p-Median
        # ----------------------------------------

        self.selected_hospitals = solve_pmedian(

            patients,

            self.candidate_hospitals,

            self.selected_var.get()

        )

        self.write_log(

            f"최종 병원 {len(self.selected_hospitals)}개 선택"

        )

        # ----------------------------------------
        # Simulation 생성
        # ----------------------------------------

        self.simulation = Simulation(

            patients,

            self.selected_hospitals,

            self.map_loader,

            duration=self.time_var.get(),

            dt=1

        )

        self.write_log("Simulation 생성 완료")

        self.run_button.config(

            state="normal"

        )

        messagebox.showinfo(

            "완료",

            "시뮬레이션 준비가 완료되었습니다."

        )

    # =====================================================
    # 시뮬레이션 실행
    # =====================================================

    def run_simulation(self):

        if self.simulation is None:

            messagebox.showwarning(

                "경고",

                "먼저 시뮬레이션을 준비하세요."

            )

            return

        self.write_log("")

        self.write_log("===== 시뮬레이션 시작 =====")

        self.root.update()

        # 실행

        result = self.simulation.run()

        self.write_log("")

        self.write_log("===== 시뮬레이션 종료 =====")

        self.write_log(

            f"총 환자 : {result['total_patients']}명"

        )

        self.write_log(

            f"사망자 : {result['dead_patients']}명"

        )

        self.write_log(

            f"치료 완료 : {result['finished_patients']}명"

        )

        self.write_log(

            f"생존율 : {result['survival_rate']*100:.2f}%"

        )

        self.write_log(

            f"평균 이동시간 : {result['average_moving_time']:.2f}초"

        )

        self.write_log(

            f"평균 대기시간 : {result['average_waiting_time']:.2f}초"

        )

        self.animation_button.config(

            state="normal"

        )

        self.result_button.config(

            state="normal"

        )

        messagebox.showinfo(

            "완료",

            "시뮬레이션이 완료되었습니다."

        )



    # =====================================================
    # 애니메이션 보기
    # =====================================================

    def show_animation(self):

        if self.simulation is None:

            return

        if len(self.simulation.history) == 0:

            messagebox.showwarning(

                "경고",

                "먼저 시뮬레이션을 실행하세요."

            )

            return

        self.write_log("애니메이션 실행")

        animation = SimulationAnimation(

            self.simulation,

        )

        animation.show()



    # =====================================================
    # 결과 보기
    # =====================================================

    def show_result(self):

        if self.simulation is None:

            return

        result = self.simulation.get_result()

        text = ""

        text += "========== 시뮬레이션 결과 ==========\n\n"

        text += f"전체 환자 : {result['total_patients']}명\n"

        text += f"사망자 : {result['dead_patients']}명\n"

        text += f"치료 완료 : {result['finished_patients']}명\n"

        text += f"생존율 : {result['survival_rate']*100:.2f}%\n\n"

        text += f"평균 이동시간 : {result['average_moving_time']:.2f}초\n"

        text += f"평균 대기시간 : {result['average_waiting_time']:.2f}초\n"

        text += f"평균 치료 시작시간 : {result['average_start_time']:.2f}초\n"

        text += "\n========== 병원별 통계 ==========\n\n"

        for hospital in result["hospital_statistics"]:

            text += (

                f"Hospital {hospital['hospital_id']}\n"

                f"  완료 환자 : {hospital['completed']}명\n"

                f"  대기 환자 : {hospital['waiting']}명\n"

                f"  치료중 : {hospital['treating']}명\n"

                f"  평균 대기시간 : "

                f"{hospital['average_waiting_time']:.2f}초\n"

                f"  평균 치료시간 : "

                f"{hospital['average_treatment_time']:.2f}초\n"

                f"  최대 대기열 : "

                f"{hospital['max_queue_length']}명\n"

                f"  병목률 : "

                f"{hospital['congestion_ratio']*100:.2f}%\n\n"

            )

        window = tk.Toplevel(self.root)

        window.title("시뮬레이션 결과")

        window.geometry("700x600")

        result_box = tk.Text(

            window,

            wrap="word",

            font=("Consolas", 10)

        )

        result_box.pack(

            fill="both",

            expand=True

        )

        result_box.insert(

            tk.END,

            text

        )

        result_box.config(

            state="disabled"

        )

    # =====================================================
    # 프로그램 실행
    # =====================================================

    def run(self):

        self.root.mainloop()


# =========================================================
# main
# =========================================================

if __name__ == "__main__":

    app = SimulationUI()

    app.run()
