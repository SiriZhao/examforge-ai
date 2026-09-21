import { forwardRef, type ButtonHTMLAttributes } from 'react';
export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'text' | 'danger'; loading?: boolean };
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button({variant = 'primary', loading, disabled, className = '', children, type = 'button', ...props}, ref) {
  return <button {...props} ref={ref} type={type} disabled={disabled || loading} aria-busy={loading || undefined} className={`button ${variant === 'text' ? 'text-button' : variant} ${className}`}>{loading && <span className="button-spinner" aria-hidden="true"/>}{children}</button>;
});
