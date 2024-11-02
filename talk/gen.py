from chalk import *
import chalk
import numpy as np
import random
from functools import partial

T = 6


def rollout(t, v, d=1):
    n = v
    for t2 in range(t, T):
        n = n + (random.random() - 0.5) / d
        yield (t2 + 1, n)


def expand(t, v):
    if t == T:
        return []
    return [(t + 1, v + 1), (t + 1, v - 1)]


def rwalk1(t, v, d=1):
    if t == T:
        return []
    return [(t + 1, v + (random.random() - 0.5) / d)]


def rwalk(t, v, d=5):
    if t == T:
        return []
    return [(t + 1, v + random.random() / d), (t + 1, v - random.random() / d)]


def bwalk(t, v, d=5):
    if t == T:
        return []
    return [(t + 1, v + 1 if random.random() > 0.5 else -1)]


def chain(t, v):
    if t == 5:
        return []
    return [(t + 1, v)]


def opt(t, v):
    if t == 3:
        return []
    return [(t + 1, 0)]


def nonopt(t, v):
    if t == T:
        return []
    if t >= 4:
        [(t + 1, 0)]
    return [(t + 1, v + 1 if t < 2 else v - 1)]


def make_chain(expand):
    queue = [(0, 0)]
    # nodes, edges = [], []
    nodes, edges, roll = [], [], [((0, 0), (0, 0.1))]
    while queue:
        (t, v) = queue[0]
        queue = queue[1:]
        new = expand(t, v)
        queue += new
        for n in new:
            edges.append(((t, v), n))
        nodes.append((t, v))

    return nodes, edges, roll


def multi(ls):
    n, e, r = [], [], []
    for n1, e1, r1 in ls:
        n.extend(n1)
        e.extend(e1)
        r.extend(r1)
    return n, e, r


def make_beam(expand, end=T, beam=5):
    queue = {}
    queue[0] = [(0, 0)]
    nodes, edges, roll = [], [], [((0, 0), (0, 0.1))]
    for t in range(end):
        random.shuffle(queue[t])
        queue[t] = queue[t][:beam]
        queue[t + 1] = []
        for t, v in queue[t]:
            if t < end - 1:
                new = expand(t, v)
                queue[t + 1] += new
                for n in new:
                    edges.append(((t, v), n))
            nodes.append((t, v))

            if t == end - 1 and t < T:
                # rollout
                for _ in range(5):
                    c = (t, v)
                    for c2 in rollout(t, v):
                        roll.append((c, c2))
                        c = c2
    return nodes, edges, roll


def draw(nodes, edges, rollout_edges, name, csize=0.2, lwidth=0.5, draw_final=True):
    ns = list(nodes)
    nodes = np.array([(t, v) for (t, v) in ns if t <= T - 1])
    finaln = np.array([(t, int(v * 2) / 2) for (t, v) in ns if t == T])
    edges = np.array(edges)
    redges = np.array(rollout_edges)

    c = circle(csize).line_width(0)
    pts = tx.to_P2(nodes)
    z = c.translate_by(pts)

    if finaln.shape[0] > 0:
        pts = tx.to_P2(finaln)
        y = c.translate_by(pts)
        y = y.concat().fill_color("green").fill_opacity(0.2)
    else:
        y = empty()

    lines = (
        Path.from_points([tx.to_P2(edges[:, 0]), tx.to_P2(edges[:, 1])], False)
        .stroke()
        .line_width(lwidth)
    )
    lines2 = (
        Path.from_points([tx.to_P2(redges[:, 0]), tx.to_P2(redges[:, 1])], False)
        .stroke()
        .line_width(lwidth)
        .line_color("gray")
    )
    if draw_final:
        final = (
            rectangle(0.3, 1)
            .line_width(lwidth)
            .translate(T, 0)
            .fill_color("purple")
            .fill_opacity(0.5)
            .line_width(0)
        )
    else:
        final = empty()
    base = (
        lines.concat()
        + lines2.concat()
        + final
        + z.concat().fill_color("white").line_width(0)
        + z.concat().fill_color("red").fill_opacity(0.2)
        + y
        + c.fill_color("blue")
    )
    base.render(name, 512)
    return base


draw(*make_chain(expand), "images/expand.png")
draw(*make_chain(chain), "images/chain.png")
draw(*make_chain(rwalk1), "images/ancestral.png", draw_final=False)

# vcat([draw(make_chain(partial(rwalk1, d=1)), "") for _ in range(3)]).render(
#    "images/reject1.png", 512
# )

draw(
    *multi([make_chain(opt), make_chain(nonopt)]),
    "images/stream.png",
    draw_final=True,
)


draw(
    *multi([make_chain(partial(rwalk1, d=1)) for _ in range(10)]),
    "images/bwalk.png",
    draw_final=False,
)

draw(
    *multi([make_chain(partial(rwalk1, d=1)) for _ in range(10)]),
    "images/reject.png",
    draw_final=True,
)

draw(*make_beam(partial(rwalk, d=1), end=T + 1), "images/beam.png", draw_final=False)

draw(*make_beam(partial(rwalk, d=1), beam=4, end=T - 1), "images/beamroll.png")

draw(*make_beam(partial(rwalk1, d=1), beam=1, end=T - 2), "images/mcroll.png")

draw(*make_chain(rwalk), "images/random.png", csize=0.1, lwidth=0.2)