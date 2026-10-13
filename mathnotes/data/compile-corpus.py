#!/usr/bin/env python3
"""
compile_corpus.py - Obsidian/Markdown Knowledge Graph Compiler
Scans workspace directories, chunks files by headers, parses wiki-links into 
graph edges, extracts 4-7 semantic tags using statistical or transformer-based 
models, and compiles everything into a unified JSON corpus ready to feed retrieval-layer.js.
"""

import os
import re
import json
import argparse
from pathlib import Path

# Try importing standard NLP/ML stack for semantic mode
try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    ML_STACK_AVAILABLE = True
except ImportError:
    ML_STACK_AVAILABLE = False
    # Fallback stopping list of English stop words
    try:
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    except ImportError:
        ENGLISH_STOP_WORDS = set([
            "a", "about", "above", "across", "after", "afterwards", "again", "against", "all", "almost", 
            "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", 
            "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", 
            "are", "around", "as", "at", "back", "be", "became", "because", "become", "becomes", "becoming", 
            "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", 
            "beyond", "bill", "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con", 
            "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", 
            "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough", "etc", 
            "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", 
            "fifty", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", 
            "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", 
            "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", 
            "him", "himself", "his", "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed", 
            "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", 
            "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", 
            "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", 
            "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", 
            "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", 
            "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps", 
            "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", 
            "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", 
            "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", 
            "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", 
            "there", "thereafter", "thereby", "therein", "thereupon", "these", "they", "thick", "thin", 
            "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", 
            "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", 
            "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", 
            "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", 
            "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", 
            "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", 
            "yourselves"
        ])

class KeywordExtractor:
    def __init__(self, mode="statistical", model_path="sentence-transformers/all-MiniLM-L6-v2"):
        self.mode = mode if ML_STACK_AVAILABLE else "statistical"
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        
        if self.mode == "semantic":
            print(f"[Extractor] Initializing local semantic transformer: {model_path}...")
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModel.from_pretrained(model_path)
                if torch.cuda.is_available():
                    self.model = self.model.to("cuda")
                self.model.eval()
                print("[Extractor] Local transformer model loaded successfully.")
            except Exception as e:
                print(f"[Extractor] Error loading transformer: {e}. Falling back to statistical mode.")
                self.mode = "statistical"

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def extract_candidates_simple(self, text, min_word_len=3, max_candidates=30):
        # Extracts single nouns, adjectives + nouns, or capitalized technical phrases
        words = re.findall(r'\b[a-zA-Z0-9_\-\\]+\b', text)
        candidates = set()
        
        # Build n-grams and filter stop words
        stop_words = ENGLISH_STOP_WORDS if 'ENGLISH_STOP_WORDS' in globals() else set()
        
        for i in range(len(words)):
            w1 = words[i].lower()
            if len(w1) >= min_word_len and w1 not in stop_words and not w1.isdigit():
                candidates.add(words[i]) # Keep original casing for output presentation
                
            # Adjective/Noun pairings (Bigrams)
            if i < len(words) - 1:
                w2 = words[i+1].lower()
                if (len(w1) >= min_word_len and len(w2) >= min_word_len and 
                    w1 not in stop_words and w2 not in stop_words and 
                    not w1.isdigit() and not w2.isdigit()):
                    candidates.add(f"{words[i]} {words[i+1]}")
                    
        return list(candidates)[:max_candidates]

    def extract_tags(self, title, content, doc_freq=None, corpus_size=1):
        full_text = f"{title} {content}"
        candidates = self.extract_candidates_simple(full_text)
        
        if not candidates:
            return ["general"]

        # Limit tag counts to optimal 4-7
        num_tags = min(max(4, len(candidates)), 7)
        
        if self.mode == "semantic":
            try:
                # Local KeyBERT Implementation
                with torch.no_grad():
                    # Embed Document
                    doc_inputs = self.tokenizer(full_text, padding=True, truncation=True, max_length=512, return_tensors="pt")
                    if torch.cuda.is_available():
                        doc_inputs = {k: v.to("cuda") for k, v in doc_inputs.items()}
                    doc_outputs = self.model(**doc_inputs)
                    doc_embedding = self._mean_pooling(doc_outputs, doc_inputs["attention_mask"]).cpu().numpy()

                    # Embed Candidates
                    cand_list = list(candidates)
                    cand_inputs = self.tokenizer(cand_list, padding=True, truncation=True, max_length=64, return_tensors="pt")
                    if torch.cuda.is_available():
                        cand_inputs = {k: v.to("cuda") for k, v in cand_inputs.items()}
                    cand_outputs = self.model(**cand_inputs)
                    cand_embeddings = self._mean_pooling(cand_outputs, cand_inputs["attention_mask"]).cpu().numpy()

                    # Calculate Cosine Similarities
                    similarities = cosine_similarity(cand_embeddings, doc_embedding).flatten()
                    ranked_indices = np.argsort(similarities)[::-1]
                    
                    selected_tags = []
                    for idx in ranked_indices:
                        tag = cand_list[idx]
                        # Avoid duplicates in lower-case
                        if tag.lower() not in [t.lower() for t in selected_tags]:
                            selected_tags.append(tag)
                        if len(selected_tags) >= num_tags:
                            break
                    return selected_tags
            except Exception as e:
                print(f"[Extractor] Error during semantic embedding: {e}. Falling back to statistical.")

        # Fallback Statistical Extractor: Weighted frequency + position scoring + TF-IDF style proxy
        scores = {}
        stop_words = ENGLISH_STOP_WORDS if 'ENGLISH_STOP_WORDS' in globals() else set()
        title_words = set(re.findall(r'\b[a-zA-Z0-9_\-\\]+\b', title.lower()))
        
        words = re.findall(r'\b[a-zA-Z0-9_\-\\]+\b', content.lower())
        total_words = len(words)

        for cand in candidates:
            cand_lower = cand.lower()
            # Count occurrences in body
            count = len(re.findall(r'\b' + re.escape(cand_lower) + r'\b', content.lower()))
            
            # 1. Base frequency score
            score = count * 2.0
            
            # 2. Title Prominence Boost (if candidate overlaps with title words)
            cand_parts = cand_lower.split()
            title_overlap = sum(1 for part in cand_parts if part in title_words)
            if title_overlap > 0:
                score += 15.0 * title_overlap
                
            # 3. Position Bias (earlier words are usually more key)
            if total_words > 0:
                # Find first appearance position
                try:
                    first_pos = content.lower().index(cand_lower) / len(content)
                    score += (1.0 - first_pos) * 5.0
                except ValueError:
                    pass
            
            # 4. TF-IDF Proxy (if Document Frequency dict is supplied)
            if doc_freq and cand_lower in doc_freq:
                df = doc_freq[cand_lower]
                idf = np.log((corpus_size + 0.5) / (df + 0.5)) if 'np' in globals() else (corpus_size / (df + 1))
                score *= (idf + 0.5)
                
            scores[cand] = score
            
        # Rank candidates by score
        sorted_cand = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        selected_tags = []
        for tag, _ in sorted_cand:
            if tag.lower() not in [t.lower() for t in selected_tags]:
                selected_tags.append(tag)
            if len(selected_tags) >= num_tags:
                break
                
        return selected_tags

