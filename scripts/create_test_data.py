#!/usr/bin/env python3
"""
Script to create test partners and contacts.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import db_manager
from app.models.partner import Partner, PartnerType
from app.models.contact import Contact


def create_test_partners_and_contacts():
    """Create test partners and contacts."""
    # Initialize database
    db_manager.init_db()
    
    # Create session
    db: Session = db_manager.sync_session_maker()
    
    try:
        # Test Partners
        partners_data = [
            {
                "name": "Grossiste Paris Nord",
                "type": PartnerType.GROSSISTE,
                "address": "123 Rue de Commerce",
                "city": "Paris",
                "postal_code": "75015",
                "country": "France",
                "phone": "+33123456789",
                "email": "contact@grossiste-paris-nord.fr",
                "is_active": True,
                "notes": "Principal grossiste pour la région parisienne"
            },
            {
                "name": "Distributeur Gaz Sud",
                "type": PartnerType.DISTRIBUTEUR,
                "address": "456 Avenue des Industries",
                "city": "Lyon",
                "postal_code": "69001",
                "country": "France",
                "phone": "+33456789123",
                "email": "info@distributeur-gaz-sud.fr",
                "is_active": True,
                "notes": "Distributeur principal pour le Sud de la France"
            },
            {
                "name": "Transport Express",
                "type": PartnerType.TRANSPORTEUR,
                "address": "789 Boulevard des Transports",
                "city": "Marseille",
                "postal_code": "13001",
                "country": "France",
                "phone": "+33456789145",
                "email": "contact@transport-express.fr",
                "is_active": True,
                "notes": "Service de transport rapide"
            },
            {
                "name": "Grossiste Lyon Centre",
                "type": PartnerType.GROSSISTE,
                "address": "321 Rue de la République",
                "city": "Lyon",
                "postal_code": "69002",
                "country": "France",
                "phone": "+33456789167",
                "email": "contact@grossiste-lyon.fr",
                "is_active": True,
                "notes": "Grossiste pour la région lyonnaise"
            },
            {
                "name": "Services Logistiques Pro",
                "type": PartnerType.AUTRE,
                "address": "654 Chemin des Services",
                "city": "Toulouse",
                "postal_code": "31000",
                "country": "France",
                "phone": "+33567890123",
                "email": "info@services-logistiques.fr",
                "is_active": True,
                "notes": "Services logistiques divers"
            }
        ]
        
        created_partners = []
        for partner_data in partners_data:
            # Check if partner already exists
            existing = db.query(Partner).filter(Partner.name == partner_data["name"]).first()
            if existing:
                print(f"Partenaire '{partner_data['name']}' existe déjà, ignoré.")
                created_partners.append(existing)
            else:
                partner = Partner(**partner_data)
                db.add(partner)
                db.flush()  # Flush to get the ID
                created_partners.append(partner)
                print(f"✓ Partenaire créé: {partner.name} ({partner.type.value})")
        
        db.commit()
        
        # Test Contacts
        contacts_data = [
            {
                "partner_id": created_partners[0].id,  # Grossiste Paris Nord
                "first_name": "Jean",
                "last_name": "Dupont",
                "position": "Responsable logistique",
                "phone": "+33612345678",
                "email": "jean.dupont@grossiste-paris-nord.fr",
                "is_primary": True,
                "notes": "Contact principal pour les livraisons"
            },
            {
                "partner_id": created_partners[0].id,  # Grossiste Paris Nord
                "first_name": "Marie",
                "last_name": "Martin",
                "position": "Assistante commerciale",
                "phone": "+33623456789",
                "email": "marie.martin@grossiste-paris-nord.fr",
                "is_primary": False,
                "notes": "Contact secondaire"
            },
            {
                "partner_id": created_partners[1].id,  # Fournisseur Gaz Sud
                "first_name": "Pierre",
                "last_name": "Bernard",
                "position": "Directeur commercial",
                "phone": "+33634567890",
                "email": "pierre.bernard@fournisseur-gaz-sud.fr",
                "is_primary": True,
                "notes": "Contact principal"
            },
            {
                "partner_id": created_partners[2].id,  # Transport Express
                "first_name": "Sophie",
                "last_name": "Leroy",
                "position": "Responsable transport",
                "phone": "+33645678901",
                "email": "sophie.leroy@transport-express.fr",
                "is_primary": True,
                "notes": "Gère les expéditions"
            },
            {
                "partner_id": created_partners[2].id,  # Transport Express
                "first_name": "Thomas",
                "last_name": "Moreau",
                "position": "Chauffeur",
                "phone": "+33656789012",
                "email": None,
                "is_primary": False,
                "notes": "Chauffeur principal"
            },
            {
                "partner_id": created_partners[3].id,  # Grossiste Lyon Centre
                "first_name": "Claire",
                "last_name": "Petit",
                "position": "Responsable des ventes",
                "phone": "+33667890123",
                "email": "claire.petit@grossiste-lyon.fr",
                "is_primary": True,
                "notes": "Contact principal"
            },
            {
                "partner_id": created_partners[4].id,  # Services Logistiques Pro
                "first_name": "Antoine",
                "last_name": "Robert",
                "position": "Gestionnaire",
                "phone": "+33678901234",
                "email": "antoine.robert@services-logistiques.fr",
                "is_primary": True,
                "notes": "Gestion des services"
            }
        ]
        
        for contact_data in contacts_data:
            # Check if contact already exists (by name and partner)
            existing = db.query(Contact).filter(
                Contact.partner_id == contact_data["partner_id"],
                Contact.first_name == contact_data["first_name"],
                Contact.last_name == contact_data["last_name"]
            ).first()
            
            if existing:
                print(f"Contact '{contact_data['first_name']} {contact_data['last_name']}' existe déjà pour ce partenaire, ignoré.")
            else:
                contact = Contact(**contact_data)
                db.add(contact)
                print(f"✓ Contact créé: {contact.first_name} {contact.last_name} ({contact.position})")
        
        db.commit()
        print("\n✓ Tous les partenaires et contacts de test ont été créés avec succès!")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Erreur lors de la création des données de test: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Création des partenaires et contacts de test...\n")
    create_test_partners_and_contacts()

