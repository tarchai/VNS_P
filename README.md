# VNS Optimization — Presentation Ready

โปรเจกต์ Python ของ Assignment Heuristic / Metaheuristic Optimization Algorithm: **Basic Variable Neighborhood Search (VNS)**

## สิ่งที่ตรงตามข้อกำหนด
- เขียน Objective, Shaking, Local Search, Neighborhood Change, Iterations, การคำนวณ Best/Mean/Worst ด้วย Python เองทั้งหมด
- **ไม่ใช้ Optimization Library**, ไม่มี Streamlit, ไม่ใช้ numpy / scipy เพื่อคำนวณคำตอบ
- ใช้ Matplotlib เฉพาะสร้าง **Convergence Curve 1 ภาพ (2 panels)** และ **Contour 2D 2 ภาพ**
- **30 runs x 100 iterations** ต่อฟังก์ชัน (ปรับได้ใน `main.py`)
- เก็บหลักฐานการคำนวณ 2 iterations **จาก Seed และรอบที่รันจริง** แยกเป็น txt และ Log 100 iterations เป็น CSV
- ตัวอย่าง Real-world: วางแผนเส้นทางรถส่งสินค้าคันเดียว (toy Traveling Salesperson Problem) พร้อมระบุว่าใช้พิกัดสมมติ ไม่ใช่เส้นทางถนนจริง

## วิธีรันบน VS Code / Windows
เปิด Terminal ในโฟลเดอร์ที่มี `main.py`:

```powershell
# ถ้า Python venv ถูก activate แล้ว
python -m pip install -r requirements.txt
python main.py

# หรือระบุ interpreter ตรง ๆ ถ้ามี .venv อยู่ในโฟลเดอร์นี้
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

หากใช้ `.venv` โฟลเดอร์แม่ (`VNS/.venv` และไฟล์อยู่ `VNS/VNS_P/...`) ให้ใช้ `..\.venv\Scripts\python.exe` แทน

รันแบบบันทึกกราฟโดยไม่เปิดหน้าต่าง:

```powershell
python main.py --no-show
```

รันเฉพาะคำนวณ ไม่สร้างกราฟ:

```powershell
python main.py --no-plots
```

ทดสอบอัลกอริทึม:

```powershell
python -m unittest -v test_vns.py
```

## โครงสร้าง
- `main.py` ตั้งค่าและรัน 2 Benchmarks, พิมพ์ผลสรุป + ตาราง
- `vns_core.py` Objective Functions, Shaking แบบ continuous, Adaptive Local Search, Basic VNS, Multi-run metrics
- `reporting.py` ฟอร์แมต Output, บันทึก CSV, รายงานคำนวณด้วยมือ 2 iterations
- `visualization.py` เฉพาะ Matplotlib; ไม่มีหน้าที่คำนวณ Optimization
- `delivery_example.py` ตัวอย่าง VNS บนเส้นทางจัดส่ง 1 คัน (Swap / 2-opt)
- `test_vns.py` Unit Tests
- `results/` สร้างอัตโนมัติ

## ค่าตั้งต้น
- Rosenbrock: `(-1,1)`, domain [-2,2], `k_max=3`, initial local step=0.25
- Rastrigin: `(-1,1)`, domain [-5.12,5.12], `k_max=5`, initial local step=0.25
- 30 runs, seeds 7 ถึง 36; แต่ละ run ทำ 100 iterations
- 1 iteration = 1 Shaking + Local Search + Acceptance (NOT วนรอบ k ครบทุกค่า)
- Local Search หาค่าต่ำสุดจาก 8 ทิศทางและ **ลด step ครึ่งหนึ่ง** เมื่อไม่พบคำตอบที่ดีขึ้น จึงไม่ได้ผูกการค้นหาอยู่แค่กริดคงที่ 0.2
- Shaking ใช้มุมและระยะสุ่มต่อเนื่อง ไม่ล็อกจุดบน grid

## Outputs ที่ได้
1. Terminal: ผลของแต่ละ Benchmark และตารางเปรียบเทียบ (Best, Mean, Worst, Best Point, Average Runtime)
2. `results/comparison.csv` — ตารางรวม
3. `results/rosenbrock_30_runs.csv`, `rastrigin_30_runs.csv` — ผล 30 Seeds
4. `results/*_iterations_seed7.csv` — Log ราย Iteration สำหรับตรวจสอบ
5. `results/*_manual_2_iterations.txt` — สรุปการคำนวณ 2 Iterations จากผลรันจริง (แสดงจุดต้น/ปลายและตัวอย่าง Moves) พร้อมการแทนค่าสมการ
7. `results/*_local_trace_seed7.csv` — รายละเอียด Local Search ทุก Move ของสอง Iterations แรก (ไว้ตรวจสอบผลโดยละเอียด)
8. `results/convergence.png` — Convergence ของ 2 ฟังก์ชันจาก Mean 30 runs และ best run (แกน Y แบบ log scale)
9. `results/rosenbrock_contour.png`, `rastrigin_contour.png` — 2D Contour พร้อมเส้นทาง accepted points
10. `results/real_world_delivery_example.txt` — ตัวอย่างงานจัดเส้นทาง 1 คัน (มีรายละเอียดสอง Iterations)

## หลักการที่ต้องอธิบายให้อาจารย์
1. **Objective:** minimization: Rosenbrock = `(1-x)^2+100*(y-x^2)^2`; Rastrigin = `20+x^2+y^2-10*(cos(2*pi*x)+cos(2*pi*y))`
2. **Shaking:** Random seed บังคับลำดับการสุ่ม ทำให้ผลทำซ้ำได้ แต่ไม่ได้บอกคำตอบที่ดีที่สุด
3. **Local Search:** ตรวจ 8 ทิศทาง และปรับระยะ Step ให้ละเอียดขึ้นอย่างเป็นระบบ (เขียนเอง)
4. **Neighborhood Change:** ถ้า `f(candidate) < f(current)` รับแล้ว `k=1`; มิฉะนั้นเพิ่ม `k` ถึง `k_max` แล้ววนใหม่
5. **Metrics:** นำ **Best Fitness ปลายทางของแต่ละ Run** มาคำนวณ min/mean/max และเฉลี่ยเวลาประมวลผล
6. **ข้อจำกัด:** เป็น Metaheuristic ไม่รับประกัน Global Optimum ทุกครั้ง; เวลารันขึ้นอยู่กับเครื่อง; เส้นทางตัวอย่างเป็น Euclidean synthetic data
7. **Known optimum (เพื่อประเมินความแม่นยำเท่านั้น):** Rosenbrock ที่ (1,1), Rastrigin ที่ (0,0), Fitness=0 ทั้งคู่; ไม่ได้นำไปใช้ขณะค้นหา

## ทดลองเปลี่ยนค่า
แก้ `RUNS`, `ITERATIONS`, `FIRST_SEED`, หรือ `CONFIGS` ใน `main.py` แล้วรันใหม่ เพื่อดูความแม่นยำ/ความเร็วกับ Neighborhood และ Budget ที่ต่างกัน
