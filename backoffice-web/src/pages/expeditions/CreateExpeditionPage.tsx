import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { expeditionService, userService, paletteService, partnerService } from '../../services/api';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Select, Tabs, Dialog } from '../../components/common';
import { ArrowLeft, Plus, X, Check } from 'lucide-react';
import { expeditionCreateSchema, ExpeditionCreateFormData } from '../../utils/validators';
import { UserRole, User } from '../../types/user';
import { Palette, ExpeditionCreate, Partner } from '../../types';

interface SelectedPalette extends Palette {
  bottleCount?: number;
}

const CreateExpeditionPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('palettes');
  const [selectedPalettes, setSelectedPalettes] = useState<SelectedPalette[]>([]);
  const [isPaletteDialogOpen, setIsPaletteDialogOpen] = useState(false);
  const [palettePage, setPalettePage] = useState(1);
  const [palettePageSize] = useState(20);
  const [tempSelectedPaletteIds, setTempSelectedPaletteIds] = useState<Set<string>>(new Set());

  // Fetch grossistes (wholesalers) - now using partners instead of users
  const { data: grossistesData } = useQuery({
    queryKey: ['partners', 'grossistes'],
    queryFn: () => partnerService.list({ 
      type: 'GROSSISTE' as any, 
      is_active: true, 
      page: 1, 
      page_size: 100 
    }),
  });

  // Fetch available palettes for dialog (with pagination)
  const { data: palettesData } = useQuery({
    queryKey: ['palettes', 'available', palettePage, palettePageSize],
    queryFn: () => paletteService.list({ status: 'EN_STOCK', page: palettePage, page_size: palettePageSize }),
    enabled: isPaletteDialogOpen,
  });

  // Fetch chauffeurs (drivers)
  const { data: chauffeursData } = useQuery({
    queryKey: ['users', 'chauffeurs'],
    queryFn: () => userService.list({ page: 1, page_size: 100, role: UserRole.CHAUFFEUR } as any),
  });

  const grossistes = grossistesData?.items || [];
  const availablePalettes = palettesData?.items || [];
  const totalPalettePages = palettesData?.total_pages || 1;
  const chauffeurs = chauffeursData?.items || [];

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    control,
  } = useForm<ExpeditionCreateFormData>({
    resolver: zodResolver(expeditionCreateSchema),
    defaultValues: {
      expected_delivery_date: new Date().toISOString().split('T')[0],
    },
  });

  const selectedGrossisteId = watch('grossiste_id');
  const selectedDriverId = watch('driver_id');

  // Pre-fill grossiste information when selected
  useEffect(() => {
    if (selectedGrossisteId) {
      const grossiste = grossistes.find((g: Partner) => g.id === selectedGrossisteId);
      if (grossiste) {
        // Pre-fill address from partner
        setValue('destination_address', grossiste.address || '');
        // Note: Contact name and phone will be filled from the contact_id selection
        // The user can select a contact from the partner's contacts
      }
    } else {
      // Clear fields when no grossiste is selected
      setValue('destination_address', '');
      setValue('destination_contact', '');
      setValue('destination_phone', '');
    }
  }, [selectedGrossisteId, grossistes, setValue]);

  // Pre-fill driver information when selected
  useEffect(() => {
    if (selectedDriverId) {
      const driver = chauffeurs.find((c: User) => c.id === selectedDriverId);
      if (driver) {
        setValue('transporter', `${driver.first_name} ${driver.last_name}`);
      }
    } else {
      setValue('transporter', '');
    }
  }, [selectedDriverId, chauffeurs, setValue]);

  const createMutation = useMutation({
    mutationFn: async (data: ExpeditionCreateFormData) => {
      // Transform data to match backend API
      const payload: ExpeditionCreate = {
        destination_address: data.destination_address || '',
        destination_contact: data.destination_contact,
        destination_phone: data.destination_phone,
        transporter: data.transporter,
        vehicle_info: data.vehicle_info,
        libelle: data.libelle,
        grossiste_id: data.grossiste_id || undefined,
        driver_id: data.driver_id || undefined,
        eta: data.expected_delivery_date ? new Date(data.expected_delivery_date).toISOString() : undefined,
        notes: data.notes,
        palette_ids: selectedPalettes.map((p) => p.id),
      };
      return expeditionService.create(payload);
    },
    onSuccess: (data) => {
      navigate(`/expeditions/${data.id}`);
    },
  });

  const onSubmit = (data: ExpeditionCreateFormData) => {
    if (selectedPalettes.length === 0) {
      alert('Veuillez sélectionner au moins une palette');
      return;
    }
    createMutation.mutate(data);
  };

  const handleTogglePaletteSelection = (paletteId: string) => {
    const newSelection = new Set(tempSelectedPaletteIds);
    if (newSelection.has(paletteId)) {
      newSelection.delete(paletteId);
    } else {
      newSelection.add(paletteId);
    }
    setTempSelectedPaletteIds(newSelection);
  };

  const handleConfirmPaletteSelection = () => {
    const newPalettes: SelectedPalette[] = availablePalettes
      .filter((p: Palette) => tempSelectedPaletteIds.has(p.id))
      .map((p: Palette) => ({
        ...p,
        bottleCount: undefined,
      }))
      .filter((p: SelectedPalette) => !selectedPalettes.find((sp) => sp.id === p.id));

    setSelectedPalettes([...selectedPalettes, ...newPalettes]);
    setTempSelectedPaletteIds(new Set());
    setIsPaletteDialogOpen(false);
    setPalettePage(1);
  };

  const handleRemovePalette = (paletteId: string) => {
    setSelectedPalettes(selectedPalettes.filter((p) => p.id !== paletteId));
  };

  const handleBottleCountChange = (paletteId: string, count: string) => {
    const numCount = count === '' ? undefined : parseInt(count, 10);
    setSelectedPalettes(
      selectedPalettes.map((p) => (p.id === paletteId ? { ...p, bottleCount: numCount } : p))
    );
  };

  const handleOpenPaletteDialog = () => {
    setIsPaletteDialogOpen(true);
    // Pre-select already selected palettes
    const alreadySelectedIds = new Set(selectedPalettes.map((p) => p.id));
    setTempSelectedPaletteIds(alreadySelectedIds);
  };

  const today = new Date().toISOString().split('T')[0];

  const tabs = [
    {
      id: 'palettes',
      label: 'Palettes',
      content: (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Palettes sélectionnées ({selectedPalettes.length})</h3>
            <Button
              type="button"
              variant="outline"
              onClick={handleOpenPaletteDialog}
            >
              <Plus className="h-4 w-4 mr-2" />
              Ajouter des palettes
            </Button>
          </div>

          {selectedPalettes.length === 0 ? (
            <div className="border rounded-lg p-8 text-center">
              <p className="text-gray-500 mb-4">Aucune palette sélectionnée</p>
              <Button
                type="button"
                variant="outline"
                onClick={handleOpenPaletteDialog}
              >
                <Plus className="h-4 w-4 mr-2" />
                Ajouter des palettes
              </Button>
            </div>
          ) : (
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Tag RFID</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Type</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Nombre de bouteilles</th>
                    <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {selectedPalettes.map((palette) => (
                    <tr key={palette.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm">
                        {palette.rfid_tag?.tag_number || 'Sans tag'}
                      </td>
                      <td className="px-4 py-3 text-sm">{palette.type}</td>
                      <td className="px-4 py-3">
                        <Input
                          type="number"
                          min="0"
                          value={palette.bottleCount || ''}
                          onChange={(e) => handleBottleCountChange(palette.id, e.target.value)}
                          placeholder="0"
                          className="w-32"
                        />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => handleRemovePalette(palette.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Palette Selection Dialog */}
          <Dialog
            isOpen={isPaletteDialogOpen}
            onClose={() => {
              setIsPaletteDialogOpen(false);
              setTempSelectedPaletteIds(new Set());
              setPalettePage(1);
            }}
            title="Sélectionner des palettes"
            size="xl"
          >
            <div className="space-y-4">
              {/* Palette List */}
              <div className="border rounded-lg max-h-96 overflow-y-auto">
                {availablePalettes.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">Aucune palette disponible</p>
                ) : (
                  <div className="divide-y">
                    {availablePalettes.map((palette: Palette) => (
                      <label
                        key={palette.id}
                        className="flex items-center p-4 hover:bg-gray-50 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={tempSelectedPaletteIds.has(palette.id)}
                          onChange={() => handleTogglePaletteSelection(palette.id)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <div className="ml-3 flex-1">
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="font-medium text-gray-900">
                                {palette.rfid_tag?.tag_number || 'Sans tag'}
                              </span>
                              <span className="text-sm text-gray-500 ml-2">- {palette.type}</span>
                            </div>
                            <span className="text-xs text-gray-400">{palette.serial_number}</span>
                          </div>
                        </div>
                      </label>
                    ))}
                  </div>
                )}
              </div>

              {/* Pagination */}
              {totalPalettePages > 1 && (
                <div className="flex items-center justify-between border-t pt-4">
                  <div className="text-sm text-gray-700">
                    Page {palettePage} sur {totalPalettePages}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setPalettePage((p) => Math.max(1, p - 1))}
                      disabled={palettePage === 1}
                    >
                      Précédent
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setPalettePage((p) => Math.min(totalPalettePages, p + 1))}
                      disabled={palettePage === totalPalettePages}
                    >
                      Suivant
                    </Button>
                  </div>
                </div>
              )}

              {/* Dialog Actions */}
              <div className="flex justify-end gap-3 pt-4 border-t">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsPaletteDialogOpen(false);
                    setTempSelectedPaletteIds(new Set());
                    setPalettePage(1);
                  }}
                >
                  Annuler
                </Button>
                <Button
                  type="button"
                  onClick={handleConfirmPaletteSelection}
                  disabled={tempSelectedPaletteIds.size === 0}
                >
                  <Check className="h-4 w-4 mr-2" />
                  Valider ({tempSelectedPaletteIds.size})
                </Button>
              </div>
            </div>
          </Dialog>
        </div>
      ),
    },
    {
      id: 'details',
      label: 'Détails expédition',
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nom du contact chez le grossiste</label>
              <Input
                {...register('destination_contact')}
                error={errors.destination_contact?.message}
                placeholder="Nom du contact"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Numéro du contact</label>
              <Input
                {...register('destination_phone')}
                error={errors.destination_phone?.message}
                placeholder="Téléphone"
                type="tel"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nom du chauffeur</label>
              <Input
                {...register('transporter')}
                error={errors.transporter?.message}
                placeholder="Nom du chauffeur"
                readOnly={!!selectedDriverId}
                className={selectedDriverId ? 'bg-gray-50' : ''}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Contact du chauffeur</label>
              <Controller
                name="driver_id"
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    options={[
                      { value: '', label: 'Sélectionner un chauffeur' },
                      ...chauffeurs.map((c: User) => ({
                        value: c.id,
                        label: `${c.first_name} ${c.last_name}${c.phone_number ? ` - ${c.phone_number}` : ''}`,
                      })),
                    ]}
                    onChange={(e) => {
                      field.onChange(e.target.value);
                      const driver = chauffeurs.find((c: User) => c.id === e.target.value);
                      if (driver) {
                        setValue('transporter', `${driver.first_name} ${driver.last_name}`);
                      }
                    }}
                  />
                )}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Plaque d'immatriculation du camion</label>
            <Input
              {...register('vehicle_info')}
              error={errors.vehicle_info?.message}
              placeholder="AB-123-CD"
            />
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="w-full">
      <div className="mb-6">
        <Link to="/expeditions">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mt-4">Créer une nouvelle expédition</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card className="w-full">
          <CardHeader>
            <CardTitle>Informations de l'expédition</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* First row: Libellé and Date du jour */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Libellé</label>
                  <Input
                    {...register('libelle')}
                    error={errors.libelle?.message}
                    placeholder="Libellé de l'expédition"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Date du jour</label>
                  <Input type="date" value={today} disabled className="bg-gray-100" />
                </div>
              </div>

              {/* Second row: Destination (Grossiste) and Adresse du grossiste */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Destination (Choisir parmi les grossistes)</label>
                  <Controller
                    name="grossiste_id"
                    control={control}
                    render={({ field }) => (
                      <Select
                        {...field}
                        options={[
                          { value: '', label: 'Sélectionner un grossiste' },
                          ...grossistes.map((g: Partner) => ({
                            value: g.id,
                            label: g.name,
                          })),
                        ]}
                        onChange={(e) => {
                          field.onChange(e.target.value);
                        }}
                      />
                    )}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Adresse du grossiste</label>
                  <Input
                    {...register('destination_address')}
                    error={errors.destination_address?.message}
                    placeholder="Adresse du grossiste"
                    className="bg-gray-50"
                  />
                </div>
              </div>

              {/* Third row: Date d'expédition */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-1">Date d'expédition</label>
                  <Input
                    type="date"
                    {...register('expected_delivery_date')}
                    error={errors.expected_delivery_date?.message}
                  />
                </div>
                <div></div>
              </div>

              {/* Tabs for Palettes and Details */}
              <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium mb-1">Notes (optionnel)</label>
                <textarea
                  {...register('notes')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={3}
                  placeholder="Notes additionnelles"
                />
              </div>

              {/* Submit buttons */}
              <div className="flex space-x-3 pt-4">
                <Button type="submit" isLoading={createMutation.isPending}>
                  Créer l'expédition
                </Button>
                <Link to="/expeditions">
                  <Button type="button" variant="outline">
                    Annuler
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
};

export default CreateExpeditionPage;
