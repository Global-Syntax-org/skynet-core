"""
Memory Skill Implementation
Provides enhanced memory management with semantic search, embeddings, and knowledge graphs.
"""

import asyncio
import json
import logging
import sqlite3
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path
import aiosqlite
import pickle
import gzip

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Individual memory entry"""
    id: str
    content: str
    memory_type: str
    importance: float
    timestamp: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    tags: Optional[List[str]] = None

@dataclass
class KnowledgeNode:
    """Knowledge graph node"""
    id: str
    content: str
    node_type: str
    properties: Dict[str, Any]
    connections: List[str]
    strength: float

@dataclass
class SearchResult:
    """Memory search result"""
    entry: MemoryEntry
    similarity_score: float
    rank: int

class MemorySkill:
    """Advanced memory management with semantic search and knowledge graphs"""
    
    def __init__(self, db_path: str = "memory.db", 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize memory skill with database and embedding model"""
        self.db_path = Path(db_path)
        self.embedding_model_name = embedding_model
        self.embedding_model = None
        self.faiss_index = None
        self.embedding_dim = 384  # Default for MiniLM
        self.memory_cache = {}
        self.knowledge_graph = {}
        
        # Memory configuration
        self.max_memory_size = 10000  # Maximum number of entries
        self.importance_threshold = 0.3  # Minimum importance to keep
        self.compression_interval = 3600  # Compress every hour
        self.last_compression = time.time()
        
    async def initialize(self):
        """Initialize database and embedding model"""
        try:
            # Initialize embedding model
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            
            # Initialize FAISS index
            self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
            
            # Initialize database
            await self._init_database()
            
            # Load existing memories
            await self._load_memories()
            
            logger.info("Memory skill initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory skill: {e}")
            raise
    
    async def _init_database(self):
        """Initialize SQLite database for persistent storage"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    embedding BLOB,
                    tags TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_graph (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    properties TEXT NOT NULL,
                    connections TEXT NOT NULL,
                    strength REAL NOT NULL
                )
            """)
            
            await db.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            
            await db.commit()
    
    async def _load_memories(self):
        """Load existing memories from database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT * FROM memories ORDER BY importance DESC") as cursor:
                    memories = await cursor.fetchall()
                
                embeddings = []
                for row in memories:
                    memory_id, content, memory_type, importance, timestamp, metadata_str, embedding_blob, tags_str = row
                    
                    # Parse metadata and tags
                    metadata = json.loads(metadata_str) if metadata_str else {}
                    tags = json.loads(tags_str) if tags_str else []
                    
                    # Deserialize embedding
                    embedding = None
                    if embedding_blob:
                        embedding = pickle.loads(embedding_blob)
                        embeddings.append(embedding)
                    
                    # Create memory entry
                    memory_entry = MemoryEntry(
                        id=memory_id,
                        content=content,
                        memory_type=memory_type,
                        importance=importance,
                        timestamp=timestamp,
                        metadata=metadata,
                        embedding=embedding,
                        tags=tags
                    )
                    
                    self.memory_cache[memory_id] = memory_entry
                
                # Add embeddings to FAISS index
                if embeddings:
                    embeddings_array = np.array(embeddings, dtype=np.float32)
                    # Normalize for cosine similarity
                    faiss.normalize_L2(embeddings_array)
                    self.faiss_index.add(embeddings_array)
                
                # Load knowledge graph
                await self._load_knowledge_graph()
                
                logger.info(f"Loaded {len(self.memory_cache)} memories from database")
                
        except Exception as e:
            logger.error(f"Failed to load memories: {e}")
    
    async def _load_knowledge_graph(self):
        """Load knowledge graph from database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT * FROM knowledge_graph") as cursor:
                    nodes = await cursor.fetchall()
                
                for row in nodes:
                    node_id, content, node_type, properties_str, connections_str, strength = row
                    
                    properties = json.loads(properties_str) if properties_str else {}
                    connections = json.loads(connections_str) if connections_str else []
                    
                    node = KnowledgeNode(
                        id=node_id,
                        content=content,
                        node_type=node_type,
                        properties=properties,
                        connections=connections,
                        strength=strength
                    )
                    
                    self.knowledge_graph[node_id] = node
                
                logger.info(f"Loaded {len(self.knowledge_graph)} knowledge graph nodes")
                
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {e}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")
        
        embedding = self.embedding_model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def _calculate_importance(self, content: str, memory_type: str, 
                            metadata: Dict[str, Any]) -> float:
        """Calculate memory importance score"""
        importance = 0.5  # Base importance
        
        # Type-based importance
        type_weights = {
            "fact": 0.8,
            "conversation": 0.6,
            "task": 0.9,
            "knowledge": 0.9,
            "experience": 0.7
        }
        importance *= type_weights.get(memory_type, 0.5)
        
        # Content length factor (longer content might be more important)
        length_factor = min(len(content) / 500, 2.0)  # Cap at 2x
        importance *= (0.5 + length_factor * 0.5)
        
        # Metadata-based adjustments
        if metadata.get("priority") == "high":
            importance *= 1.5
        elif metadata.get("priority") == "low":
            importance *= 0.7
        
        if metadata.get("source") == "user":
            importance *= 1.2
        
        # Frequency factor (if mentioned before)
        frequency = metadata.get("frequency", 1)
        importance *= min(1 + (frequency - 1) * 0.1, 2.0)
        
        return min(importance, 1.0)  # Cap at 1.0
    
    async def store_memory(self, content: str, memory_type: str,
                          metadata: Optional[Dict[str, Any]] = None,
                          tags: Optional[List[str]] = None,
                          importance: Optional[float] = None) -> Dict[str, Any]:
        """Store new memory with semantic embedding"""
        try:
            if not self.embedding_model:
                await self.initialize()
            
            # Generate unique ID
            memory_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()
            
            # Prepare metadata
            metadata = metadata or {}
            metadata.update({
                "created": datetime.now().isoformat(),
                "access_count": 0,
                "last_accessed": datetime.now().isoformat()
            })
            
            # Calculate importance if not provided
            if importance is None:
                importance = self._calculate_importance(content, memory_type, metadata)
            
            # Generate embedding
            embedding = self._generate_embedding(content)
            
            # Create memory entry
            memory_entry = MemoryEntry(
                id=memory_id,
                content=content,
                memory_type=memory_type,
                importance=importance,
                timestamp=datetime.now().isoformat(),
                metadata=metadata,
                embedding=embedding,
                tags=tags or []
            )
            
            # Store in cache
            self.memory_cache[memory_id] = memory_entry
            
            # Add to FAISS index
            embedding_array = np.array([embedding], dtype=np.float32)
            faiss.normalize_L2(embedding_array)
            self.faiss_index.add(embedding_array)
            
            # Store in database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO memories (id, content, memory_type, importance, timestamp, metadata, embedding, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory_id,
                    content,
                    memory_type,
                    importance,
                    memory_entry.timestamp,
                    json.dumps(metadata),
                    pickle.dumps(embedding),
                    json.dumps(tags or [])
                ))
                await db.commit()
            
            # Check if compression needed
            await self._check_compression()
            
            return {
                "success": True,
                "memory_id": memory_id,
                "importance": importance,
                "memory_type": memory_type
            }
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def search_memories(self, query: str, 
                            memory_types: Optional[List[str]] = None,
                            limit: int = 10,
                            min_similarity: float = 0.3,
                            time_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """Search memories using semantic similarity"""
        try:
            if not self.embedding_model:
                await self.initialize()
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            query_array = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_array)
            
            # Search in FAISS index
            similarities, indices = self.faiss_index.search(query_array, min(limit * 2, len(self.memory_cache)))
            
            # Filter and rank results
            results = []
            memory_list = list(self.memory_cache.values())
            
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx >= len(memory_list) or similarity < min_similarity:
                    continue
                
                memory = memory_list[idx]
                
                # Apply filters
                if memory_types and memory.memory_type not in memory_types:
                    continue
                
                if time_range:
                    memory_time = datetime.fromisoformat(memory.timestamp)
                    start_time = datetime.fromisoformat(time_range[0])
                    end_time = datetime.fromisoformat(time_range[1])
                    if not (start_time <= memory_time <= end_time):
                        continue
                
                # Update access metadata
                memory.metadata["access_count"] = memory.metadata.get("access_count", 0) + 1
                memory.metadata["last_accessed"] = datetime.now().isoformat()
                
                result = SearchResult(
                    entry=memory,
                    similarity_score=float(similarity),
                    rank=i + 1
                )
                results.append(result)
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            results = results[:limit]
            
            return {
                "success": True,
                "query": query,
                "results": [asdict(r) for r in results],
                "count": len(results),
                "total_memories": len(self.memory_cache)
            }
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def create_knowledge_graph(self, topic: str, 
                                   memory_ids: Optional[List[str]] = None,
                                   max_nodes: int = 50) -> Dict[str, Any]:
        """Create knowledge graph from memories"""
        try:
            # Get memories for knowledge graph
            if memory_ids:
                memories = [self.memory_cache[mid] for mid in memory_ids if mid in self.memory_cache]
            else:
                # Search for memories related to topic
                search_result = await self.search_memories(topic, limit=max_nodes)
                if not search_result["success"]:
                    return search_result
                
                memories = [SearchResult(**r)["entry"] for r in search_result["results"]]
            
            # Create knowledge nodes
            nodes = {}
            connections = {}
            
            for memory in memories:
                node_id = f"memory_{memory.id}"
                
                # Extract key concepts (simplified - could use NLP)
                concepts = self._extract_concepts(memory.content)
                
                node = KnowledgeNode(
                    id=node_id,
                    content=memory.content,
                    node_type=memory.memory_type,
                    properties={
                        "importance": memory.importance,
                        "timestamp": memory.timestamp,
                        "concepts": concepts,
                        "tags": memory.tags
                    },
                    connections=[],
                    strength=memory.importance
                )
                
                nodes[node_id] = node
                
                # Track concept connections
                for concept in concepts:
                    if concept not in connections:
                        connections[concept] = []
                    connections[concept].append(node_id)
            
            # Create connections between nodes with shared concepts
            for concept, node_ids in connections.items():
                if len(node_ids) > 1:
                    for i, node_id1 in enumerate(node_ids):
                        for node_id2 in node_ids[i+1:]:
                            if node_id2 not in nodes[node_id1].connections:
                                nodes[node_id1].connections.append(node_id2)
                            if node_id1 not in nodes[node_id2].connections:
                                nodes[node_id2].connections.append(node_id1)
            
            # Store in knowledge graph
            graph_id = hashlib.md5(f"{topic}{time.time()}".encode()).hexdigest()
            
            # Save to database
            async with aiosqlite.connect(self.db_path) as db:
                for node in nodes.values():
                    await db.execute("""
                        INSERT OR REPLACE INTO knowledge_graph 
                        (id, content, node_type, properties, connections, strength)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        node.id,
                        node.content,
                        node.node_type,
                        json.dumps(node.properties),
                        json.dumps(node.connections),
                        node.strength
                    ))
                await db.commit()
            
            # Update cache
            self.knowledge_graph.update(nodes)
            
            return {
                "success": True,
                "graph_id": graph_id,
                "topic": topic,
                "nodes": len(nodes),
                "connections": sum(len(n.connections) for n in nodes.values()) // 2,
                "knowledge_graph": {nid: asdict(node) for nid, node in nodes.items()}
            }
            
        except Exception as e:
            logger.error(f"Failed to create knowledge graph: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text (simplified implementation)"""
        # This is a simplified concept extraction
        # In practice, you'd use NLP libraries like spaCy or NLTK
        
        import re
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter common words (basic stop words)
        stop_words = {
            'the', 'and', 'are', 'was', 'for', 'with', 'this', 'that',
            'have', 'has', 'had', 'will', 'can', 'could', 'should', 'would'
        }
        
        concepts = [word for word in words if word not in stop_words]
        
        # Get unique concepts with frequency > 1 or important words
        concept_freq = {}
        for concept in concepts:
            concept_freq[concept] = concept_freq.get(concept, 0) + 1
        
        # Return top concepts
        important_concepts = [
            concept for concept, freq in concept_freq.items() 
            if freq > 1 or len(concept) > 6
        ]
        
        return important_concepts[:10]  # Limit to top 10
    
    async def compress_memories(self, target_size: Optional[int] = None) -> Dict[str, Any]:
        """Compress memory storage by removing low-importance entries"""
        try:
            current_size = len(self.memory_cache)
            target_size = target_size or self.max_memory_size
            
            if current_size <= target_size:
                return {
                    "success": True,
                    "message": "No compression needed",
                    "current_size": current_size,
                    "target_size": target_size
                }
            
            # Sort memories by importance and recency
            memories = list(self.memory_cache.values())
            memories.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
            
            # Keep top memories
            kept_memories = memories[:target_size]
            removed_memories = memories[target_size:]
            
            # Update cache
            self.memory_cache = {m.id: m for m in kept_memories}
            
            # Rebuild FAISS index
            if kept_memories:
                embeddings = [m.embedding for m in kept_memories if m.embedding]
                if embeddings:
                    embeddings_array = np.array(embeddings, dtype=np.float32)
                    faiss.normalize_L2(embeddings_array)
                    
                    # Create new index
                    self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)
                    self.faiss_index.add(embeddings_array)
            
            # Remove from database
            removed_ids = [m.id for m in removed_memories]
            if removed_ids:
                async with aiosqlite.connect(self.db_path) as db:
                    placeholders = ','.join(['?' for _ in removed_ids])
                    await db.execute(f"DELETE FROM memories WHERE id IN ({placeholders})", removed_ids)
                    await db.commit()
            
            self.last_compression = time.time()
            
            return {
                "success": True,
                "original_size": current_size,
                "new_size": len(kept_memories),
                "removed": len(removed_memories),
                "compression_ratio": f"{(1 - len(kept_memories)/current_size)*100:.1f}%"
            }
            
        except Exception as e:
            logger.error(f"Failed to compress memories: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _check_compression(self):
        """Check if memory compression is needed"""
        current_time = time.time()
        
        # Compress if too many memories or time interval passed
        if (len(self.memory_cache) > self.max_memory_size or 
            current_time - self.last_compression > self.compression_interval):
            
            await self.compress_memories()
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            memory_types = {}
            importance_dist = {"high": 0, "medium": 0, "low": 0}
            total_importance = 0
            
            for memory in self.memory_cache.values():
                # Count by type
                memory_types[memory.memory_type] = memory_types.get(memory.memory_type, 0) + 1
                
                # Importance distribution
                if memory.importance > 0.7:
                    importance_dist["high"] += 1
                elif memory.importance > 0.4:
                    importance_dist["medium"] += 1
                else:
                    importance_dist["low"] += 1
                
                total_importance += memory.importance
            
            avg_importance = total_importance / len(self.memory_cache) if self.memory_cache else 0
            
            return {
                "success": True,
                "total_memories": len(self.memory_cache),
                "knowledge_graph_nodes": len(self.knowledge_graph),
                "memory_types": memory_types,
                "importance_distribution": importance_dist,
                "average_importance": avg_importance,
                "index_size": self.faiss_index.ntotal if self.faiss_index else 0,
                "last_compression": datetime.fromtimestamp(self.last_compression).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

# Global instance for skill registration
memory_skill = MemorySkill()

# Skill function exports for orchestrator
async def store_memory(content: str, memory_type: str, **kwargs) -> Dict[str, Any]:
    """Store new memory"""
    return await memory_skill.store_memory(content, memory_type, **kwargs)

async def search_memories(query: str, **kwargs) -> Dict[str, Any]:
    """Search memories using semantic similarity"""
    return await memory_skill.search_memories(query, **kwargs)

async def create_knowledge_graph(topic: str, **kwargs) -> Dict[str, Any]:
    """Create knowledge graph from memories"""
    return await memory_skill.create_knowledge_graph(topic, **kwargs)

async def compress_memories(**kwargs) -> Dict[str, Any]:
    """Compress memory storage"""
    return await memory_skill.compress_memories(**kwargs)

async def get_memory_stats() -> Dict[str, Any]:
    """Get memory system statistics"""
    return await memory_skill.get_memory_stats()
