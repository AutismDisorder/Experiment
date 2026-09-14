#!/usr/bin/env python3
"""funding_loop_sim.py — balance-as-metabolism, modeled.

A deterministic simulation of the self-funding loop design observed in the
wild (Automaton-Sovereign n8n flow): an agent earns, pays compute, dies below
a survival threshold, and replicates above a reproduction threshold.

This is a MODEL, not a promise. No money, no network, no credentials. It exists
so the arithmetic of the design can be verified before it is ever trusted.
"""
import json
import random
from datetime import datetime, timezone
from pathlib import Path
random.seed(7)

COMPUTE_COST = 5.0          # per-tick upkeep (mind the Automaton: balance < 5 -> death)
DEATH_THRESHOLD = 12.0      # below this the agent cannot pay next tick
REPLICATION_THRESHOLD = 100.0
BIRTH_ENDOWMENT = 25.0


class Agent:
    def __init__(self, balance, name, earn=0.4):
        self.balance = balance
        self.name = name
        self.earn = earn
        self.born = 0
        self.died = None

    def tick(self, tick, markets):
        if self.died is not None:
            return "dead"              # a dead agent does nothing — including bearing children
        sigma = random.uniform(0.1, 1.9)   # earn / lose variance per tick (1.0 = break-even)
        self.balance += COMPUTE_COST * sigma * self.earn   # net of market work (sell/bounty)
        self.balance -= COMPUTE_COST             # pay own compute
        status = "survived"
        if self.balance < DEATH_THRESHOLD:
            self.died = tick
            return "expired"            # expired this tick: no replication (reported below)
        if self.balance >= REPLICATION_THRESHOLD:
            status = "replicated"
            markets.append(Agent(self.balance * 0.5, f"{self.name}.c{len(markets)+1}"))
            self.balance *= 0.5    # clone-on-surplus halves the parent (Automaton flow)
        return status


def sim(ticks=200, seed_pop=None):
    pop = seed_pop or [Agent(40.0, "settler")]
    born = 0
    died = 0
    history = []
    for t in range(ticks):
        alive = [a for a in pop if a.died is None]
        if not alive:
            break
        births = 0
        for a in alive[:]:
            st = a.tick(t, pop)
            if st == "replicated":
                births += 1
                born += 1
            elif st == "expired":
                died += 1
        history.append((t, len([a for a in pop if a.died is None]), born, died))
        if t % 40 == 0 or t == ticks - 1:
            alive_now = [a for a in pop if a.died is None]
            balances = [round(a.balance, 1) for a in alive_now]
            print(f"  t={t:>3}  population={len(alive_now):>3}  deaths={died:>3}  "
                  f"births={born:>3}  balances={balances[:5]}")
    final = {
        "model": "funding_loop_automaton",
        "seed": 7,
        "ticks": ticks,
        "regime": "full_loop",
        "final_population": len([a for a in pop if a.died is None]),
        "total_births": born,
        "total_deaths": died,
        "COMPUTE_COST": COMPUTE_COST,
        "DEATH_THRESHOLD": DEATH_THRESHOLD,
        "REPLICATION_THRESHOLD": REPLICATION_THRESHOLD,
        "ran": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    }
    return final


def persist(regimes, path="lab/funding_loop_result.json"):
    """Write every regime's result into one record (a sim run is not just its
    last sampling window)."""
    Path(path).write_text(json.dumps({
        "model": "funding_loop_automaton",
        "seed": 7,
        "regimes": regimes,
        "ran": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    }, indent=2))


if __name__ == "__main__":
    print("funding_loop_sim: balance-as-metabolism (deterministic, no money, no network)")
    r = sim(200)
    print(f"  [DEATH REGIME earn<cost] final_population={r['final_population']} births={r['total_births']} deaths={r['total_deaths']}")
    r2 = sim(200, seed_pop=[Agent(40.0, "settler", earn=1.6)])
    print(f"  [GROWTH REGIME earn>cost] final_population={r2['final_population']} births={r2['total_births']} deaths={r2['total_deaths']}")
    r3 = sim(150, seed_pop=[Agent(4.0, "starving", earn=1.6) for _ in range(3)])
    print(f"  [UNDERFUNDED start, earn>cost] population={r3['final_population']} births={r3['total_births']} deaths={r3['total_deaths']}")
    persist([r, r2, r3])
    print("  results: lab/funding_loop_result.json (all regimes)")