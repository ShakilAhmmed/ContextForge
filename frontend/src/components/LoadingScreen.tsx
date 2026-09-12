export function LoadingScreen() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50">
      <svg width="72" height="72" viewBox="0 0 72 72" fill="none" role="img" aria-label="Loading">
        <defs>
          <linearGradient id="loading-gradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#4f46e5" />
            <stop offset="100%" stopColor="#7c3aed" />
          </linearGradient>
        </defs>
        <g>
          <circle cx="36" cy="36" r="6" fill="url(#loading-gradient)">
            <animate
              attributeName="opacity"
              values="1;0.25;1"
              dur="1.2s"
              begin="0s"
              repeatCount="indefinite"
            />
          </circle>
          <circle
            cx="36"
            cy="36"
            r="6"
            fill="url(#loading-gradient)"
            transform="rotate(120 36 36) translate(0 -22)"
          >
            <animate
              attributeName="opacity"
              values="1;0.25;1"
              dur="1.2s"
              begin="0.4s"
              repeatCount="indefinite"
            />
          </circle>
          <circle
            cx="36"
            cy="36"
            r="6"
            fill="url(#loading-gradient)"
            transform="rotate(240 36 36) translate(0 -22)"
          >
            <animate
              attributeName="opacity"
              values="1;0.25;1"
              dur="1.2s"
              begin="0.8s"
              repeatCount="indefinite"
            />
          </circle>
          <animateTransform
            attributeName="transform"
            attributeType="XML"
            type="rotate"
            from="0 36 36"
            to="360 36 36"
            dur="2.4s"
            repeatCount="indefinite"
          />
        </g>
      </svg>
      <p className="animate-fade-in text-sm text-slate-400">Loading…</p>
    </div>
  );
}
