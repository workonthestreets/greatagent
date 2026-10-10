/* @license lucide-static ISC (https://lucide.dev). Glyph paths copied from Lucide; Mark is the Meridian quatrefoil. */
import type { ReactNode } from "react";

type IconProps = { size?: number; className?: string };

function Svg({ size = 18, className, children }: IconProps & { children: ReactNode }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"
      className={className} aria-hidden="true" focusable="false">
      {children}
    </svg>
  );
}

export const ArrowUpRight = (p: IconProps) => <Svg {...p}><path d="M7 7h10v10" /><path d="M7 17 17 7" /></Svg>;
export const Check = (p: IconProps) => <Svg {...p}><path d="M20 6 9 17l-5-5" /></Svg>;
export const X = (p: IconProps) => <Svg {...p}><path d="M18 6 6 18" /><path d="m6 6 12 12" /></Svg>;
export const Bell = (p: IconProps) => (
  <Svg {...p}>
    <path d="M10.268 21a2 2 0 0 0 3.464 0" />
    <path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326" />
  </Svg>
);
export const Send = (p: IconProps) => (
  <Svg {...p}>
    <path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z" />
    <path d="m21.854 2.147-10.94 10.939" />
  </Svg>
);
export const Phone = (p: IconProps) => (
  <Svg {...p}>
    <path d="M13.832 16.568a1 1 0 0 0 1.213-.303l.355-.465A2 2 0 0 1 17 15h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2A18 18 0 0 1 2 4a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v3a2 2 0 0 1-.8 1.6l-.468.351a1 1 0 0 0-.292 1.233 14 14 0 0 0 6.392 6.384" />
  </Svg>
);
export const Mail = (p: IconProps) => (
  <Svg {...p}><path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7" /><rect x="2" y="4" width="20" height="16" rx="2" /></Svg>
);
export const User = (p: IconProps) => (
  <Svg {...p}><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></Svg>
);
export const Clock = (p: IconProps) => <Svg {...p}><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></Svg>;
export const Pause = (p: IconProps) => (
  <Svg {...p}><rect x="14" y="3" width="5" height="18" rx="1" /><rect x="5" y="3" width="5" height="18" rx="1" /></Svg>
);

export const ArrowLeft = (p: IconProps) => <Svg {...p}><path d="m12 19-7-7 7-7" /><path d="M19 12H5" /></Svg>;
export const ArrowRight = (p: IconProps) => <Svg {...p}><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></Svg>;
export const Coins = (p: IconProps) => (
  <Svg {...p}>
    <circle cx="8" cy="8" r="6" /><path d="M18.09 10.37A6 6 0 1 1 10.34 18" /><path d="M7 6h1v4" /><path d="m16.71 13.88.7.71-2.82 2.82" />
  </Svg>
);
export const Medal = (p: IconProps) => (
  <Svg {...p}>
    <path d="M7.21 15 2.66 7.14a2 2 0 0 1 .13-2.2L4.4 2.8A2 2 0 0 1 6 2h12a2 2 0 0 1 1.6.8l1.6 2.14a2 2 0 0 1 .14 2.2L16.79 15" />
    <path d="M11 12 5.12 2.2" /><path d="m13 12 5.88-9.8" /><path d="M8 7h8" /><circle cx="12" cy="17" r="5" /><path d="M12 18v-2h-.5" />
  </Svg>
);
export const Award = (p: IconProps) => (
  <Svg {...p}>
    <path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526" />
    <circle cx="12" cy="8" r="6" />
  </Svg>
);
export const Trophy = (p: IconProps) => (
  <Svg {...p}>
    <path d="M10 14.66v1.626a2 2 0 0 1-.976 1.696A5 5 0 0 0 7 21.978" /><path d="M14 14.66v1.626a2 2 0 0 0 .976 1.696A5 5 0 0 1 17 21.978" />
    <path d="M18 9h1.5a1 1 0 0 0 0-5H18" /><path d="M4 22h16" /><path d="M6 9a6 6 0 0 0 12 0V3a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1z" />
    <path d="M6 9H4.5a1 1 0 0 1 0-5H6" />
  </Svg>
);
export const Truck = (p: IconProps) => (
  <Svg {...p}>
    <path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2" /><path d="M15 18H9" />
    <path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14" />
    <circle cx="17" cy="18" r="2" /><circle cx="7" cy="18" r="2" />
  </Svg>
);
export const Package = (p: IconProps) => (
  <Svg {...p}>
    <path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z" />
    <path d="M12 22V12" /><path d="m3.3 7 7.703 4.734a2 2 0 0 0 1.994 0L20.7 7" /><path d="m7.5 4.27 9 5.15" />
  </Svg>
);
export const Store = (p: IconProps) => (
  <Svg {...p}>
    <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7" /><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
    <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4" /><path d="M2 7h20" />
    <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7" />
  </Svg>
);

/** Medal catalogue icon names (hub `medals.icon`) to glyphs; unknown names fall back to the medal. */
const MEDAL_ICONS: Record<string, (p: IconProps) => JSX.Element> = {
  check: Check, user: User, x: X, pause: Pause, clock: Clock, award: Award, trophy: Trophy, coins: Coins, medal: Medal,
};
export const MedalIcon = ({ name, ...p }: IconProps & { name: string }) => (MEDAL_ICONS[name] ?? Medal)(p);

/** Meridian quatrefoil mark, coloured through currentColor. */
export function Mark({ size = 24 }: { size?: number }) {
  return (
    <svg viewBox="0 0 318.75 330.05" width={size} height={size} xmlns="http://www.w3.org/2000/svg" fill="currentColor" aria-hidden="true">
      <path d="M291.67,201.01c-13.58-10.8-27.47-22.56-41.49-35.34,14.38-13.45,28.65-25.98,42.68-37.63,33.14-27.51,34.7-77.82,3.3-107.29-.49-.46-.98-.92-1.47-1.38-31.88-29.92-82.82-24.47-107.81,11.4-8.47,12.16-17.63,24.58-27.51,37.17-9.88-12.58-19.04-25.01-27.51-37.17C106.87-5.1,55.94-10.54,24.06,19.38c-.49.46-.98.92-1.47,1.38-31.4,29.47-29.84,79.79,3.3,107.29,14.03,11.65,28.31,24.17,42.68,37.63-14.02,12.78-27.91,24.54-41.49,35.34-34.2,27.19-36.35,78.36-4.49,108.26l1.47,1.38c31.4,29.47,81.51,24.74,106.86-10.06,8.87-12.19,18.35-24.59,28.46-37.14,10.11,12.55,19.59,24.95,28.46,37.14,25.35,34.81,75.46,39.53,106.86,10.06l1.47-1.38c31.85-29.9,29.7-81.07-4.49-108.26Z" />
    </svg>
  );
}
