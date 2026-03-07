#!/usr/bin/env python3
"""
LinkedIn Queens board detector.
Monitors screen, detects the game grid, outputs a color-numbered board.

Install deps:
    pip install mss opencv-python numpy
"""

import time
import numpy as np
import cv2
import mss


# ── Screen capture ────────────────────────────────────────────────────────────

def capture_screen(sct):
    monitor = sct.monitors[1]
    shot = sct.grab(monitor)
    img = np.array(shot)
    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)


# ── Grid detection ────────────────────────────────────────────────────────────

def find_queens_grid(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / h if h > 0 else 0
        area = w * h
        if 0.85 < aspect < 1.15 and area > 40_000 and w > 200:
            candidates.append((x, y, w, h, area))

    if not candidates:
        return None

    candidates.sort(key=lambda c: c[4], reverse=True)
    x, y, w, h, _ = candidates[0]
    return (x, y, w, h)


# ── Size detection ────────────────────────────────────────────────────────────

def count_lines_in_slice(slice_1d, dark_thresh=60):
    is_dark = slice_1d < dark_thresh
    n, in_line = 0, False
    for dark in is_dark:
        if not in_line and dark:
            in_line = True
            n += 1
        elif in_line and not dark:
            in_line = False
    return n


def detect_grid_size(img, bbox):
    x, y, w, h = bbox
    pad_x, pad_y = int(w * 0.02), int(h * 0.02)
    region = cv2.cvtColor(
        img[y+pad_y : y+h-pad_y, x+pad_x : x+w-pad_x],
        cv2.COLOR_RGB2GRAY
    )
    rh, rw = region.shape

    row_counts = [
        count_lines_in_slice(region[int(rh * f), :])
        for f in [0.2, 0.35, 0.5, 0.65, 0.8]
    ]
    n = int(np.median(row_counts)) + 1

    #print(f"row_counts: {row_counts}, n={n}", flush=True)
    return n if 5 <= n <= 12 else None


# ── Board extraction ──────────────────────────────────────────────────────────

def sample_cell(img, cx, cy, cell_w, cell_h):
    # Inner 40% of cell only
    rx = max(1, int(cell_w * 0.2))
    ry = max(1, int(cell_h * 0.2))
    patch = img[cy-ry:cy+ry, cx-rx:cx+rx]
    if patch.size == 0:
        return np.zeros(3)
    # Median per channel — robust to edge bleed pixels
    return np.median(patch.reshape(-1, 3), axis=0)


def extract_board(img, bbox, n):
    x, y, w, h = bbox
    cell_w, cell_h = w / n, h / n

    samples = []
    for row in range(n):
        for col in range(n):
            cx = int(x + (col + 0.5) * cell_w)
            cy = int(y + (row + 0.5) * cell_h)
            samples.append(sample_cell(img, cx, cy, cell_w, cell_h))

    samples = np.array(samples)

    # Quantize to collapse near-identical colors (e.g. orange variants)
    # then get unique quantized colors as palette candidates
    quantized = (samples / 15).astype(int)
    unique_quantized = np.unique(quantized, axis=0).astype(float) * 15

    # Farthest-point on the reduced unique set
    mean = unique_quantized.mean(axis=0)
    start_idx = np.argmax(np.linalg.norm(unique_quantized - mean, axis=1))
    palette = [unique_quantized[start_idx]]
    for _ in range(min(n - 1, len(unique_quantized) - 1)):
        dists = np.min([np.linalg.norm(unique_quantized - p, axis=1) for p in palette], axis=0)
        palette.append(unique_quantized[np.argmax(dists)])

    palette = np.array(palette)

    # Assign each cell to nearest palette color
    labels = []
    for color in samples:
        dists = np.linalg.norm(palette - color, axis=1)
        labels.append(str(np.argmin(dists) + 1))

    board = []
    for row in range(n):
        board.append(labels[row * n : (row + 1) * n])
    return board


# ── Output ────────────────────────────────────────────────────────────────────

def print_board(board):
    for i,row in enumerate(board):
        print(row, flush=True)


def boards_equal(a, b):
    if a is None or b is None:
        return False
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return False
    return all(a[r][c] == b[r][c] for r in range(len(a)) for c in range(len(a[r])))


# ── Main loop ─────────────────────────────────────────────────────────────────

def main(poll_interval=0):
    print("Monitoring screen for LinkedIn Queens puzzle... (Ctrl+C to stop)\n", flush=True)
    last_board = None

    with mss.mss() as sct:
        while True:
            img = capture_screen(sct)

            bbox = find_queens_grid(img)
            if bbox is None:
                time.sleep(poll_interval)
                continue

            n = detect_grid_size(img, bbox)
            if n is None:
                time.sleep(poll_interval)
                continue

            board = extract_board(img, bbox, n)

            if not boards_equal(board, last_board):
                print(f"── Detected {n}×{n} Queens board ──", flush=True)
                print_board(board)
                print(flush=True)
                last_board = board

            time.sleep(poll_interval)


if __name__ == "__main__":
    main()