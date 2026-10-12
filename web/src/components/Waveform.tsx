import { LineChart, Line, ReferenceArea, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { PHASE_COLORS } from "../lib/types";

interface Props {
  wristY: (number | null)[];
  wristTimesSec?: number[];
  phaseBoundariesSec?: Record<string, [number, number]>;
  phaseBoundaries: Record<string, [number, number]>;
}

export function Waveform({ wristY, phaseBoundaries, wristTimesSec, phaseBoundariesSec }: Props) {
  const useSeconds = !!phaseBoundariesSec && wristTimesSec?.length === wristY.length;
  const data = wristY.map((y, i) => ({ x: useSeconds ? wristTimesSec[i] : i, y }));
  const boundaries = useSeconds ? phaseBoundariesSec : phaseBoundaries;

  return (
    <div style={{ height: 120 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 6, right: 4, bottom: 0, left: 4 }}>
          <XAxis hide type="number" dataKey="x" domain={["dataMin", "dataMax"]} />
          <YAxis hide reversed domain={["dataMin", "dataMax"]} />
          {Object.entries(boundaries).map(([phase, [lo, hi]]) => (
            <ReferenceArea
              key={phase}
              x1={lo}
              x2={hi}
              fill={PHASE_COLORS[phase] ?? "var(--steel)"}
              fillOpacity={0.14}
              stroke="none"
            />
          ))}
          <Line type="linear" dataKey="y" stroke="var(--teal)" strokeWidth={2.4} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
