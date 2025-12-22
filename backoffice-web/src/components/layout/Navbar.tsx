import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Menu, User, LogOut, Settings, ChevronDown, Sun, Moon } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../theme/ThemeProvider';
import { NotificationsDropdown } from './NotificationsDropdown';

interface NavbarProps {
  onMenuClick: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const { mode, toggleTheme } = useTheme();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  const handleLogout = async () => {
    await logout();
  };

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Get user display name
  const getUserDisplayName = () => {
    if (!user) return 'Utilisateur';
    if (user.role === 'ADMIN') return 'System Administrator';
    return `${user.first_name} ${user.last_name}`;
  };

  const getUserRole = () => {
    if (!user) return '';
    const roleLabels: Record<string, string> = {
      ADMIN: 'Administrateur',
      RESPONSABLE_LOGISTIQUE: 'Responsable Logistique',
      OPERATEUR_USINE: 'Opérateur Usine',
      CHAUFFEUR: 'Chauffeur',
    };
    return roleLabels[user.role] || user.role;
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-4 md:px-6">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="mr-4 inline-flex items-center justify-center rounded-md p-2 hover:bg-accent md:hidden"
        >
          <Menu className="h-6 w-6" />
        </button>

        {/* Logo */}
        <div className="flex items-center space-x-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <span className="text-lg font-bold">G</span>
          </div>
          <span className="hidden text-lg font-semibold md:inline-block">
            GazTracker
          </span>
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Right side actions */}
        <div className="flex items-center gap-2">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-accent transition-colors"
              title={mode === 'light' ? 'Mode sombre' : 'Mode clair'}
            >
              {mode === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>

          {/* Notifications dropdown */}
          <NotificationsDropdown />

          {/* Preferences (Coming soon) */}
          <button
            className="p-2 rounded-lg hover:bg-accent transition-colors opacity-50 cursor-not-allowed"
            title="Préférences (à venir)"
            disabled
          >
            <Settings className="h-5 w-5" />
          </button>

          {/* User profile dropdown */}
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center gap-2 rounded-lg px-3 py-2 hover:bg-accent transition-colors"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                <User className="h-4 w-4" />
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium">{getUserDisplayName()}</p>
                <p className="text-xs text-muted-foreground">{getUserRole()}</p>
              </div>
              <ChevronDown className="h-4 w-4 text-muted-foreground hidden md:block" />
            </button>

            {/* User dropdown menu */}
            {isUserMenuOpen && (
              <div className="absolute right-0 mt-2 w-56 rounded-lg border bg-card shadow-lg z-50">
                <div className="p-3 border-b">
                  <p className="font-medium">{getUserDisplayName()}</p>
                  <p className="text-sm text-muted-foreground">{user?.email}</p>
                  <p className="text-xs text-muted-foreground mt-1">{getUserRole()}</p>
                </div>
                <div className="py-1">
                  <Link
                    to="/profile"
                    onClick={() => setIsUserMenuOpen(false)}
                    className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-accent transition-colors"
                  >
                    <User className="h-4 w-4" />
                    Mon profil
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2 px-4 py-2 text-sm hover:bg-accent transition-colors text-red-600"
                  >
                    <LogOut className="h-4 w-4" />
                    Déconnexion
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
