"""
Notification Templates

HTML and text templates for different types of notifications.
"""

from typing import Dict, Any
from datetime import datetime


class NotificationTemplates:
    """HTML templates for notifications."""

    @staticmethod
    def _base_html_template(title: str, content: str) -> str:
        """
        Base HTML template for emails.

        Args:
            title: Email title
            content: HTML content

        Returns:
            Complete HTML email
        """
        return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f4f4f4;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }}
        .info-box {{
            background-color: white;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }}
        .warning-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .success-box {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
        }}
        .danger-box {{
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 20px 0;
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #777;
            font-size: 12px;
        }}
        .detail {{
            margin: 8px 0;
        }}
        .label {{
            font-weight: bold;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 GazTracker</h1>
        <p>{title}</p>
    </div>
    <div class="content">
        {content}
        <div class="footer">
            <p>Ceci est un message automatique de GazTracker.</p>
            <p>Pour toute question, contactez-nous à support@gaztracker.com</p>
        </div>
    </div>
</body>
</html>
"""

    @classmethod
    def expedition_created(cls, data: Dict[str, Any]) -> tuple[str, str]:
        """
        Template for expedition created notification.

        Args:
            data: Expedition data

        Returns:
            Tuple of (subject, html_body)
        """
        reference = data.get("reference_number", "N/A")
        destination = data.get("destination_address", "N/A")
        palette_count = data.get("palette_count", 0)

        subject = f"Nouvelle expédition créée - {reference}"

        content = f"""
        <h2>Nouvelle Expédition Créée</h2>
        <div class="success-box">
            <p>Une nouvelle expédition a été créée avec succès.</p>
        </div>
        <div class="info-box">
            <div class="detail"><span class="label">Référence:</span> {reference}</div>
            <div class="detail"><span class="label">Destination:</span> {destination}</div>
            <div class="detail"><span class="label">Nombre de palettes:</span> {palette_count}</div>
        </div>
        """

        return subject, cls._base_html_template(subject, content)

    @classmethod
    def expedition_departed(cls, data: Dict[str, Any]) -> tuple[str, str]:
        """
        Template for expedition departed notification.

        Args:
            data: Expedition data

        Returns:
            Tuple of (subject, html_body)
        """
        reference = data.get("reference_number", "N/A")
        destination = data.get("destination_address", "N/A")
        eta = data.get("eta", "N/A")
        otp_code = data.get("otp_code", "")

        subject = f"Expédition en route - {reference}"

        content = f"""
        <h2>📦 Votre Expédition est Partie</h2>
        <div class="info-box">
            <p>L'expédition est maintenant en route vers sa destination.</p>
        </div>
        <div class="info-box">
            <div class="detail"><span class="label">Référence:</span> {reference}</div>
            <div class="detail"><span class="label">Destination:</span> {destination}</div>
            <div class="detail"><span class="label">Arrivée estimée:</span> {eta}</div>
        </div>
        """

        if otp_code:
            content += f"""
        <div class="success-box">
            <p><span class="label">Code OTP de validation:</span></p>
            <h1 style="text-align: center; color: #28a745; letter-spacing: 5px;">{otp_code}</h1>
            <p style="text-align: center; font-size: 12px; color: #666;">
                Ce code sera nécessaire pour valider la livraison
            </p>
        </div>
        """

        return subject, cls._base_html_template(subject, content)

    @classmethod
    def delivery_confirmation(cls, data: Dict[str, Any]) -> tuple[str, str]:
        """
        Template for delivery confirmation notification.

        Args:
            data: Expedition data

        Returns:
            Tuple of (subject, html_body)
        """
        reference = data.get("reference_number", "N/A")
        delivery_date = data.get("delivery_date", datetime.now().strftime("%Y-%m-%d %H:%M"))

        subject = f"Livraison confirmée - {reference}"

        content = f"""
        <h2>✅ Livraison Confirmée</h2>
        <div class="success-box">
            <p>L'expédition a été livrée et validée avec succès.</p>
        </div>
        <div class="info-box">
            <div class="detail"><span class="label">Référence:</span> {reference}</div>
            <div class="detail"><span class="label">Date de livraison:</span> {delivery_date}</div>
        </div>
        <p>Merci d'avoir utilisé GazTracker pour le suivi de votre expédition.</p>
        """

        return subject, cls._base_html_template(subject, content)

    @classmethod
    def delay_alert(cls, data: Dict[str, Any]) -> tuple[str, str]:
        """
        Template for delivery delay alert.

        Args:
            data: Expedition data

        Returns:
            Tuple of (subject, html_body)
        """
        reference = data.get("reference_number", "N/A")
        eta = data.get("eta", "N/A")
        current_status = data.get("status", "N/A")

        subject = f"⚠️ Alerte Retard - {reference}"

        content = f"""
        <h2>⚠️ Retard de Livraison Détecté</h2>
        <div class="warning-box">
            <p>L'expédition est en retard par rapport à l'heure d'arrivée prévue.</p>
        </div>
        <div class="info-box">
            <div class="detail"><span class="label">Référence:</span> {reference}</div>
            <div class="detail"><span class="label">ETA prévu:</span> {eta}</div>
            <div class="detail"><span class="label">Statut actuel:</span> {current_status}</div>
        </div>
        <p>Nous suivons la situation de près et vous tiendrons informé.</p>
        """

        return subject, cls._base_html_template(subject, content)

    @classmethod
    def rfid_anomaly(cls, data: Dict[str, Any]) -> tuple[str, str]:
        """
        Template for RFID anomaly alert.

        Args:
            data: Palette/RFID data

        Returns:
            Tuple of (subject, html_body)
        """
        rfid_tag = data.get("rfid_tag", "N/A")
        palette_id = data.get("palette_id", "N/A")
        issue = data.get("issue", "Anomalie détectée")

        subject = f"🔴 Anomalie RFID - {rfid_tag}"

        content = f"""
        <h2>🔴 Anomalie RFID Détectée</h2>
        <div class="danger-box">
            <p>Une anomalie a été détectée sur un tag RFID.</p>
        </div>
        <div class="info-box">
            <div class="detail"><span class="label">Tag RFID:</span> {rfid_tag}</div>
            <div class="detail"><span class="label">Palette ID:</span> {palette_id}</div>
            <div class="detail"><span class="label">Problème:</span> {issue}</div>
        </div>
        <p>Veuillez vérifier la palette et le tag RFID dès que possible.</p>
        """

        return subject, cls._base_html_template(subject, content)

    @classmethod
    def expedition_problem(cls, data: Dict[str, Any]) -> tuple[str, str]:
        """
        Template for expedition problem notification.

        Args:
            data: Expedition data

        Returns:
            Tuple of (subject, html_body)
        """
        reference = data.get("reference_number", "N/A")
        problem = data.get("problem_description", "Problème non spécifié")

        subject = f"🚨 Problème Expédition - {reference}"

        content = f"""
        <h2>🚨 Problème sur l'Expédition</h2>
        <div class="danger-box">
            <p>Un problème a été signalé sur l'expédition.</p>
        </div>
        <div class="info-box">
            <div class="detail"><span class="label">Référence:</span> {reference}</div>
            <div class="detail"><span class="label">Description:</span></div>
            <p style="margin-top: 10px; padding: 10px; background-color: #fff; border-radius: 3px;">
                {problem}
            </p>
        </div>
        <p>Notre équipe a été notifiée et travaille sur la résolution du problème.</p>
        """

        return subject, cls._base_html_template(subject, content)

    @classmethod
    def validation_required(cls, data: Dict[str, Any]) -> tuple[str, str]:
        """
        Template for validation required notification.

        Args:
            data: Expedition data

        Returns:
            Tuple of (subject, html_body)
        """
        reference = data.get("reference_number", "N/A")
        otp_code = data.get("otp_code", "")

        subject = f"Validation requise - {reference}"

        content = f"""
        <h2>🔐 Validation Requise</h2>
        <div class="warning-box">
            <p>Une validation est nécessaire pour finaliser l'expédition.</p>
        </div>
        <div class="info-box">
            <div class="detail"><span class="label">Référence:</span> {reference}</div>
        </div>
        """

        if otp_code:
            content += f"""
        <div class="success-box">
            <p><span class="label">Code OTP de validation:</span></p>
            <h1 style="text-align: center; color: #2c3e50; letter-spacing: 5px;">{otp_code}</h1>
            <p style="text-align: center; font-size: 12px; color: #666;">
                Utilisez ce code pour valider la réception
            </p>
        </div>
        """

        return subject, cls._base_html_template(subject, content)

    @classmethod
    def get_sms_template(cls, notification_type: str, data: Dict[str, Any]) -> str:
        """
        Get SMS template for a notification type.

        Args:
            notification_type: Type of notification
            data: Notification data

        Returns:
            SMS message (max 160 characters)
        """
        reference = data.get("reference_number", "N/A")

        templates = {
            "EXPEDITION_CREEE": f"GazTracker: Expedition {reference} creee.",
            "EXPEDITION_DEPART": f"GazTracker: Expedition {reference} partie. OTP: {data.get('otp_code', 'N/A')}",
            "CONFIRMATION_LIVRAISON": f"GazTracker: Expedition {reference} livree avec succes.",
            "ALERTE_RETARD": f"ALERTE: Expedition {reference} en retard.",
            "PROBLEME_EXPEDITION": f"PROBLEME: Expedition {reference}. Verifiez details.",
            "VALIDATION_REQUISE": f"GazTracker: Code OTP {data.get('otp_code', 'N/A')} pour {reference}",
        }

        return templates.get(notification_type, f"GazTracker: Notification pour {reference}")
