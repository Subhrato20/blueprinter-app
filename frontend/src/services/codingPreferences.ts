import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

export interface CodingPreference {
  id: string;
  category: string;
  preference_text: string;
  context?: string;
  strength: 'weak' | 'moderate' | 'strong' | 'absolute';
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface NewCodingPreference {
  category: string;
  preference_text: string;
  context?: string;
  strength: 'weak' | 'moderate' | 'strong' | 'absolute';
}

export interface CodingStyleSummary {
  category: string;
  preference_count: number;
  top_preferences: string[];
}

export interface SimilaritySearchRequest {
  query_text: string;
  similarity_threshold?: number;
  max_results?: number;
}

export interface SimilaritySearchResponse {
  preferences: CodingPreference[];
  similarities: number[];
}

export interface CodingSignal {
  signal_type: string;
  signal_data: Record<string, any>;
  confidence_score?: number;
}

class CodingPreferencesService {
  private async getAuthHeaders() {
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      throw new Error('No active session');
    }

    return {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    };
  }

  async getPreferences(category?: string): Promise<CodingPreference[]> {
    const headers = await this.getAuthHeaders();
    const url = category 
      ? `/api/coding-preferences/?category=${category}`
      : '/api/coding-preferences/';
    
    const response = await fetch(url, { headers });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch preferences: ${response.statusText}`);
    }
    
    return response.json();
  }

  async getStyleSummary(): Promise<CodingStyleSummary[]> {
    const headers = await this.getAuthHeaders();
    const response = await fetch('/api/coding-preferences/summary', { headers });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch style summary: ${response.statusText}`);
    }
    
    return response.json();
  }

  async createPreference(preference: NewCodingPreference): Promise<CodingPreference> {
    const headers = await this.getAuthHeaders();
    const response = await fetch('/api/coding-preferences/', {
      method: 'POST',
      headers,
      body: JSON.stringify(preference)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create preference: ${response.statusText}`);
    }
    
    return response.json();
  }

  async updatePreference(
    id: string, 
    updates: Partial<NewCodingPreference>
  ): Promise<CodingPreference> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`/api/coding-preferences/${id}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(updates)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update preference: ${response.statusText}`);
    }
    
    return response.json();
  }

  async deletePreference(id: string): Promise<void> {
    const headers = await this.getAuthHeaders();
    const response = await fetch(`/api/coding-preferences/${id}`, {
      method: 'DELETE',
      headers
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete preference: ${response.statusText}`);
    }
  }

  async searchSimilarPreferences(
    request: SimilaritySearchRequest
  ): Promise<SimilaritySearchResponse> {
    const headers = await this.getAuthHeaders();
    const response = await fetch('/api/coding-preferences/search', {
      method: 'POST',
      headers,
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to search preferences: ${response.statusText}`);
    }
    
    return response.json();
  }

  async createCodingSignal(signal: CodingSignal): Promise<{ id: string }> {
    const headers = await this.getAuthHeaders();
    const response = await fetch('/api/coding-preferences/signals', {
      method: 'POST',
      headers,
      body: JSON.stringify(signal)
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create coding signal: ${response.statusText}`);
    }
    
    return response.json();
  }

  // Helper methods for common preference categories
  async addFrontendPreference(
    text: string, 
    context?: string, 
    strength: 'weak' | 'moderate' | 'strong' | 'absolute' = 'moderate'
  ): Promise<CodingPreference> {
    return this.createPreference({
      category: 'frontend_framework',
      preference_text: text,
      context,
      strength
    });
  }

  async addBackendPreference(
    text: string, 
    context?: string, 
    strength: 'weak' | 'moderate' | 'strong' | 'absolute' = 'moderate'
  ): Promise<CodingPreference> {
    return this.createPreference({
      category: 'backend_pattern',
      preference_text: text,
      context,
      strength
    });
  }

  async addCodeStylePreference(
    text: string, 
    context?: string, 
    strength: 'weak' | 'moderate' | 'strong' | 'absolute' = 'moderate'
  ): Promise<CodingPreference> {
    return this.createPreference({
      category: 'code_style',
      preference_text: text,
      context,
      strength
    });
  }

  async addArchitecturePreference(
    text: string, 
    context?: string, 
    strength: 'weak' | 'moderate' | 'strong' | 'absolute' = 'moderate'
  ): Promise<CodingPreference> {
    return this.createPreference({
      category: 'architecture',
      preference_text: text,
      context,
      strength
    });
  }

  async addTestingPreference(
    text: string, 
    context?: string, 
    strength: 'weak' | 'moderate' | 'strong' | 'absolute' = 'moderate'
  ): Promise<CodingPreference> {
    return this.createPreference({
      category: 'testing',
      preference_text: text,
      context,
      strength
    });
  }

  // Signal tracking methods
  async trackFileCreation(filePath: string, language?: string): Promise<void> {
    await this.createCodingSignal({
      signal_type: 'file_created',
      signal_data: {
        file_path: filePath,
        language,
        timestamp: new Date().toISOString()
      }
    });
  }

  async trackCodePattern(patternType: string, context?: string): Promise<void> {
    await this.createCodingSignal({
      signal_type: 'code_pattern_used',
      signal_data: {
        pattern_type: patternType,
        context,
        timestamp: new Date().toISOString()
      }
    });
  }

  async trackRefactoring(refactorType: string, trigger?: string): Promise<void> {
    await this.createCodingSignal({
      signal_type: 'refactor_applied',
      signal_data: {
        refactor_type: refactorType,
        trigger,
        timestamp: new Date().toISOString()
      }
    });
  }

  async trackTestWritten(testType: string, framework?: string): Promise<void> {
    await this.createCodingSignal({
      signal_type: 'test_written',
      signal_data: {
        test_type: testType,
        framework,
        timestamp: new Date().toISOString()
      }
    });
  }
}

export const codingPreferencesService = new CodingPreferencesService();
