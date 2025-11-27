"""
Seed Test Data Script

Populates the database with realistic test data for GazTracker system.
Based on Côte d'Ivoire gas distribution hierarchy.

Run with: python scripts/seed_test_data.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
import asyncio
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal
from app.models import (
    Groupe, GrandDistributeur, CentreRemplisseur, Depot,
    Partner, PartnerType, User, UserRole,
    Palette, PaletteType, PaletteStatus,
    RFIDTag, RFIDTagStatus
)


def create_test_data(db: Session):
    """Create comprehensive test data."""
    
    print("🌱 Starting database seed...")
    
    # ==================== 1. GROUPES ====================
    print("\n📦 Creating Groupes...")
    
    groupe_petroci = Groupe(
        name="Pétroci Holding",
        code="PETROCI",
        address="Abidjan Plateau",
        city="Abidjan",
        phone="+225 27 20 00 00 00",
        email="contact@petroci.ci",
        is_active=True,
        notes="Société Nationale d'Opérations Pétrolières de Côte d'Ivoire"
    )
    db.add(groupe_petroci)
    
    groupe_sodigaz = Groupe(
        name="SODIGAZ",
        code="SODIGAZ",
        address="Abidjan Marcory",
        city="Abidjan",
        phone="+225 27 21 00 00 00",
        email="info@sodigaz.ci",
        is_active=True,
        notes="Société de Distribution de Gaz"
    )
    db.add(groupe_sodigaz)
    
    groupe_petro_ivoire = Groupe(
        name="Pétro Ivoire",
        code="PETRO_IV",
        address="Abidjan Treichville",
        city="Abidjan",
        phone="+225 27 22 00 00 00",
        email="contact@petroivoire.ci",
        is_active=True
    )
    db.add(groupe_petro_ivoire)
    
    db.commit()
    print(f"✅ Created {db.query(Groupe).count()} Groupes")
    
    # ==================== 2. GRANDS DISTRIBUTEURS ====================
    print("\n🏢 Creating Grands Distributeurs...")
    
    gd_cev3 = GrandDistributeur(
        name="CEV3 (PETROCI)",
        code="CEV3",
        groupe_id=groupe_petroci.id,
        address="Zone Industrielle Yopougon",
        city="Abidjan",
        phone="+225 27 23 00 00 00",
        email="cev3@petroci.ci",
        is_active=True,
        notes="Compagnie d'Embouteillage et de Vente de Gaz"
    )
    db.add(gd_cev3)
    
    gd_idc = GrandDistributeur(
        name="IDC WEST AFRICA",
        code="IDC_WA",
        groupe_id=groupe_petroci.id,
        address="Abidjan Koumassi",
        city="Abidjan",
        phone="+225 27 24 00 00 00",
        email="contact@idc-westafrica.com",
        is_active=True,
        notes="International Distribution Company"
    )
    db.add(gd_idc)
    
    gd_sodigaz_dist = GrandDistributeur(
        name="SODIGAZ Distribution",
        code="SODIGAZ_D",
        groupe_id=groupe_sodigaz.id,
        address="Abidjan Marcory Zone 4",
        city="Abidjan",
        phone="+225 27 25 00 00 00",
        email="distribution@sodigaz.ci",
        is_active=True
    )
    db.add(gd_sodigaz_dist)
    
    db.commit()
    print(f"✅ Created {db.query(GrandDistributeur).count()} Grands Distributeurs")
    
    # ==================== 3. CENTRES REMPLISSEURS ====================
    print("\n🏭 Creating Centres Remplisseurs...")
    
    centre_yopougon = CentreRemplisseur(
        name="Centre Remplisseur Yopougon",
        code="CR_YOP",
        grand_distributeur_id=gd_cev3.id,
        address="Zone Industrielle, Boulevard du Gabon",
        city="Yopougon",
        postal_code="18 BP 2036",
        country="Côte d'Ivoire",
        phone="+225 27 23 50 00 00",
        email="cr.yopougon@petroci.ci",
        contact_name="Konan Kouassi",
        contact_phone="+225 07 50 00 00 00",
        is_active=True,
        latitude=5.3364,
        longitude=-4.0267,
        notes="Principal centre de remplissage CEV3 - Capacité 5000 bouteilles/jour"
    )
    db.add(centre_yopougon)
    
    centre_koumassi = CentreRemplisseur(
        name="Centre Remplisseur Koumassi",
        code="CR_KOU",
        grand_distributeur_id=gd_idc.id,
        address="Zone Industrielle Koumassi",
        city="Koumassi",
        postal_code="01 BP 4521",
        country="Côte d'Ivoire",
        phone="+225 27 24 60 00 00",
        email="cr.koumassi@idc-wa.com",
        contact_name="Aminata Traoré",
        contact_phone="+225 07 60 00 00 00",
        is_active=True,
        latitude=5.2906,
        longitude=-3.9469,
        notes="Centre IDC - Capacité 3000 bouteilles/jour"
    )
    db.add(centre_koumassi)
    
    centre_marcory = CentreRemplisseur(
        name="Centre Remplisseur Marcory",
        code="CR_MAR",
        grand_distributeur_id=gd_sodigaz_dist.id,
        address="Marcory Résidentiel, Rue des Jardins",
        city="Marcory",
        postal_code="08 BP 1234",
        country="Côte d'Ivoire",
        phone="+225 27 25 70 00 00",
        email="cr.marcory@sodigaz.ci",
        contact_name="Yao N'Guessan",
        contact_phone="+225 07 70 00 00 00",
        is_active=True,
        latitude=5.2767,
        longitude=-3.9769,
        notes="Centre SODIGAZ - Capacité 4000 bouteilles/jour"
    )
    db.add(centre_marcory)
    
    db.commit()
    print(f"✅ Created {db.query(CentreRemplisseur).count()} Centres Remplisseurs")
    
    # ==================== 4. PARTNERS (GROSSISTES) ====================
    print("\n🤝 Creating Partners (Grossistes)...")
    
    grossiste1 = Partner(
        name="GAZ PLUS Distribution",
        code="GP001",
        type=PartnerType.GROSSISTE,
        contact_name="Moussa Diallo",
        contact_phone="+225 07 80 00 00 01",
        address="Adjamé Marché, Rue 12",
        city="Adjamé",
        phone="+225 27 26 00 00 01",
        email="contact@gazplus.ci",
        is_active=True,
        notes="Principal grossiste zone Adjamé"
    )
    db.add(grossiste1)
    
    grossiste2 = Partner(
        name="DISTRIBUTION MODERNE GAZ",
        code="DMG002",
        type=PartnerType.GROSSISTE,
        contact_name="Fatou Bamba",
        contact_phone="+225 07 80 00 00 02",
        address="Treichville, Boulevard VGE",
        city="Treichville",
        phone="+225 27 26 00 00 02",
        email="info@dmgaz.ci",
        is_active=True,
        notes="Grossiste couvrant Treichville et environs"
    )
    db.add(grossiste2)
    
    grossiste3 = Partner(
        name="SUPER GAZ IVOIRE",
        code="SGI003",
        type=PartnerType.GROSSISTE,
        contact_name="Ibrahim Coulibaly",
        contact_phone="+225 07 80 00 00 03",
        address="Abobo Gare, Avenue Principale",
        city="Abobo",
        phone="+225 27 26 00 00 03",
        email="contact@supergazivoire.ci",
        is_active=True,
        notes="Grand réseau de distribution Abobo"
    )
    db.add(grossiste3)
    
    db.commit()
    print(f"✅ Created {db.query(Partner).filter(Partner.type == PartnerType.GROSSISTE).count()} Grossistes")
    
    # ==================== 5. DEPOTS ====================
    print("\n📍 Creating Dépôts...")
    
    # Dépôts pour GAZ PLUS
    depot1_main = Depot(
        name="Dépôt Principal GAZ PLUS Adjamé",
        code="DP_GP_ADJ",
        partner_id=grossiste1.id,
        address="Adjamé Marché, Rue 12",
        city="Adjamé",
        latitude=5.3515,
        longitude=-4.0218,
        contact_name="Moussa Diallo",
        contact_phone="+225 07 80 00 00 01",
        capacity_b28=100,
        capacity_b12=200,
        capacity_b6=300,
        is_active=True,
        is_main_depot=True
    )
    db.add(depot1_main)
    
    depot1_sec = Depot(
        name="Dépôt Secondaire GAZ PLUS Williamsville",
        code="DS_GP_WIL",
        partner_id=grossiste1.id,
        address="Williamsville, Carrefour Solibra",
        city="Williamsville",
        latitude=5.3892,
        longitude=-3.9985,
        contact_name="Aya Koné",
        contact_phone="+225 07 80 00 00 11",
        capacity_b28=50,
        capacity_b12=100,
        capacity_b6=150,
        is_active=True,
        is_main_depot=False
    )
    db.add(depot1_sec)
    
    # Dépôts pour DMG
    depot2_main = Depot(
        name="Dépôt Principal DMG Treichville",
        code="DP_DMG_TRE",
        partner_id=grossiste2.id,
        address="Treichville, Boulevard VGE",
        city="Treichville",
        latitude=5.2767,
        longitude=-4.0041,
        contact_name="Fatou Bamba",
        contact_phone="+225 07 80 00 00 02",
        capacity_b28=80,
        capacity_b12=150,
        capacity_b6=200,
        is_active=True,
        is_main_depot=True
    )
    db.add(depot2_main)
    
    # Dépôts pour SUPER GAZ
    depot3_main = Depot(
        name="Dépôt Principal SUPER GAZ Abobo",
        code="DP_SGI_ABO",
        partner_id=grossiste3.id,
        address="Abobo Gare, Avenue Principale",
        city="Abobo",
        latitude=5.4167,
        longitude=-4.0208,
        contact_name="Ibrahim Coulibaly",
        contact_phone="+225 07 80 00 00 03",
        capacity_b28=120,
        capacity_b12=250,
        capacity_b6=350,
        is_active=True,
        is_main_depot=True
    )
    db.add(depot3_main)
    
    depot3_sec = Depot(
        name="Dépôt Secondaire SUPER GAZ Anyama",
        code="DS_SGI_ANY",
        partner_id=grossiste3.id,
        address="Anyama, Carrefour Mairie",
        city="Anyama",
        latitude=5.4950,
        longitude=-3.9486,
        contact_name="Saliou Touré",
        contact_phone="+225 07 80 00 00 31",
        capacity_b28=60,
        capacity_b12=120,
        capacity_b6=180,
        is_active=True,
        is_main_depot=False
    )
    db.add(depot3_sec)
    
    db.commit()
    print(f"✅ Created {db.query(Depot).count()} Dépôts")
    
    # ==================== 6. REVENDEURS ====================
    print("\n🏪 Creating Revendeurs...")
    
    revendeur1 = Partner(
        name="Boutique Kouadio Gaz",
        code="REV001",
        type=PartnerType.REVENDEUR,
        parent_grossiste_id=grossiste1.id,
        contact_name="Kouadio Jean",
        contact_phone="+225 05 00 00 00 01",
        address="Adjamé 220 Logements",
        city="Adjamé",
        phone="+225 25 20 00 00 01",
        is_active=True,
        notes="Revendeur exclusif GAZ PLUS"
    )
    db.add(revendeur1)
    
    # Dépôt du revendeur
    depot_rev1 = Depot(
        name="Boutique Kouadio Gaz",
        code="REV_KOU_ADJ",
        partner_id=revendeur1.id,
        address="Adjamé 220 Logements",
        city="Adjamé",
        latitude=5.3600,
        longitude=-4.0150,
        contact_name="Kouadio Jean",
        contact_phone="+225 05 00 00 00 01",
        capacity_b28=10,
        capacity_b12=20,
        capacity_b6=30,
        is_active=True,
        is_main_depot=True
    )
    db.add(depot_rev1)
    
    revendeur2 = Partner(
        name="Espace Gaz Moderne",
        code="REV002",
        type=PartnerType.REVENDEUR,
        parent_grossiste_id=grossiste3.id,
        contact_name="Adama Sanogo",
        contact_phone="+225 05 00 00 00 02",
        address="Abobo PK18",
        city="Abobo",
        phone="+225 25 20 00 00 02",
        is_active=True,
        notes="Revendeur SUPER GAZ - Zone PK18"
    )
    db.add(revendeur2)
    
    depot_rev2 = Depot(
        name="Espace Gaz Moderne PK18",
        code="REV_EGM_ABO",
        partner_id=revendeur2.id,
        address="Abobo PK18, Carrefour Pharmacie",
        city="Abobo",
        latitude=5.4250,
        longitude=-4.0150,
        contact_name="Adama Sanogo",
        contact_phone="+225 05 00 00 00 02",
        capacity_b28=15,
        capacity_b12=25,
        capacity_b6=40,
        is_active=True,
        is_main_depot=True
    )
    db.add(depot_rev2)
    
    db.commit()
    print(f"✅ Created {db.query(Partner).filter(Partner.type == PartnerType.REVENDEUR).count()} Revendeurs")
    
    # ==================== 7. USERS ====================
    print("\n👤 Creating Users...")
    
    # Admin
    admin = User(
        email="admin@gaztracker.ci",
        name="Administrateur Système",
        role=UserRole.ADMIN,
        phone="+225 07 00 00 00 00",
        is_active=True
    )
    admin.set_password("Admin@123")
    db.add(admin)
    
    # Responsable Logistique Centre
    resp_log = User(
        email="logistique@cev3.ci",
        name="Konan Kouassi",
        role=UserRole.RESPONSABLE_LOGISTIQUE,
        phone="+225 07 50 00 00 00",
        is_active=True
    )
    resp_log.set_password("Log@123")
    db.add(resp_log)
    
    # Opérateur Usine
    operateur = User(
        email="operateur@cev3.ci",
        name="Brou Marcel",
        role=UserRole.OPERATEUR_USINE,
        phone="+225 07 51 00 00 00",
        is_active=True
    )
    operateur.set_password("Op@123")
    db.add(operateur)
    
    # Chauffeur
    chauffeur1 = User(
        email="chauffeur1@transport.ci",
        name="Koné Seydou",
        role=UserRole.CHAUFFEUR,
        phone="+225 07 90 00 00 01",
        is_active=True
    )
    chauffeur1.set_password("Chauf@123")
    db.add(chauffeur1)
    
    chauffeur2 = User(
        email="chauffeur2@transport.ci",
        name="Diomandé Lassina",
        role=UserRole.CHAUFFEUR,
        phone="+225 07 90 00 00 02",
        is_active=True
    )
    chauffeur2.set_password("Chauf@123")
    db.add(chauffeur2)
    
    # Grossiste User
    grossiste_user = User(
        email="contact@gazplus.ci",
        name="Moussa Diallo",
        role=UserRole.GROSSISTE,
        phone="+225 07 80 00 00 01",
        is_active=True
    )
    grossiste_user.set_password("Gros@123")
    db.add(grossiste_user)
    
    db.commit()
    print(f"✅ Created {db.query(User).count()} Users")
    
    # ==================== 8. RFID TAGS ====================
    print("\n🏷️ Creating RFID Tags...")
    
    for i in range(1, 51):  # 50 RFID tags
        tag = RFIDTag(
            tag_id=f"RFID{i:04d}",
            label=f"Tag Palette #{i:04d}",
            status=RFIDTagStatus.ACTIVE,
            notes=f"Tag RFID pour palette de test {i}"
        )
        db.add(tag)
    
    db.commit()
    print(f"✅ Created {db.query(RFIDTag).count()} RFID Tags")
    
    # ==================== 9. PALETTES ====================
    print("\n📦 Creating Palettes...")
    
    rfid_tags = db.query(RFIDTag).all()
    palette_types = [PaletteType.B6, PaletteType.B12, PaletteType.B28]
    
    for i, rfid_tag in enumerate(rfid_tags[:30], 1):  # 30 palettes
        palette_type = palette_types[i % 3]
        capacity = {PaletteType.B6: 48, PaletteType.B12: 24, PaletteType.B28: 12}[palette_type]
        
        palette = Palette(
            serial_number=f"PAL-2025-{i:05d}",
            reference_code=f"REF-{i:04d}",
            rfid_tag_id=rfid_tag.id,
            type=palette_type,
            capacity=capacity,
            status=PaletteStatus.AU_CENTRE,
            is_full=True,
            current_centre_remplisseur_id=centre_yopougon.id,
            manufacturing_date=datetime.now() - timedelta(days=365),
            notes=f"Palette {palette_type.value} - Stock Centre Yopougon",
            created_by_id=admin.id
        )
        db.add(palette)
    
    db.commit()
    print(f"✅ Created {db.query(Palette).count()} Palettes")
    
    print("\n" + "="*60)
    print("✨ SEED COMPLETED SUCCESSFULLY! ✨")
    print("="*60)
    print(f"""
