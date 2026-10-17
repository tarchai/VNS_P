"""Matplotlib output only; show/save convergence curve only."""
from pathlib import Path


def plot_figures(output_dir, results, show=True):
    import matplotlib.pyplot as plt

    folder = Path(output_dir)
    folder.mkdir(exist_ok=True, parents=True)

    # One two-panel convergence image showing MEAN of 30 independent runs.
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))

    for ax, (name, item) in zip(axes, results.items()):
        trials = item['trials']
        n = len(trials[0]['history'])

        mean_curve = [
            sum(tr['history'][i] for tr in trials) / len(trials)
            for i in range(n)
        ]

        best_seed_run = min(trials, key=lambda t: t['best_fitness'])

        ax.semilogy(
            range(n),
            [v + 1e-12 for v in mean_curve],
            label='Mean best-so-far (30 runs)',
            lw=2
        )

        ax.semilogy(
            range(n),
            [v + 1e-12 for v in best_seed_run['history']],
            label='Best run',
            lw=1.4,
            alpha=0.8
        )

        ax.set_title(name)
        ax.set_xlabel('Iteration (shaking call)')
        ax.set_ylabel('Best fitness (log scale, +1e-12)')
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)

    fig.suptitle('VNS Convergence - 30 runs x 100 iterations')
    fig.tight_layout()
    fig.savefig(folder / 'convergence.png', dpi=150)

    if show:
        plt.show()

    plt.close('all')