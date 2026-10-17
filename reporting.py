"""Terminal summaries, CSV, actual hand-calculation logs. Standard library only."""
import csv
import math
from pathlib import Path


def metric_number(value):
    if abs(value) < 1e-14:
        return '0'
    return f'{value:.8g}'


def print_report(results):
    print('\n' + '='*76)
    print('VNS OPTIMIZATION | 30 runs x 100 iterations | Minimization')
    print('='*76)
    for name, item in results.items():
        s = item['summary']
        print(f'\n{name} ({s["runs"]} runs x {s["iterations"]} iterations)')
        print(f'  Best / Mean / Worst : {metric_number(s["best"])} / '
              f'{metric_number(s["mean"])} / {metric_number(s["worst"])}')
        print(f'  Best point          : ({s["best_point"][0]:.8f}, '
              f'{s["best_point"][1]:.8f})')
        print(f'  f(x_best, y_best)   : {s["best"]:.12g}')
        print(f'  Average runtime     : {s["average_runtime"]:.6f} s')
        print(f'  Success <= 1e-6     : {s["success_count"]}/{s["runs"]}')
        print(f'  Best seed           : {s["best_seed"]}')

    print('\n' + '-'*106)
    print(f'{"FUNCTION":<13} {"BEST":>13} {"MEAN":>13} {"WORST":>13} '
          f'{"AVG TIME (s)":>15} {"SUCCESS":>11}')
    print('-'*106)
    for name, item in results.items():
        s = item['summary']
        print(f'{name:<13} {metric_number(s["best"]):>13} '
              f'{metric_number(s["mean"]):>13} '
              f'{metric_number(s["worst"]):>13} '
              f'{s["average_runtime"]:>15.6f} '
              f'{s["success_count"]:>8}/{s["runs"]:<2}')
    print('-'*106)


def save_csv(path, rows, columns):
    with Path(path).open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({field:row.get(field) for field in columns})


def f_expression(name, point):
    """Objective substitution formatted using the *actual* coordinates."""
    x,y = point
    if name == 'Rosenbrock':
        a = (1-x)**2
        b = 100*(y-x*x)**2
        return (f'f({x:.9f}, {y:.9f}) = [1-({x:.9f})]^2 '
                f'+ 100*[({y:.9f})-({x:.9f})^2]^2 '
                f'= {a:.10g} + {b:.10g} = {a+b:.12g}')
    a = x*x+y*y
    b = 10*(math.cos(2*math.pi*x)+math.cos(2*math.pi*y))
    return (f'f({x:.9f}, {y:.9f}) = 20+({x:.9f})^2+({y:.9f})^2 '
            f'-10*[cos(2*pi*({x:.9f}))+cos(2*pi*({y:.9f}))] '
            f'= 20+{a:.10g}-{b:.10g} = {20+a-b:.12g}')


def save_hand_calculation(path, name, run, settings):
    """Concise 2-iteration explanation grounded in the actual log.

    The full accepted local-search paths are saved in a separate CSV.
    """
    lines = [
        f'{name} | FIRST TWO ACTUAL VNS ITERATIONS | seed={run["seed"]}',
        'One iteration = one Shaking + Local Search + acceptance check.',
        'The sampled Shaking points and LS results below come from run_vns, not invented.',
        f'LS: 8 directions; step starts {settings.local_step}, halves when no better neighbor;',
        f'    minimum step {settings.local_min_step}.',
        'Numeric expressions show rounded coordinates, final fitness uses full precision.',
        'For ALL local-search moves, see the corresponding local_trace_seed7.csv file.',
        '',
    ]
    for item in run['logs'][:2]:
        trace = item['local_path']
        lines.extend([
            '='*68,
            f'ITERATION {item["iteration"]} | k={item["k"]}',
            '1) Current objective:',
            '   ' + f_expression(name, item['before']),
            '2) Shaking:',
            f'   Current {item["before"]} -> Shaking {item["shaken"]}',
            '   ' + f_expression(name, item['shaken']),
            '3) Local Search: accepted better neighbors:',
        ])
        view_ids = list(range(min(4, len(trace))))
        if len(trace) > 6:
            view_ids += [len(trace)-2, len(trace)-1]
        else:
            view_ids = list(range(len(trace)))
        last_idx = None
        for idx in view_ids:
            if last_idx is not None and idx > last_idx + 1:
                lines.append(f'   ... {idx-last_idx-1} additional moves (see CSV) ...')
            point,value,step = trace[idx]
            lines.append(f'   move {idx:03d}: ({point[0]:.9f}, {point[1]:.9f}), '
                         f'f={value:.12g}, step={step:.7f}')
            last_idx = idx
        lines.extend([
            f'   Total accepted Local Search moves: {max(0,len(trace)-1)}',
            '   Final local-search evaluation:',
            '   ' + f_expression(name, item['local']),
            '4) Neighborhood Change:',
            f'   Compare candidate f={item["local_fitness"]:.12g} '
            f'vs current f={item["before_fitness"]:.12g}.',
            f'   Decision: {"ACCEPT -> reset k=1" if item["accepted"] else "REJECT -> next k"}',
            f'   New current point {item["after"]}, '
            f'Best Fitness={item["after_fitness"]:.12g}, next k={item["next_k"]}',
            '',
        ])
    Path(path).write_text('\n'.join(lines), encoding='utf-8')

