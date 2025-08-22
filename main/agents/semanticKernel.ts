/**
 * Semantic Kernel Orchestrator - Type Definitions
 * 
 * This file contains TypeScript type definitions for reference.
 * The actual implementation is in semantic_kernel.py
 */

export interface KernelSettings {
  kernel: {
    version: string;
    environment: string;
    debug_mode: boolean;
    orchestration_mode: string;
    fallback_strategy: string;
  };
  ai_models: {
    primary: AIModelConfig;
    fallback_chain: AIModelConfig[];
  };
  plugins: {
    authentication: AuthConfig;
    memory: MemoryConfig;
    logging: LoggingConfig;
  };
  skill_discovery: SkillDiscoveryConfig;
  routing: RoutingConfig;
  signals: SignalConfig;
}

export interface AIModelConfig {
  provider: string;
  model: string;
  api_key_env: string;
  endpoint: string;
  max_tokens: number;
  temperature: number;
  timeout: number;
}

export interface SkillManifest {
  skillId: string;
  name: string;
  description: string;
  version: string;
  category: string;
  priority: number;
  capabilities: string[];
  functions: SkillFunction[];
  signals: Record<string, SignalDefinition>;
  routing: RoutingOptions;
}

export interface SkillFunction {
  name: string;
  description: string;
  parameters: Record<string, any>;
  returns: Record<string, any>;
}

export interface SignalDefinition {
  description: string;
  data: Record<string, string>;
}

export interface RoutingOptions {
  fallback_enabled: boolean;
  cache_responses: boolean;
  rate_limiting: {
    enabled: boolean;
    requests_per_minute: number;
  };
}

export interface AuthConfig {
  enabled: boolean;
  providers: string[];
  token_refresh_interval: number;
  encryption_key_env: string;
}

export interface MemoryConfig {
  provider: string;
  storage_type: string;
  max_entries: number;
  ttl_seconds: number;
  compression_enabled: boolean;
  search_enabled: boolean;
  embedding_model: string;
}

export interface LoggingConfig {
  level: string;
  format: string;
  handlers: string[];
  file_path: string;
  max_file_size_mb: number;
  backup_count: number;
}

export interface SkillDiscoveryConfig {
  auto_discovery: boolean;
  scan_paths: string[];
  manifest_pattern: string;
  load_priority: string[];
  hot_reload: boolean;
  validation_strict: boolean;
}

export interface RoutingConfig {
  strategy: string;
  cache_enabled: boolean;
  cache_ttl_seconds: number;
  circuit_breaker: {
    enabled: boolean;
    failure_threshold: number;
    recovery_timeout: number;
    half_open_max_calls: number;
  };
  rate_limiting: {
    enabled: boolean;
    requests_per_minute: number;
    burst_allowance: number;
  };
}

export interface SignalConfig {
  global_handlers: Record<string, string>;
  propagation: {
    bubble_up: boolean;
    async_processing: boolean;
    max_queue_size: number;
  };
}
