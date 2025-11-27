import { useState, useEffect } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Card, CardHeader, CardTitle, CardContent, Button } from '../../components/common';
import { Palette, RefreshCw, RotateCcw, Check } from 'lucide-react';

const ThemeSettingsPage = () => {
  const { theme, mode, setMode, setThemeColors, resetTheme, applyLogoTheme } = useTheme();
  const [extractedColors, setExtractedColors] = useState<string[]>([]);
  const [isExtracting, setIsExtracting] = useState(false);
  const [selectedPrimary, setSelectedPrimary] = useState(theme.colors.primary);

  useEffect(() => {
    // Extract colors from logo on mount
    extractColors();
  }, []);

  const extractColors = async () => {
    setIsExtracting(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/theme/extract-from-logo', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setExtractedColors(data.colors || []);
      }
    } catch (error) {
      console.error('Error extracting colors:', error);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleColorChange = (colorKey: string, value: string) => {
    setThemeColors({ [colorKey]: value } as any);
  };

  const handleApplyExtractedColor = (color: string) => {
    setSelectedPrimary(color);
    setThemeColors({ primary: color });
  };

  const handleApplyLogoTheme = async () => {
    await applyLogoTheme();
    window.location.reload(); // Reload to apply changes
  };

  const handleReset = () => {
    if (confirm('Voulez-vous réinitialiser le thème aux paramètres par défaut ?')) {
      resetTheme();
      window.location.reload();
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Paramètres du Thème</h1>
        <p className="text-muted-foreground">
          Personnalisez l'apparence de l'application
        </p>
      </div>

      {/* Mode clair/sombre */}
      <Card>
        <CardHeader>
          <CardTitle>Mode d'affichage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <button
              onClick={() => setMode('light')}
              className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                mode === 'light'
                  ? 'border-primary bg-primary/10'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-center">
                <div className="text-2xl mb-2">☀️</div>
                <div className="font-medium">Mode Clair</div>
              </div>
            </button>
            <button
              onClick={() => setMode('dark')}
              className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                mode === 'dark'
                  ? 'border-primary bg-primary/10'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-center">
                <div className="text-2xl mb-2">🌙</div>
                <div className="font-medium">Mode Sombre</div>
              </div>
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Couleurs du logo */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Couleurs du Logo</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Couleurs extraites du logo de votre groupe
              </p>
            </div>
            <Button
              onClick={handleApplyLogoTheme}
              variant="outline"
              size="sm"
              disabled={isExtracting}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isExtracting ? 'animate-spin' : ''}`} />
              Appliquer thème du logo
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {extractedColors.length > 0 ? (
            <div className="grid grid-cols-5 gap-4">
              {extractedColors.map((color, index) => (
                <button
                  key={index}
                  onClick={() => handleApplyExtractedColor(color)}
                  className="relative group"
                >
                  <div
                    className="w-full h-20 rounded-lg border-2 transition-all hover:scale-105"
                    style={{
                      backgroundColor: color,
                      borderColor: selectedPrimary === color ? theme.colors.primary : 'transparent',
                    }}
                  >
                    {selectedPrimary === color && (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Check className="h-6 w-6 text-white drop-shadow-lg" />
                      </div>
                    )}
                  </div>
                  <div className="mt-2 text-xs text-center font-mono">{color}</div>
                </button>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Palette className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>Chargement des couleurs...</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Personnalisation des couleurs */}
      <Card>
        <CardHeader>
          <CardTitle>Personnalisation des Couleurs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-6">
            {Object.entries(theme.colors).map(([key, value]) => (
              <div key={key} className="space-y-2">
                <label className="block text-sm font-medium capitalize">
                  {key === 'primary' && '🎨 '}
                  {key === 'success' && '✅ '}
                  {key === 'warning' && '⚠️ '}
                  {key === 'error' && '❌ '}
                  {key === 'info' && 'ℹ️ '}
                  {key.replace(/_/g, ' ')}
                </label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={value}
                    onChange={(e) => handleColorChange(key, e.target.value)}
                    className="h-10 w-20 rounded border cursor-pointer"
                  />
                  <input
                    type="text"
                    value={value}
                    onChange={(e) => handleColorChange(key, e.target.value)}
                    className="flex-1 px-3 py-2 border rounded font-mono text-sm"
                    placeholder="#000000"
                  />
                  <div
                    className="w-10 h-10 rounded border"
                    style={{ backgroundColor: value }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex justify-end gap-4">
            <Button onClick={handleReset} variant="outline">
              <RotateCcw className="h-4 w-4 mr-2" />
              Réinitialiser
            </Button>
            <Button onClick={() => window.location.reload()}>
              <Check className="h-4 w-4 mr-2" />
              Appliquer
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Aperçu */}
      <Card>
        <CardHeader>
          <CardTitle>Aperçu</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-2">
              <button
                className="px-4 py-2 rounded"
                style={{ backgroundColor: theme.colors.primary, color: 'white' }}
              >
                Bouton Primary
              </button>
              <button
                className="px-4 py-2 rounded"
                style={{ backgroundColor: theme.colors.secondary, color: 'white' }}
              >
                Bouton Secondary
              </button>
              <button
                className="px-4 py-2 rounded"
                style={{ backgroundColor: theme.colors.accent, color: 'white' }}
              >
                Bouton Accent
              </button>
            </div>
            <div className="flex gap-2">
              <div
                className="flex-1 p-4 rounded"
                style={{ backgroundColor: theme.colors.success, color: 'white' }}
              >
                ✅ Succès
              </div>
              <div
                className="flex-1 p-4 rounded"
                style={{ backgroundColor: theme.colors.warning, color: 'white' }}
              >
                ⚠️ Avertissement
              </div>
              <div
                className="flex-1 p-4 rounded"
                style={{ backgroundColor: theme.colors.error, color: 'white' }}
              >
                ❌ Erreur
              </div>
              <div
                className="flex-1 p-4 rounded"
                style={{ backgroundColor: theme.colors.info, color: 'white' }}
              >
                ℹ️ Info
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ThemeSettingsPage;

