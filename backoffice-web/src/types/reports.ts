// Reports and analytics types

export interface DashboardOverview {
  palette_stats: {
    total: number;
    available: number;
    in_transit: number;
    utilization_rate: number;
  };
  expedition_stats: {
    total: number;
    in_transit: number;
    completed_today: number;
    delayed: number;
  };
  notification_stats: {
    total: number;
    sent_today: number;
    failed_today: number;
  };
  recent_activity: {
    recent_expeditions: number;
    recent_deliveries: number;
    pending_validations: number;
  };
  alerts: {
    delayed_expeditions: number;
    pending_validations: number;
    failed_notifications: number;
  };
  trends: {
    expeditions_7days: Array<{ date: string; count: number }>;
    deliveries_7days: Array<{ date: string; count: number }>;
  };
  health_score: number;
  health_status: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR';
}

export interface PerformanceReport {
  time_period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  expedition_metrics: {
    total_expeditions: number;
    completed_expeditions: number;
    in_progress_expeditions: number;
    cancelled_expeditions: number;
    average_delivery_time_hours: number;
    success_rate: number;
  };
  palette_metrics: {
    total_palettes: number;
    active_palettes: number;
    utilization_rate: number;
    total_movements: number;
  };
  notification_metrics: {
    total_notifications: number;
    sent_notifications: number;
    failed_notifications: number;
    success_rate: number;
  };
  top_destinations: Array<{
    destination: string;
    expedition_count: number;
    total_palettes: number;
  }>;
  health_score: number;
  recommendations: string[];
}

export interface TopDestination {
  destination: string;
  expedition_count: number;
  total_palettes: number;
  average_delivery_time_hours: number;
  success_rate: number;
}

export interface UserPerformance {
  user_id: number;
  username: string;
  role: string;
  expeditions_created: number;
  expeditions_delivered: number;
  palettes_created: number;
  average_delivery_time_hours: number;
  success_rate: number;
}

export interface ExportRequest {
  format: 'csv' | 'json';
  start_date?: string;
  end_date?: string;
  filters?: Record<string, any>;
}

export interface ExportResponse {
  file_url: string;
  filename: string;
  format: string;
  record_count: number;
  generated_at: string;
}