📊 Summary:
  - {db.query(Groupe).count()} Groupes
  - {db.query(GrandDistributeur).count()} Grands Distributeurs
  - {db.query(CentreRemplisseur).count()} Centres Remplisseurs
  - {db.query(Partner).filter(Partner.type == PartnerType.GROSSISTE).count()} Grossistes
  - {db.query(Partner).filter(Partner.type == PartnerType.REVENDEUR).count()} Revendeurs
  - {db.query(Depot).count()} Dépôts
  - {db.query(User).count()} Users
  - {db.query(RFIDTag).count()} RFID Tags
  - {db.query(Palette).count()} Palettes

🔐 Test User Credentials:
  Admin:          admin@gaztracker.ci / Admin@123
  Logistique:     logistique@cev3.ci / Log@123
  Opérateur:      operateur@cev3.ci / Op@123
  Chauffeur 1:    chauffeur1@transport.ci / Chauf@123
  Chauffeur 2:    chauffeur2@transport.ci / Chauf@123
  Grossiste:      contact@gazplus.ci / Gros@123
    """)


def main():
    """Main function to run seed."""
    print("🚀 GazTracker - Database Seed Script")
    print("="*60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(Groupe).count()
        if existing_count > 0:
            response = input(f"\n⚠️  Database already has {existing_count} Groupe(s). Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("❌ Seed cancelled.")
                return
        
        # Create test data
        create_test_data(db)
        
        print("\n✅ All done! You can now test the system with realistic data.")
        
    except Exception as e:
        print(f"\n❌ Error during seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

