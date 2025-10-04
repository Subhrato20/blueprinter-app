import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Search, X, Check, AlertCircle } from 'lucide-react';

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
  const [editingPreference, setEditingPreference] = useState<CodingPreference | null>(null);
  const [newPreference, setNewPreference] = useState<NewPreference>({
    category: 'code_style',
    preference_text: '',
    context: '',
    strength: 'moderate'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CodingPreference[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);

  const API_BASE = 'http://localhost:8001/api/coding-preferences';

  useEffect(() => {
    loadPreferences();
    loadSummary();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPreferences(data);
      } else {
        console.error('Failed to load preferences');
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    try {
      const response = await fetch(`${API_BASE}/summary`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (error) {
      console.error('Error loading summary:', error);
    }
  };

  const handleAddPreference = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted with data:', newPreference);
    try {
      const response = await fetch(`${API_BASE}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newPreference),
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('Successfully added preference:', data);
        setNewPreference({
          category: 'code_style',
          preference_text: '',
          context: '',
          strength: 'moderate'
        });
        setShowAddForm(false);
        await loadPreferences();
        await loadSummary();
      } else {
        const errorText = await response.text();
        console.error('Failed to add preference:', response.status, errorText);
      }
    } catch (error) {
      console.error('Error adding preference:', error);
    }
  };

  const handleUpdatePreference = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingPreference) return;

    try {
      const response = await fetch(`${API_BASE}/${editingPreference.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category: editingPreference.category,
          preference_text: editingPreference.preference_text,
          context: editingPreference.context,
          strength: editingPreference.strength
        }),
      });

      if (response.ok) {
        setEditingPreference(null);
        await loadPreferences();
        await loadSummary();
      } else {
        console.error('Failed to update preference');
      }
    } catch (error) {
      console.error('Error updating preference:', error);
    }
  };

  const handleDeletePreference = async (id: string) => {
    if (!confirm('Are you sure you want to delete this preference?')) return;

    try {
      const response = await fetch(`${API_BASE}/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await loadPreferences();
        await loadSummary();
      } else {
        console.error('Failed to delete preference');
      }
    } catch (error) {
      console.error('Error deleting preference:', error);
    }
  };

  const handleSearchSimilarPreferences = async () => {
    if (!searchQuery.trim()) return;

    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data);
        setShowSearchResults(true);
      } else {
        console.error('Failed to search preferences');
      }
    } catch (error) {
      console.error('Error searching preferences:', error);
    }
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Coding Preferences</h1>
          <p className="text-gray-600">Manage your coding style and preferences</p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Preference
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {summary.map((item) => (
          <div key={item.category} className="bg-white p-4 rounded-lg shadow border">
            <h3 className="font-semibold text-gray-900">{formatCategory(item.category)}</h3>
            <p className="text-2xl font-bold text-blue-600">{item.preference_count}</p>
            <p className="text-sm text-gray-600">preferences</p>
          </div>
        ))}
      </div>

      {/* Search */}
      <div className="bg-white p-4 rounded-lg shadow border">
        <h3 className="font-semibold text-gray-900 mb-3">Search Similar Preferences</h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Describe what you're looking for..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSearchSimilarPreferences}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Search className="h-4 w-4" />
            Search
          </button>
        </div>
      </div>

      {/* Search Results */}
      {showSearchResults && (
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-gray-900">Search Results</h3>
            <button
              onClick={() => setShowSearchResults(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          {searchResults.length > 0 ? (
            <div className="space-y-2">
              {searchResults.map((pref) => (
                <div key={pref.id} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-sm font-medium text-blue-600">
                        {formatCategory(pref.category)}
                      </span>
                      <p className="text-gray-900">{pref.preference_text}</p>
                      {pref.context && (
                        <p className="text-sm text-gray-600">{pref.context}</p>
                      )}
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      pref.strength === 'weak' ? 'bg-gray-100 text-gray-600' :
                      pref.strength === 'moderate' ? 'bg-yellow-100 text-yellow-600' :
                      pref.strength === 'strong' ? 'bg-orange-100 text-orange-600' :
                      'bg-red-100 text-red-600'
                    }`}>
                      {pref.strength}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No similar preferences found.</p>
          )}
        </div>
      )}

      {/* Add Form */}
      {showAddForm && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Add New Preference</h3>
            <button
              onClick={() => setShowAddForm(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
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
                Preference
              </label>
              <textarea
                value={newPreference.preference_text}
                onChange={(e) => setNewPreference({...newPreference, preference_text: e.target.value})}
                placeholder="Describe your coding preference..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Context (optional)
              </label>
              <input
                type="text"
                value={newPreference.context}
                onChange={(e) => setNewPreference({...newPreference, context: e.target.value})}
                placeholder="When this applies..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                  <option key={strength.value} value={strength.value}>
                    {strength.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <Check className="h-4 w-4" />
                Add Preference
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Edit Form */}
      {editingPreference && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Edit Preference</h3>
            <button
              onClick={() => setEditingPreference(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <form onSubmit={handleUpdatePreference} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={editingPreference.category}
                onChange={(e) => setEditingPreference({...editingPreference, category: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {CATEGORIES.map(cat => (
                  <option key={cat} value={cat}>{formatCategory(cat)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Preference
              </label>
              <textarea
                value={editingPreference.preference_text}
                onChange={(e) => setEditingPreference({...editingPreference, preference_text: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Context (optional)
              </label>
              <input
                type="text"
                value={editingPreference.context || ''}
                onChange={(e) => setEditingPreference({...editingPreference, context: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Strength
              </label>
              <select
                value={editingPreference.strength}
                onChange={(e) => setEditingPreference({...editingPreference, strength: e.target.value as any})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {STRENGTHS.map(strength => (
                  <option key={strength.value} value={strength.value}>
                    {strength.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <Check className="h-4 w-4" />
                Update Preference
              </button>
              <button
                type="button"
                onClick={() => setEditingPreference(null)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Preferences List */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">Your Preferences</h2>
        {preferences.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow border text-center">
            <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No preferences yet</h3>
            <p className="text-gray-600 mb-4">Start building your coding profile by adding your first preference.</p>
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add Your First Preference
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {preferences.map((pref) => (
              <div key={pref.id} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded">
                        {formatCategory(pref.category)}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        pref.strength === 'weak' ? 'bg-gray-100 text-gray-600' :
                        pref.strength === 'moderate' ? 'bg-yellow-100 text-yellow-600' :
                        pref.strength === 'strong' ? 'bg-orange-100 text-orange-600' :
                        'bg-red-100 text-red-600'
                      }`}>
                        {pref.strength}
                      </span>
                    </div>
                    <p className="text-gray-900 mb-2">{pref.preference_text}</p>
                    {pref.context && (
                      <p className="text-sm text-gray-600 mb-2">{pref.context}</p>
                    )}
                    <p className="text-xs text-gray-500">
                      Added {new Date(pref.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => setEditingPreference(pref)}
                      className="text-blue-600 hover:text-blue-800 p-1"
                      title="Edit"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeletePreference(pref.id)}
                      className="text-red-600 hover:text-red-800 p-1"
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CodingPreferencesManager;