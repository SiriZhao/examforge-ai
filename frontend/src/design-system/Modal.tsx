import { useEffect, useId, useRef, type ReactNode } from 'react';
import { Icon } from './Icon';
export function Modal({open, title, onClose, children}: {open: boolean; title: string; onClose: () => void; children: ReactNode}) {
  const ref = useRef<HTMLDialogElement>(null); const id = useId(); const closeRef = useRef(onClose); closeRef.current = onClose;
  useEffect(() => {
    const dialog = ref.current; if (!open || !dialog) return;
    const trigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    dialog.showModal();
    return () => {dialog.close(); trigger?.focus();};
  }, [open]);
  return <dialog ref={ref} className="settings-dialog" aria-labelledby={id} onCancel={e => {e.preventDefault();closeRef.current();}}>
    <div className="section-heading"><h2 id={id}>{title}</h2><button type="button" className="icon-button" aria-label="关闭弹窗" onClick={onClose}><Icon name="close"/></button></div>{open && children}
  </dialog>;
}
