# Aylaz API Documentation

API REST pour l'application mobile Aylaz (plateforme immobilière).

**Base URL:** `http://localhost:8000/api/v1/`

---

## 🔐 Authentification

### Token Authentication

Pour accéder aux endpoints protégés, ajoute le token dans le header:

```
Authorization: Token YOUR_TOKEN_HERE
```

### Get Auth Token

**POST** `/api/auth/token/`

Envoie tes credentials pour obtenir un token:

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "vendeur1",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

---

## 📝 Endpoints

### Authentification

#### Register
**POST** `/api/v1/users/register/`

Créer un nouveau compte:

```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**
```json
{
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

#### Logout
**POST** `/api/v1/users/logout/` (Authentifié)

---

### Utilisateurs

#### Get Current User
**GET** `/api/v1/users/me/` (Authentifié)

Récupérer les infos du user actuel:

```bash
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "id": 1,
  "username": "vendeur1",
  "email": "vendeur1@example.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "profile": {
    "phone_number": "+212612345678",
    "bio": "Agent immobilier professionnel",
    "avatar": "http://localhost:8000/media/avatars/2026/03/avatar.jpg"
  },
  "date_joined": "2026-03-14T10:00:00Z"
}
```

#### Update Current User
**PUT** `/api/v1/users/me/` (Authentifié)

Modifier ton profil:

```json
{
  "email": "newemail@example.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "profile": {
    "phone_number": "+212612345678",
    "bio": "Agent immobilier à Casablanca"
  }
}
```

---

### Annonces (Listings)

#### List Listings
**GET** `/api/v1/listings/`

Récupérer la liste des annonces publiées:

```bash
curl -X GET http://localhost:8000/api/v1/listings/ \
  -H "Content-Type: application/json"
```

**Query Parameters:**
- `city` - Filtrer par ville
- `district` - Filtrer par quartier
- `property_type` - Type de bien (apartment, house, villa, land, office)
- `listing_type` - Vente ou location (sale, rent)
- `search` - Recherche texte (titre, description, ville)
- `ordering` - Tri (-created_at, price, views_count)
- `page` - Numéro de page (pagination)

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/listings/?city=Casablanca&listing_type=sale&ordering=-price"
```

**Response:**
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/listings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Bel appartement 3 chambres",
      "price": 850000,
      "city": "Casablanca",
      "district": "Anfa",
      "property_type": "apartment",
      "listing_type": "sale",
      "surface_area": 120,
      "bedrooms": 3,
      "bathrooms": 2,
      "image": "http://localhost:8000/media/listings/2026/03/image.jpg",
      "views_count": 42,
      "created_at": "2026-03-14T10:00:00Z"
    }
  ]
}
```

#### Get Listing Detail
**GET** `/api/v1/listings/{id}/`

Récupérer les détails complets d'une annonce:

```bash
curl -X GET http://localhost:8000/api/v1/listings/1/
```

**Response:**
```json
{
  "id": 1,
  "title": "Bel appartement 3 chambres avec terrasse",
  "property_type": "apartment",
  "listing_type": "sale",
  "city": "Casablanca",
  "district": "Anfa",
  "price": 850000,
  "surface_area": 120,
  "bedrooms": 3,
  "bathrooms": 2,
  "kitchen_equipped": true,
  "swimming_pool": false,
  "garden": false,
  "garage": true,
  "parking": true,
  "terrace": true,
  "balcony": true,
  "air_conditioning": true,
  "furnished": false,
  "security": true,
  "description": "Superbe appartement neuf...",
  "image": "http://localhost:8000/media/listings/2026/03/image.jpg",
  "owner_email": "vendor@example.com",
  "owner_phone": "+212612345678",
  "owner_whatsapp": "+212612345678",
  "owner_username": "vendeur1",
  "owner_name": "Jean Dupont",
  "status": "published",
  "is_featured": false,
  "views_count": 42,
  "created_at": "2026-03-14T10:00:00Z",
  "updated_at": "2026-03-15T14:30:00Z",
  "images": [
    {
      "id": 1,
      "image": "http://localhost:8000/media/listings/2026/03/photo1.jpg",
      "alt_text": "Vue du salon",
      "order": 0
    },
    {
      "id": 2,
      "image": "http://localhost:8000/media/listings/2026/03/photo2.jpg",
      "alt_text": "Vue de la terrasse",
      "order": 1
    }
  ]
}
```

#### Create Listing
**POST** `/api/v1/listings/` (Authentifié)

Créer une nouvelle annonce:

```bash
curl -X POST http://localhost:8000/api/v1/listings/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Appartement 2 chambres",
    "property_type": "apartment",
    "listing_type": "rent",
    "city": "Marrakech",
    "district": "Medina",
    "price": 5000,
    "surface_area": 85,
    "bedrooms": 2,
    "bathrooms": 1,
    "kitchen_equipped": true,
    "swimming_pool": false,
    "description": "Bel appartement...",
    "owner_email": "your@email.com",
    "owner_phone": "+212612345678"
  }'
```

#### Update Listing
**PUT** `/api/v1/listings/{id}/` (Authentifié, Owner only)

Modifier une annonce:

```bash
curl -X PUT http://localhost:8000/api/v1/listings/1/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 900000,
    "description": "Nouvelle description..."
  }'
```

#### Delete Listing
**DELETE** `/api/v1/listings/{id}/` (Authentifié, Owner only)

Supprimer une annonce:

```bash
curl -X DELETE http://localhost:8000/api/v1/listings/1/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

### Favoris

#### Get Favorites
**GET** `/api/v1/favorites/` (Authentifié)

Récupérer tes favoris:

```bash
curl -X GET http://localhost:8000/api/v1/favorites/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

#### Toggle Favorite
**POST** `/api/v1/listings/{id}/toggle_favorite/` (Authentifié)

Ajouter/retirer des favoris:

```bash
curl -X POST http://localhost:8000/api/v1/listings/1/toggle_favorite/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "status": "added to favorites"
}
```

#### Delete Favorite
**DELETE** `/api/v1/favorites/{id}/` (Authentifié)

---

### Contacts

#### Get Contacts
**GET** `/api/v1/contacts/` (Authentifié)

Récupérer tes demandes de contact (envoyées et reçues):

```bash
curl -X GET http://localhost:8000/api/v1/contacts/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

#### Send Contact Message
**POST** `/api/v1/contacts/` (Authentifié)

Envoyer un message de contact:

```bash
curl -X POST http://localhost:8000/api/v1/contacts/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "listing": 1,
    "email": "buyer@example.com",
    "phone": "+212612345678",
    "message": "Je suis intéressé par cette annonce..."
  }'
