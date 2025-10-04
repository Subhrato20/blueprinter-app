import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

// Types
interface CodingPreference {
  id: string;
  category: string;
  preference_text: string;
  context?: string;
  strength: 'weak' | 'moderate' | 'strong' | 'absolute';
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

interface CodingStyleSummary {
  category: string;
  preference_count: number;
  top_preferences: string[];
}

interface NewPreference {
  category: string;
  preference_text: string;
  context: string;
  strength: 'weak' | 'moderate' | 'strong' | 'absolute';
}

const CATEGORIES = [
  'frontend_framework',
  'backend_pattern', 
  'code_style',
  'architecture',
  'testing',
  'deployment',
  'documentation',
  'naming_convention'
];

const STRENGTHS = [
  { value: 'weak', label: 'Weak', color: 'text-gray-500' },
  { value: 'moderate', label: 'Moderate', color: 'text-yellow-600' },
  { value: 'strong', label: 'Strong', color: 'text-orange-600' },
  { value: 'absolute', label: 'Absolute', color: 'text-red-600' }
];

const CodingPreferencesManager: React.FC = () => {
  const [preferences, setPreferences] = useState<CodingPreference[]>([]);
  const [summary, setSummary] = useState<CodingStyleSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CodingPreference[]>([]);
  const [newPreference, setNewPreference] = useState<NewPreference>({
    category: 'code_style',
    preference_text: '',
    context: '',
    strength: 'moderate'
  });

  const supabase = createClient(
    import.meta.env.VITE_SUPABASE_URL,
    import.meta.env.VITE_SUPABASE_ANON_KEY
  );

  useEffect(() => {
    loadPreferences();
    loadSummary();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        console.error('No active session');
        return;
      }

      const response = await fetch('/api/coding-preferences/', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPreferences(data);
      }
    } catch (error) {
      console.error('Failed to load preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) return;

      const response = await fetch('/api/coding-preferences/summary', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (error) {
      console.error('Failed to load summary:', error);
    }
  };

  const handleAddPreference = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) return;

      const response = await fetch('/api/coding-preferences/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newPreference)
      });

      if (response.ok) {
        await loadPreferences();
        await loadSummary();
        setNewPreference({
          category: 'code_style',
          preference_text: '',
          context: '',
          strength: 'moderate'
        });
        setShowAddForm(false);
      }
    } catch (error) {
      console.error('Failed to add preference:', error);
    }
  };

  const handleDeletePreference = async (id: string) => {
    if (!confirm('Are you sure you want to delete this preference?')) return;

    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) return;

      const response = await fetch(`/api/coding-preferences/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        await loadPreferences();
        await loadSummary();
      }
    } catch (error) {
      console.error('Failed to delete preference:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) return;

      const response = await fetch('/api/coding-preferences/search', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query_text: searchQuery,
          similarity_threshold: 0.7,
          max_results: 10
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.preferences);
      }
    } catch (error) {
      console.error('Failed to search preferences:', error);
    }
  };

  const getStrengthColor = (strength: string) => {
    const strengthConfig = STRENGTHS.find(s => s.value === strength);
    return strengthConfig?.color || 'text-gray-500';
  };

  const formatCategory = (category: string) => {
    return category.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Coding Preferences</h1>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Add Preference
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {summary.map((item) => (
          <div key={item.category} className="bg-white p-4 rounded-lg shadow border">
            <h3 className="font-semibold text-gray-900">{formatCategory(item.category)}</h3>
            <p className="text-2xl font-bold text-blue-600">{item.preference_count}</p>
            <div className="mt-2 space-y-1">
              {item.top_preferences.slice(0, 2).map((pref, idx) => (
                <p key={idx} className="text-sm text-gray-600 truncate">{pref}</p>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Search */}
      <div className="bg-white p-4 rounded-lg shadow border">
        <h2 className="text-xl font-semibold mb-4">Search Preferences</h2>
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for similar preferences..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSearch}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Search
          </button>
        </div>
        
        {searchResults.length > 0 && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Search Results:</h3>
            <div className="space-y-2">
              {searchResults.map((pref) => (
                <div key={pref.id} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{pref.preference_text}</p>
                      {pref.context && <p className="text-sm text-gray-600">{pref.context}</p>}
                    </div>
                    <span className={`text-sm font-medium ${getStrengthColor(pref.strength)}`}>
                      {pref.strength}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Add Form Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold mb-4">Add Coding Preference</h2>
            <form onSubmit={handleAddPreference} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={newPreference.category}
                  onChange={(e) => setNewPreference({...newPreference, category: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {CATEGORIES.map(cat => (
                    <option key={cat} value={cat}>{formatCategory(cat)}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preference Text
                </label>
                <input
                  type="text"
                  value={newPreference.preference_text}
                  onChange={(e) => setNewPreference({...newPreference, preference_text: e.target.value})}
                  placeholder="e.g., Use TypeScript for all frontend code"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Context (Optional)
                </label>
                <textarea
                  value={newPreference.context}
                  onChange={(e) => setNewPreference({...newPreference, context: e.target.value})}
                  placeholder="Additional context about when this preference applies..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Strength
                </label>
                <select
                  value={newPreference.strength}
                  onChange={(e) => setNewPreference({...newPreference, strength: e.target.value as any})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {STRENGTHS.map(strength => (
                    <option key={strength.value} value={strength.value}>{strength.label}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex gap-2 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add Preference
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Preferences List */}
      <div className="bg-white rounded-lg shadow border">
        <div className="p-4 border-b">
          <h2 className="text-xl font-semibold">Your Coding Preferences</h2>
        </div>
        <div className="divide-y">
          {preferences.map((pref) => (
            <div key={pref.id} className="p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded">
                      {formatCategory(pref.category)}
                    </span>
                    <span className={`text-sm font-medium ${getStrengthColor(pref.strength)}`}>
                      {pref.strength}
                    </span>
                  </div>
                  <p className="font-medium text-gray-900 mb-1">{pref.preference_text}</p>
                  {pref.context && (
                    <p className="text-sm text-gray-600 mb-2">{pref.context}</p>
                  )}
                  <p className="text-xs text-gray-500">
                    Added {new Date(pref.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDeletePreference(pref.id)}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CodingPreferencesManager;
