"""Self-tests: run python -m unittest -v test_vns.py"""
import math
import unittest
from vns_core import (Settings, rosenbrock, rastrigin, neighborhood,
                      shake, local_search, run_vns, experiment)
from delivery_example import run_demo
import random


class TestVNS(unittest.TestCase):
    def setUp(self):
        self.cfg = Settings(iterations=12, k_max=3, local_max_moves=50)

    def test_known_benchmark_minima(self):
        self.assertAlmostEqual(rosenbrock(1,1),0)
        self.assertAlmostEqual(rastrigin(0,0),0)
        self.assertGreater(rosenbrock(-1,1),0)

    def test_neighborhood_eight_directions(self):
        pts = neighborhood((0,0), .2, (-2,2))
        self.assertEqual(len(pts),8)
        self.assertIn((.2,.2),pts)

    def test_shaking_continuous_and_within_bounds(self):
        rng = random.Random(7)
        pts = [shake((0,0),2,.6,(-2,2),rng) for _ in range(20)]
        self.assertTrue(all(-2<=x<=2 and -2<=y<=2 for x,y in pts))
        self.assertTrue(any(abs(x/0.2-round(x/0.2)) > .001 for x,y in pts))

    def test_local_search_never_worsens_input(self):
        start=(-.8,.8)
        p,v,trace,n=local_search(start,rosenbrock,self.cfg,True)
        self.assertLessEqual(v,rosenbrock(*start)+1e-12)
        self.assertGreater(n,0)
        self.assertAlmostEqual(v,rosenbrock(*p),places=10)
        self.assertGreaterEqual(len(trace),1)

    def test_reproducible_seed(self):
        a=run_vns(rosenbrock,self.cfg,seed=7)
        b=run_vns(rosenbrock,self.cfg,seed=7)
        self.assertEqual(a['history'],b['history'])
        self.assertEqual(a['best_point'],b['best_point'])
        self.assertEqual([x['shaken'] for x in a['logs']],
                         [x['shaken'] for x in b['logs']])

    def test_exact_iteration_count(self):
        a=run_vns(rastrigin,self.cfg,seed=2)
        self.assertEqual(len(a['logs']),self.cfg.iterations)
        self.assertEqual(len(a['history']),self.cfg.iterations+1)

    def test_best_so_far_monotone(self):
        a=run_vns(rastrigin,self.cfg,seed=7)
        self.assertTrue(all(b<=a+1e-12 for a,b in zip(a['history'],a['history'][1:])))

    def test_acceptance_rule(self):
        a=run_vns(rosenbrock,self.cfg,seed=7)
        for log in a['logs']:
            self.assertEqual(log['accepted'],
                log['local_fitness'] < log['before_fitness'] - 1e-12)

    def test_summary_math(self):
        a,s=experiment(rastrigin,self.cfg,runs=3,first_seed=7)
        values=[r['best_fitness'] for r in a]
        self.assertEqual(s['best'],min(values))
        self.assertEqual(s['worst'],max(values))
        self.assertAlmostEqual(s['mean'],sum(values)/len(values))

    def test_input_validation(self):
        with self.assertRaises(ValueError):
            run_vns(rosenbrock,Settings(iterations=0),7)
        with self.assertRaises(ValueError):
            run_vns(rosenbrock,Settings(start=(10,10)),7)

    def test_delivery_example(self):
        result=run_demo(7,20)
        self.assertLessEqual(result['best_distance'],result['initial_distance'])
        self.assertEqual(result['end_route'][0],0)
        self.assertEqual(result['end_route'][-1],0)


if __name__=='__main__':
    unittest.main()
