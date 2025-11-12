import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationService } from '../../services/api';
import {
  Card,
  CardContent,
  Button,
  Select,
  Dialog,
  ConfirmDialog,
} from '../../components/common';
import { Input } from '../../components/common/Input';
import {
  Notification,
  NotificationType,
  NotificationStatus,
  NotificationChannel,
  NotificationCreate,
} from '../../types';
import {
  Plus,
  Send,
  RefreshCw,
  AlertCircle,
  Mail,
  MessageSquare,
  Filter,
  Eye,
  CheckCircle,
  XCircle,
  Clock,
} from 'lucide-react';
import { formatDate } from '../../utils/formatters';

const NotificationsPage = () => {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState<NotificationStatus | ''>('');
  const [typeFilter, setTypeFilter] = useState<NotificationType | ''>('');
  const [channelFilter, setChannelFilter] = useState<NotificationChannel | ''>('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDetailsDialogOpen, setIsDetailsDialogOpen] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);
  const [notificationToSend, setNotificationToSend] = useState<Notification | null>(null);
  const [notificationToRetry, setNotificationToRetry] = useState<Notification | null>(null);

  const queryClient = useQueryClient();

  // Fetch notifications
  const { data, isLoading } = useQuery({
    queryKey: ['notifications', page, pageSize, statusFilter, typeFilter, channelFilter],
    queryFn: () =>
      notificationService.list({
        page,
        page_size: pageSize,
        status: statusFilter || undefined,
        type: typeFilter || undefined,
        channel: channelFilter || undefined,
      }),
  });

  // Fetch statistics
  const { data: statistics } = useQuery({
    queryKey: ['notification-statistics'],
    queryFn: () => notificationService.getStatistics(),
  });

  // Send notification mutation
  const sendMutation = useMutation({
    mutationFn: (id: string) => notificationService.send(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notification-statistics'] });
      setNotificationToSend(null);
    },
  });

  // Retry failed notifications mutation
  const retryMutation = useMutation({
    mutationFn: () => notificationService.retryFailed(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notification-statistics'] });
      setNotificationToRetry(null);
    },
  });

  // Create and send notification mutation
  const createAndSendMutation = useMutation({
    mutationFn: (data: NotificationCreate) => notificationService.sendNow(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      queryClient.invalidateQueries({ queryKey: ['notification-statistics'] });
      setIsCreateDialogOpen(false);
    },
  });

  const getStatusIcon = (status: NotificationStatus) => {
    switch (status) {
      case NotificationStatus.SENT:
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case NotificationStatus.FAILED:
        return <XCircle className="h-4 w-4 text-red-600" />;
      case NotificationStatus.PENDING:
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case NotificationStatus.RETRYING:
        return <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: NotificationStatus) => {
    switch (status) {
      case NotificationStatus.SENT:
        return 'bg-green-100 text-green-800';
      case NotificationStatus.FAILED:
        return 'bg-red-100 text-red-800';
      case NotificationStatus.PENDING:
        return 'bg-yellow-100 text-yellow-800';
      case NotificationStatus.RETRYING:
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getChannelIcon = (channel: NotificationChannel) => {
    switch (channel) {
      case NotificationChannel.EMAIL:
        return <Mail className="h-4 w-4" />;
      case NotificationChannel.SMS:
        return <MessageSquare className="h-4 w-4" />;
      case NotificationChannel.BOTH:
        return (
          <div className="flex items-center space-x-1">
            <Mail className="h-4 w-4" />
            <MessageSquare className="h-4 w-4" />
          </div>
        );
      default:
        return null;
    }
  };

  const handleCreateNotification = () => {
    setIsCreateDialogOpen(true);
  };

  const handleViewDetails = (notification: Notification) => {
    setSelectedNotification(notification);
    setIsDetailsDialogOpen(true);
  };

  const handleSendNotification = (notification: Notification) => {
    setNotificationToSend(notification);
  };

  const handleRetryFailed = () => {
    setNotificationToRetry({} as Notification);
  };

  const handleCreateAndSend = (formData: NotificationCreate) => {
    createAndSendMutation.mutate(formData);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-muted-foreground">Gérer vos notifications et alertes</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={handleRetryFailed}
            disabled={retryMutation.isPending}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Réessayer les échecs
          </Button>
          <Button onClick={handleCreateNotification}>
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle notification
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid gap-4 md:grid-cols-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total</p>
                  <p className="text-2xl font-bold">{statistics.total_notifications}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Envoyées</p>
                  <p className="text-2xl font-bold text-green-600">
                    {statistics.by_status.SENT || 0}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Échecs</p>
                  <p className="text-2xl font-bold text-red-600">
                    {statistics.by_status.FAILED || 0}
                  </p>
                </div>
                <XCircle className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Taux de succès</p>
                  <p className="text-2xl font-bold">
                    {statistics.success_rate.toFixed(1)}%
                  </p>
                </div>
                <RefreshCw className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex items-center space-x-4">
            <Filter className="h-5 w-5 text-muted-foreground" />
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as NotificationStatus | '')}
              className="w-48"
              options={[
                { value: '', label: 'Tous les statuts' },
                ...Object.values(NotificationStatus).map((status) => ({
                  value: status,
                  label: status,
                })),
              ]}
            />
            <Select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as NotificationType | '')}
              className="w-64"
              options={[
                { value: '', label: 'Tous les types' },
                ...Object.values(NotificationType).map((type) => ({
                  value: type,
                  label: type.replace(/_/g, ' '),
                })),
              ]}
            />
            <Select
              value={channelFilter}
              onChange={(e) => setChannelFilter(e.target.value as NotificationChannel | '')}
              className="w-48"
              options={[
                { value: '', label: 'Tous les canaux' },
                ...Object.values(NotificationChannel).map((channel) => ({
                  value: channel,
                  label: channel,
                })),
              ]}
            />
            {(statusFilter || typeFilter || channelFilter) && (
              <Button
                variant="outline"
                onClick={() => {
                  setStatusFilter('');
                  setTypeFilter('');
                  setChannelFilter('');
                }}
              >
                Réinitialiser
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Notifications Table */}
      <Card>
        {isLoading ? (
          <CardContent className="p-8 text-center">Chargement...</CardContent>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Canal</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Destinataire</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Statut</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Sujet</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Date création</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                      Aucune notification trouvée
                    </td>
                  </tr>
                ) : (
                  data?.items.map((notification) => (
                    <tr key={notification.id} className="border-b hover:bg-accent/50">
                      <td className="px-4 py-3">
                        <span className="text-sm font-medium">
                          {notification.type.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-2">
                          {getChannelIcon(notification.channel)}
                          <span className="text-sm">{notification.channel}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {notification.recipient_email || notification.recipient_phone || '-'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(notification.status)}
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded ${getStatusColor(
                              notification.status
                            )}`}
                          >
                            {notification.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm max-w-xs truncate">
                        {notification.subject || '-'}
                      </td>
                      <td className="px-4 py-3 text-sm">{formatDate(notification.created_at)}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end space-x-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewDetails(notification)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          {notification.status === NotificationStatus.PENDING && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleSendNotification(notification)}
                              disabled={sendMutation.isPending}
                            >
                              <Send className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <CardContent className="p-4 border-t">
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Page {data.page} sur {data.total_pages} ({data.total} notifications)
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Précédent
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                  disabled={page === data.total_pages}
                >
                  Suivant
                </Button>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Create Notification Dialog */}
      <CreateNotificationDialog
        isOpen={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        onSubmit={handleCreateAndSend}
        isLoading={createAndSendMutation.isPending}
      />

      {/* Details Dialog */}
      {selectedNotification && (
        <NotificationDetailsDialog
          notification={selectedNotification}
          isOpen={isDetailsDialogOpen}
          onClose={() => {
            setIsDetailsDialogOpen(false);
            setSelectedNotification(null);
          }}
        />
      )}

      {/* Send Confirmation */}
      <ConfirmDialog
        isOpen={!!notificationToSend}
        title="Envoyer la notification"
        message={`Voulez-vous envoyer cette notification maintenant ?`}
        onConfirm={() => {
          if (notificationToSend) {
            sendMutation.mutate(notificationToSend.id);
          }
        }}
        onClose={() => setNotificationToSend(null)}
        confirmText="Envoyer"
        cancelText="Annuler"
      />

      {/* Retry Failed Confirmation */}
      <ConfirmDialog
        isOpen={!!notificationToRetry}
        title="Réessayer les notifications échouées"
        message="Voulez-vous réessayer toutes les notifications échouées ?"
        onConfirm={() => {
          retryMutation.mutate();
        }}
        onClose={() => setNotificationToRetry(null)}
        confirmText="Réessayer"
        cancelText="Annuler"
      />
    </div>
  );
};

// Create Notification Dialog Component
interface CreateNotificationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: NotificationCreate) => void;
  isLoading: boolean;
}

const CreateNotificationDialog: React.FC<CreateNotificationDialogProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
}) => {
  const [formData, setFormData] = useState<NotificationCreate>({
    type: NotificationType.EXPEDITION_CREEE,
    channel: NotificationChannel.EMAIL,
    message: '',
    subject: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.message) return;
    if (formData.channel === NotificationChannel.EMAIL && !formData.recipient_email) return;
    if (formData.channel === NotificationChannel.SMS && !formData.recipient_phone) return;
    onSubmit(formData);
    setFormData({
      type: NotificationType.EXPEDITION_CREEE,
      channel: NotificationChannel.EMAIL,
      message: '',
      subject: '',
    });
  };

  return (
    <Dialog isOpen={isOpen} onClose={onClose} title="Créer une notification">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Type</label>
          <Select
            value={formData.type}
            onChange={(e) =>
              setFormData({ ...formData, type: e.target.value as NotificationType })
            }
            required
            options={Object.values(NotificationType).map((type) => ({
              value: type,
              label: type.replace(/_/g, ' '),
            }))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Canal</label>
          <Select
            value={formData.channel}
            onChange={(e) =>
              setFormData({ ...formData, channel: e.target.value as NotificationChannel })
            }
            required
            options={Object.values(NotificationChannel).map((channel) => ({
              value: channel,
              label: channel,
            }))}
          />
        </div>

        {(formData.channel === NotificationChannel.EMAIL || formData.channel === NotificationChannel.BOTH) && (
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <Input
              type="email"
              value={formData.recipient_email || ''}
              onChange={(e) =>
                setFormData({ ...formData, recipient_email: e.target.value })
              }
              required={formData.channel === NotificationChannel.EMAIL || formData.channel === NotificationChannel.BOTH}
            />
          </div>
        )}

        {(formData.channel === NotificationChannel.SMS || formData.channel === NotificationChannel.BOTH) && (
          <div>
            <label className="block text-sm font-medium mb-1">Téléphone</label>
            <Input
              type="tel"
              value={formData.recipient_phone || ''}
              onChange={(e) =>
                setFormData({ ...formData, recipient_phone: e.target.value })
              }
              required={formData.channel === NotificationChannel.SMS || formData.channel === NotificationChannel.BOTH}
              placeholder="+33612345678"
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-1">Sujet</label>
          <Input
            value={formData.subject || ''}
            onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Message</label>
          <textarea
            className="w-full px-3 py-2 border rounded-md"
            rows={4}
            value={formData.message}
            onChange={(e) => setFormData({ ...formData, message: e.target.value })}
            required
          />
        </div>

        <div className="flex justify-end space-x-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Annuler
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Envoi...' : 'Créer et envoyer'}
          </Button>
        </div>
      </form>
    </Dialog>
  );
};

// Notification Details Dialog Component
interface NotificationDetailsDialogProps {
  notification: Notification;
  isOpen: boolean;
  onClose: () => void;
}

const NotificationDetailsDialog: React.FC<NotificationDetailsDialogProps> = ({
  notification,
  isOpen,
  onClose,
}) => {
  return (
    <Dialog isOpen={isOpen} onClose={onClose} title="Détails de la notification">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-muted-foreground">Type</label>
          <p className="mt-1">{notification.type.replace(/_/g, ' ')}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-muted-foreground">Canal</label>
          <p className="mt-1">{notification.channel}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-muted-foreground">Statut</label>
          <p className="mt-1">{notification.status}</p>
        </div>
        {notification.recipient_email && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground">Email</label>
            <p className="mt-1">{notification.recipient_email}</p>
          </div>
        )}
        {notification.recipient_phone && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground">Téléphone</label>
            <p className="mt-1">{notification.recipient_phone}</p>
          </div>
        )}
        {notification.subject && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground">Sujet</label>
            <p className="mt-1">{notification.subject}</p>
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-muted-foreground">Message</label>
          <p className="mt-1 whitespace-pre-wrap">{notification.message}</p>
        </div>
        {notification.error_message && (
          <div>
            <label className="block text-sm font-medium text-red-600">Erreur</label>
            <p className="mt-1 text-red-600">{notification.error_message}</p>
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-muted-foreground">
            Tentatives de réessai
          </label>
          <p className="mt-1">{notification.retry_count}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-muted-foreground">Créée le</label>
          <p className="mt-1">{formatDate(notification.created_at)}</p>
        </div>
        {notification.sent_at && (
          <div>
            <label className="block text-sm font-medium text-muted-foreground">Envoyée le</label>
            <p className="mt-1">{formatDate(notification.sent_at)}</p>
          </div>
        )}
      </div>
    </Dialog>
  );
};

export default NotificationsPage;
