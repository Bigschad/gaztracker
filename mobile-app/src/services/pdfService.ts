import * as FileSystem from 'expo-file-system';
import * as Print from 'expo-print';
import { DeliveryNote, Expedition, Palette } from '../types';

interface PDFOptions {
  expedition: Expedition;
  palettes: Palette[];
  signature?: {
    type: 'GRAPHIC' | 'OTP' | 'HYBRID';
    graphicData?: string;
    timestamp: number;
  };
}

class PDFService {
  /**
   * Génère un bon de livraison en PDF
   */
  async generateDeliveryNote(options: PDFOptions): Promise<string> {
    const { expedition, palettes, signature } = options;

    // Créer le contenu HTML du PDF
    const htmlContent = this.generateHTMLContent(expedition, palettes, signature);

    try {
      // Générer le PDF avec expo-print
      const { uri } = await Print.printToFileAsync({
        html: htmlContent,
        base64: false,
      });

      return uri;
    } catch (error) {
      console.error('Error generating PDF:', error);
      // Fallback: sauvegarder en HTML si la génération PDF échoue
      const fileName = `BL_${expedition.referenceNumber}_${Date.now()}.html`;
      const fileUri = `${FileSystem.documentDirectory}${fileName}`;

      await FileSystem.writeAsStringAsync(fileUri, htmlContent, {
        encoding: FileSystem.EncodingType.UTF8,
      });

      return fileUri;
    }
  }

  /**
   * Génère le contenu HTML du bon de livraison
   */
  private generateHTMLContent(
    expedition: Expedition,
    palettes: Palette[],
    signature?: PDFOptions['signature']
  ): string {
    const date = new Date().toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });

    const totalPalettes = palettes.length;
    const totalBottles = palettes.reduce((sum, p) => sum + p.currentFill, 0);

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Bon de Livraison - ${expedition.referenceNumber}</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
      color: #333;
    }
    .header {
      border-bottom: 3px solid #007AFF;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .header h1 {
      margin: 0;
      color: #007AFF;
      font-size: 28px;
    }
    .header-info {
      display: flex;
      justify-content: space-between;
      margin-top: 10px;
    }
    .section {
      margin-bottom: 30px;
    }
    .section-title {
      font-size: 18px;
      font-weight: bold;
      color: #333;
      margin-bottom: 10px;
      border-bottom: 2px solid #ddd;
      padding-bottom: 5px;
    }
    .info-row {
      display: flex;
      margin-bottom: 8px;
    }
    .info-label {
      font-weight: bold;
      width: 150px;
    }
    .info-value {
      flex: 1;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }
    th, td {
      border: 1px solid #ddd;
      padding: 10px;
      text-align: left;
    }
    th {
      background-color: #f5f5f5;
      font-weight: bold;
    }
    .summary {
      background-color: #f9f9f9;
      padding: 15px;
      border-radius: 5px;
      margin-top: 20px;
    }
    .summary-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .signature-section {
      margin-top: 40px;
      border-top: 2px solid #ddd;
      padding-top: 20px;
    }
    .signature-box {
      margin-top: 20px;
      min-height: 100px;
      border: 1px solid #ddd;
      padding: 10px;
    }
    .signature-image {
      max-width: 300px;
      max-height: 150px;
    }
    .qr-code {
      text-align: center;
      margin-top: 20px;
    }
    .footer {
      margin-top: 40px;
      text-align: center;
      color: #666;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>BON DE LIVRAISON</h1>
    <div class="header-info">
      <div>
        <div class="info-row">
          <span class="info-label">N° BL:</span>
          <span class="info-value">${expedition.referenceNumber}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Date:</span>
          <span class="info-value">${date}</span>
        </div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Informations Expédition</div>
    <div class="info-row">
      <span class="info-label">Chauffeur:</span>
      <span class="info-value">${expedition.transporter || 'N/A'}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Véhicule:</span>
      <span class="info-value">${expedition.vehicleInfo || 'N/A'}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Date départ:</span>
      <span class="info-value">${
        expedition.dateDeparture
          ? new Date(expedition.dateDeparture).toLocaleDateString('fr-FR')
          : 'N/A'
      }</span>
    </div>
  </div>

  <div class="section">
    <div class="section-title">Client / Destination</div>
    <div class="info-row">
      <span class="info-label">Adresse:</span>
      <span class="info-value">${expedition.destinationAddress}</span>
    </div>
    ${expedition.destinationContact ? `
    <div class="info-row">
      <span class="info-label">Contact:</span>
      <span class="info-value">${expedition.destinationContact}</span>
    </div>
    ` : ''}
    ${expedition.destinationPhone ? `
    <div class="info-row">
      <span class="info-label">Téléphone:</span>
      <span class="info-value">${expedition.destinationPhone}</span>
    </div>
    ` : ''}
  </div>

  <div class="section">
    <div class="section-title">Palettes Livrées</div>
    <table>
      <thead>
        <tr>
          <th>N° Série</th>
          <th>Type</th>
          <th>Remplissage</th>
          <th>Capacité</th>
          <th>RFID</th>
        </tr>
      </thead>
      <tbody>
        ${palettes
          .map(
            (palette) => `
        <tr>
          <td>${palette.serialNumber}</td>
          <td>${palette.type}</td>
          <td>${palette.currentFill}</td>
          <td>${palette.capacity}</td>
          <td>${palette.rfidTag?.tagNumber || 'N/A'}</td>
        </tr>
        `
          )
          .join('')}
      </tbody>
    </table>
  </div>

  <div class="summary">
    <div class="summary-row">
      <span><strong>Total palettes:</strong></span>
      <span><strong>${totalPalettes}</strong></span>
    </div>
    <div class="summary-row">
      <span><strong>Total bouteilles:</strong></span>
      <span><strong>${totalBottles}</strong></span>
    </div>
  </div>

  ${signature ? `
  <div class="signature-section">
    <div class="section-title">Signature</div>
    <div class="info-row">
      <span class="info-label">Type:</span>
      <span class="info-value">${signature.type}</span>
    </div>
    <div class="info-row">
      <span class="info-label">Date:</span>
      <span class="info-value">${new Date(signature.timestamp).toLocaleString('fr-FR')}</span>
    </div>
    ${signature.graphicData ? `
    <div class="signature-box">
      <img src="data:image/png;base64,${signature.graphicData}" class="signature-image" alt="Signature" />
    </div>
    ` : ''}
  </div>
  ` : ''}

  <div class="qr-code">
    <p>QR Code pour consultation rapide</p>
    <!-- TODO: Générer QR code avec les données de l'expédition -->
  </div>

  <div class="footer">
    <p>Document généré le ${date}</p>
    <p>GazTracker - Système de gestion des palettes</p>
  </div>
</body>
</html>
    `;
  }

  /**
   * Génère un QR code pour le bon de livraison
   */
  generateQRCodeData(expedition: Expedition): string {
    return JSON.stringify({
      type: 'DELIVERY_NOTE',
      expeditionId: expedition.id,
      referenceNumber: expedition.referenceNumber,
      date: new Date().toISOString(),
    });
  }

  /**
   * Partage le PDF généré
   */
  async sharePDF(fileUri: string): Promise<void> {
    // TODO: Implémenter le partage avec expo-sharing
    console.log('PDF généré:', fileUri);
  }
}

export const pdfService = new PDFService();

