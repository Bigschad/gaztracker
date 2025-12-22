import { useEffect } from 'react';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastProps {
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
  onClose: () => void;
}

const Toast = ({ type, title, message, duration = 5000, onClose }: ToastProps) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const icons = {
    success: <CheckCircle className="w-5 h-5 text-green-500" />,
    error: <AlertCircle className="w-5 h-5 text-red-500" />,
    warning: <AlertTriangle className="w-5 h-5 text-yellow-500" />,
    info: <Info className="w-5 h-5 text-blue-500" />,
  };

  const bgColors = {
    success: 'bg-green-50 border-green-200',
    error: 'bg-red-50 border-red-200',
    warning: 'bg-yellow-50 border-yellow-200',
    info: 'bg-blue-50 border-blue-200',
  };

  const textColors = {
    success: 'text-green-900',
    error: 'text-red-900',
    warning: 'text-yellow-900',
    info: 'text-blue-900',
  };

  return (
    <div
      className={`fixed top-4 right-4 z-50 flex items-start p-4 border rounded-lg shadow-lg max-w-md animate-in slide-in-from-top-5 ${bgColors[type]}`}
      role="alert"
    >
      <div className="flex-shrink-0">{icons[type]}</div>
      <div className="ml-3 flex-1">
        {title && (
          <h3 className={`text-sm font-semibold ${textColors[type]}`}>{title}</h3>
        )}
        <p className={`text-sm ${title ? 'mt-1' : ''} ${textColors[type]}`}>{message}</p>
      </div>
      <button
        onClick={onClose}
        className={`ml-3 flex-shrink-0 inline-flex ${textColors[type]} hover:opacity-70 focus:outline-none`}
        aria-label="Fermer"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
};

export default Toast;
