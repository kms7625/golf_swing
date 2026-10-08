import { LineChart, Line, ReferenceArea, ResponsiveContainer, YAxis } from "recharts";
import { PHASE_COLORS } from "../lib/types";

interface Props {
  wristY: number[];
  phaseBoundaries: Record<string, [number, number]>;
}

export function Waveform({ wristY, phaseBoundaries }: Props) {
  const data = wristY.map((y, i) => ({ i, y }));

  return (
    <div style={{ height: 120 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 6, right: 4, bottom: 0, left: 4 }}>
          <YAxis hide reversed domain={["dataMin", "dataMax"]} />
          {Object.entries(phaseBoundaries).map(([phase, [lo, hi]]) => (
            <ReferenceArea
              key={phase}
              x1={lo}
              x2={hi}
              fill={PHASE_COLORS[phase] ?? "var(--steel)"}
              fillOpacity={0.14}
              stroke="none"
            />
          ))}
          <Line type="monotone" dataKey="y" stroke="var(--teal)" strokeWidth={2.4} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