class MarkdownGraphCompiler:
    def __init__(self, root_dir, output_file="corpus.json", extractor_mode="statistical", model_path=None):
        self.root_dir = Path(root_dir)
        self.output_file = output_file
        self.extractor_mode = extractor_mode
        self.model_path = model_path
        
        # Graph State
        self.nodes = {} # id -> { id, title, description, tags, neighbors }
        self.id_to_filename = {} # slugified_id -> relative_file_path or section
        self.title_to_id = {} # Lowercase section title -> slugified_id
        
    def slugify(self, text):
        # Standard slugification for node IDs
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9_\-\\]', '_', slug)
        slug = re.sub(r'_+', '_', slug)
        return slug.strip('_')

    def parse_markdown_headers(self, file_path):
        """
        Parses a markdown file and splits it into sections by headers (# , ##, ###).
        If no headers exist, treats the entire file as a single section.
        """
        relative_path = file_path.relative_to(self.root_dir)
        file_slug = self.slugify(file_path.stem)
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"[Parser] Failed to read {file_path}: {e}")
            return []

        # Find all header boundaries
        # Pattern: ^(#{1,6})\s+(.*)$
        lines = content.splitlines()
        sections = []
        current_header = file_path.stem # Default to file name
        current_body = []
        current_level = 0
        
        for line in lines:
            header_match = re.match(r'^(#{1,6})\s+(.*)$', line)
            if header_match:
                # Flush previous section
                if current_body or current_header != file_path.stem:
                    sections.append({
                        "file_slug": file_slug,
                        "header": current_header,
                        "body": "\n".join(current_body).strip(),
                        "level": current_level,
                        "path": str(relative_path)
                    })
                current_level = len(header_match.group(1))
                current_header = header_match.group(2).strip()
                current_body = []
            else:
                current_body.append(line)
                
        # Flush the final section
        if current_body or current_header:
            sections.append({
                "file_slug": file_slug,
                "header": current_header,
                "body": "\n".join(current_body).strip(),
                "level": current_level,
                "path": str(relative_path)
              })
            
        return sections

    def scan_and_register(self):
        """
        Traverses the directory, parses headers, and registers nodes in the graph.
        """
        print(f"[Compiler] Scanning {self.root_dir} recursively for Markdown files...")
        md_files = list(self.root_dir.rglob("*.md"))
        print(f"[Compiler] Found {len(md_files)} Markdown files.")
        
        raw_sections = []
        for file_path in md_files:
            sections = self.parse_markdown_headers(file_path)
            raw_sections.extend(sections)
            
        print(f"[Compiler] Parsed {len(raw_sections)} document sections.")
        
        # Register nodes
        for idx, sec in enumerate(raw_sections):
            # Create a unique node ID: file_slug + header_slug
            header_slug = self.slugify(sec["header"])
            node_id = f"{sec['file_slug']}_{header_slug}" if header_slug and header_slug != sec['file_slug'] else sec['file_slug']
            
            # De-duplicate IDs
            orig_id = node_id
            counter = 1
            while node_id in self.nodes:
                node_id = f"{orig_id}_{counter}"
                counter += 1
                
            self.nodes[node_id] = {
                "id": node_id,
                "title": sec["header"],
                "description": sec["body"],
                "tags": [],
                "neighbors": [],
                "raw_path": sec["path"]
            }
            
            # Map index lookups for resolving links later
            self.id_to_filename[node_id] = sec["path"]
            self.title_to_id[sec["header"].lower()] = node_id
            # Also map the file-level title
            self.title_to_id[Path(sec["path"]).stem.lower()] = node_id
            
        print(f"[Compiler] Registered {len(self.nodes)} node structures in memory.")

    def parse_graph_edges(self):
        """
        Scans description text for WikiLinks and Markdown links to create edge mappings.
        """
        print("[Compiler] Parsing inter-node connections (links)...")
        edge_count = 0
        
        for node_id, node in self.nodes.items():
            content = node["description"]
            neighbors = set()
            
            # 1. Parse Wiki-links: [[Page Name]] or [[Page Name|Alias]]
            wiki_links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
            for link in wiki_links:
                link_clean = link.strip().lower()
                # Try to map to a registered node title
                if link_clean in self.title_to_id:
                    neighbors.add(self.title_to_id[link_clean])
                # Try to fuzzy match matching filenames
                else:
                    for tid, nid in self.title_to_id.items():
                        if link_clean in tid or tid in link_clean:
                            neighbors.add(nid)
                            break

            # 2. Parse Standard Markdown links: [Link Text](file.md) or (path/to/file.md#Header)
            md_links = re.findall(r'\[[^\]]+\]\(([^)]+\.md)(?:#[^)]+)?\)', content)
            for link in md_links:
                link_stem = Path(link).stem.lower()
                if link_stem in self.title_to_id:
                    neighbors.add(self.title_to_id[link_stem])
                    
            node["neighbors"] = list(neighbors)
            edge_count += len(node["neighbors"])
            
        print(f"[Compiler] Spliced {edge_count} directed edges across the knowledge graph.")

    def compile(self):
        self.scan_and_register()
        self.parse_graph_edges()
        
        if not self.nodes:
            print("[Compiler] Warning: No node data extracted. Exiting compilation.")
            return []

        # Compute document frequencies across corpus for statistical TF-IDF boost
        doc_frequencies = {}
        for node in self.nodes.values():
            words_seen = set(re.findall(r'\b[a-zA-Z0-9_\-\\]+\b', node["description"].lower()))
            for w in words_seen:
                doc_frequencies[w] = doc_frequencies.get(w, 0) + 1
                
        # Initialize Keyword/Tag Extractor
        extractor = KeywordExtractor(mode=self.extractor_mode, model_path=self.model_path)
        
        print("[Compiler] Extracting 4-7 semantic signatures per node...")
        processed_count = 0
        
        for node_id, node in self.nodes.items():
            node["tags"] = extractor.extract_tags(
                title=node["title"], 
                content=node["description"], 
                doc_freq=doc_frequencies,
                corpus_size=len(self.nodes)
            )
            processed_count += 1
            if processed_count % 100 == 0:
                print(f"  Processed {processed_count}/{len(self.nodes)} nodes...")
                
        # Format corpus to final schema
        final_corpus = []
        for node_id, node in self.nodes.items():
            final_corpus.append({
                "id": node["id"],
                "title": node["title"],
                "description": node["description"],
                "tags": node["tags"],
                "neighbors": node["neighbors"]
            })
            
        # Write to JSON file
        print(f"[Compiler] Compiling and saving final corpus to {self.output_file}...")
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(final_corpus, f, indent=2, ensure_ascii=False)
            print(f"[Compiler] SUCCESS: Saved {len(final_corpus)} compiled nodes to '{self.output_file}'.")
        except Exception as e:
            print(f"[Compiler] Failed to write compiled file: {e}")
            
        return final_corpus

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively index Markdown files into a semantic knowledge graph JSON.")
    parser.add_argument("--dir", default=".", help="Root directory to scan recursively for Markdown files.")
    parser.add_argument("--output", default="corpus.json", help="Path to write compiled output JSON file.")
    parser.add_argument("--mode", default="statistical", choices=["statistical", "semantic"], 
                        help="Tag extraction mode. 'semantic' runs local HuggingFace embeddings (requires Torch/Sklearn).")
    parser.add_argument("--model-path", default="sentence-transformers/all-MiniLM-L6-v2", 
                        help="HuggingFace model path/identifier (used in semantic mode).")
                        
    args = parser.parse_args()
    
    compiler = MarkdownGraphCompiler(
        root_dir=args.dir,
        output_file=args.output,
        extractor_mode=args.mode,
        model_path=args.model_path
    )
    compiler.compile()
