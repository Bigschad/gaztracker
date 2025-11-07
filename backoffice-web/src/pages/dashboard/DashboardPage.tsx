import { useQuery } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/common';
import { reportService } from '../../services/api';
import { Package, Truck, Bell, TrendingUp } from 'lucide-react';
import { formatNumber, formatPercentage } from '../../utils/formatters';

const DashboardPage = () => {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => reportService.getDashboard(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <p>Chargement...</p>
      </div>
    );
  }

  const stats = [
    {
      title: 'Palettes Total',
      value: formatNumber(dashboard?.palette_stats.total),
      icon: Package,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Expéditions en cours',
      value: formatNumber(dashboard?.expedition_stats.in_transit),
      icon: Truck,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Notifications',
      value: formatNumber(dashboard?.notification_stats.total),
      icon: Bell,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Taux d\'utilisation',
      value: formatPercentage(dashboard?.palette_stats.utilization_rate),
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Tableau de bord</h1>
        <p className="text-muted-foreground">
          Vue d'ensemble de votre système GazTracker
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.title}</p>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.bgColor}`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Alerts */}
      {dashboard && dashboard.alerts && (
        <div className="grid gap-4 md:grid-cols-3 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Expéditions en retard</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-red-600">
                {dashboard.alerts.delayed_expeditions}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Validations en attente</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-yellow-600">
                {dashboard.alerts.pending_validations}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Notifications échouées</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-orange-600">
                {dashboard.alerts.failed_notifications}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Health Score */}
      {dashboard && (
        <Card>
          <CardHeader>
            <CardTitle>Santé du système</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all"
                    style={{ width: `${dashboard.health_score}%` }}
                  />
                </div>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold">{dashboard.health_score}%</p>
                <p className="text-sm text-muted-foreground">
                  {dashboard.health_status}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DashboardPage;
