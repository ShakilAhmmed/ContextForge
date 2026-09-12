import { useMemo, useState } from "react";

import type { ChunkPoint } from "../../api/types";

const WIDTH = 800;
const HEIGHT = 440;
const PADDING = 24;
const POINT_RADIUS = 4;
const POINT_RADIUS_HOVER = 7;

function scale(points: ChunkPoint[]) {
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const spanX = maxX - minX || 1;
  const spanY = maxY - minY || 1;

  return (point: ChunkPoint) => ({
    cx: PADDING + ((point.x - minX) / spanX) * (WIDTH - 2 * PADDING),
    cy: HEIGHT - PADDING - ((point.y - minY) / spanY) * (HEIGHT - 2 * PADDING),
  });
}

export function ChunkScatterPlot({ points }: { points: ChunkPoint[] }) {
  const [hovered, setHovered] = useState<number | null>(null);
  const project = useMemo(() => scale(points), [points]);

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="w-full"
        role="img"
        aria-label="Chunk embedding scatter plot"
      >
        <rect x={0} y={0} width={WIDTH} height={HEIGHT} className="fill-slate-50" />
        {points.map((point, index) => {
          const { cx, cy } = project(point);
          const isHovered = hovered === index;
          return (
            <circle
              key={index}
              cx={cx}
              cy={cy}
              r={isHovered ? POINT_RADIUS_HOVER : POINT_RADIUS}
              className={`cursor-pointer transition-all duration-150 ${
                isHovered ? "fill-indigo-600" : "fill-indigo-400/70"
              }`}
              onMouseEnter={() => setHovered(index)}
              onMouseLeave={() => setHovered((current) => (current === index ? null : current))}
            />
          );
        })}
      </svg>

      {hovered !== null && (
        <div
          className="pointer-events-none absolute z-10 w-72 rounded-lg bg-slate-900 p-3 text-xs text-white shadow-lg"
          style={{
            left: `${(project(points[hovered]).cx / WIDTH) * 100}%`,
            top: `${(project(points[hovered]).cy / HEIGHT) * 100}%`,
            transform: "translate(-50%, -115%)",
          }}
        >
          <p className="mb-1 font-semibold text-slate-300">Chunk {hovered + 1}</p>
          <p className="line-clamp-6 whitespace-pre-wrap">{points[hovered].text}</p>
        </div>
      )}
    </div>
  );
}
