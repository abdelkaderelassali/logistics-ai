# Documentation: Cahier des Charges - IA Distribuée & Systèmes Multi-Agents

Ce projet est la fusion de l'interface **Smart-Logistics-Route-Optimizer** (React + Neo4j) et du **Système Multi-Agents** (Python + LangGraph) qui répond strictement aux exigences du cahier des charges.

## 1. Stack Technologique Obligatoire Respectée
- **LangChain / LangGraph** : Utilisé pour la création, la définition et l'orchestration des 4 agents (Recherche, Analyse, Validation, Rédaction). Le graphe d'états gère le flux de travail séquentiel.
- **LlamaIndex** : Implémenté dans `python_backend/app/rag_pipeline.py`. Il indexe les documents privés situés dans `python_backend/data` (PDFs, textes) et gère le retrieval.
- **LLM Provider** : **Groq** avec le modèle `llama-3.1-8b-instant`, extrêmement rapide et adapté aux configurations matérielles légères (i5).
- **Python** : Backend AI complet (FastAPI).
- **Vector Store** : **ChromaDB** est utilisé pour le stockage vectoriel en local dans le répertoire `chroma_db/`.

## 2. Composants Requis
### RAG via LlamaIndex
Le pipeline RAG effectue :
- L'ingestion des règles de transport, des capacités de flotte et des maintenances depuis `data/`.
- L'indexation avec les embeddings HuggingFace (`BAAI/bge-small-en-v1.5`) et ChromaDB.
- Le retrieval sémantique pour fournir le contexte à l'agent de recherche.

### Agents LangChain (LangGraph)
Le système s'articule autour de 4 agents spécialisés :
1. **Agent Recherche** : Formule la requête RAG pour extraire les contraintes depuis ChromaDB.
2. **Agent Analyse** : Élabore un plan logistique basé sur la demande et le contexte.
3. **Agent Validation** : Vérifie la faisabilité (poids, horaires, péages) et signale les anomalies.
4. **Agent Rédaction** : Synthétise le tout de manière professionnelle pour l'utilisateur final.

### Orchestration
L'orchestration est réalisée avec `langgraph` dans `python_backend/app/orchestrator.py` qui définit clairement le flux conditionnel et séquentiel entre les agents et maintient un état global `LogisticsState`.

## 3. L'Interface (Frontend)
Le frontend React a été mis à jour pour inclure un panneau **"AI Assistant"**. L'utilisateur peut y saisir une requête en langage naturel (ex: "Je veux transporter 15 tonnes de Rabat à Casablanca à 14h00") et le système affiche en temps réel les déductions et analyses des 4 agents IA.

## Comment Démarrer
Lancez le fichier `start.bat` à la racine pour démarrer simultanément :
1. Le backend de routing (Node.js)
2. Le backend AI Multi-Agents (Python FastAPI)
3. L'interface React


## 4. Docker Deployment
Vous pouvez lancer le projet complet avec une seule commande:
``bash
docker-compose up -d --build
``
Cela lancera l'interface React sur le port 3000 et le backend FastAPI sur le port 8000.
