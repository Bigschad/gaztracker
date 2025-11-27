#!/usr/bin/env python3
"""
Script pour créer des données de démonstration via l'API GazTracker
"""

import requests
from random import choice, randint
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
TOKEN = None  # Will be set after login


def login():
    """Se connecter et récupérer le token"""
    global TOKEN
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": "admin@gaztracker.com",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        TOKEN = response.json()["access_token"]
        print("✅ Connexion réussie")
        return True
    else:
        print(f"❌ Erreur de connexion: {response.text}")
        return False


def get_headers():
    """Retourner les headers avec le token"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }


def get_or_create_groupes():
    """Récupérer ou créer des groupes"""
    print("\n📦 Gestion des Groupes...")
    
    # D'abord récupérer les groupes existants
    response = requests.get(
        f"{BASE_URL}/api/v1/groupes",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        groupes = response.json()
        if len(groupes) > 0:
            print(f"  ℹ️  {len(groupes)} groupes existants récupérés")
            return groupes
    
    # Sinon créer les groupes
    groupes_data = [
        {
            "name": "PETROCI Holding",
            "code": "PETROCI",
            "address": "Rue des Pétroles, Plateau",
            "city": "Abidjan",
            "phone": "+225 27 20 30 40 50",
            "email": "contact@petroci.ci",
            "is_active": True
        },
        {
            "name": "SODIGAZ CI",
            "code": "SODIGAZ",
            "address": "Boulevard Valéry Giscard d'Estaing, Marcory",
            "city": "Abidjan",
            "phone": "+225 27 21 31 41 51",
            "email": "info@sodigaz.ci",
            "is_active": True
        },
        {
            "name": "IVOIRE GAZ",
            "code": "IVOGAZ",
            "address": "Zone Industrielle, Yopougon",
            "city": "Abidjan",
            "phone": "+225 27 22 32 42 52",
            "email": "contact@ivoiregaz.ci",
            "is_active": True
        }
    ]
    
    groupes = []
    for data in groupes_data:
        response = requests.post(
            f"{BASE_URL}/api/v1/groupes",
            json=data,
            headers=get_headers()
        )
        if response.status_code in [200, 201]:
            groupes.append(response.json())
            print(f"  ✓ {data['name']}")
    
    print(f"✅ {len(groupes)} groupes créés")
    return groupes


def create_grands_distributeurs(groupes):
    """Créer des grands distributeurs"""
    print("\n🏢 Création des Grands Distributeurs...")
    
    gd_data = [
        {"name": "Total Energies CI", "code": "TOTAL_CI", "groupe": groupes[0], "city": "Abidjan"},
        {"name": "Shell CI", "code": "SHELL_CI", "groupe": groupes[0], "city": "Abidjan"},
        {"name": "Oryx Energies", "code": "ORYX", "groupe": groupes[0], "city": "Abidjan"},
        {"name": "Vivo Energy CI", "code": "VIVO", "groupe": groupes[1], "city": "Abidjan"},
        {"name": "Puma Energy", "code": "PUMA", "groupe": groupes[1], "city": "San Pedro"},
        {"name": "Afriquia Gaz CI", "code": "AFRIQUIA", "groupe": groupes[2], "city": "Yamoussoukro"},
        {"name": "Butagaz CI", "code": "BUTAGAZ", "groupe": groupes[2], "city": "Bouaké"},
    ]
    
    gds = []
    for data in gd_data:
        payload = {
            "name": data["name"],
            "code": data["code"],
            "groupe_id": data["groupe"]["id"],
            "address": f"{randint(1, 999)} Avenue {choice(['de la République', 'du Commerce', 'Principale'])}",
            "city": data["city"],
            "phone": f"+225 27 {randint(20, 29)} {randint(10, 99)} {randint(10, 99)} {randint(10, 99)}",
            "email": f"contact@{data['code'].lower()}.ci",
            "is_active": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/grand-distributeurs",
            json=payload,
            headers=get_headers()
        )
        if response.status_code in [200, 201]:
            gds.append(response.json())
            print(f"  ✓ {data['name']}")
        else:
            print(f"  ✗ Erreur pour {data['name']}: {response.text}")
    
    print(f"✅ {len(gds)} grands distributeurs créés")
    return gds


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🚀 GÉNÉRATION DE DONNÉES DE DÉMONSTRATION GAZTRACKER (via API)")
    print("="*60)
    
    # Se connecter
    if not login():
        return
    
    # Créer les données
    groupes = get_or_create_groupes()
    
    if len(groupes) == 0:
        print("\n❌ Impossible de récupérer ou créer des groupes")
        return
    
    gds = create_grands_distributeurs(groupes)
    
    print("\n" + "="*60)
    print("✅ GÉNÉRATION TERMINÉE !")
    print("="*60)
    print(f"\n📊 Résumé:")
    print(f"   • Groupes:              {len(groupes)}")
    print(f"   • Grands Distributeurs: {len(gds)}")
    print("\n🎉 Testez l'application : http://localhost:3000\n")


if __name__ == "__main__":
    main()

