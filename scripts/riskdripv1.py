"""
RiskDrip.py

A disciplined capital deployment simulator for options trading.

This script models a repeatable investment strategy where a fixed percentage 
of a portfolio is allocated to a basket of options each round. Most expire worthless, 
but a single high-return contract (a "missile") can grow the portfolio. 
Capital exposure is titrated like a chemistry dropper — slow, deliberate, and asymmetric.

Author: Leslie Cuadra

"""

import matplotlib.pyplot as plt
import numpy as np

def simulate_riskdrip_v2(
    starting_balance=800,
    base_allocation_pct=1.0,
    missile_chance=0.15,
    tenner_chance=0.04,
    gain_range=(1.0, 2.5),
    tenner_gain=8.0,
    loss_cap=0.15,
    cashout_pct=0.80,
    cooldown_allocation_pct=0.15,
    rounds=1000,
    seed=None,
    log_events=False
):
    if seed is not None:
        np.random.seed(seed)

    balances = [starting_balance]
    in_cooldown = False
    events = []

    for i in range(rounds):
        current_balance = balances[-1]

        # Adjust allocation %
        if in_cooldown:
            allocation_pct = cooldown_allocation_pct
            in_cooldown = False  # reset after one round
        else:
            allocation_pct = base_allocation_pct

        allocation = allocation_pct * current_balance

        # Simulate outcome
        rupture = False
        if np.random.rand() < missile_chance:
            if np.random.rand() < tenner_chance:
                gain = allocation * tenner_gain
                rupture = True
            else:
                gain = allocation * np.random.uniform(*gain_range)
        else:
            loss = allocation * np.random.uniform(0.01, loss_cap)
            gain = allocation - loss

        # Update balance
        new_balance = current_balance - allocation + gain

        # Cash-out logic
        if rupture:
            cashout_value = new_balance * cashout_pct
            if log_events:
                events.append(f"[Round {i}] 💥 Tenner hit! Portfolio: ${new_balance:.2f} → cashing out to ${cashout_value:.2f}")
            new_balance = cashout_value
            in_cooldown = True

        balances.append(new_balance)

    return balances, events

strategies = {
    "100% YOLO + Stops + Cashout": 1.0,
    "50% Alloc + Stops": 0.5,
    "20% Alloc + Stops": 0.2,
}

plt.figure(figsize=(12, 6))
logs = {}

for label, alloc in strategies.items():
    result, events = simulate_riskdrip_v2(
        base_allocation_pct=alloc,
        rounds=1000,
        seed=41,
        log_events=True
    )
    plt.plot(result, label=label)
    logs[label] = events

plt.title("RiskDrip v2.0 - Convex Strategy with Cashouts & Cooldowns")
plt.xlabel("Rounds")
plt.ylabel("Portfolio Value ($)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Optional: Print rupture logs
for label, events in logs.items():
    print(f"\n=== {label} ===")
    for e in events:
        print(e)
