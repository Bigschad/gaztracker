import { useState, useCallback } from 'react';
import Toast, { ToastType } from '../components/common/Toast';

interface ToastConfig {
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
}

export const useToast = () => {
  const [toast, setToast] = useState<ToastConfig | null>(null);

  const showToast = useCallback((config: ToastConfig) => {
    setToast(config);
  }, []);

  const hideToast = useCallback(() => {
    setToast(null);
  }, []);

  const ToastContainer = useCallback(() => {
    if (!toast) return null;

    return (
      <Toast
        type={toast.type}
        title={toast.title}
        message={toast.message}
        duration={toast.duration}
        onClose={hideToast}
      />
    );
  }, [toast, hideToast]);

  return {
    showToast,
    hideToast,
    ToastContainer,
  };
};
