#!/usr/bin/env python3
"""
Script pour créer des données de démonstration pour GazTracker
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from random import choice, randint, sample
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import db_manager
from app.models import *
from app.utils.security import hash_password

# Initialize database
db_manager.init_db()

# Create session factory
def SessionLocal():
    """Create a new database session"""
    return db_manager.sync_session_maker()


def clear_data(db: Session):
    """Supprime toutes les données existantes (sauf admin)"""
    print("🗑️  Nettoyage des données existantes...")
    
    # Fonction helper pour supprimer seulement si la table existe
    def safe_delete(model_class, table_name=None):
        try:
            db.query(model_class).delete()
            return True
        except Exception as e:
            if "does not exist" in str(e) or "UndefinedTable" in str(e):
                print(f"   ⚠️  Table {table_name or model_class.__tablename__} n'existe pas encore, ignorée")
                return False
            else:
                raise
    
    # Supprimer dans l'ordre inverse des dépendances
    safe_delete(Notification, "notifications")
    safe_delete(DetailRetour, "details_retour")
    safe_delete(BonReceptionRetour, "bons_reception_retour")
    safe_delete(LivraisonDetail, "livraisons_details")
    safe_delete(CollecteVide, "collectes_vides")
    safe_delete(BonEnlevement, "bons_enlevement")
    safe_delete(PaletteMovement, "palette_movements")
    
    # Pour Palette, vérifier si la table existe avant de modifier
    try:
        db.query(Palette).filter(Palette.rfid_tag_id.isnot(None)).update({Palette.rfid_tag_id: None})
        db.query(Palette).delete()
    except Exception as e:
        if "does not exist" in str(e) or "UndefinedTable" in str(e):
            print("   ⚠️  Table palettes n'existe pas encore, ignorée")
        else:
            raise
    
    # Contacts
    safe_delete(Contact, "contacts")
    
    # Dépôts
    safe_delete(Depot, "depots")
    
    # Centres Remplisseurs
    safe_delete(CentreRemplisseur, "centres_remplisseurs")
    
    # Partenaires
    safe_delete(Partner, "partners")
    
    # Grands Distributeurs
    safe_delete(GrandDistributeur, "grand_distributeurs")
    
    # Groupes
    safe_delete(Groupe, "groupes")
    
    # Utilisateurs (sauf admin)
    try:
        db.query(User).filter(User.email != 'admin@gaztracker.com').delete()
    except Exception as e:
        if "does not exist" in str(e) or "UndefinedTable" in str(e):
            print("   ⚠️  Table users n'existe pas encore, ignorée")
        else:
            raise
    
    db.commit()
    print("✅ Données nettoyées")


def create_groupes(db: Session):
    """Créer des groupes"""
    print("\n📦 Création des Groupes...")
    
    groupes_data = [
        {
            "name": "PETROCI Holding",
            "code": "PETROCI",
            "address": "Rue des Pétroles, Plateau",
            "city": "Abidjan",
            "postal_code": "01 BP 1234",
            "phone": "+225 27 20 30 40 50",
            "email": "contact@petroci.ci",
            "notes": "Groupe leader dans la distribution de gaz en Côte d'Ivoire"
        },
        {
            "name": "SODIGAZ CI",
            "code": "SODIGAZ",
            "address": "Boulevard Valéry Giscard d'Estaing, Marcory",
            "city": "Abidjan",
            "postal_code": "06 BP 2345",
            "phone": "+225 27 21 31 41 51",
            "email": "info@sodigaz.ci",
            "notes": "Société de distribution de gaz domestique"
        },
        {
            "name": "IVOIRE GAZ",
            "code": "IVOGAZ",
            "address": "Zone Industrielle, Yopougon",
            "city": "Abidjan",
            "postal_code": "23 BP 3456",
            "phone": "+225 27 22 32 42 52",
            "email": "contact@ivoiregaz.ci",
            "notes": "Distributeur régional de gaz"
        }
    ]
    
    groupes = []
    for data in groupes_data:
        groupe = Groupe(**data)
        db.add(groupe)
        groupes.append(groupe)
    
    db.commit()
    print(f"✅ {len(groupes)} groupes créés")
    return groupes


def create_grands_distributeurs(db: Session, groupes):
    """Créer des grands distributeurs"""
    print("\n🏢 Création des Grands Distributeurs...")
    
    gd_data = [
        # PETROCI
        {"name": "Total Energies CI", "code": "TOTAL_CI", "groupe": groupes[0], "city": "Abidjan"},
        {"name": "Shell CI", "code": "SHELL_CI", "groupe": groupes[0], "city": "Abidjan"},
        {"name": "Oryx Energies", "code": "ORYX", "groupe": groupes[0], "city": "Abidjan"},
        # SODIGAZ
        {"name": "Vivo Energy CI", "code": "VIVO", "groupe": groupes[1], "city": "Abidjan"},
        {"name": "Puma Energy", "code": "PUMA", "groupe": groupes[1], "city": "San Pedro"},
        # IVOIRE GAZ
        {"name": "Afriquia Gaz CI", "code": "AFRIQUIA", "groupe": groupes[2], "city": "Yamoussoukro"},
        {"name": "Butagaz CI", "code": "BUTAGAZ", "groupe": groupes[2], "city": "Bouaké"},
    ]
    
    gds = []
    for i, data in enumerate(gd_data):
        gd = GrandDistributeur(
            name=data["name"],
            code=data["code"],
            groupe_id=data["groupe"].id,
            address=f"{randint(1, 999)} Avenue {choice(['de la République', 'du Commerce', 'Principale'])}",
            city=data["city"],
            phone=f"+225 27 {randint(20, 29)} {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
            email=f"contact@{data['code'].lower()}.ci",
            is_active=True
        )
        db.add(gd)
        gds.append(gd)
    
    db.commit()
    print(f"✅ {len(gds)} grands distributeurs créés")
    return gds


def create_centres_remplisseurs(db: Session, gds):
    """Créer des centres remplisseurs"""
    print("\n🏭 Création des Centres Remplisseurs...")
    
    cities = ["Abidjan", "Bouaké", "San Pedro", "Yamoussoukro", "Korhogo", "Daloa"]
    centres = []
    
    for gd in gds:
        # 2-3 centres par grand distributeur
        nb_centres = randint(2, 3)
        for i in range(nb_centres):
            city = choice(cities)
            centre = CentreRemplisseur(
                name=f"Centre {gd.name} - {city}",
                code=f"{gd.code}_CR{i+1:02d}",
                grand_distributeur_id=gd.id,
                address=f"Zone Industrielle {choice(['Nord', 'Sud', 'Est', 'Ouest'])}",
                city=city,
                postal_code=f"{randint(10, 99)} BP {randint(1000, 9999)}",
                country="Côte d'Ivoire",
                phone=f"+225 27 {randint(20, 29)} {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
                email=f"centre.{city.lower()}@{gd.code.lower()}.ci",
                contact_name=f"{choice(['Kouassi', 'Koffi', 'Yao', 'N\'Guessan'])} {choice(['Jean', 'Marie', 'Paul', 'Sophie'])}",
                contact_phone=f"+225 07 {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
                latitude=5.0 + randint(-300, 300) / 100,
                longitude=-5.0 + randint(-300, 300) / 100,
                capacity_b28=randint(500, 2000),
                capacity_b12=randint(1000, 3000),
                capacity_b6=randint(2000, 5000),
                is_active=True,
                notes=f"Centre de remplissage {city}"
            )
            db.add(centre)
            centres.append(centre)
    
    db.commit()
    print(f"✅ {len(centres)} centres remplisseurs créés")
    return centres


def create_partners(db: Session, gds):
    """Créer des partenaires (grossistes et détaillants)"""
    print("\n🤝 Création des Partenaires...")
    
    partners = []
    
    # Grossistes
    grossistes_names = [
        "Grossiste Plateau", "Grossiste Marcory", "Grossiste Yopougon",
        "Grossiste Cocody", "Grossiste Adjamé", "Grossiste Treichville",
        "Distribution Bouaké", "Distribution San Pedro", "Distribution Yamoussoukro"
    ]
    
    for name in grossistes_names:
        partner = Partner(
            name=name,
            code=f"GRO_{len(partners)+1:03d}",
            type=PartnerType.GROSSISTE,
            address=f"{randint(1, 999)} Rue {choice(['du Commerce', 'Principale', 'des Affaires'])}",
            city=choice(["Abidjan", "Bouaké", "San Pedro", "Yamoussoukro"]),
            postal_code=f"{randint(10, 99)} BP {randint(1000, 9999)}",
            phone=f"+225 27 {randint(20, 29)} {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
            email=f"contact@{name.lower().replace(' ', '')}.ci",
            contact_name=f"{choice(['Kouadio', 'Konan', 'Brou', 'Tanoh'])} {choice(['Marc', 'Eric', 'Alain', 'Didier'])}",
            contact_phone=f"+225 07 {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
            is_active=True
        )
        db.add(partner)
        partners.append(partner)
    
    # Détaillants
    detaillants_names = [
        "Boutique Gaz Express", "Point Gaz Plus", "Station Gaz Service",
        "Gaz Center", "Pro Gaz", "Gaz Direct", "Rapid Gaz",
        "Super Gaz", "Gaz Confort", "Eco Gaz"
    ]
    
    for name in detaillants_names:
        partner = Partner(
            name=name,
            code=f"DET_{len(partners)+1:03d}",
            type=PartnerType.DETAILLANT,
            address=f"{randint(1, 999)} Avenue {choice(['de la Paix', 'du Progrès', 'de l\'Indépendance'])}",
            city=choice(["Abidjan", "Bouaké", "Daloa", "Korhogo"]),
            postal_code=f"{randint(10, 99)} BP {randint(1000, 9999)}",
            phone=f"+225 27 {randint(20, 29)} {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
            email=f"contact@{name.lower().replace(' ', '')}.ci",
            contact_name=f"{choice(['Traoré', 'Coulibaly', 'Ouattara', 'Diallo'])} {choice(['Ibrahim', 'Mohamed', 'Amadou', 'Abou'])}",
            contact_phone=f"+225 05 {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
            is_active=True
        )
        db.add(partner)
        partners.append(partner)
    
    db.commit()
    print(f"✅ {len(partners)} partenaires créés ({len(grossistes_names)} grossistes, {len(detaillants_names)} détaillants)")
    return partners


def create_depots(db: Session, partners):
    """Créer des dépôts"""
    print("\n📍 Création des Dépôts...")
    
    depots = []
    
    # Dépôts pour les grossistes
    grossistes = [p for p in partners if p.type == PartnerType.GROSSISTE]
    
    for partner in grossistes:
        # 1-2 dépôts par grossiste
        nb_depots = randint(1, 2)
        for i in range(nb_depots):
            is_main = i == 0
            depot = Depot(
                name=f"Dépôt {partner.name} - {choice(['Principal', 'Secondaire', 'Nord', 'Sud'])}",
                code=f"{partner.code}_DEP{i+1}",
                partner_id=partner.id,
                address=f"Zone {choice(['Industrielle', 'Commerciale', 'Logistique'])}",
                city=partner.city,
                postal_code=partner.postal_code,
                latitude=5.0 + randint(-300, 300) / 100,
                longitude=-5.0 + randint(-300, 300) / 100,
                contact_name=f"{choice(['Assé', 'Aké', 'Anoh', 'Kouamé'])} {choice(['Pierre', 'Jacques', 'Louis', 'André'])}",
                contact_phone=f"+225 07 {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
                capacity_b28=randint(200, 1000),
                capacity_b12=randint(500, 1500),
                capacity_b6=randint(1000, 3000),
                is_main_depot=is_main,
                is_active=True,
                notes=f"{'Dépôt principal' if is_main else 'Dépôt secondaire'} de {partner.name}"
            )
            db.add(depot)
            depots.append(depot)
    
    db.commit()
    print(f"✅ {len(depots)} dépôts créés")
    return depots


def create_users(db: Session):
    """Créer des utilisateurs"""
    print("\n👥 Création des Utilisateurs...")
    
    users_data = [
        # Gestionnaires
        {"email": "gestionnaire1@gaztracker.com", "first_name": "Kouassi", "last_name": "Jean", "role": UserRole.GESTIONNAIRE, "phone": "+225 07 01 02 03 04"},
        {"email": "gestionnaire2@gaztracker.com", "first_name": "Koffi", "last_name": "Marie", "role": UserRole.GESTIONNAIRE, "phone": "+225 07 11 12 13 14"},
        # Magasiniers
        {"email": "magasinier1@gaztracker.com", "first_name": "Yao", "last_name": "Paul", "role": UserRole.MAGASINIER, "phone": "+225 07 21 22 23 24"},
        {"email": "magasinier2@gaztracker.com", "first_name": "N'Guessan", "last_name": "Sophie", "role": UserRole.MAGASINIER, "phone": "+225 07 31 32 33 34"},
        {"email": "magasinier3@gaztracker.com", "first_name": "Kouadio", "last_name": "Marc", "role": UserRole.MAGASINIER, "phone": "+225 07 41 42 43 44"},
        # Contrôleurs
        {"email": "controleur1@gaztracker.com", "first_name": "Konan", "last_name": "Eric", "role": UserRole.CONTROLEUR, "phone": "+225 07 51 52 53 54"},
        {"email": "controleur2@gaztracker.com", "first_name": "Brou", "last_name": "Alain", "role": UserRole.CONTROLEUR, "phone": "+225 07 61 62 63 64"},
        # Chauffeurs
        {"email": "chauffeur1@gaztracker.com", "first_name": "Traoré", "last_name": "Ibrahim", "role": UserRole.CHAUFFEUR, "phone": "+225 05 01 02 03 04"},
        {"email": "chauffeur2@gaztracker.com", "first_name": "Coulibaly", "last_name": "Mohamed", "role": UserRole.CHAUFFEUR, "phone": "+225 05 11 12 13 14"},
        {"email": "chauffeur3@gaztracker.com", "first_name": "Ouattara", "last_name": "Amadou", "role": UserRole.CHAUFFEUR, "phone": "+225 05 21 22 23 24"},
        {"email": "chauffeur4@gaztracker.com", "first_name": "Diallo", "last_name": "Abou", "role": UserRole.CHAUFFEUR, "phone": "+225 05 31 32 33 34"},
    ]
    
    users = []
    for data in users_data:
        user = User(
            email=data["email"],
            password=hash_password("demo123"),
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data["phone"],
            role=data["role"],
            is_active=True
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✅ {len(users)} utilisateurs créés")
    return users


def create_contacts(db: Session, partners, centres):
    """Créer des contacts"""
    print("\n📞 Création des Contacts...")
    
    contacts = []
    
    # Contacts pour les partenaires
    for partner in sample(partners, min(10, len(partners))):
        for i in range(randint(1, 3)):
            contact = Contact(
                first_name=choice(['Kouassi', 'Koffi', 'Yao', 'Traoré', 'Konan']),
                last_name=choice(['Jean', 'Marie', 'Paul', 'Ibrahim', 'Eric']),
                email=f"contact{i+1}@{partner.code.lower()}.ci",
                phone=f"+225 0{randint(5, 7)} {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
                position=choice(['Directeur', 'Responsable', 'Agent', 'Coordinateur']),
                partner_id=partner.id,
                is_primary=i == 0,
                notes=f"Contact {choice(['commercial', 'technique', 'administratif'])} de {partner.name}"
            )
            db.add(contact)
            contacts.append(contact)
    
    # Contacts pour les centres remplisseurs
    for centre in sample(centres, min(10, len(centres))):
        contact = Contact(
            first_name=choice(['Assé', 'Aké', 'Anoh', 'Kouamé']),
            last_name=choice(['Pierre', 'Jacques', 'Louis', 'André']),
            email=f"contact@{centre.code.lower()}.ci",
            phone=f"+225 07 {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
            position=choice(['Chef de centre', 'Responsable technique', 'Agent']),
            centre_remplisseur_id=centre.id,
            is_primary=True,
            notes=f"Contact principal du {centre.name}"
        )
        db.add(contact)
        contacts.append(contact)
    
    db.commit()
    print(f"✅ {len(contacts)} contacts créés")
    return contacts


def create_palettes(db: Session, centres, partners, depots):
    """Créer des palettes"""
    print("\n📦 Création des Palettes...")
    
    palettes = []
    base_date = datetime.now() - timedelta(days=180)
    
    # Palettes aux centres remplisseurs
    for centre in centres:
        nb_palettes = randint(50, 150)
        for i in range(nb_palettes):
            palette_type = choice([PaletteType.B28, PaletteType.B12, PaletteType.B6])
            status = choice([
                PaletteStatus.AU_CENTRE,
                PaletteStatus.EN_COURS_CHARGEMENT,
                PaletteStatus.EN_LIVRAISON
            ])
            
            palette = Palette(
                numero=f"PAL-{centre.code}-{i+1:04d}",
                type=palette_type,
                status=status,
                current_centre_remplisseur_id=centre.id if status in [PaletteStatus.AU_CENTRE, PaletteStatus.EN_COURS_CHARGEMENT] else None,
                date_last_fill=base_date + timedelta(days=randint(0, 180)),
                condition=choice([PaletteCondition.NEUVE, PaletteCondition.BON_ETAT, PaletteCondition.USAGEE]),
                notes=f"Palette {palette_type.value} du centre {centre.name}"
            )
            db.add(palette)
            palettes.append(palette)
    
    # Palettes chez les grossistes
    grossistes = [p for p in partners if p.type == PartnerType.GROSSISTE]
    for grossiste in grossistes:
        nb_palettes = randint(30, 80)
        for i in range(nb_palettes):
            palette_type = choice([PaletteType.B28, PaletteType.B12, PaletteType.B6])
            
            palette = Palette(
                numero=f"PAL-{grossiste.code}-{i+1:04d}",
                type=palette_type,
                status=PaletteStatus.AU_DEPOT,
                current_partner_id=grossiste.id,
                date_last_fill=base_date + timedelta(days=randint(0, 180)),
                condition=choice([PaletteCondition.BON_ETAT, PaletteCondition.USAGEE]),
                notes=f"Palette {palette_type.value} chez {grossiste.name}"
            )
            db.add(palette)
            palettes.append(palette)
    
    db.commit()
    print(f"✅ {len(palettes)} palettes créées")
    return palettes


def create_bons_enlevement(db: Session, centres, partners, depots, users):
    """Créer des bons d'enlèvement"""
    print("\n📋 Création des Bons d'Enlèvement...")
    
    bons = []
    base_date = datetime.now() - timedelta(days=90)
    grossistes = [p for p in partners if p.type == PartnerType.GROSSISTE]
    magasiniers = [u for u in users if u.role == UserRole.MAGASINIER]
    
    for i in range(50):
        centre = choice(centres)
        grossiste = choice(grossistes)
        depot_principal = choice([d for d in depots if d.partner_id == grossiste.id])
        magasinier = choice(magasiniers) if magasiniers else None
        
        date_creation = base_date + timedelta(days=randint(0, 90))
        status = choice([
            BonEnlevementStatus.EN_ATTENTE,
            BonEnlevementStatus.EN_COURS_CHARGEMENT,
            BonEnlevementStatus.EN_ROUTE,
            BonEnlevementStatus.EN_COURS_LIVRAISON,
            BonEnlevementStatus.TERMINE,
        ])
        
        bon = BonEnlevement(
            numero_bon=f"BE-{date_creation.strftime('%Y%m')}-{i+1:04d}",
            reference=f"REF-{randint(10000, 99999)}",
            centre_remplisseur_id=centre.id,
            grossiste_id=grossiste.id,
            depot_principal_id=depot_principal.id,
            vehicule_immatriculation=f"{choice(['AA', 'AB', 'AC', 'AD'])}-{randint(1000, 9999)}-{choice(['CI', 'AB'])}",
            chauffeur_nom=f"{choice(['Traoré', 'Coulibaly', 'Ouattara'])} {choice(['Ibrahim', 'Mohamed', 'Amadou'])}",
            chauffeur_societe=grossiste.name,
            chauffeur_phone=f"+225 05 {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
            status=status,
            date_creation=date_creation,
            date_validation=date_creation + timedelta(hours=1) if status != BonEnlevementStatus.EN_ATTENTE else None,
            date_debut_chargement=date_creation + timedelta(hours=2) if status not in [BonEnlevementStatus.EN_ATTENTE] else None,
            date_depart=date_creation + timedelta(hours=4) if status not in [BonEnlevementStatus.EN_ATTENTE, BonEnlevementStatus.EN_COURS_CHARGEMENT] else None,
            date_debut_livraison=date_creation + timedelta(hours=6) if status in [BonEnlevementStatus.EN_COURS_LIVRAISON, BonEnlevementStatus.TERMINE] else None,
            date_fin=date_creation + timedelta(hours=8) if status == BonEnlevementStatus.TERMINE else None,
            magasinier_id=magasinier.id if magasinier and status != BonEnlevementStatus.EN_ATTENTE else None,
            palette_count=randint(10, 50),
            livraison_count=randint(1, 5),
            observations=f"Livraison {choice(['urgente', 'normale', 'planifiée'])} pour {grossiste.name}",
            instructions_livraison="Livrer en priorité les palettes B28"
        )
        db.add(bon)
        bons.append(bon)
    
    db.commit()
    print(f"✅ {len(bons)} bons d'enlèvement créés")
    return bons


