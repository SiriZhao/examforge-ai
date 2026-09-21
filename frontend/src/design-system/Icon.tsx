import type React from 'react';
export type IconName = 'spark' | 'home' | 'folder' | 'cards' | 'arrow' | 'upload' | 'file' | 'settings' | 'check' | 'book' | 'bolt' | 'target' | 'download' | 'close' | 'plus' | 'map' | 'trash';
export function Icon({name, size = 20}: {name: IconName; size?: number}) {
  const paths: Record<IconName, React.ReactNode> = {
    spark: <><path d="m12 3 2.3 6.7L21 12l-6.7 2.3L12 21l-2.3-6.7L3 12l6.7-2.3Z"/><path d="m20 2 .5 1.5L22 4l-1.5.5L20 6l-.5-1.5L18 4l1.5-.5Z"/></>,
    home: <><path d="m3 10 9-7 9 7v10H3Z"/><path d="M9 20v-7h6v7"/></>, folder: <path d="M3 6h7l2 3h9v11H3Zm0 0V4h7l2 2h9v3"/>,
    cards: <><rect x="7" y="6" width="13" height="15" rx="2"/><path d="M16 3H4v14M11 11h5m-5 4h3"/></>,
    arrow: <path d="M4 12h15m-6-6 6 6-6 6"/>, upload: <><path d="M12 16V3m-5 5 5-5 5 5M4 15v5h16v-5"/></>,
    file: <><path d="M5 3h9l5 5v13H5Zm9 0v6h5M9 13h6m-6 4h6"/></>,
    settings: <><path d="m9 3-1 3-3 1 1 3-2 2 2 2-1 3 3 1 1 3h6l1-3 3-1-1-3 2-2-2-2 1-3-3-1-1-3Z"/><circle cx="12" cy="12" r="3"/></>,
    check: <path d="m5 12 4 4L19 6"/>, book: <><path d="M12 6C8 3 4 4 3 4v15c4-1 7 0 9 2 2-2 5-3 9-2V4c-4-1-7 0-9 2Zm0 0v15"/></>,
    bolt: <path d="m13 2-9 12h7l-1 8 10-13h-7Z"/>, target: <><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></>,
    download: <><path d="M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4"/></>, close: <path d="m6 6 12 12M6 18 18 6"/>, plus: <path d="M12 5v14M5 12h14"/>,
    map: <><rect x="3" y="9" width="6" height="6" rx="1"/><path d="M9 12h5M14 5v14m0-14h4m-4 7h4m-4 7h4"/><path d="M18 3h3v4h-3Zm0 7h3v4h-3Zm0 7h3v4h-3Z"/></>,
    trash: <><path d="M4 7h16M9 7V4h6v3m3 0-1 14H7L6 7m4 4v6m4-6v6"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