```

#### Get Listing Contacts
**GET** `/api/v1/listings/{id}/contacts/` (Authentifié, Owner only)

Récupérer tous les contacts reçus pour une annonce:

```bash
curl -X GET http://localhost:8000/api/v1/listings/1/contacts/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

## 🧪 Test Quick Start

### 1. Register
```bash
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'
```

### 2. Get Token
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### 3. List Listings
```bash
curl -X GET http://localhost:8000/api/v1/listings/?city=Casablanca
```

### 4. Get User Info
```bash
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## 📱 Mobile Integration Examples

### React Native / JavaScript

```javascript
const API_URL = 'http://localhost:8000/api/v1';
let TOKEN = null;

// Register
async function register(username, email, password) {
  const response = await fetch(`${API_URL}/users/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username,
      email,
      password,
      password_confirm: password
    })
  });
  const data = await response.json();
  TOKEN = data.token;
  return data;
}

// Get listings
async function getListings(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(
    `${API_URL}/listings/?${params}`,
    { headers: { 'Authorization': `Token ${TOKEN}` } }
  );
  return response.json();
}

// Create listing
async function createListing(listingData) {
  const response = await fetch(`${API_URL}/listings/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Token ${TOKEN}`
    },
    body: JSON.stringify(listingData)
  });
  return response.json();
}
```

---

## 🔧 Déploiement

Pour adapter l'API en production:

1. **Update CORS origins** dans `.env`:
   ```
   CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   ```

2. **Update API_URL** dans l'app mobile:
   ```javascript
   const API_URL = 'https://api.yourdomain.com/api/v1';
   ```

3. **SSL/HTTPS** obligatoire en production

4. **Rate limiting** activé (100/hour anonymous, 1000/hour authenticated)

---

## 📚 Ressources

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Postman Collection](./postman_collection.json) - À télécharger
- [Mobile Architecture Guide](./MOBILE_ARCHITECTURE.md)