def save_reports(folder, results, delivery):
    folder = Path(folder)
    folder.mkdir(exist_ok=True, parents=True)
    summary_rows = []
    for name,item in results.items():
        trials = item['trials']
        settings = item['settings']
        s = item['summary']
        summary_rows.append({'function':name, **s,
                             'best_x':s['best_point'][0], 'best_y':s['best_point'][1]})
        save_csv(folder / f'{name.lower()}_30_runs.csv', [
            {'seed':t['seed'], 'best_x':t['best_point'][0],
             'best_y':t['best_point'][1], 'best_fitness':t['best_fitness'],
             'runtime_seconds':t['runtime'], 'evaluations':t['evaluations']}
            for t in trials], ['seed','best_x','best_y','best_fitness','runtime_seconds','evaluations'])
        demo = trials[0]  # Seed 7, fully reproducible
        save_csv(folder / f'{name.lower()}_iterations_seed7.csv', [
            {'iteration':e['iteration'], 'k':e['k'],
             'before':e['before'], 'shaken':e['shaken'],
             'shaken_fitness':e['shaken_fitness'],
             'local':e['local'], 'local_fitness':e['local_fitness'],
             'decision':'ACCEPT' if e['accepted'] else 'REJECT',
             'best_fitness':e['after_fitness'], 'next_k':e['next_k']}
            for e in demo['logs']],
            ['iteration','k','before','shaken','shaken_fitness','local',
             'local_fitness','decision','best_fitness','next_k'])
        save_hand_calculation(folder / f'{name.lower()}_manual_2_iterations.txt',
                              name, demo, settings)
        trace_rows = []
        for entry in demo['logs'][:2]:
            for move,(point,value,step) in enumerate(entry['local_path']):
                trace_rows.append({'iteration':entry['iteration'],
                    'move':move, 'x':point[0], 'y':point[1],
                    'fitness':value, 'step':step})
        save_csv(folder / f'{name.lower()}_local_trace_seed7.csv',
                 trace_rows, ['iteration','move','x','y','fitness','step'])
    save_csv(folder / 'comparison.csv', summary_rows,
             ['function','runs','iterations','best','mean','worst','best_x',
              'best_y','best_seed','average_runtime','success_count'])
    lines = [
        'REAL WORLD EXAMPLE: ONE VEHICLE / FIVE CUSTOMERS (TOY TSP)',
        'All coordinates are synthetic; distances are Euclidean units, NOT road km.',
        'Objective: minimize total round trip distance to depot (stop 0).',
        'Neighborhoods: swap any customers, or reverse a segment (2-opt).',
        f'Initial route: {delivery["start_route"]}',
        f'Initial distance: {delivery["initial_distance"]:.8f}',
        f'Best route: {delivery["end_route"]}',
        f'Best distance: {delivery["best_distance"]:.8f}',
        f'Improvement: {delivery["improvement"]:.8f} distance units',
        '',
        'FIRST TWO ITERATIONS:',
    ]
    for i, shake, local, acc, best in delivery['trace'][:2]:
        lines.append(f'Iteration {i}: shake={shake}, local={local}, '
                     f'{"ACCEPT" if acc else "REJECT"}, best={best:.8f}')
    (folder / 'real_world_delivery_example.txt').write_text('\n'.join(lines), encoding='utf-8')
