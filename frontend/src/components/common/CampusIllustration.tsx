export function CampusIllustration() {
  return (
    <svg viewBox="0 0 400 260" className="h-full w-full" fill="none">
      <line x1="0" y1="210" x2="400" y2="210" stroke="#1c2333" strokeWidth="1.5" strokeDasharray="4 4" />

      <polygon points="40,140 80,100 120,140" fill="#e8b4ac" stroke="#1c2333" strokeWidth="2" />
      <rect x="50" y="140" width="60" height="60" fill="#fbf8f0" stroke="#1c2333" strokeWidth="2" />
      <ellipse cx="80" cy="170" rx="10" ry="14" fill="none" stroke="#1c2333" strokeWidth="2" />
      <line x1="80" y1="92" x2="80" y2="100" stroke="#1c2333" strokeWidth="2" />
      <polygon points="80,88 92,92 80,96" fill="#5c7a5c" stroke="#1c2333" strokeWidth="1.5" />
      <circle cx="30" cy="185" r="16" fill="#dce6da" stroke="#1c2333" strokeWidth="1.5" />

      <rect x="150" y="120" width="90" height="80" fill="#fbf8f0" stroke="#1c2333" strokeWidth="2" />
      <path d="M150 120 Q195 75 240 120 Z" fill="#f4e4a8" stroke="#1c2333" strokeWidth="2" />
      <circle cx="195" cy="103" r="11" fill="#fbf8f0" stroke="#1c2333" strokeWidth="2" />
      <line x1="195" y1="103" x2="195" y2="96" stroke="#1c2333" strokeWidth="1.5" />
      <line x1="195" y1="103" x2="200" y2="103" stroke="#1c2333" strokeWidth="1.5" />
      <rect x="168" y="150" width="14" height="14" fill="none" stroke="#1c2333" strokeWidth="1.5" />
      <rect x="208" y="150" width="14" height="14" fill="none" stroke="#1c2333" strokeWidth="1.5" />
      <rect x="185" y="170" width="20" height="30" fill="none" stroke="#1c2333" strokeWidth="1.5" />

      <polygon points="270,140 310,105 350,140" fill="#dce6da" stroke="#1c2333" strokeWidth="2" />
      <rect x="280" y="140" width="60" height="60" fill="#fbf8f0" stroke="#1c2333" strokeWidth="2" />
      <rect x="292" y="158" width="12" height="14" fill="none" stroke="#1c2333" strokeWidth="1.5" />
      <rect x="316" y="158" width="12" height="14" fill="none" stroke="#1c2333" strokeWidth="1.5" />
      <circle cx="360" cy="190" r="14" fill="#dce6da" stroke="#1c2333" strokeWidth="1.5" />

      <path
        d="M20 225 Q100 200 150 215 T260 205"
        stroke="#5c7a5c"
        strokeWidth="2.5"
        strokeDasharray="1 8"
        strokeLinecap="round"
        fill="none"
      />

      <g transform="translate(110,196)">
        <circle cx="0" cy="0" r="6" fill="#1c2333" />
        <line x1="0" y1="6" x2="0" y2="22" stroke="#1c2333" strokeWidth="3" strokeLinecap="round" />
        <line x1="0" y1="12" x2="-8" y2="19" stroke="#1c2333" strokeWidth="3" strokeLinecap="round" />
        <line x1="0" y1="12" x2="8" y2="8" stroke="#1c2333" strokeWidth="3" strokeLinecap="round" />
        <line x1="0" y1="22" x2="-6" y2="34" stroke="#1c2333" strokeWidth="3" strokeLinecap="round" />
        <line x1="0" y1="22" x2="6" y2="34" stroke="#1c2333" strokeWidth="3" strokeLinecap="round" />
      </g>

      <g transform="translate(270,190)">
        <line x1="0" y1="0" x2="0" y2="30" stroke="#1c2333" strokeWidth="2.5" />
        <rect x="0" y="-4" width="34" height="14" fill="#f5f1e8" stroke="#1c2333" strokeWidth="2" />
        <polygon points="34,-4 42,3 34,10" fill="#f5f1e8" stroke="#1c2333" strokeWidth="2" />
        <text x="6" y="7" fontFamily="Georgia, serif" fontSize="9" fontWeight="bold" fill="#1c2333">
          MOIRA
        </text>
      </g>
    </svg>
  );
}