def create_bons_reception_retour(db: Session, centres, partners, depots, users):
    """Créer des bons de réception retour"""
    print("\n🔄 Création des Bons de Réception Retour...")
    
    bons = []
    base_date = datetime.now() - timedelta(days=90)
    grossistes = [p for p in partners if p.type == PartnerType.GROSSISTE]
    controleurs = [u for u in users if u.role == UserRole.CONTROLEUR]
    magasiniers = [u for u in users if u.role == UserRole.MAGASINIER]
    
    for i in range(30):
        centre = choice(centres)
        grossiste = choice(grossistes)
        depot = choice([d for d in depots if d.partner_id == grossiste.id])
        controleur = choice(controleurs) if controleurs else None
        magasinier = choice(magasiniers) if magasiniers else None
        
        date_creation = base_date + timedelta(days=randint(0, 90))
        status = choice([
            BonReceptionRetourStatus.EN_ATTENTE,
            BonReceptionRetourStatus.EN_ROUTE,
            BonReceptionRetourStatus.ARRIVE,
            BonReceptionRetourStatus.EN_COURS_CONTROLE,
            BonReceptionRetourStatus.VALIDE,
        ])
        
        bon = BonReceptionRetour(
            numero_bon=f"BRR-{date_creation.strftime('%Y%m')}-{i+1:04d}",
            numero_bl=f"BL-{randint(10000, 99999)}",
            numero_facture=f"FACT-{randint(10000, 99999)}",
            grossiste_id=grossiste.id,
            depot_depart_id=depot.id,
            centre_remplisseur_id=centre.id,
            vehicule_immatriculation=f"{choice(['AA', 'AB', 'AC', 'AD'])}-{randint(1000, 9999)}-{choice(['CI', 'AB'])}",
            chauffeur_nom=f"{choice(['Traoré', 'Coulibaly', 'Ouattara'])} {choice(['Ibrahim', 'Mohamed', 'Amadou'])}",
            chauffeur_phone=f"+225 05 {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
            status=status,
            date_creation=date_creation,
            date_depart=date_creation + timedelta(hours=1) if status != BonReceptionRetourStatus.EN_ATTENTE else None,
            date_arrivee=date_creation + timedelta(hours=3) if status not in [BonReceptionRetourStatus.EN_ATTENTE, BonReceptionRetourStatus.EN_ROUTE] else None,
            date_debut_controle=date_creation + timedelta(hours=4) if status in [BonReceptionRetourStatus.EN_COURS_CONTROLE, BonReceptionRetourStatus.VALIDE] else None,
            date_validation=date_creation + timedelta(hours=6) if status == BonReceptionRetourStatus.VALIDE else None,
            controleur_id=controleur.id if controleur and status in [BonReceptionRetourStatus.EN_COURS_CONTROLE, BonReceptionRetourStatus.VALIDE] else None,
            magasinier_id=magasinier.id if magasinier and status not in [BonReceptionRetourStatus.EN_ATTENTE, BonReceptionRetourStatus.EN_ROUTE] else None,
            quantite_attendue_b28=randint(10, 30),
            quantite_attendue_b12=randint(20, 50),
            quantite_attendue_b6=randint(30, 80),
            quantite_recue_b28=randint(10, 30) if status not in [BonReceptionRetourStatus.EN_ATTENTE, BonReceptionRetourStatus.EN_ROUTE] else None,
            quantite_recue_b12=randint(20, 50) if status not in [BonReceptionRetourStatus.EN_ATTENTE, BonReceptionRetourStatus.EN_ROUTE] else None,
            quantite_recue_b6=randint(30, 80) if status not in [BonReceptionRetourStatus.EN_ATTENTE, BonReceptionRetourStatus.EN_ROUTE] else None,
            observations=f"Retour de palettes vides de {grossiste.name}"
        )
        
        # Calculer le taux d'acceptation si validé
        if status == BonReceptionRetourStatus.VALIDE and bon.quantite_recue_b28 and bon.quantite_recue_b12 and bon.quantite_recue_b6:
            total_attendu = bon.quantite_attendue_b28 + bon.quantite_attendue_b12 + bon.quantite_attendue_b6
            total_recu = bon.quantite_recue_b28 + bon.quantite_recue_b12 + bon.quantite_recue_b6
            bon.taux_acceptation = round((total_recu / total_attendu * 100) if total_attendu > 0 else 0, 2)
        
        db.add(bon)
        bons.append(bon)
    
    db.commit()
    print(f"✅ {len(bons)} bons de réception retour créés")
    return bons


