export function MentorCharacter() {
  return (
    <svg viewBox="0 0 240 290" fill="none" xmlns="http://www.w3.org/2000/svg" width={220} height={268}>
      <defs>
        <radialGradient id="mc-skin" cx="38%" cy="32%" r="62%">
          <stop offset="0%" stopColor="#F8D4B4" />
          <stop offset="55%" stopColor="#EEB888" />
          <stop offset="100%" stopColor="#CE8E5C" />
        </radialGradient>
        <linearGradient id="mc-suit" x1="15%" y1="0%" x2="85%" y2="100%">
          <stop offset="0%" stopColor="#1D3A6A" />
          <stop offset="100%" stopColor="#0B1D40" />
        </linearGradient>
        <linearGradient id="mc-lapel" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#162E58" />
          <stop offset="100%" stopColor="#0A1830" />
        </linearGradient>
        <linearGradient id="mc-hair" x1="10%" y1="0%" x2="90%" y2="100%">
          <stop offset="0%" stopColor="#3A1E10" />
          <stop offset="100%" stopColor="#170A04" />
        </linearGradient>
        <filter id="mc-drop" x="-20%" y="-10%" width="140%" height="130%">
          <feDropShadow dx="0" dy="6" stdDeviation="8" floodColor="#000B18" floodOpacity="0.55" />
        </filter>
      </defs>

      {/* Floor shadow */}
      <ellipse cx="120" cy="284" rx="62" ry="7" fill="#000B18" opacity="0.45" />

      {/* ── Body / Suit ── */}
      <path
        d="M25 290 L38 200 Q54 168 80 157 L108 149 L120 167 L132 149 L160 157 Q186 168 202 200 L215 290 Z"
        fill="url(#mc-suit)"
        filter="url(#mc-drop)"
      />
      {/* Left lapel */}
      <path d="M80 157 L108 149 L101 178 L62 192 Z" fill="url(#mc-lapel)" />
      {/* Right lapel */}
      <path d="M160 157 L132 149 L139 178 L178 192 Z" fill="url(#mc-lapel)" />
      {/* Shirt strip */}
      <path d="M108 149 L120 167 L132 149 L126 146 L120 161 L114 146 Z" fill="#DDE5F4" opacity="0.92" />
      {/* Tie */}
      <polygon points="116,149 124,149 127,194 120,201 113,194" fill="#1D4ED8" />
      <polygon points="113,147 127,147 124,149 116,149" fill="#1E40AF" />
      {/* Pocket square */}
      <path d="M57 178 L66 174 L70 182 L59 186 Z" fill="#DDE5F4" opacity="0.28" />
      {/* Suit buttons */}
      <circle cx="120" cy="218" r="2.5" fill="#0F1E3A" stroke="#1E3564" strokeWidth="0.8" />
      <circle cx="120" cy="233" r="2.5" fill="#0F1E3A" stroke="#1E3564" strokeWidth="0.8" />

      {/* ── Neck ── */}
      <rect x="108" y="134" width="24" height="20" rx="8" fill="url(#mc-skin)" />

      {/* ── Head ── */}
      <ellipse cx="120" cy="98" rx="47" ry="50" fill="url(#mc-skin)" filter="url(#mc-drop)" />
      {/* Face shadow right */}
      <ellipse cx="148" cy="102" rx="22" ry="30" fill="#B07040" opacity="0.09" />
      {/* Forehead highlight */}
      <ellipse cx="107" cy="76" rx="20" ry="15" fill="#FFF0DF" opacity="0.13" />

      {/* ── Ears ── */}
      <ellipse cx="73" cy="101" rx="7" ry="10" fill="url(#mc-skin)" />
      <ellipse cx="74" cy="101" rx="4" ry="7" fill="#C88058" opacity="0.35" />
      <ellipse cx="167" cy="101" rx="7" ry="10" fill="url(#mc-skin)" />
      <ellipse cx="166" cy="101" rx="4" ry="7" fill="#C88058" opacity="0.35" />

      {/* ── Hair ── */}
      <path d="M75 84 Q77 47 120 44 Q163 47 165 84 Q161 65 142 61 Q120 57 98 61 Q79 65 75 84 Z" fill="url(#mc-hair)" />
      <path d="M75 84 Q71 93 72 105 Q71 97 74 90 Z" fill="url(#mc-hair)" />
      <path d="M165 84 Q169 93 168 105 Q169 97 166 90 Z" fill="url(#mc-hair)" />
      {/* Hair highlight */}
      <path d="M96 56 Q113 51 133 55 Q117 53 102 57 Z" fill="#5C3320" opacity="0.45" />

      {/* ── Eyebrows ── */}
      <path d="M89 82 Q99 78 110 81" stroke="#3A1E10" strokeWidth="3" strokeLinecap="round" />
      <path d="M130 81 Q141 78 151 82" stroke="#3A1E10" strokeWidth="3" strokeLinecap="round" />

      {/* ── Eye whites ── */}
      <ellipse cx="100" cy="95" rx="10" ry="11" fill="white" />
      <ellipse cx="140" cy="95" rx="10" ry="11" fill="white" />
      {/* Irises */}
      <circle cx="101" cy="96" r="7" fill="#3D5070" />
      <circle cx="141" cy="96" r="7" fill="#3D5070" />
      {/* Pupils */}
      <circle cx="102" cy="97" r="4" fill="#0E1520" />
      <circle cx="142" cy="97" r="4" fill="#0E1520" />
      {/* Highlights */}
      <circle cx="104" cy="94" r="2" fill="white" />
      <circle cx="144" cy="94" r="2" fill="white" />

      {/* ── Glasses ── */}
      <rect x="87" y="86" width="26" height="18" rx="6" stroke="#3A5070" strokeWidth="1.5" fill="rgba(37,99,235,0.07)" />
      <rect x="127" y="86" width="26" height="18" rx="6" stroke="#3A5070" strokeWidth="1.5" fill="rgba(37,99,235,0.07)" />
      <path d="M113 95 Q120 93 127 95" stroke="#3A5070" strokeWidth="1.5" />
      <path d="M87 93 Q79 91 73 93" stroke="#3A5070" strokeWidth="1.5" />
      <path d="M153 93 Q161 91 167 93" stroke="#3A5070" strokeWidth="1.5" />

      {/* ── Nose ── */}
      <path d="M117 109 Q115 117 120 119 Q125 117 123 109" stroke="#B07848" strokeWidth="1.5" fill="none" strokeLinecap="round" opacity="0.65" />

      {/* ── Cheek blush ── */}
      <ellipse cx="86" cy="112" rx="14" ry="9" fill="#E8907A" opacity="0.11" />
      <ellipse cx="154" cy="112" rx="14" ry="9" fill="#E8907A" opacity="0.11" />

      {/* ── Smile ── */}
      <path d="M105 127 Q120 137 135 127" stroke="#B07050" strokeWidth="2.5" fill="none" strokeLinecap="round" />
    </svg>
  );
}
