import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Select,
} from '../../components/common';
import { reportService } from '../../services/api';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  Package,
  Truck,
  TrendingUp,
  Download,
  MapPin,
} from 'lucide-react';
import { formatNumber, formatPercentage } from '../../utils/formatters';

type ReportTab = 'overview' | 'palettes' | 'expeditions' | 'performance' | 'destinations';

const ReportsPage = () => {
  const [activeTab, setActiveTab] = useState<ReportTab>('overview');
  const [daysFilter, setDaysFilter] = useState(30);

  // Dashboard overview
  const { data: dashboard, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: () => reportService.getDashboard(),
  });

  // Performance report
  const { data: performance, isLoading: performanceLoading } = useQuery({
    queryKey: ['performance-report', daysFilter],
    queryFn: () => reportService.getPerformanceReport({ days: daysFilter }),
  });

  // Top destinations
  const { data: topDestinations, isLoading: destinationsLoading } = useQuery({
    queryKey: ['top-destinations'],
    queryFn: () => reportService.getTopDestinations(10),
  });

  // User performance (unused for now but kept for future use)
  // const { data: userPerformance, isLoading: userPerformanceLoading } = useQuery({
  //   queryKey: ['user-performance'],
  //   queryFn: () => reportService.getUserPerformance(),
  // });

  const handleExport = async (type: 'expeditions' | 'palettes', format: 'csv' | 'json') => {
    try {
      const blob =
        type === 'expeditions'
          ? await reportService.exportExpeditions({ format })
          : await reportService.exportPalettes({ format });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${type}-export.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export error:', error);
      alert('Erreur lors de l\'export');
    }
  };

  const tabs = [
    { id: 'overview' as ReportTab, label: 'Vue d\'ensemble', icon: TrendingUp },
    { id: 'palettes' as ReportTab, label: 'Palettes', icon: Package },
    { id: 'expeditions' as ReportTab, label: 'Expéditions', icon: Truck },
    { id: 'performance' as ReportTab, label: 'Performance', icon: TrendingUp },
    { id: 'destinations' as ReportTab, label: 'Destinations', icon: MapPin },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Rapports</h1>
          <p className="text-muted-foreground">Consulter les rapports et statistiques</p>
        </div>
        <div className="flex items-center space-x-2">
          <Select
            value={daysFilter.toString()}
            onChange={(e) => setDaysFilter(Number(e.target.value))}
            className="w-32"
            options={[
              { value: '7', label: '7 jours' },
              { value: '30', label: '30 jours' },
              { value: '90', label: '90 jours' },
              { value: '365', label: '1 an' },
            ]}
          />
          <Button variant="outline" onClick={() => handleExport('expeditions', 'csv')}>
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6 border-b">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {dashboardLoading ? (
            <Card>
              <CardContent className="p-8 text-center">Chargement...</CardContent>
            </Card>
          ) : dashboard ? (
            <>
              {/* Key Metrics */}
              <div className="grid gap-4 md:grid-cols-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Palettes totales</p>
                        <p className="text-2xl font-bold">
                          {formatNumber(dashboard.palette_stats.total)}
                        </p>
                      </div>
                      <Package className="h-8 w-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Expéditions en cours</p>
                        <p className="text-2xl font-bold">
                          {formatNumber(dashboard.expedition_stats.in_transit)}
                        </p>
                      </div>
                      <Truck className="h-8 w-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Taux d'utilisation</p>
                        <p className="text-2xl font-bold">
                          {formatPercentage(dashboard.palette_stats.utilization_rate)}
                        </p>
                      </div>
                      <TrendingUp className="h-8 w-8 text-orange-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Score santé</p>
                        <p className="text-2xl font-bold">{dashboard.health_score}%</p>
                        <p className="text-xs text-muted-foreground">{dashboard.health_status}</p>
                      </div>
                      <TrendingUp className="h-8 w-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Trends Charts */}
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Expéditions (7 derniers jours)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={dashboard.trends.expeditions_7days}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="count" stroke="#0088FE" name="Expéditions" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Livraisons (7 derniers jours)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={dashboard.trends.deliveries_7days}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="count" stroke="#00C49F" name="Livraisons" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              {/* Alerts */}
              <Card>
                <CardHeader>
                  <CardTitle>Alertes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div className="p-4 bg-red-50 rounded-lg">
                      <p className="text-sm text-red-600 font-medium">Expéditions en retard</p>
                      <p className="text-2xl font-bold text-red-600">
                        {dashboard.alerts.delayed_expeditions}
                      </p>
                    </div>
                    <div className="p-4 bg-yellow-50 rounded-lg">
                      <p className="text-sm text-yellow-600 font-medium">Validations en attente</p>
                      <p className="text-2xl font-bold text-yellow-600">
                        {dashboard.alerts.pending_validations}
                      </p>
                    </div>
                    <div className="p-4 bg-orange-50 rounded-lg">
                      <p className="text-sm text-orange-600 font-medium">Notifications échouées</p>
                      <p className="text-2xl font-bold text-orange-600">
                        {dashboard.alerts.failed_notifications}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : null}
        </div>
      )}

      {/* Palettes Tab */}
      {activeTab === 'palettes' && dashboard && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Statistiques des palettes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <p className="text-sm text-muted-foreground">Total</p>
                  <p className="text-2xl font-bold">{dashboard.palette_stats.total}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Disponibles</p>
                  <p className="text-2xl font-bold text-green-600">
                    {dashboard.palette_stats.available}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">En transit</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {dashboard.palette_stats.in_transit}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Expeditions Tab */}
      {activeTab === 'expeditions' && dashboard && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Statistiques des expéditions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div>
                  <p className="text-sm text-muted-foreground">Total</p>
                  <p className="text-2xl font-bold">{dashboard.expedition_stats.total}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">En cours</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {dashboard.expedition_stats.in_transit}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Complétées aujourd'hui</p>
                  <p className="text-2xl font-bold text-green-600">
                    {dashboard.expedition_stats.completed_today}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">En retard</p>
                  <p className="text-2xl font-bold text-red-600">
                    {dashboard.expedition_stats.delayed}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <div className="space-y-6">
          {performanceLoading ? (
            <Card>
              <CardContent className="p-8 text-center">Chargement...</CardContent>
            </Card>
          ) : performance ? (
            <>
              <div className="grid gap-4 md:grid-cols-3">
                <Card>
                  <CardHeader>
                    <CardTitle>Métriques expéditions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Total</span>
                      <span className="font-bold">
                        {formatNumber(performance.expedition_metrics.total_expeditions)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Complétées</span>
                      <span className="font-bold text-green-600">
                        {formatNumber(performance.expedition_metrics.completed_expeditions)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Taux de succès</span>
                      <span className="font-bold">
                        {formatPercentage(performance.expedition_metrics.success_rate)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Temps moyen</span>
                      <span className="font-bold">
                        {performance.expedition_metrics.average_delivery_time_hours.toFixed(1)}h
                      </span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Métriques palettes</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Total</span>
                      <span className="font-bold">
                        {formatNumber(performance.palette_metrics.total_palettes)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Actives</span>
                      <span className="font-bold text-blue-600">
                        {formatNumber(performance.palette_metrics.active_palettes)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Taux d'utilisation</span>
                      <span className="font-bold">
                        {formatPercentage(performance.palette_metrics.utilization_rate)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Mouvements</span>
                      <span className="font-bold">
                        {formatNumber(performance.palette_metrics.total_movements)}
                      </span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Score santé</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-center">
                      <p className="text-4xl font-bold mb-2">{performance.health_score}%</p>
                      <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary transition-all"
                          style={{ width: `${performance.health_score}%` }}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {performance.recommendations && performance.recommendations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Recommandations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="list-disc list-inside space-y-1">
                      {performance.recommendations.map((rec, idx) => (
                        <li key={idx} className="text-sm">
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </>
          ) : null}
        </div>
      )}

      {/* Destinations Tab */}
      {activeTab === 'destinations' && (
        <div className="space-y-6">
          {destinationsLoading ? (
            <Card>
              <CardContent className="p-8 text-center">Chargement...</CardContent>
            </Card>
          ) : topDestinations && topDestinations.length > 0 ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Top 10 destinations</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={topDestinations}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="destination" angle={-45} textAnchor="end" height={100} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="expedition_count" fill="#0088FE" name="Expéditions" />
                      <Bar dataKey="total_palettes" fill="#00C49F" name="Palettes" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Détails des destinations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="px-4 py-3 text-left text-sm font-medium">Destination</th>
                          <th className="px-4 py-3 text-left text-sm font-medium">Expéditions</th>
                          <th className="px-4 py-3 text-left text-sm font-medium">Palettes</th>
                          <th className="px-4 py-3 text-left text-sm font-medium">Temps moyen</th>
                          <th className="px-4 py-3 text-left text-sm font-medium">Taux de succès</th>
                        </tr>
                      </thead>
                      <tbody>
                        {topDestinations.map((dest, idx) => (
                          <tr key={idx} className="border-b hover:bg-accent/50">
                            <td className="px-4 py-3">{dest.destination}</td>
                            <td className="px-4 py-3">{dest.expedition_count}</td>
                            <td className="px-4 py-3">{dest.total_palettes}</td>
                            <td className="px-4 py-3">
                              {dest.average_delivery_time_hours.toFixed(1)}h
                            </td>
                            <td className="px-4 py-3">
                              {formatPercentage(dest.success_rate)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                Aucune donnée disponible
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default ReportsPage;
