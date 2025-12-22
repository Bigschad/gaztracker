import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Package,
  Users,
  Bell,
  BarChart3,
  X,
  Tag,
  Building2,
  UserCircle,
  Layers,
  Factory,
  Warehouse,
  FileText,
  ChevronDown,
  ChevronRight,
  Store,
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { GroupeLogo } from './GroupeLogo';
import clsx from 'clsx';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  adminOnly?: boolean;
}

interface NavSection {
  name: string;
  icon?: React.ComponentType<{ className?: string }>;
  items: NavItem[];
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { isAdmin } = useAuth();
  const [expandedSections, setExpandedSections] = useState<string[]>(['operations', 'organisation']);

  const toggleSection = (sectionName: string) => {
    setExpandedSections((prev) =>
      prev.includes(sectionName)
        ? prev.filter((s) => s !== sectionName)
        : [...prev, sectionName]
    );
  };

  // Top level items (no submenu)
  const topItems: NavItem[] = [
    {
      name: 'Tableau de bord',
      path: '/dashboard',
      icon: LayoutDashboard,
    },
    {
      name: 'Rapports',
      path: '/reports',
      icon: BarChart3,
    },
  ];

  // Sections with subitems
  const sections: NavSection[] = [
    {
      name: 'Opérations',
      items: [
        {
          name: 'Enlèvements',
          path: '/bons-enlevement',
          icon: FileText,
        },
        {
          name: 'Retours',
          path: '/bons-reception-retour',
          icon: FileText,
        },
        {
          name: 'Palettes',
          path: '/palettes',
          icon: Package,
        },
        {
          name: 'Tags RFID',
          path: '/rfid-tags',
          icon: Tag,
        },
      ],
    },
    {
      name: 'Organisation',
      items: [
        {
          name: 'Dépôts',
          path: '/depots',
          icon: Warehouse,
        },
        {
          name: 'Partenaires',
          path: '/partners',
          icon: Building2,
        },
        {
          name: 'Centres Remplisseurs',
          path: '/centres-remplisseurs',
          icon: Factory,
        },
        {
          name: 'Distributeurs',
          path: '/distributeurs',
          icon: Store,
        },
        {
          name: 'Groupes',
          path: '/groupes',
          icon: Layers,
        },
      ],
    },
    {
      name: 'Paramétrages',
      items: [
        {
          name: 'Contacts',
          path: '/contacts',
          icon: UserCircle,
        },
        {
          name: 'Utilisateurs',
          path: '/users',
          icon: Users,
          adminOnly: true,
        },
        {
          name: 'Réglages',
          path: '/settings',
          icon: Bell,
        },
      ],
    },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 transform border-r bg-card transition-transform duration-200 ease-in-out md:relative md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col">
          {/* Mobile close button */}
          <div className="flex h-16 items-center justify-between px-4 border-b md:hidden">
            <span className="text-lg font-semibold">Menu</span>
            <button
              onClick={onClose}
              className="inline-flex items-center justify-center rounded-md p-2 hover:bg-accent"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Group Logo */}
          <GroupeLogo />

          {/* Navigation */}
          <nav className="flex-1 space-y-1 overflow-y-auto p-4">
            {/* Top level items */}
            {topItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => onClose()}
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )
                  }
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                </NavLink>
              );
            })}

            {/* Sections with subitems */}
            {sections.map((section) => {
              const isExpanded = expandedSections.includes(section.name.toLowerCase());
              const filteredItems = section.items.filter((item) =>
                item.adminOnly ? isAdmin() : true
              );

              if (filteredItems.length === 0) return null;

              return (
                <div key={section.name} className="space-y-1">
                  {/* Section header */}
                  <button
                    onClick={() => toggleSection(section.name.toLowerCase())}
                    className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm font-semibold text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
                  >
                    <span>{section.name}</span>
                    {isExpanded ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </button>

                  {/* Section items */}
                  {isExpanded && (
                    <div className="ml-2 space-y-1">
                      {filteredItems.map((item) => {
                        const Icon = item.icon;
                        return (
                          <NavLink
                            key={item.path}
                            to={item.path}
                            onClick={() => onClose()}
                            className={({ isActive }) =>
                              clsx(
                                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                                isActive
                                  ? 'bg-primary text-primary-foreground'
                                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                              )
                            }
                          >
                            <Icon className="h-4 w-4" />
                            {item.name}
                          </NavLink>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </nav>
        </div>
      </aside>
    </>
  );
};

export { Sidebar };
