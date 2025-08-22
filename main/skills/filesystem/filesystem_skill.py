"""
Filesystem Skill Implementation
Provides file system operations with security, compression, and advanced search capabilities.
"""

import asyncio
import os
import json
import hashlib
import logging
import time
import zipfile
# import py7zr  # Optional - will skip 7z if not available
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import mimetypes
import shutil
import fnmatch
import re

logger = logging.getLogger(__name__)

@dataclass
class FileMetadata:
    """File metadata information"""
    path: str
    name: str
    size: int
    created: str
    modified: str
    type: str
    mime_type: str
    checksum: str
    permissions: str

@dataclass
class SearchResult:
    """File search result"""
    path: str
    name: str
    size: int
    matches: List[str]
    metadata: Dict[str, Any]

class FilesystemSkill:
    """Advanced filesystem operations with security and compression"""
    
    def __init__(self, sandbox_path: Optional[str] = None):
        """Initialize filesystem skill with optional sandbox"""
        self.sandbox_path = Path(sandbox_path) if sandbox_path else None
        self.max_file_size = 100 * 1024 * 1024  # 100MB default limit
        self.allowed_extensions = {
            '.txt', '.json', '.xml', '.csv', '.md', '.py', '.js', '.html',
            '.css', '.yaml', '.yml', '.ini', '.conf', '.log'
        }
        self.blocked_paths = {'/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin'}
        
    def _validate_path(self, path: str) -> Path:
        """Validate and resolve file path within sandbox"""
        try:
            file_path = Path(path).resolve()
            
            # Check if within sandbox
            if self.sandbox_path:
                if not str(file_path).startswith(str(self.sandbox_path.resolve())):
                    raise PermissionError(f"Path outside sandbox: {path}")
            
            # Check blocked paths
            for blocked in self.blocked_paths:
                if str(file_path).startswith(blocked):
                    raise PermissionError(f"Access to blocked path: {path}")
                    
            return file_path
            
        except Exception as e:
            logger.error(f"Path validation failed for {path}: {e}")
            raise ValueError(f"Invalid path: {path}")
    
    def _get_file_metadata(self, file_path: Path) -> FileMetadata:
        """Get comprehensive file metadata"""
        try:
            stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Calculate checksum for files
            checksum = ""
            if file_path.is_file() and stat.st_size < self.max_file_size:
                with open(file_path, 'rb') as f:
                    checksum = hashlib.md5(f.read()).hexdigest()
            
            return FileMetadata(
                path=str(file_path),
                name=file_path.name,
                size=stat.st_size,
                created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                type="file" if file_path.is_file() else "directory",
                mime_type=mime_type or "unknown",
                checksum=checksum,
                permissions=oct(stat.st_mode)[-3:]
            )
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {file_path}: {e}")
            raise
    
    async def read_file(self, path: str, encoding: str = "utf-8", 
                       max_size: Optional[int] = None) -> Dict[str, Any]:
        """Read file content with size and encoding validation"""
        try:
            file_path = self._validate_path(path)
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {path}",
                    "error_type": "FileNotFoundError"
                }
            
            if not file_path.is_file():
                return {
                    "success": False,
                    "error": f"Path is not a file: {path}",
                    "error_type": "IsADirectoryError"
                }
            
            # Check file size
            file_size = file_path.stat().st_size
            size_limit = max_size or self.max_file_size
            
            if file_size > size_limit:
                return {
                    "success": False,
                    "error": f"File too large: {file_size} bytes (limit: {size_limit})",
                    "error_type": "FileTooLargeError"
                }
            
            # Read file content
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try binary read if text fails
                with open(file_path, 'rb') as f:
                    content = f.read()
                    content = f"<binary content: {len(content)} bytes>"
            
            metadata = self._get_file_metadata(file_path)
            
            return {
                "success": True,
                "content": content,
                "metadata": asdict(metadata),
                "encoding": encoding,
                "size": file_size
            }
            
        except Exception as e:
            logger.error(f"Failed to read file {path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def write_file(self, path: str, content: str, 
                        encoding: str = "utf-8", 
                        create_dirs: bool = True,
                        backup: bool = False) -> Dict[str, Any]:
        """Write content to file with optional backup"""
        try:
            file_path = self._validate_path(path)
            
            # Check file extension
            if file_path.suffix.lower() not in self.allowed_extensions:
                return {
                    "success": False,
                    "error": f"File extension not allowed: {file_path.suffix}",
                    "error_type": "PermissionError"
                }
            
            # Create directories if needed
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup if requested and file exists
            backup_path = None
            if backup and file_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = file_path.with_suffix(f".{timestamp}.bak")
                shutil.copy2(file_path, backup_path)
            
            # Write content
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            metadata = self._get_file_metadata(file_path)
            
            return {
                "success": True,
                "path": str(file_path),
                "size": len(content.encode(encoding)),
                "metadata": asdict(metadata),
                "backup_path": str(backup_path) if backup_path else None
            }
            
        except Exception as e:
            logger.error(f"Failed to write file {path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def list_directory(self, path: str, recursive: bool = False,
                           pattern: Optional[str] = None,
                           file_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """List directory contents with filtering options"""
        try:
            dir_path = self._validate_path(path)
            
            if not dir_path.exists():
                return {
                    "success": False,
                    "error": f"Directory not found: {path}",
                    "error_type": "FileNotFoundError"
                }
            
            if not dir_path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {path}",
                    "error_type": "NotADirectoryError"
                }
            
            items = []
            
            def should_include(item_path: Path) -> bool:
                """Check if item should be included based on filters"""
                # Pattern filter
                if pattern and not fnmatch.fnmatch(item_path.name, pattern):
                    return False
                
                # File type filter
                if file_types:
                    if item_path.is_file():
                        return item_path.suffix.lower() in [ft.lower() for ft in file_types]
                    else:
                        return "directory" in [ft.lower() for ft in file_types]
                
                return True
            
            # Traverse directory
            if recursive:
                for item in dir_path.rglob("*"):
                    if should_include(item):
                        try:
                            metadata = self._get_file_metadata(item)
                            items.append(asdict(metadata))
                        except Exception as e:
                            logger.warning(f"Failed to get metadata for {item}: {e}")
            else:
                for item in dir_path.iterdir():
                    if should_include(item):
                        try:
                            metadata = self._get_file_metadata(item)
                            items.append(asdict(metadata))
                        except Exception as e:
                            logger.warning(f"Failed to get metadata for {item}: {e}")
            
            # Sort by name
            items.sort(key=lambda x: x['name'].lower())
            
            return {
                "success": True,
                "path": str(dir_path),
                "items": items,
                "count": len(items),
                "recursive": recursive,
                "pattern": pattern,
                "file_types": file_types
            }
            
        except Exception as e:
            logger.error(f"Failed to list directory {path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def search_files(self, root_path: str, query: str,
                          search_content: bool = False,
                          case_sensitive: bool = False,
                          regex: bool = False,
                          file_types: Optional[List[str]] = None,
                          max_results: int = 100) -> Dict[str, Any]:
        """Search for files by name and optionally content"""
        try:
            root_dir = self._validate_path(root_path)
            
            if not root_dir.exists() or not root_dir.is_dir():
                return {
                    "success": False,
                    "error": f"Invalid search root: {root_path}",
                    "error_type": "FileNotFoundError"
                }
            
            results = []
            flags = 0 if case_sensitive else re.IGNORECASE
            
            # Compile regex pattern
            if regex:
                try:
                    pattern = re.compile(query, flags)
                except re.error as e:
                    return {
                        "success": False,
                        "error": f"Invalid regex pattern: {e}",
                        "error_type": "RegexError"
                    }
            else:
                # Escape special characters for literal search
                escaped_query = re.escape(query)
                pattern = re.compile(escaped_query, flags)
            
            # Search files
            for file_path in root_dir.rglob("*"):
                if len(results) >= max_results:
                    break
                
                if not file_path.is_file():
                    continue
                
                # File type filter
                if file_types and file_path.suffix.lower() not in [ft.lower() for ft in file_types]:
                    continue
                
                matches = []
                
                # Search filename
                if pattern.search(file_path.name):
                    matches.append(f"filename: {file_path.name}")
                
                # Search content if requested
                if search_content and file_path.suffix.lower() in self.allowed_extensions:
                    try:
                        file_size = file_path.stat().st_size
                        if file_size <= self.max_file_size:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                content_matches = pattern.findall(content)
                                if content_matches:
                                    matches.extend([f"content: {match}" for match in content_matches[:5]])
                    except Exception as e:
                        logger.debug(f"Could not search content in {file_path}: {e}")
                
                # Add to results if matches found
                if matches:
                    try:
                        metadata = self._get_file_metadata(file_path)
                        result = SearchResult(
                            path=str(file_path),
                            name=file_path.name,
                            size=metadata.size,
                            matches=matches,
                            metadata=asdict(metadata)
                        )
                        results.append(asdict(result))
                    except Exception as e:
                        logger.warning(f"Failed to get metadata for {file_path}: {e}")
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "search_content": search_content,
                "case_sensitive": case_sensitive,
                "regex": regex,
                "max_results": max_results
            }
            
        except Exception as e:
            logger.error(f"Failed to search files in {root_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def compress_files(self, source_paths: List[str], 
                           output_path: str,
                           format: str = "zip",
                           compression_level: int = 6) -> Dict[str, Any]:
        """Compress files and directories"""
        try:
            output_file = self._validate_path(output_path)
            
            # Validate source paths
            validated_sources = []
            for source in source_paths:
                source_path = self._validate_path(source)
                if source_path.exists():
                    validated_sources.append(source_path)
                else:
                    logger.warning(f"Source path not found: {source}")
            
            if not validated_sources:
                return {
                    "success": False,
                    "error": "No valid source paths found",
                    "error_type": "FileNotFoundError"
                }
            
            # Create output directory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            compressed_files = []
            total_original_size = 0
            
            if format.lower() == "zip":
                with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, 
                                   compresslevel=compression_level) as zipf:
                    for source_path in validated_sources:
                        if source_path.is_file():
                            zipf.write(source_path, source_path.name)
                            total_original_size += source_path.stat().st_size
                            compressed_files.append(str(source_path))
                        elif source_path.is_dir():
                            for file_path in source_path.rglob("*"):
                                if file_path.is_file():
                                    arcname = file_path.relative_to(source_path.parent)
                                    zipf.write(file_path, arcname)
                                    total_original_size += file_path.stat().st_size
                                    compressed_files.append(str(file_path))
            
            elif format.lower() == "7z":
                try:
                    import py7zr
                    with py7zr.SevenZipFile(output_file, 'w') as archive:
                        for source_path in validated_sources:
                            if source_path.is_file():
                                archive.write(source_path, source_path.name)
                                total_original_size += source_path.stat().st_size
                                compressed_files.append(str(source_path))
                            elif source_path.is_dir():
                                archive.writeall(source_path, source_path.name)
                                for file_path in source_path.rglob("*"):
                                    if file_path.is_file():
                                        total_original_size += file_path.stat().st_size
                                        compressed_files.append(str(file_path))
                except ImportError:
                    return {
                        "success": False,
                        "error": "7z compression requires py7zr package",
                        "error_type": "ImportError"
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported compression format: {format}",
                    "error_type": "ValueError"
                }
            
            # Get compressed file size
            compressed_size = output_file.stat().st_size
            compression_ratio = (1 - compressed_size / total_original_size) * 100 if total_original_size > 0 else 0
            
            return {
                "success": True,
                "output_path": str(output_file),
                "format": format,
                "compression_level": compression_level,
                "files_compressed": len(compressed_files),
                "original_size": total_original_size,
                "compressed_size": compressed_size,
                "compression_ratio": f"{compression_ratio:.1f}%",
                "compressed_files": compressed_files[:20]  # Limit list size
            }
            
        except Exception as e:
            logger.error(f"Failed to compress files: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

# Global instance for skill registration
filesystem_skill = FilesystemSkill()

# Skill function exports for orchestrator
async def read_file(path: str, **kwargs) -> Dict[str, Any]:
    """Read file content"""
    return await filesystem_skill.read_file(path, **kwargs)

async def write_file(path: str, content: str, **kwargs) -> Dict[str, Any]:
    """Write content to file"""
    return await filesystem_skill.write_file(path, content, **kwargs)

async def list_directory(path: str, **kwargs) -> Dict[str, Any]:
    """List directory contents"""
    return await filesystem_skill.list_directory(path, **kwargs)

async def search_files(root_path: str, query: str, **kwargs) -> Dict[str, Any]:
    """Search for files"""
    return await filesystem_skill.search_files(root_path, query, **kwargs)

async def compress_files(source_paths: List[str], output_path: str, **kwargs) -> Dict[str, Any]:
    """Compress files and directories"""
    return await filesystem_skill.compress_files(source_paths, output_path, **kwargs)
