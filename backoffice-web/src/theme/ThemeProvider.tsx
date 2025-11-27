import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  muted: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface Theme {
  mode: 'light' | 'dark';
  colors: ThemeColors;
  fonts?: {
    sans?: string;
    mono?: string;
  };
}

interface ThemeContextType {
  theme: Theme;
  mode: 'light' | 'dark';
  setMode: (mode: 'light' | 'dark') => void;
  toggleTheme: () => void;
  setThemeColors: (colors: Partial<ThemeColors>) => void;
  resetTheme: () => void;
  applyLogoTheme: () => Promise<void>;
}

const defaultTheme: Theme = {
  mode: 'light',
  colors: {
    primary: '#3b82f6',
    secondary: '#8b5cf6',
    accent: '#10b981',
    muted: '#94a3b8',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
  },
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    // Load from localStorage
    const saved = localStorage.getItem('gaztracker-theme');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return defaultTheme;
      }
    }
    return defaultTheme;
  });

  const [mode, setModeState] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('gaztracker-theme-mode');
    return (saved as 'light' | 'dark') || 'light';
  });

  // Apply theme to CSS variables
  useEffect(() => {
    const root = document.documentElement;
    
    // Apply colors as CSS variables
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });

    // Apply mode
    if (mode === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Save to localStorage
    localStorage.setItem('gaztracker-theme', JSON.stringify(theme));
    localStorage.setItem('gaztracker-theme-mode', mode);
  }, [theme, mode]);

  const setMode = (newMode: 'light' | 'dark') => {
    setModeState(newMode);
    setTheme(prev => ({ ...prev, mode: newMode }));
  };

  const toggleTheme = () => {
    setMode(mode === 'light' ? 'dark' : 'light');
  };

  const setThemeColors = (colors: Partial<ThemeColors>) => {
    setTheme(prev => ({
      ...prev,
      colors: { ...prev.colors, ...colors },
    }));
  };

  const resetTheme = () => {
    setTheme(defaultTheme);
    setModeState('light');
    localStorage.removeItem('gaztracker-theme');
    localStorage.removeItem('gaztracker-theme-mode');
  };

  const applyLogoTheme = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/theme/extract-from-logo', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.suggested_theme) {
          setThemeColors(data.suggested_theme);
        }
      }
    } catch (error) {
      console.error('Error applying logo theme:', error);
    }
  };

  return (
    <ThemeContext.Provider
      value={{
        theme,
        mode,
        setMode,
        toggleTheme,
        setThemeColors,
        resetTheme,
        applyLogoTheme,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