def create_notifications(db: Session, users):
    """Créer des notifications"""
    print("\n🔔 Création des Notifications...")
    
    notifications = []
    base_date = datetime.now() - timedelta(days=30)
    
    notification_templates = [
        {
            "title": "Nouveau bon d'enlèvement",
            "message": "Un nouveau bon d'enlèvement BE-{} a été créé",
            "type": NotificationType.INFO,
            "category": NotificationCategory.ENLEVEMENT
        },
        {
            "title": "Bon d'enlèvement validé",
            "message": "Le bon d'enlèvement BE-{} a été validé",
            "type": NotificationType.SUCCESS,
            "category": NotificationCategory.ENLEVEMENT
        },
        {
            "title": "Livraison terminée",
            "message": "La livraison du bon BE-{} est terminée",
            "type": NotificationType.SUCCESS,
            "category": NotificationCategory.ENLEVEMENT
        },
        {
            "title": "Retour de palettes",
            "message": "Un retour de palettes BRR-{} est en attente de contrôle",
            "type": NotificationType.WARNING,
            "category": NotificationCategory.RETOUR
        },
        {
            "title": "Contrôle validé",
            "message": "Le contrôle du bon BRR-{} a été validé avec succès",
            "type": NotificationType.SUCCESS,
            "category": NotificationCategory.RETOUR
        },
        {
            "title": "Stock faible",
            "message": "Le stock de palettes B28 est inférieur à 50 unités",
            "type": NotificationType.WARNING,
            "category": NotificationCategory.STOCK
        },
        {
            "title": "Palette endommagée",
            "message": "Une palette {} nécessite une inspection",
            "type": NotificationType.WARNING,
            "category": NotificationCategory.MAINTENANCE
        },
    ]
    
    for user in users:
        # Créer 5-15 notifications par utilisateur
        nb_notifs = randint(5, 15)
        for i in range(nb_notifs):
            template = choice(notification_templates)
            date = base_date + timedelta(days=randint(0, 30), hours=randint(0, 23))
            is_read = randint(0, 100) > 30  # 70% de chances d'être lues
            
            notif = Notification(
                user_id=user.id,
                title=template["title"],
                message=template["message"].format(f"{randint(100, 999):04d}"),
                type=template["type"],
                category=template["category"],
                is_read=is_read,
                read_at=date + timedelta(hours=randint(1, 24)) if is_read else None,
                created_at=date
            )
            db.add(notif)
            notifications.append(notif)
    
    db.commit()
    print(f"✅ {len(notifications)} notifications créées")
    return notifications


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🚀 GÉNÉRATION DE DONNÉES DE DÉMONSTRATION GAZTRACKER")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Nettoyage
        clear_data(db)
        
        # Création des données
        groupes = create_groupes(db)
        gds = create_grands_distributeurs(db, groupes)
        centres = create_centres_remplisseurs(db, gds)
        partners = create_partners(db, gds)
        depots = create_depots(db, partners)
        users = create_users(db)
        contacts = create_contacts(db, partners, centres)
        palettes = create_palettes(db, centres, partners, depots)
        bons_enlevement = create_bons_enlevement(db, centres, partners, depots, users)
        bons_retour = create_bons_reception_retour(db, centres, partners, depots, users)
        notifications = create_notifications(db, users)
        
        print("\n" + "="*60)
        print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS !")
        print("="*60)
        print(f"\n📊 Résumé:")
        print(f"   • Groupes:                {len(groupes)}")
        print(f"   • Grands Distributeurs:   {len(gds)}")
        print(f"   • Centres Remplisseurs:   {len(centres)}")
        print(f"   • Partenaires:            {len(partners)}")
        print(f"   • Dépôts:                 {len(depots)}")
        print(f"   • Utilisateurs:           {len(users)}")
        print(f"   • Contacts:               {len(contacts)}")
        print(f"   • Palettes:               {len(palettes)}")
        print(f"   • Bons d'Enlèvement:      {len(bons_enlevement)}")
        print(f"   • Bons Réception Retour:  {len(bons_retour)}")
        print(f"   • Notifications:          {len(notifications)}")
        print("\n🎉 Vous pouvez maintenant tester l'application !")
        print("   Login: admin@gaztracker.com / admin123")
        print("   Ou utilisez les comptes créés avec le mot de passe: demo123\n")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

