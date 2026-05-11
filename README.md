# 🚚 Intelligent Logistics & Routing Assistant

**Système Multi-Agents avec RAG & Orchestration LangChain**

Ce projet implémente un Système Multi-Agents (SMA) avancé avec la technologie RAG (Retrieval-Augmented Generation) pour résoudre un cas d'usage logistique concret. Il a été développé dans le cadre du module **IA Distribuée & Systèmes Multi-Agents** (Année Universitaire 2025–2026).

## 📋 Cas d'Usage

### **Intelligent Logistics & Routing Assistant**

Un système conçu pour aider une entreprise de logistique à **planifier des itinéraires de transport** en respectant les contraintes des camions (capacités, localisation, maintenance) et les réglementations routières (péages, horaires d'accès urbain).

**Justification du choix :**
- La logistique implique de multiples paramètres décisionnels (coût, temps, disponibilité, compliance réglementaire).
- Les règles métiers sont documentées de manière privée (interne à l'entreprise).
- Cela justifie parfaitement l'utilisation du **RAG** (pour contextualiser avec des données privées) et de **plusieurs agents spécialisés** (planification, vérification réglementaire, rédaction).
- La **collaboration inter-agents** apporte une vraie valeur ajoutée : une analyse partagée et validée des contraintes plutôt qu'une seule réponse monolithique.

---

## 🏗️ Architecture du Système

L'architecture suit le modèle séquentiel avec 4 agents spécialisés orchestrés par **LangGraph** :

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Request                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   Agent Recherche (Recherche)  │
        │   - Extraie les faits pertinents │
        │   - Utilise l'outil RAG        │
        └────────────────┬────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   Agent Analyse (Analyste)     │
        │   - Propose un camion adéquat  │
        │   - Formule un plan initial    │
        └────────────────┬────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   Agent Validation (Vérif.)    │
        │   - Vérifie la conformité      │
        │   - Soulève les anomalies      │
        │   - Propose des alternatives   │
        └────────────────┬────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   Agent Rédaction (Rédacteur)  │
        │   - Compile la réponse finale  │
        │   - Format professionnel       │
        └────────────────┬────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Final Logistics Plan                          │
└─────────────────────────────────────────────────────────────────┘
```

### **Composants Clés**

#### 1. **Agent Recherche** (`src/agents.py` → `recherche_node`)
- **Rôle** : Extraire les informations pertinentes de la base de connaissances privée.
- **Outil** : `logistics_knowledge_base` (RAG via LlamaIndex).
- **Entrée** : Requête utilisateur.
- **Sortie** : Contexte structuré des faits pertinents.

#### 2. **Agent Analyse** (`src/agents.py` → `analyse_node`)
- **Rôle** : Analyser les contraintes et proposer une solution initiale.
- **Outils** : Aucun outil direct (utilise le contexte RAG de l'Agent Recherche).
- **Logique** : Matching entre la demande et les ressources disponibles.
- **Sortie** : Plan d'action proposé (truck, route, horaires).

#### 3. **Agent Validation** (`src/agents.py` → `validation_node`)
- **Rôle** : Vérifier la conformité du plan par rapport aux règles métiers.
- **Outils** : Aucun outil direct.
- **Logique** : Vérification des contraintes (capacité, maintenance, restrictions horaires, péages).
- **Sortie** : Rapport de validation avec approbation ou alternatives.

#### 4. **Agent Rédaction** (`src/agents.py` → `redaction_node`)
- **Rôle** : Produire une réponse finale structurée et professionnelle.
- **Outils** : Aucun outil direct.
- **Logique** : Compilation et formatage des résultats précédents.
- **Sortie** : Réponse client finale.

---

## 🔍 Pipeline RAG (LlamaIndex + ChromaDB)

### **Étapes du Pipeline**

1. **Ingestion**
   - **Source** : Fichiers texte dans `data/`
   - **Fichiers** :
     - `fleet_rules.txt` : Spécifications des camions (capacités, localisations, maintenance)
     - `city_regulations.txt` : Restrictions urbaines (horaires, classes de véhicules)
     - `maintenance_logs.txt` : Historique de maintenance des camions
   - **Méthode** : `SimpleDirectoryReader` de LlamaIndex

2. **Chunking**
   - Les documents sont découpés en chunks (sentences par défaut dans LlamaIndex).
   - Permet une meilleure granularité du retrieval.

3. **Embedding**
   - **Modèle** : `BAAI/bge-small-en-v1.5` (HuggingFaceEmbedding)
   - **Avantages** : Vectorisation locale (pas d'API), performant, gratuit.
   - **Dimension** : 384 dimensions.

4. **Indexation & Stockage Vectoriel**
   - **Vector Store** : ChromaDB (persistant dans `./chroma_db/`)
   - **Avantage** : Stockage local, persistance, pas de dépendance serveur.

5. **Retrieval**
   - **Query Engine** : LlamaIndex `as_query_engine(similarity_top_k=3)`
   - **Extraction** : Top 3 résultats les plus similaires au query.
   - **Augmentation** : Les passages récupérés sont injectés dans les prompts des agents.

---

## 💻 Technologies Utilisées

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **LLM** | Groq API (`llama-3.1-8b-instant`) | Inférence très rapide (~300 req/min) |
| **Agents & Orchestration** | LangChain + LangGraph | Framework multi-agents, gestion du flux |
| **RAG** | LlamaIndex | Ingestion, indexation, retrieval |
| **Embeddings** | HuggingFace (`BAAI/bge-small-en-v1.5`) | Vectorisation locale |
| **Vector Store** | ChromaDB | Stockage persistant des embeddings |
| **Langage** | Python 3.9+ | Implémentation |

---

## 📦 Installation & Configuration

### **Prérequis**
- Python 3.9 ou supérieur
- Une clé API Groq (gratuite, https://console.groq.com)
- ~500 MB d'espace disque (pour ChromaDB + modèles HuggingFace)

### **Étapes d'Installation**

1. **Clonez le dépôt** (ou téléchargez-le)
   ```bash
   git clone <repo_url>
   cd Logistics_Project
   ```

2. **Créez un environnement virtuel** (recommandé)
   ```bash
   python -m venv venv
   # Sur Windows
   venv\Scripts\activate
   # Sur macOS/Linux
   source venv/bin/activate
   ```

3. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurez les variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditez .env et insérez votre GROQ_API_KEY
   ```
   Exemple de `.env` :
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxx...
   ```

5. **Testez la connexion** (optionnel mais recommandé)
   ```bash
   python test_connection.py
   ```
   Cela vérifiera que tous les composants sont correctement configurés.

---

## 🚀 Exécution

### **Lancer le Système Principal**
```bash
python main.py
```

Vous verrez une invite interactive :
```
==================================================
🚚 Intelligent Logistics & Routing Assistant 🚚
==================================================
Initializing the Multi-Agent System...
✅ System Online. Agents are ready.
Type 'exit' or 'quit' to stop.

Client Request > 
```

### **Exemple de Requête**
```
Client Request > I need to transport 18 tons of goods from Rabat to Casablanca city center at 08:30 AM. What truck should I use?
```

Le système exécutera séquentiellement les 4 agents et produira une réponse finale structurée.

### **Lancer un Test RAG Isolé**
```bash
python rag_test.py
```
Cela teste uniquement le pipeline RAG sans les agents.

---

## 🧪 Test de Connexion & Diagnostic

Utilisez le script de test pour diagnostiquer les problèmes :
```bash
python test_connection.py
```

**Résultat attendu :**
```
[1/5] Testing environment configuration...
✅ Environment variables loaded successfully.

[2/5] Testing Groq API connection...
✅ Groq API connection successful. Response: System ready...

[3/5] Testing HuggingFace embeddings...
✅ HuggingFace embeddings loaded successfully. Embedding dimension: 384

[4/5] Testing RAG pipeline...
✅ RAG pipeline initialized successfully.

[5/5] Testing orchestrator...
✅ Orchestrator built successfully.

Results: 5/5 tests passed
✅ All tests passed! You're ready to use the system.
```

---

## 📂 Structure du Projet

```
Logistics_Project/
├── main.py                    # Point d'entrée principal (interactive CLI)
├── rag_test.py               # Test isolé du pipeline RAG
├── test_connection.py         # Diagnostic de connexion et dépendances
├── requirements.txt           # Dépendances Python
├── .env.example              # Template de configuration
├── README.md                 # Ce fichier
├── src/
│   ├── agents.py            # Définition des prompts et logique des agents
│   ├── orchestrator.py       # Graphe LangGraph (orchestration des agents)
│   └── rag_pipeline.py       # Pipeline RAG (LlamaIndex + ChromaDB)
├── data/
│   ├── fleet_rules.txt       # Données privées : spécifications des camions
│   ├── city_regulations.txt  # Données privées : restrictions urbaines
│   └── maintenance_logs.txt  # Données privées : logs de maintenance
└── chroma_db/                # Vector store persistant (ChromaDB)
    └── chroma.sqlite3        # Base de données ChromaDB
```

---

## 🎯 Fonctionnalités Clés

### **1. Multi-Agents Distribué**
- 4 agents spécialisés avec des rôles et responsabilités distincts.
- Communication via état partagé (LangGraph StateGraph).
- Chaque agent peut être testé indépendamment.

### **2. RAG Avancé**
- Ingestion automatique de documents textes.
- Vectorisation locale (pas d'API externe).
- Retrieval sémantique pour la pertinence.
- Persistance des embeddings.

### **3. Orchestration Intelligente**
- Flux séquentiel bien défini (Recherche → Analyse → Validation → Rédaction).
- État global partagé entre agents.
- Gestion des erreurs et fallbacks.

### **4. Conformité Réglementaire**
- Vérification automatique des contraintes métiers.
- Suggestions d'alternatives en cas de violation.
- Traçabilité complète des décisions.

---

## 📊 Exemples de Résultats

### **Scénario 1 : Transport conforme**
```
User Request: I need to transport 15 tons from Rabat to Casablanca at 14:00.

[Agent Recherche] Found: Truck Beta (20T, Rabat), Highway A1 (toll 50 MAD)
[Agent Analyse] Truck Beta selected, departure 14:00
[Agent Validation] ✅ APPROVED - No city center restriction at 14:00
[Agent Rédaction] 
  ---
  Recommended Truck: Beta (20 tons)
  ...
```

### **Scénario 2 : Violation détectée & alternative**
```
User Request: I need to transport 18 tons from Rabat to Casablanca at 08:30.

[Agent Recherche] Found: Truck Alpha (10T), Truck Beta (20T), 08:30 restriction in Casablanca
[Agent Analyse] Truck Beta selected, departure 08:30
[Agent Validation] ⚠️ VIOLATION - Casablanca city center restricted 07:00-10:00
               Alternative: Postpone to 10:30 or take ring road
[Agent Rédaction]
  ---
  ❌ Original Plan: Not feasible (city center restrictions)
  ✅ Alternative: Departure 10:30 via ring road
  ...
```

---

## 🔒 Sécurité & Bonnes Pratiques

✅ **API Keys :** Stockées dans `.env` (non versionné avec Git).
✅ **Données privées :** Restent locales, jamais envoyées à des tiers (sauf via LLM).
✅ **Authentification :** Groq API key requise (pas de données sensibles en clair).
✅ **Logging :** Les agents affichent leurs actions pour la traçabilité.

---

## 📝 Documentation Technique Détaillée

### **RAG Pipeline**
Voir [Étapes du Pipeline RAG](#-pipeline-rag-llamaindex--chromadb) ci-dessus pour les détails sur :
- Ingestion & chunking
- Modèles d'embeddings
- Stratégie de retrieval

### **Agents & Prompts**
Tous les prompts des agents sont définis dans `src/agents.py` :
- `RECHERCHE_SYSTEM_PROMPT`
- `ANALYSE_SYSTEM_PROMPT`
- `VALIDATION_SYSTEM_PROMPT`
- `REDACTION_SYSTEM_PROMPT`

Vous pouvez ajuster ces prompts pour affiner le comportement des agents.

### **Orchestration & État**
L'état global est défini dans `src/orchestrator.py` :
```python
class LogisticsState(TypedDict):
    user_request: str           # Requête utilisateur initiale
    rag_context: str            # Contexte récupéré par RAG
    analysis_plan: str          # Plan proposé par l'analyste
    validation_report: str      # Rapport de validation
    final_response: str         # Réponse finale
```

---

## 🚨 Dépannage

### **Problème : GROQ_API_KEY non trouvée**
```
❌ GROQ_API_KEY not found in environment variables.
```
**Solution :** 
1. Créez un fichier `.env` dans le répertoire racine.
2. Ajoutez votre clé : `GROQ_API_KEY=gsk_...`
3. Relancez le script.

### **Problème : Erreur de connexion à Groq**
```
❌ Groq API connection failed: ...
```
**Solution :**
1. Vérifiez votre clé API sur https://console.groq.com.
2. Vérifiez votre connexion Internet.
3. Groq peut être temporairement indisponible (vérifiez le statut).

### **Problème : Modèles HuggingFace non trouvés**
```
❌ HuggingFace embeddings failed: ...
```
**Solution :**
1. HuggingFace téléchargera le modèle la première fois (~50 MB).
2. Vérifiez votre connexion Internet.
3. L'espace disque est suffisant (~500 MB).

### **Problème : ChromaDB non fonctionnel**
```
❌ RAG pipeline initialization failed: ...
```
**Solution :**
1. Supprimez le dossier `chroma_db/` pour réinitialiser la base.
2. Relancez le script (il recréera la base).

---

## 🎓 Améliorations Possibles

- ✨ Ajouter des agents supplémentaires (Cost Optimization, Environmental Impact)
- 📈 Impl ementer un parallélisation d'agents (au lieu de séquentiel)
- 🔄 Intégrer une boucle de feedback utilisateur pour l'amélioration continue
- 📱 Créer une API REST (FastAPI) pour l'intégration système
- 🎨 Développer une interface Web (Streamlit ou React)
- 💾 Supporter d'autres formats de données (JSON, CSV, PDF)

---

## 📞 Support & Questions

Pour toute question ou problème technique, veuillez consulter la section [Dépannage](#-dépannage) ou ouvrir une issue sur GitHub.

---

## 📄 Licence

Ce projet est fourni à titre éducatif dans le cadre du module "IA Distribuée & Systèmes Multi-Agents" (2025–2026).

---

**Bon développement ! 🚀**
