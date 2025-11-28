import { useQuery } from '@tanstack/react-query';
import { groupeService } from '../../services/api';
import { Building2 } from 'lucide-react';

export const GroupeLogo = () => {
  // Fetch the first active group (assuming single group per deployment)
  const { data: groupes } = useQuery({
    queryKey: ['groupes-active'],
    queryFn: () => groupeService.list({ skip: 0, limit: 1, is_active: true }),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  const groupe = groupes?.[0];

  if (!groupe) {
    return null;
  }

  return (
    <div className="px-4 py-6 border-b">
      <div className="flex flex-col items-center gap-3">
        {/* Logo */}
        <div className="flex items-center justify-center w-20 h-20 rounded-lg bg-primary/10 overflow-hidden">
          {groupe.logo_url ? (
            <img
              src={groupe.logo_url?.startsWith('http') ? groupe.logo_url : `${import.meta.env.VITE_API_URL || ''}${groupe.logo_url}`}
              alt={groupe.name}
              className="w-full h-full object-contain p-2"
              onError={(e) => {
                // Fallback to icon if image fails to load
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                const parent = target.parentElement;
                if (parent) {
                  const icon = document.createElement('div');
                  icon.innerHTML = '<svg class="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>';
                  parent.appendChild(icon.firstChild!);
                }
              }}
            />
          ) : (
            <Building2 className="w-10 h-10 text-primary" />
          )}
        </div>

        {/* Group Name */}
        <div className="text-center">
          <p className="text-sm font-semibold text-foreground line-clamp-2">
            {groupe.name}
          </p>
          {groupe.code && (
            <p className="text-xs text-muted-foreground">
              {groupe.code}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

