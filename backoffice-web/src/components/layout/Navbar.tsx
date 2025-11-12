import { Menu, Bell, User, LogOut, Sun, Moon } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../theme/ThemeProvider';

interface NavbarProps {
  onMenuClick: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const handleLogout = async () => {
    await logout();
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
        <div className="flex items-center space-x-2">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="inline-flex items-center justify-center rounded-md p-2 hover:bg-accent"
            title={theme === 'light' ? 'Mode sombre' : 'Mode clair'}
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>

          {/* Notifications */}
          <button
            className="inline-flex items-center justify-center rounded-md p-2 hover:bg-accent"
            title="Notifications"
          >
            <Bell className="h-5 w-5" />
          </button>

          {/* User menu */}
          <div className="relative group">
            <button className="flex items-center space-x-2 rounded-md p-2 hover:bg-accent">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
                <User className="h-4 w-4" />
              </div>
              <span className="hidden text-sm font-medium md:inline-block">
                {user ? `${user.first_name} ${user.last_name}` : ''}
              </span>
            </button>

            {/* Dropdown menu */}
            <div className="absolute right-0 mt-2 w-48 origin-top-right rounded-md bg-card shadow-lg ring-1 ring-black ring-opacity-5 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
              <div className="py-1">
                <div className="px-4 py-2 text-sm text-muted-foreground border-b">
                  <p className="font-medium text-foreground">
                    {user ? `${user.first_name} ${user.last_name}` : ''}
                  </p>
                  <p className="text-xs">{user?.email}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center px-4 py-2 text-sm text-foreground hover:bg-accent"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Déconnexion
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
