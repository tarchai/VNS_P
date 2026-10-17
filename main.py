"""Run the assignment: python main.py  (or python main.py --no-show)."""
import sys
from pathlib import Path

from vns_core import Settings, rosenbrock, rastrigin, experiment
from reporting import print_report, save_reports
from delivery_example import run_demo

# ------------------- SETTINGS: EDIT THESE TO EXPERIMENT -------------------
RUNS = 30
ITERATIONS = 100
FIRST_SEED = 7       # 30 trials use seeds 7, 8, ..., 36
OUTPUT_FOLDER = Path(__file__).resolve().parent / 'results'

CONFIGS = {
    'Rosenbrock': Settings(
        start=(-1.0, 1.0), bounds=(-2.0, 2.0), iterations=ITERATIONS,
        k_max=3, shaking_radius=0.55, local_step=0.25,
        local_min_step=0.0001, local_max_moves=240,
    ),
    'Rastrigin': Settings(
        start=(-1.0, 1.0), bounds=(-5.12, 5.12), iterations=ITERATIONS,
        k_max=5, shaking_radius=0.50, local_step=0.25,
        local_min_step=0.0001, local_max_moves=120,
    ),
}
# ---------------------------------------------------------------------------


def main():
    if '--help' in sys.argv:
        print('Run: python main.py [--no-show | --no-plots]')
        return
    results = {}
    for name, objective in [('Rosenbrock',rosenbrock), ('Rastrigin',rastrigin)]:
        cfg = CONFIGS[name]
        trials, summary = experiment(objective,cfg,runs=RUNS,first_seed=FIRST_SEED)
        results[name] = {'objective':objective, 'settings':cfg,
                         'trials':trials, 'summary':summary}
    print_report(results)
    delivery = run_demo(seed=FIRST_SEED, iterations=20)
    print('\nREAL-WORLD APPLICATION - ONE VEHICLE DELIVERY ROUTE (TOY TSP)')
    print(f'  Initial distance : {delivery["initial_distance"]:.4f} units')
    print(f'  Best distance    : {delivery["best_distance"]:.4f} units')
    print(f'  Improvement      : {delivery["improvement"]:.4f} units')
    print(f'  Best route       : {delivery["end_route"]}')
    print('  (Synthetic coordinates; not actual road distances)')
    save_reports(OUTPUT_FOLDER,results,delivery)
    if '--no-plots' not in sys.argv:
        try:
            from visualization import plot_figures
            plot_figures(OUTPUT_FOLDER,results,show=('--no-show' not in sys.argv))
        except ImportError as exc:
            print('\nMatplotlib not found. Install: python -m pip install matplotlib')
            raise exc
    print(f'\nDetailed logs, manual calculations, CSV and graphs: {OUTPUT_FOLDER}')


if __name__ == '__main__':
    main()
