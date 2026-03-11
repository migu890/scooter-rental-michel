# Scooter Rental Michel

## Projektbeschreibung

Scooter Rental Michel ist eine Webanwendung zum Verwalten und Ausleihen von E-Scootern.  
Die Applikation wurde mit **Python**, **Flask** und einer **relationalen Datenbank** umgesetzt.

Die Anwendung unterstützt zwei Rollen:

- **Provider**: verwaltet E-Scooter
- **Rider**: kann verfügbare Scooter ausleihen und zurückgeben

Zusätzlich stellt die Anwendung eine REST-API zur Verfügung, über die ausgewählte Daten auch ohne Browser abgefragt werden können.

---

## Verwendete Technologien

- **Programmiersprache:** Python 3.9+
- **Web-Framework:** Flask
- **Datenbank:** MariaDB / MySQL
- **ORM:** SQLAlchemy
- **Migrationen:** Flask-Migrate
- **Authentifizierung:** Flask-Login
- **Formulare:** Flask-WTF
- **Frontend:** HTML + Bootstrap 5
- **Deployment:** Jelastic Cloud
- **WSGI / Webserver:** abhängig vom Deployment-Setup dokumentiert

---

## Funktionsumfang

### Benutzerverwaltung
- Registrierung mit eindeutigem Benutzernamen und eindeutiger E-Mail
- Login / Logout
- Rollenbasierter Zugriff (Provider / Rider)

### Provider-Funktionen
- Scooter hinzufügen
- Scooter bearbeiten
- Scooter löschen
- Status und Standort verwalten

### Rider-Funktionen
- Verfügbare Scooter im Dashboard anzeigen
- Scooter über Dropdown auswählen
- Miete starten
- Miete beenden
- gefahrene Kilometer erfassen
- Preisberechnung auf Basis von Grundpreis + Minutenpreis

### REST-API
- API-Login mit Benutzername/E-Mail und Passwort
- Token-basierte Authentifizierung ohne Browser
- verfügbare Scooter abrufen
- eigene Mieten abrufen

---

## Projektstruktur

```text
scooter_rental/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   │
│   ├── auth/
│   │   ├── forms.py
│   │   └── routes.py
│   │
│   ├── web/
│   │   └── routes.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── services/
│   │   ├── pricing.py
│   │   └── rental_service.py
│   │
│   └── templates/
│       ├── base.html
│       ├── auth_login.html
│       ├── auth_register.html
│       ├── dashboard.html
│       ├── scooters.html
│       └── rental.html
│
├── migrations/
├── tests/
├── wsgi.py
├── requirements.txt
└── README.md